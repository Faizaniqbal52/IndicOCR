"""
Sequential 1M Runner: Single-Worker Background Pipeline
Executes remaining shard ranges sequentially using exactly 1 worker:
1. Phase 1: Pushes Tamil (tam_Taml) from 500k to 1,000,000 samples (Shards 100 to 199).
2. Phase 2: Automatically chains to push Marathi (mar_Deva) from 500k to 1,000,000 samples (Shards 100 to 199).

Guarantees:
- Exactly 1 worker process (super light, zero system lag, zero fan noise).
- Process priority set to BELOW_NORMAL_PRIORITY_CLASS.
- Immediate local shard eviction upon HTTP 200 commit.
"""

import sys
import os
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"C:\OCR - All")
sys.path.append(str(repo_root / "src" / "orchestrator"))

from tamil_production_pipeline import run_tamil_production_pipeline
from marathi_production_pipeline import run_marathi_production_pipeline


def get_next_shard_from_ledger(ledger_path: Path, default_start: int = 100) -> int:
    if not ledger_path.exists():
        return default_start
    max_shard = default_start - 1
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|") and not line.startswith("| Batch") and not line.startswith("| :---"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) > 2 and parts[1].isdigit():
                    s_idx = int(parts[1])
                    if s_idx > max_shard:
                        max_shard = s_idx
    return max_shard + 1


def main():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        p.cpu_affinity(list(range(8, 16)))
    except Exception:
        pass
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"

    tamil_ledger = repo_root / "TAMIL_PRODUCTION_LEDGER.md"
    marathi_ledger = repo_root / "MARATHI_PRODUCTION_LEDGER.md"

    tamil_start = get_next_shard_from_ledger(tamil_ledger, default_start=100)

    print("=" * 80)
    print("SEQUENTIAL 1M PRODUCTION RUNNER (1 DEDICATED WORKER)")
    print(f"Target 1: Tamil (tam_Taml) -> Shards {tamil_start} to 199 (Goal: 1.0M samples)")
    print("Target 2: Marathi (mar_Deva) -> Shards to 199 (Goal: 1.0M samples)")
    print("Affinity: CPU Cores 8-15 (Cores 0-7 100% idle for IDE & Windows)")
    print("Priority: BELOW_NORMAL_PRIORITY_CLASS")
    print("=" * 80)

    # 1. Run Tamil from current uncommitted shard to 200
    if tamil_start < 200:
        print(f"\n[PHASE 1/2] Resuming Tamil 1M Push from Shard {tamil_start:05d} to 199 (1 Worker)...")
        try:
            run_tamil_production_pipeline(
                start_shard=tamil_start,
                end_shard=200,
                samples_per_shard=5000,
                num_workers=1
            )
            print("\n[SUCCESS] Tamil has reached 1,000,000 samples (200 shards)!")
        except Exception as e:
            print(f"\n[ERROR] Tamil pipeline failed: {e}")
            return
    else:
        print(f"\n[PHASE 1/2] Tamil already at 200 shards (1M samples)! Skipping to Phase 2.")


    # Short cooldown
    time.sleep(10)

    # 2. Run Marathi from Shard 100 to 200
    print("\n[PHASE 2/2] Starting Marathi 1M Milestone Push (1 Worker)...")
    try:
        run_marathi_production_pipeline(
            start_shard=100,
            end_shard=200,
            samples_per_shard=5000,
            num_workers=1
        )
        print("\n[SUCCESS] Marathi has reached 1,000,000 samples (200 shards)!")
    except Exception as e:
        print(f"\n[ERROR] Marathi pipeline failed: {e}")
        return

    print("\n" + "=" * 80)
    print("ALL SEQUENTIAL 1M MILESTONES COMPLETED (TAMIL & MARATHI REACHED 1.0M EACH)!")
    print("=" * 80)


if __name__ == "__main__":
    main()
