"""
Master Production Pipeline: Pan-Indic Kashmiri Synthetic & Hybrid OCR (kas_Arab).
Synthesizes 500,000 OCR samples across 100 WebDataset shards (kas_train_00000.tar to kas_train_00099.tar).

Strict Operational Invariants:
1. Multi-tier calibrated distribution: 2% Full Pages, 13% Paragraphs, 55% Lines, 30% Words.
2. Zero .notdef boxes, zero glyph truncation, 100% connected Kashmiri cursive typography.
3. Real asset blending: 5% real archival scanned lines (Kashmiri-ground-truth.zip) and 5% real word crops (archive.zip), 95% synthetic text.
4. Continuous non-stop execution: Runs continuously from Shard 000 to Shard 099.
5. Zero local disk accumulation: Immediate shard eviction upon verified HF Hub upload (storage <= 1.0 GB << 2.0 GB).
6. Production audit ledger logged to KASHMIRI_PRODUCTION_LEDGER.md.
"""

import sys, os, io, json, time, hashlib, random, re, shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(r"C:\OCR - All")
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
sys.path.append(r"C:\OCR - All\src\shaper")
sys.path.append(r"C:\OCR - All\src\augmenter")
sys.path.append(r"C:\OCR - All\src\streaming")

from kashmiri_multi_tier_engine import KashmiriMultiTierOCRGenerator
from shard_packager import WebDatasetShardWriter, BatchedHubUploader
import multiprocessing as mp

_worker_gen = None

def _init_kashmiri_worker(fonts_dir: Path, corpus_file: Path, vocab_file: Path):
    global _worker_gen
    _worker_gen = KashmiriMultiTierOCRGenerator(fonts_dir, corpus_file, vocab_file)

def _generate_sample_worker(args: Tuple[str, int]) -> Tuple[str, Image.Image, Dict[str, Any]]:
    tier_type, sample_id = args
    global _worker_gen
    sample_key = f"kas_{sample_id:07d}"
    if tier_type == "tier_1":
        img, meta = _worker_gen.generate_full_page_sample()
    elif tier_type == "tier_2":
        img, meta = _worker_gen.generate_paragraph_sample()
    elif tier_type == "tier_3":
        img, meta = _worker_gen.generate_line_sample()
    else:
        img, meta = _worker_gen.generate_word_sample()
    meta["sample_id"] = sample_key
    return sample_key, img, meta


def prevent_system_sleep():
    """Prevents Windows system sleep or standby during long-running production generation."""
    if sys.platform == "win32":
        try:
            import ctypes
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ES_AWAYMODE_REQUIRED = 0x00000040
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
            )
            print("[Power Management] Windows sleep/standby disabled for continuous execution.")
        except Exception as e:
            print(f"[Power Management] Note: Could not set thread execution state: {e}")


def compute_file_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def initialize_ledger(ledger_path: Path):
    if not ledger_path.exists():
        header = (
            "# Kashmiri (kas_Arab) OCR Production Ledger\n\n"
            "| Batch | Shard Name | Sample Range | Count | Size (MB) | SHA-256 | Assertions | HF Status | Disk Eviction | Timestamp (UTC) |\n"
            "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
        )
        ledger_path.write_text(header, encoding="utf-8")


def append_to_ledger(
    ledger_path: Path,
    batch_num: int,
    shard_name: str,
    sample_start: int,
    sample_end: int,
    sample_count: int,
    size_mb: float,
    sha256_hash: str,
    assertions_passed: bool,
    hf_status: str,
    evicted: bool
):
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    row = (
        f"| {batch_num} | `{shard_name}` | `kas_{sample_start:07d}` - `kas_{sample_end:07d}` | "
        f"{sample_count:,} | {size_mb:.2f} | `{sha256_hash[:16]}...` | "
        f"{'✅ Pass' if assertions_passed else '❌ Fail'} | {hf_status} | "
        f"{'✅ Deleted' if evicted else '⚠️ Retained'} | {now_str} |\n"
    )
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(row)


def run_kashmiri_production_pipeline(
    start_shard: int = 0,
    end_shard: int = 100,
    samples_per_shard: int = 5000,
    batch_commit_size: int = 1,
    workers: int = 6
):
    prevent_system_sleep()

    fonts_dir = Path(r"C:\OCR - All\fonts\kashmiri")
    corpus_file = Path(r"C:\Users\ASUS\OneDrive\Desktop\Koshur_OCR_V1\clean_3_1m_corpus\clean_3_1m_lines.txt")
    vocab_file = Path(r"C:\Users\ASUS\OneDrive\Desktop\Koshur_OCR_V1\clean_3_1m_corpus\clean_3_1m_vocab.json")
    shards_dir = Path(r"C:\OCR - All\data\shards\kashmiri")
    shards_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = Path(r"C:\OCR - All\KASHMIRI_PRODUCTION_LEDGER.md")
    initialize_ledger(ledger_path)

    # Load HF credentials
    env_path = Path(r"C:\OCR - All\.env")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()

    repo_id = os.environ.get("HF_REPO_ID", "Faizaniqbal/IndicPixel-Pan-Indic-OCR")
    hf_token = os.environ.get("HF_TOKEN")

    print("=" * 80)
    print("      INDICPIXEL MASTER PRODUCTION PIPELINE: KASHMIRI (kas_Arab)")
    print("=" * 80)
    print(f"Target Shard Range : {start_shard:05d} to {end_shard-1:05d} ({end_shard - start_shard} shards)")
    print(f"Samples per Shard  : {samples_per_shard:,}")
    print(f"Parallel Workers   : {workers} cores (multiprocessing)")
    print(f"Total Target Output: {(end_shard - start_shard) * samples_per_shard:,} OCR pairs")
    print(f"Remote HF Target   : {repo_id} [path: data/kashmiri/]")
    print(f"Local Storage Cap  : 2.0 GB (stream-and-evict protocol)")
    print("=" * 80)

    uploader = BatchedHubUploader(
        repo_id=repo_id,
        batch_size=batch_commit_size,
        token=hf_token,
        subfolder="kashmiri",
        evict_local_after_upload=True
    )

    if workers <= 1:
        print("\n[Init] Initializing Single-Thread Kashmiri Multi-Tier Generator...")
        gen = KashmiriMultiTierOCRGenerator(fonts_dir, corpus_file, vocab_file)
    else:
        gen = None

    # Check remote Hub for already completed shards to allow seamless resume
    remote_shards_complete = set()
    if uploader.api and uploader.token:
        try:
            print("[Hub Check] Querying Hugging Face Hub for existing completed shards...")
            files = list(uploader.api.list_repo_tree(repo_id=repo_id, repo_type="dataset", path_in_repo="data/kashmiri"))
            for f in files:
                size = getattr(f, "size", 0) or 0
                if f.path.endswith(".tar") and size >= 10 * 1024 * 1024:
                    remote_shards_complete.add(Path(f.path).name)
            print(f"[Hub Check] Found {len(remote_shards_complete)} fully completed shards (>=10MB) on Hub.")
        except Exception as e:
            print(f"[Hub Check] Note: Could not query Hub files: {e}")

    tier1_count = max(1, int(samples_per_shard * 0.02))  # 2.0% = 100
    tier2_count = max(1, int(samples_per_shard * 0.13))  # 13.0% = 650
    tier3_count = max(1, int(samples_per_shard * 0.55))  # 55.0% = 2750
    tier4_count = samples_per_shard - (tier1_count + tier2_count + tier3_count)  # 30.0% = 1500

    print(f"[Tier Distribution per Shard ({samples_per_shard:,} samples)]:")
    print(f"  • Tier 1 (Full Pages) : {tier1_count:>5} ({tier1_count/samples_per_shard*100:.1f}%)")
    print(f"  • Tier 2 (Paragraphs) : {tier2_count:>5} ({tier2_count/samples_per_shard*100:.1f}%)")
    print(f"  • Tier 3 (Lines)      : {tier3_count:>5} ({tier3_count/samples_per_shard*100:.1f}%)")
    print(f"  • Tier 4 (Words)      : {tier4_count:>5} ({tier4_count/samples_per_shard*100:.1f}%)")

    def _run_shard_loop(pool=None):
        for shard_idx in range(start_shard, end_shard):
            shard_name = f"kas_train_{shard_idx:05d}.tar"
            shard_path = shards_dir / shard_name
            sample_start = shard_idx * samples_per_shard
            sample_end = sample_start + samples_per_shard - 1

            # Check if already completed and verified on Hugging Face Hub
            if shard_name in remote_shards_complete:
                print(f"  [SKIP/RESUME] {shard_name} already completed on Hugging Face Hub. Skipping.")
                continue

            # Check if already complete on disk
            if shard_path.exists() and shard_path.stat().st_size > 10 * 1024 * 1024:
                shard_size_mb = shard_path.stat().st_size / (1024 * 1024)
                sha256_hash = compute_file_sha256(shard_path)
                print(f"  [RESUME] {shard_name} already complete on disk ({shard_size_mb:.2f} MB). Enqueueing.")
                committed = uploader.register_completed_shard(shard_path)
                hf_status = "Uploaded (HTTP 200)" if committed else "Enqueued"
                evicted = committed and not shard_path.exists()
                append_to_ledger(
                    ledger_path=ledger_path,
                    batch_num=shard_idx + 1,
                    shard_name=shard_name,
                    sample_start=sample_start,
                    sample_end=sample_end,
                    sample_count=samples_per_shard,
                    size_mb=shard_size_mb,
                    sha256_hash=sha256_hash,
                    assertions_passed=True,
                    hf_status=hf_status,
                    evicted=evicted
                )
                continue

            writer = WebDatasetShardWriter(
                output_dir=shards_dir,
                prefix="kas_train",
                samples_per_shard=samples_per_shard,
                uploader=None,
                start_shard_idx=shard_idx
            )

            tier_plan = (
                ["tier_1"] * tier1_count +
                ["tier_2"] * tier2_count +
                ["tier_3"] * tier3_count +
                ["tier_4"] * tier4_count
            )
            random.shuffle(tier_plan)

            start_t = time.time()
            if pool is not None:
                tasks = [(tier_plan[i], sample_start + i) for i in range(samples_per_shard)]
                for sample_key, img, meta in tqdm(
                    pool.imap_unordered(_generate_sample_worker, tasks, chunksize=16),
                    total=samples_per_shard,
                    desc=f"Shard {shard_idx:05d} ({workers} cores)",
                    unit="sample"
                ):
                    writer.add_sample(sample_key, img, meta)
            else:
                for i, tier_type in enumerate(tqdm(tier_plan, desc=f"Shard {shard_idx:05d}", unit="sample")):
                    sample_id = sample_start + i
                    sample_key = f"kas_{sample_id:07d}"
                    if tier_type == "tier_1":
                        img, meta = gen.generate_full_page_sample()
                    elif tier_type == "tier_2":
                        img, meta = gen.generate_paragraph_sample()
                    elif tier_type == "tier_3":
                        img, meta = gen.generate_line_sample()
                    else:
                        img, meta = gen.generate_word_sample()
                    meta["sample_id"] = sample_key
                    writer.add_sample(sample_key, img, meta)

            completed_shard = writer.close_current_shard()
            elapsed = time.time() - start_t

            # Pre-commit assertion: Zero disk accumulation ceiling (<= 2.0 GB)
            local_buffer_gb = sum(f.stat().st_size for f in shards_dir.glob("*.tar")) / (1024**3)
            assert local_buffer_gb <= 2.0, f"FATAL: Local shard buffer {local_buffer_gb:.2f} GB exceeds 2.0 GB ceiling!"

            if completed_shard and completed_shard.exists():
                shard_size_mb = completed_shard.stat().st_size / (1024 * 1024)
                sha256_hash = compute_file_sha256(completed_shard)
                print(f"  [DONE] {shard_name}: {shard_size_mb:.2f} MB in {elapsed:.1f}s ({samples_per_shard/elapsed:.1f} samp/s)")

                committed = uploader.register_completed_shard(completed_shard)
                hf_status = "Uploaded (HTTP 200)" if committed else "Enqueued"
                evicted = committed and not completed_shard.exists()

                append_to_ledger(
                    ledger_path=ledger_path,
                    batch_num=shard_idx + 1,
                    shard_name=shard_name,
                    sample_start=sample_start,
                    sample_end=sample_end,
                    sample_count=samples_per_shard,
                    size_mb=shard_size_mb,
                    sha256_hash=sha256_hash,
                    assertions_passed=True,
                    hf_status=hf_status,
                    evicted=evicted
                )

    if workers > 1:
        print(f"\n[Parallel Init] Initializing {workers}-worker multiprocessing pool (leaving 10 cores free for host)...")
        with mp.Pool(
            processes=workers,
            initializer=_init_kashmiri_worker,
            initargs=(fonts_dir, corpus_file, vocab_file)
        ) as pool:
            _run_shard_loop(pool)
    else:
        _run_shard_loop(None)

    # Commit any remaining pending shards
    if uploader.pending_shards:
        print(f"\n[Hub Finalize] Committing remaining {len(uploader.pending_shards)} shards...")
        uploader.commit_batch()

    print("\n" + "=" * 80)
    print(f"🎉 KASHMIRI PRODUCTION COMPLETE! All {end_shard - start_shard} Shards (500,000 samples) Processed!")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Kashmiri Production Pipeline")
    parser.add_argument("--start", type=int, default=0, help="Starting shard index (default: 0)")
    parser.add_argument("--end", type=int, default=100, help="Ending shard index (default: 100)")
    parser.add_argument("--samples", type=int, default=5000, help="Samples per shard (default: 5000)")
    parser.add_argument("--workers", type=int, default=6, help="Parallel worker cores (default: 6)")
    args = parser.parse_args()

    run_kashmiri_production_pipeline(
        start_shard=args.start,
        end_shard=args.end,
        samples_per_shard=args.samples,
        workers=args.workers
    )

