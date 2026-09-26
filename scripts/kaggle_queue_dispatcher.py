"""
===================================================================================
INDICPIXEL KAGGLE PRODUCTION FLEET QUEUE DISPATCHER 2.0
Autonomous Slot Monitor, Failure Recovery, and Dynamic Queue Dispatcher
===================================================================================
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(r"c:\OCR - All")
WORKERS_BASE = REPO_ROOT / "kaggle_workers"

# Completed languages in Hugging Face Repository - NEVER QUEUE OR RERUN
COMPLETED_LANGS = {
    "kan": "Kannada (100 shards / 500k samples)",
    "nep": "Nepali (100 shards / 500k samples)",
    "sat": "Santali (100 shards / 500k samples)",
    "bho": "Bhojpuri (100 shards / 500k samples)",
    "kas": "Kashmiri (100 shards / 500k samples)",
    "doi": "Dogri (50 shards / 250k samples)",
    "gom": "Konkani (50 shards / 250k samples)",
    "mai": "Maithili (50 shards / 250k samples)",
}

# All supported languages in the fleet (Active Runs + Genuine Expansion)
FLEET_REGISTRY = {
    "pan": ("Punjabi",  "ac2sny/indicpixel-prod-pan"),
    "snd": ("Sindhi",   "ac2sny/indicpixel-prod-snd"),
    "brx": ("Bodo",     "ac2sny/indicpixel-prod-brx"),
    "mni": ("Manipuri", "ac2sny/indicpixel-prod-mni"),
    "awa": ("Awadhi",   "ac2sny/indicpixel-prod-awa"),
    "new": ("Newari",   "ac2sny/indicpixel-prod-new"),
    "tcy": ("Tulu",     "ac2sny/indicpixel-prod-tcy"),
    "anp": ("Angika",   "ac2sny/indicpixel-prod-anp"),
}


def check_kernel_status(kernel_id: str) -> str:
    try:
        res = subprocess.run(
            [sys.executable, "-m", "kaggle", "kernels", "status", kernel_id],
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
            return out if out else "UNKNOWN"
    except Exception as e:
        return f"UNKNOWN: {e}"


def push_worker(code: str) -> bool:
    worker_dir = WORKERS_BASE / f"worker_{code}"
    if not worker_dir.exists():
        print(f"[DISPATCHER ERROR] Worker directory does not exist: {worker_dir}", flush=True)
        return False

    name, slug = FLEET_REGISTRY[code]
    print(f"\n[DISPATCHER] Launching worker {name} ({code}) from {worker_dir.name}...", flush=True)
    try:
        res = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "kaggle", "kernels", "push", "-p", str(worker_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60
        )
        if "successfully pushed" in res.stdout:
            print(f"[DISPATCHER SUCCESS] {name} ({slug}) pushed and queued on Kaggle Cloud!", flush=True)
            return True
        else:
            print(f"[DISPATCHER WARN] Push response: {res.stdout.strip()} | {res.stderr.strip()}", flush=True)
            return False
    except Exception as e:
        print(f"[DISPATCHER ERROR] Failed to push {code}: {e}", flush=True)
        return False


def run_fleet_dispatcher(
    initial_active: List[str],
    queued_langs: List[str],
    max_concurrent: int = 4,
    poll_interval: int = 45,
    auto_retry_errors: bool = True,
    max_retries_per_worker: int = 2
):
    print("=" * 80)
    print("KAGGLE PRODUCTION FLEET QUEUE DISPATCHER 2.0")
    print(f"Max Concurrent Slots : {max_concurrent}")
    print(f"Initial Active Fleet : {initial_active}")
    print(f"Queued for Launch    : {queued_langs}")
    print(f"Poll Interval        : {poll_interval}s")
    print(f"Auto-Retry on Error  : {auto_retry_errors} (Max {max_retries_per_worker} retries)")
    print("=" * 80, flush=True)

    active_map: Dict[str, str] = {code: FLEET_REGISTRY[code][1] for code in initial_active if code in FLEET_REGISTRY}
    pending_queue: List[str] = [code for code in queued_langs if code in FLEET_REGISTRY and code not in active_map]
    retry_counts: Dict[str, int] = {code: 0 for code in FLEET_REGISTRY}
    completed_langs: List[str] = []

    cycle = 0
    while active_map or pending_queue:
        cycle += 1
        time.sleep(poll_interval)
        print(f"\n--- [Cycle #{cycle} @ {time.strftime('%H:%M:%S')}] Active: {len(active_map)} | Queued: {len(pending_queue)} | Done: {len(completed_langs)} ---", flush=True)

        # Check each active kernel
        for code in list(active_map.keys()):
            slug = active_map[code]
            name = FLEET_REGISTRY[code][0]
            st = check_kernel_status(slug)
            print(f"  [{code.upper():<4}] {name:<14} -> {st}", flush=True)

            if st == "COMPLETE":
                print(f"  >>> [MILESTONE] {name} ({code}) COMPLETED ALL SHARDS ON KAGGLE CLOUD!", flush=True)
                completed_langs.append(code)
                del active_map[code]

            elif st == "ERROR":
                if auto_retry_errors and retry_counts[code] < max_retries_per_worker:
                    retry_counts[code] += 1
                    print(f"  >>> [AUTO-RESUME] {name} ({code}) encountered ERROR. Auto-resuming (Attempt {retry_counts[code]}/{max_retries_per_worker})...", flush=True)
                    if push_worker(code):
                        print(f"  >>> [RESUMED] {name} re-pushed. Will auto-skip existing shards on Hub!", flush=True)
                    else:
                        print(f"  >>> [FAIL] Could not re-push {code}. Unblocking slot.", flush=True)
                        del active_map[code]
                else:
                    print(f"  >>> [QUARANTINE] {name} ({code}) failed and exceeded retry limits. Unblocking slot for next language.", flush=True)
                    del active_map[code]

        # Dispatch pending languages if slots are available
        while len(active_map) < max_concurrent and pending_queue:
            next_code = pending_queue.pop(0)
            next_name, next_slug = FLEET_REGISTRY[next_code]
            print(f"[DISPATCHER] Free slot detected ({len(active_map)}/{max_concurrent}). Launching {next_name} ({next_code})...", flush=True)
            if push_worker(next_code):
                active_map[next_code] = next_slug
                print(f"[DISPATCHER] {next_name} is now actively running in slot {len(active_map)}!", flush=True)
            else:
                # Re-queue at the end
                pending_queue.append(next_code)
                break

    print("\n" + "=" * 80)
    print("ALL PRODUCTION WORKERS HAVE FINISHED EXECUTION!")
    print(f"Completed Languages: {completed_langs}")
    print("=" * 80, flush=True)


def main():
    parser = argparse.ArgumentParser(description="IndicPixel Kaggle Fleet Queue Dispatcher")
    parser.add_argument(
        "--active",
        type=str,
        default="",
        help="Comma-separated language codes currently running on Kaggle (e.g. 'mni')"
    )
    parser.add_argument(
        "--queue",
        type=str,
        default="",
        help="Comma-separated language codes to queue (e.g. 'pan,snd,brx,bho,mai,gom,kas,doi')"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=4,
        help="Max simultaneous running kernels (default: 4, Kaggle allows up to 5)"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=45,
        help="Seconds between status checks (default: 45s)"
    )
    parser.add_argument(
        "--no-retry",
        action="store_true",
        help="Do not automatically re-push/resume errored workers"
    )
    args = parser.parse_args()

    raw_queued = [c.strip().lower() for c in args.queue.split(",") if c.strip()]
    queued_langs = []
    for c in raw_queued:
        if c in COMPLETED_LANGS:
            print(f"[REDUNDANCY GUARD] Refusing to queue '{c}': ALREADY COMPLETED on Hugging Face ({COMPLETED_LANGS[c]}).")
            continue
        queued_langs.append(c)

    # If no active specified, detect automatically from Kaggle
    if not active_langs:
        print("Detecting currently running Kaggle kernels...", flush=True)
        for code, (name, slug) in FLEET_REGISTRY.items():
            st = check_kernel_status(slug)
            if st == "RUNNING" or st == "QUEUED":
                active_langs.append(code)
                print(f"  [FOUND RUNNING] {name} ({code})")

    run_fleet_dispatcher(
        initial_active=active_langs,
        queued_langs=queued_langs,
        max_concurrent=args.max_concurrent,
        poll_interval=args.poll_interval,
        auto_retry_errors=not args.no_retry
    )


if __name__ == "__main__":
    main()
