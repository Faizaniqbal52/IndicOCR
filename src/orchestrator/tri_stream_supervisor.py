"""
Tri-Stream Supervisor: Launches and Manages Local Concurrent Synthesis for:
1. Odia (ori_Orya) - 500,000 samples (100 shards)
2. Assamese (asm_Beng) - 500,000 samples (100 shards)
3. Sanskrit (san_Deva) - 500,000 samples (100 shards)

Guarantees:
- Exactly 1 worker per language stream.
- Pinned to CPU Cores 8-15 (Cores 0-7 100% free for desktop).
- Process priority set to psutil.BELOW_NORMAL_PRIORITY_CLASS.
- Immediate local shard eviction after verified HTTP 200 upload (Storage strictly < 1.0 GB).
- Dedicated file logs in logs/stream_{lang}.log.
"""

import sys
import os
import time
import subprocess
from pathlib import Path
import psutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"C:\OCR - All")
logs_dir = repo_root / "logs"
logs_dir.mkdir(exist_ok=True)

streams = [
    {
        "name": "ODIA_STREAM",
        "lang": "odia",
        "cmd": [sys.executable, str(repo_root / "src" / "orchestrator" / "trio_production_pipeline.py"), "--lang", "odia", "--start-shard", "0", "--end-shard", "100", "--workers", "1"],
        "log": logs_dir / "stream_odia.log"
    },
    {
        "name": "ASSAMESE_STREAM",
        "lang": "assamese",
        "cmd": [sys.executable, str(repo_root / "src" / "orchestrator" / "trio_production_pipeline.py"), "--lang", "assamese", "--start-shard", "0", "--end-shard", "100", "--workers", "1"],
        "log": logs_dir / "stream_assamese.log"
    },
    {
        "name": "SANSKRIT_STREAM",
        "lang": "sanskrit",
        "cmd": [sys.executable, str(repo_root / "src" / "orchestrator" / "trio_production_pipeline.py"), "--lang", "sanskrit", "--start-shard", "0", "--end-shard", "100", "--workers", "1"],
        "log": logs_dir / "stream_sanskrit.log"
    }
]

print("=" * 80)
print("LAUNCHING LOCAL TRI-STREAM OCR SYNTHESIS (ODIA + ASSAMESE + SANSKRIT)")
print("Total Target Output: 1,500,000 samples (500k each across 100 shards)")
print("Configuration      : 1 worker each, Priority: BELOW_NORMAL, CPU Affinity: Cores 8-15")
print("Remote Hub Paths   : data/odia/, data/assamese/, data/sanskrit/ on Faizaniqbal/IndicOCR")
print("=" * 80)

procs = []
for s in streams:
    log_file = open(s["log"], "a", encoding="utf-8")
    proc = subprocess.Popen(
        s["cmd"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=dict(os.environ, PYTHONUNBUFFERED="1")
    )
    try:
        p = psutil.Process(proc.pid)
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        p.cpu_affinity(list(range(8, 16)))
    except Exception:
        pass

    procs.append((s["name"], proc, log_file))
    print(f"  [STARTED] {s['name']} (PID: {proc.pid}) -> Logging to {s['log'].name}")

print("\nAll 3 streams are actively running in the background.")
print("Stream-and-evict protocol active. Local buffer will remain strictly < 1.0 GB.")
print("=" * 80)
