"""
Multi-Core Parallel Worker for Odia, Assamese, and Sanskrit
Executes sample generation, augmentation, and WebP compression
across isolated worker processes with strict anti-lag priority and thread limits.
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

from trio_multi_tier_engine import OdiaMultiTierOCRGenerator, AssameseMultiTierOCRGenerator, SanskritMultiTierOCRGenerator

_generator = None


def init_worker(lang_name: str, fonts_dir_str: str, data_dir_str: str, worker_id: int):
    global _generator
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        try:
            import psutil
            p = psutil.Process()
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            num_cores = os.cpu_count() or 16
            if num_cores >= 8:
                p.cpu_affinity(list(range(num_cores // 2, num_cores)))
        except Exception:
            pass

    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    try:
        import cv2
        cv2.setNumThreads(1)
    except Exception:
        pass

    seed = (os.getpid() * 10007) ^ int(time.time() * 1000) ^ (worker_id * 31337)
    random.seed(seed)

    fonts_p = Path(fonts_dir_str)
    data_p = Path(data_dir_str)

    if lang_name == "odia":
        _generator = OdiaMultiTierOCRGenerator(fonts_p, data_p)
    elif lang_name == "assamese":
        _generator = AssameseMultiTierOCRGenerator(fonts_p, data_p)
    else:
        _generator = SanskritMultiTierOCRGenerator(fonts_p, data_p)


def generate_single_sample_task(args: Tuple[str, str, bool]) -> Tuple[str, bytes, bytes, Dict[str, Any]]:
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

    json_bytes = json.dumps(meta, ensure_ascii=False).encode('utf-8')
    return sample_key, webp_bytes, json_bytes, meta
