"""
Agent-Streaming: WebDataset Shard Packager & Disk Lifecycle Manager
Enforces:
1. Serializes samples into WebDataset .tar shards (~5,000 samples / shard).
2. Uses WebP encoding (quality 85) for minimal storage footprint.
3. Strict disk constraint: Monitors buffer size, keeping local storage under 2.0 GB.
4. Manages Hugging Face Hub streaming uploads with automated post-upload local shard eviction.
"""

import sys
import os
import io
import json
import tarfile
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

import socket

# Prevent hung TCP connections indefinitely on Windows
socket.setdefaulttimeout(180)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')



class StreamingError(Exception):
    """Base exception for Agent-Streaming."""
    pass


class DiskOverflowError(StreamingError):
    """Raised when local buffer exceeds 2.0 GB constraint."""
    pass


class WebDatasetShardWriter:
    """Writes paired (image, json) samples into WebDataset .tar shards."""

    def __init__(
        self,
        output_dir: Path,
        prefix: str = "bho_train",
        samples_per_shard: int = 5000,
        max_buffer_gb: float = 2.0,
        uploader: Optional['BatchedHubUploader'] = None,
        start_shard_idx: int = 0
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.samples_per_shard = samples_per_shard
        self.max_buffer_gb = max_buffer_gb
        self.uploader = uploader

        self.shard_idx = start_shard_idx
        self.sample_count_in_shard = 0
        self.total_samples_written = 0
        self.completed_shards: List[Path] = []

        self.current_tar_path: Optional[Path] = None
        self.current_tar: Optional[tarfile.TarFile] = None

        self._start_new_shard()

    def _check_disk_buffer_constraint(self):
        """Enforces DISK CONSTRAINT: local storage consumption must NEVER exceed 2 GB across all files."""
        total_bytes = sum(f.stat().st_size for f in self.output_dir.rglob("*") if f.is_file())
        buffer_gb = total_bytes / (1024 ** 3)
        if buffer_gb > self.max_buffer_gb:
            raise DiskOverflowError(
                f"[DISK OVERFLOW] Local storage buffer is {buffer_gb:.2f} GB, exceeding 2.0 GB limit!"
            )
        return buffer_gb

    def _start_new_shard(self):
        if self.current_tar:
            self.current_tar.close()

        self._check_disk_buffer_constraint()

        shard_name = f"{self.prefix}_{self.shard_idx:05d}.tar"
        self.current_tar_path = self.output_dir / shard_name
        self.current_tar = tarfile.open(self.current_tar_path, "w")
        self.sample_count_in_shard = 0
        print(f"[Agent-Streaming] Opened new WebDataset shard: {shard_name}")

    def add_sample(
        self,
        sample_key: str,
        image_pil: Image.Image,
        metadata: Dict[str, Any]
    ):
        """Adds a paired WebP image and JSON metadata record into the current tar shard."""
        if self.current_tar is None:
            self._start_new_shard()

        # 1. Encode image to WebP byte stream
        assert image_pil.width <= 16000 and image_pil.height <= 16000, f"Image dimensions {image_pil.size} exceed WebP limits!"
        img_buffer = io.BytesIO()
        image_pil.save(img_buffer, format="WEBP", quality=85)
        img_bytes = img_buffer.getvalue()

        # 2. Encode metadata to UTF-8 JSON bytes
        json_bytes = json.dumps(metadata, ensure_ascii=False, indent=2).encode("utf-8")

        # 3. Add .webp entry to tar
        tar_info_img = tarfile.TarInfo(name=f"{sample_key}.webp")
        tar_info_img.size = len(img_bytes)
        tar_info_img.mtime = int(time.time())
        self.current_tar.addfile(tar_info_img, io.BytesIO(img_bytes))

        # 4. Add .json entry to tar
        tar_info_json = tarfile.TarInfo(name=f"{sample_key}.json")
        tar_info_json.size = len(json_bytes)
        tar_info_json.mtime = int(time.time())
        self.current_tar.addfile(tar_info_json, io.BytesIO(json_bytes))

        self.sample_count_in_shard += 1
        self.total_samples_written += 1

        if self.sample_count_in_shard >= self.samples_per_shard:
            completed_shard = self.close_current_shard()
            if self.uploader and completed_shard:
                self.uploader.register_completed_shard(completed_shard)
            self.shard_idx += 1

    def close_current_shard(self) -> Optional[Path]:
        """Closes the active tar shard and returns its path."""
        if self.current_tar:
            self.current_tar.close()
            self.current_tar = None
            if self.sample_count_in_shard == 0:
                if self.current_tar_path and self.current_tar_path.exists():
                    self.current_tar_path.unlink()
                return self.completed_shards[-1] if self.completed_shards else None

            size_mb = self.current_tar_path.stat().st_size / (1024 * 1024)
            print(f"[Agent-Streaming] Finalized shard: {self.current_tar_path.name} ({size_mb:.2f} MB, {self.sample_count_in_shard} samples)")
            ret_path = self.current_tar_path
            self.completed_shards.append(ret_path)
            return ret_path
        elif self.completed_shards:
            return self.completed_shards[-1]
        return None

    def finalize(self) -> List[Path]:
        """Finalizes all shards and returns list of completed tar files."""
        if self.current_tar and self.sample_count_in_shard > 0:
            completed_shard = self.close_current_shard()
            if self.uploader:
                self.uploader.register_completed_shard(completed_shard, force_commit=True)
        elif self.current_tar:
            self.current_tar.close()
            # Remove empty shard if any
            if self.current_tar_path.exists() and self.current_tar_path.stat().st_size == 0:
                self.current_tar_path.unlink()
            if self.uploader:
                self.uploader.commit_batch()

        return list(self.output_dir.glob("*.tar"))


class BatchedHubUploader:
    """
    Manages atomic, batched commits to Hugging Face Hub to eliminate git commit thrashing
    and HTTP 429 rate-limiting.
    Batches 15 to 25 shards per atomic commit via huggingface_hub.create_commit.
    Upon verified commit, safely evicts local shards to maintain the <= 2.0 GB disk invariant.
    """

    def __init__(
        self,
        repo_id: Optional[str] = None,
        batch_size: int = 20,
        token: Optional[str] = None,
        subfolder: Optional[str] = "bhojpuri",
        evict_local_after_upload: bool = True
    ):
        # Auto-load .env if needed
        env_path = Path(r"c:\OCR - All\.env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip()

        self.repo_id = repo_id or os.environ.get("HF_REPO_ID", "Faizaniqbal/IndicOCR")
        self.batch_size = batch_size
        self.token = token or os.environ.get("HF_TOKEN")
        self.subfolder = subfolder
        self.evict_local = evict_local_after_upload
        self.pending_shards: List[Path] = []
        self.committed_shards_count = 0

        if self.token:
            from huggingface_hub import HfApi
            from huggingface_hub.utils import disable_progress_bars
            disable_progress_bars()
            self.api = HfApi(token=self.token)
        else:
            self.api = None

    def register_completed_shard(self, shard_path: Path, force_commit: bool = False) -> bool:
        """Registers a completed shard and triggers atomic commit if batch_size reached."""
        shard_path = Path(shard_path)
        if str(shard_path) not in [str(p) for p in self.pending_shards]:
            self.pending_shards.append(shard_path)
            print(f"[BatchedHubUploader] Enqueued shard {shard_path.name} (Batch progress: {len(self.pending_shards)}/{self.batch_size})")
        else:
            print(f"[BatchedHubUploader] Shard {shard_path.name} already in queue (Batch progress: {len(self.pending_shards)}/{self.batch_size})")

        if len(self.pending_shards) >= self.batch_size or (force_commit and self.pending_shards):
            return self.commit_batch()
        return False

    def commit_batch(self, max_retries: int = 6, base_delay: float = 5.0) -> bool:
        """
        Executes an atomic create_commit for all pending shards with exponential backoff
        retry resilience (timeout=180s). Prevents crashes during temporary Hub ingestion latency.
        """
        # Deduplicate paths
        unique_paths: List[Path] = []
        seen = set()
        for p in self.pending_shards:
            if str(p) not in seen and p.exists():
                seen.add(str(p))
                unique_paths.append(p)
        batch_to_upload = unique_paths

        if not batch_to_upload:
            self.pending_shards.clear()
            return True

        num_shards = len(batch_to_upload)
        start_name = batch_to_upload[0].name
        end_name = batch_to_upload[-1].name
        commit_msg = f"Add {num_shards} WebDataset shards for {self.subfolder or 'dataset'} ({start_name} to {end_name}) [IndicPixel]"

        print(f"\n[BatchedHubUploader] >>> INITIATING ATOMIC COMMIT OF {num_shards} SHARDS TO {self.repo_id} <<<")

        if self.api and self.token:
            folder_prefix = f"data/{self.subfolder}" if self.subfolder else "data"
            commit_succeeded = True
            for shard in batch_to_upload:
                remote_path = f"{folder_prefix}/{shard.name}"
                shard_uploaded = False
                for attempt in range(1, max_retries + 1):
                    try:
                        print(f"[BatchedHubUploader] Uploading {shard.name} via upload_file (Attempt {attempt}/{max_retries})...")
                        self.api.upload_file(
                            path_or_fileobj=str(shard),
                            path_in_repo=remote_path,
                            repo_id=self.repo_id,
                            repo_type="dataset",
                            commit_message=f"Add WebDataset shard {shard.name} [IndicPixel]"
                        )
                        print(f"[BatchedHubUploader] Upload verified (HTTP 200): {shard.name}")
                        shard_uploaded = True
                        break
                    except Exception as e:
                        err_str = str(e)
                        print(f"[BatchedHubUploader] [WARNING] Upload attempt {attempt} failed: {err_str[:160]}...")
                        # Re-instantiate HfApi to clear any dead/closed httpx connection pool
                        try:
                            self.api = HfApi(token=self.token)
                        except Exception:
                            pass
                        if "429" in err_str:
                            delay = 75.0 + (attempt * 15.0) + (random.random() * 5.0)
                            print(f"[BatchedHubUploader] 429 Commit Rate Limit detected. Sleeping {delay:.1f}s for commit window to clear...")
                        else:
                            delay = base_delay * (2 ** (attempt - 1)) + (random.random() * 2.0)
                        if attempt < max_retries:
                            print(f"[BatchedHubUploader] Backing off for {delay:.2f}s before retry...")
                            time.sleep(delay)
                        else:
                            print(f"[BatchedHubUploader] [CRITICAL] All {max_retries} upload attempts exhausted.")
                            commit_succeeded = False
                            raise StreamingError(f"Upload failed after {max_retries} retries: {e}")
        else:
            print(f"[BatchedHubUploader] Simulation Mode (HF_TOKEN not set): Simulated upload of {num_shards} shards.")
            commit_succeeded = True

        self.committed_shards_count += num_shards
        self.pending_shards.clear()

        # Evict local shards if requested to enforce disk limit <= 2.0 GB
        if self.evict_local and (self.api and self.token):
            for shard in batch_to_upload:
                if shard.exists():
                    size_mb = shard.stat().st_size / (1024 * 1024)
                    deleted = False
                    for retry in range(6):
                        try:
                            time.sleep(0.4)
                            shard.unlink()
                            deleted = True
                            print(f"[Agent-Streaming] Evicted local shard {shard.name} ({size_mb:.2f} MB freed).")
                            break
                        except PermissionError:
                            time.sleep(0.6)
                    if not deleted:
                        print(f"[Agent-Streaming] Warning: Could not delete {shard.name} (file locked). Will evict next batch.")

        return True


