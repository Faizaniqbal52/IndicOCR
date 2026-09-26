"""
Agent-Shaper / Agent-Augmenter Multi-Core Parallel Worker for Konkani (gom_Deva)
Executes high-throughput sample generation, augmentation, and WebP compression
across isolated worker processes on multi-core systems.
"""

import sys
import os
import io
import json
import time
import random
from pathlib import Path
from typing import Tuple, Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parent.parent / "shaper"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "augmenter"))

from konkani_multi_tier_engine import KonkaniMultiTierOCRGenerator

_generator = None


def init_worker(fonts_dir_str: str, data_dir_str: str, worker_id: int):
    """Initializes the KonkaniMultiTierOCRGenerator inside the isolated worker process."""
    global _generator
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    seed = (os.getpid() * 10007) ^ int(time.time() * 1000) ^ (worker_id * 31337)
    random.seed(seed)
    _generator = KonkaniMultiTierOCRGenerator(Path(fonts_dir_str), Path(data_dir_str))


def generate_single_sample_task(args: Tuple[str, str, bool]) -> Tuple[str, bytes, bytes, Dict[str, Any]]:
    """
    Worker task: generates 1 sample, compresses directly to WebP, and serializes metadata.
    Returns (sample_key, webp_bytes, json_bytes, metadata_dict).
    """
    global _generator
    sample_key, tier_type, is_clean = args
    gen = _generator

    if tier_type == "full_page":
        img, meta = gen.generate_full_page_sample(is_clean=is_clean)
    elif tier_type == "paragraph":
        img, meta = gen.generate_paragraph_sample(is_clean=is_clean)
    elif tier_type == "line":
        img, meta = gen.generate_line_sample(is_clean=is_clean)
    else:
        img, meta = gen.generate_word_sample(is_clean=is_clean)

    meta["sample_key"] = sample_key
    meta["is_clean"] = is_clean

    img_buf = io.BytesIO()
    img.save(img_buf, format="WEBP", quality=85)
    webp_bytes = img_buf.getvalue()

    json_bytes = json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8")
    return sample_key, webp_bytes, json_bytes, meta
