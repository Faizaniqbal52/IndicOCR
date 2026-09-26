"""
===================================================================================
INDICPIXEL UNIVERSAL KAGGLE CLOUD FLEET FACTORY & DEPLOYER
Automated generation, staging, and deployment of dedicated Kaggle Cloud workers
===================================================================================
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(r"c:\OCR - All")
SOURCE_PIPELINE = REPO_ROOT / "kaggle_cloud_pipeline" / "indicpixel_kaggle_production_pipeline.py"
WORKERS_BASE = REPO_ROOT / "kaggle_workers"

# 19 Completed Languages in Hugging Face Repository (Faizaniqbal/IndicOCR) - DO NOT RE-RUN
COMPLETED_LANGS = {
    "kan": "Kannada (100 shards / 500k samples)",
    "nep": "Nepali (100 shards / 500k samples)",
    "sat": "Santali (100 shards / 500k samples)",
    "bho": "Bhojpuri (100 shards / 500k samples)",
    "kas": "Kashmiri (100 shards / 500k samples)",
    "doi": "Dogri (50 shards / 250k samples)",
    "gom": "Konkani (50 shards / 250k samples)",
    "mai": "Maithili (50 shards / 250k samples)",
    "hin": "Hindi (200 shards / 1M samples)",
    "ben": "Bengali (200 shards / 1M samples)",
    "tam": "Tamil (200 shards / 1M samples)",
    "mar": "Marathi (200 shards / 1M samples)",
    "urd": "Urdu (200 shards / 1M samples)",
    "tel": "Telugu (100 shards / 500k samples)",
    "guj": "Gujarati (100 shards / 500k samples)",
    "mal": "Malayalam (100 shards / 500k samples)",
    "ori": "Odia (100 shards / 500k samples)",
    "asm": "Assamese (100 shards / 500k samples)",
    "san": "Sanskrit (100 shards / 500k samples)",
}

# 4 In-Progress Languages on Kaggle Cloud (Running to reach 100 shards)
ACTIVE_CLOUD_RUNS = [
    ("mni", "Manipuri", "ac2sny/indicpixel-prod-mni"),
    ("pan", "Punjabi",  "ac2sny/indicpixel-prod-pan"),
    ("snd", "Sindhi",   "ac2sny/indicpixel-prod-snd"),
    ("brx", "Bodo",     "ac2sny/indicpixel-prod-brx"),
]

# Genuinely New Expansion Languages (0 Shards in HF Repository)
NEW_EXPANSION_LANGS = [
    ("awa", "Awadhi",   "ac2sny/indicpixel-prod-awa"),
    ("new", "Newari",   "ac2sny/indicpixel-prod-new"),
    ("tcy", "Tulu",     "ac2sny/indicpixel-prod-tcy"),
    ("anp", "Angika",   "ac2sny/indicpixel-prod-anp"),
]

ALL_SUPPORTED_LANGS = ACTIVE_CLOUD_RUNS + NEW_EXPANSION_LANGS
LANG_MAP = {code: (name, slug) for code, name, slug in ALL_SUPPORTED_LANGS}


def check_kernel_status(slug: str) -> str:
    try:
        res = subprocess.run(
            [sys.executable, "-m", "kaggle", "kernels", "status", slug],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        out = res.stdout.strip()
        if "KernelWorkerStatus.COMPLETE" in out:
            return "COMPLETE"
        elif "KernelWorkerStatus.RUNNING" in out:
            return "RUNNING"
        elif "KernelWorkerStatus.ERROR" in out:
            return "ERROR"
        elif "KernelWorkerStatus.QUEUED" in out:
            return "QUEUED"
        else:
            return out if out else "NOT FOUND / NEVER RUN"
    except Exception as e:
        return f"CHECK ERROR ({e})"


def prepare_worker(code: str, name: str, slug: str, master_code: str) -> Path:
    w_dir = WORKERS_BASE / f"worker_{code}"
    w_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write kernel-metadata.json
    meta = {
        "id": slug,
        "title": f"indicpixel-prod-{code}",
        "code_file": "pipeline.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": "true",
        "enable_gpu": "false",
        "enable_tpu": "false",
        "enable_internet": "true",
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": []
    }
    with open(w_dir / "kernel-metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # 2. Inject default target language into pipeline.py
    worker_code = master_code.replace(
        'target_langs_env = os.environ.get("TARGET_LANGS", "kan").strip()',
        f'target_langs_env = os.environ.get("TARGET_LANGS", "{code}").strip()'
    )
    # Also handle fallback replace if present
    if 'target_langs_env = os.environ.get("TARGET_LANGS", "").strip()' in worker_code:
        worker_code = worker_code.replace(
            'target_langs_env = os.environ.get("TARGET_LANGS", "").strip()',
            f'target_langs_env = os.environ.get("TARGET_LANGS", "{code}").strip()'
        )

    with open(w_dir / "pipeline.py", "w", encoding="utf-8") as f:
        f.write(worker_code)

    return w_dir


def push_worker(w_dir: Path) -> bool:
    print(f"  [PUSH] Uploading {w_dir.name} to Kaggle Cloud via API...", flush=True)
    try:
        res = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "kaggle", "kernels", "push", "-p", str(w_dir)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if "successfully pushed" in res.stdout:
            print(f"  [PUSH SUCCESS] {w_dir.name} deployed cleanly to Kaggle Cloud!", flush=True)
            return True
        else:
            print(f"  [PUSH WARNING] Kaggle responded: {res.stdout.strip()} | {res.stderr.strip()}", flush=True)
            return False
    except Exception as e:
        print(f"  [PUSH ERROR] Failed to push {w_dir.name}: {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="IndicPixel Kaggle Fleet Factory & Deployer")
    parser.add_argument(
        "--langs",
        type=str,
        default="all",
        help="Comma-separated language codes to prepare (e.g. 'pan,snd,brx,bho,mai,gom,kas,doi') or 'all'"
    )
    parser.add_argument("--push", action="store_true", help="Automatically push prepared workers to Kaggle")
    parser.add_argument("--status", action="store_true", help="Check live status of all supported workers on Kaggle")
    args = parser.parse_args()

    print("=" * 80)
    print("INDICPIXEL KAGGLE PRODUCTION FLEET FACTORY")
    print("=" * 80)

    if args.status:
        print(f"{'Code':<6} | {'Language':<16} | {'Kernel Slug':<30} | {'Status'}", flush=True)
        print("-" * 75, flush=True)
        for code, name, slug in ALL_SUPPORTED_LANGS:
            st = check_kernel_status(slug)
            print(f"{code:<6} | {name:<16} | {slug:<30} | {st}", flush=True)
        return

    # Select target languages
    if args.langs.lower() == "all":
        targets = ALL_SUPPORTED_LANGS
    elif args.langs.lower() == "resume":
        # Target errored or interrupted active runs
        targets = [(c, n, s) for c, n, s in ALL_SUPPORTED_LANGS if c in ["pan", "snd", "brx", "mni"]]
    elif args.langs.lower() == "next":
        # Target the truly unstarted new expansion languages (0 shards on HF)
        targets = NEW_EXPANSION_LANGS
    else:
        req_codes = [c.strip().lower() for c in args.langs.split(",") if c.strip()]
        targets = []
        for c in req_codes:
            if c in COMPLETED_LANGS:
                print(f"[REDUNDANCY GUARD] '{c}' is ALREADY COMPLETED on Hugging Face: {COMPLETED_LANGS[c]}. Skipping.")
                continue
            if c in LANG_MAP:
                targets.append((c, LANG_MAP[c][0], LANG_MAP[c][1]))
            else:
                print(f"[WARN] Unknown language code '{c}'. Skipping.")

    print(f"Selected {len(targets)} languages: {[t[0] for t in targets]}")
    print(f"Reading master pipeline template from: {SOURCE_PIPELINE}...")
    with open(SOURCE_PIPELINE, "r", encoding="utf-8") as f:
        master_code = f.read()

    WORKERS_BASE.mkdir(parents=True, exist_ok=True)
    prepared_dirs = []

    for code, name, slug in targets:
        w_dir = prepare_worker(code, name, slug, master_code)
        prepared_dirs.append((code, name, slug, w_dir))
        print(f"  [STAGED] {name:<14} ({code}): {w_dir}")

    if args.push:
        print("\n" + "=" * 80)
        print("PUSHING PREPARED WORKERS TO KAGGLE CLOUD")
        print("=" * 80)
        for code, name, slug, w_dir in prepared_dirs:
            push_worker(w_dir)

    print("\n[COMPLETE] Fleet preparation finished successfully!")


if __name__ == "__main__":
    main()
