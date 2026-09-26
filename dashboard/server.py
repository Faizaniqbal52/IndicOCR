import sys
import os
import re
import json
import time
from pathlib import Path
from typing import Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = Path(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\3dbba92f-a15a-4629-9d9c-b3b34712581d\.system_generated\tasks")
LEDGER_PATH = REPO_ROOT / "BHOJPURI_PRODUCTION_LEDGER.md"
PORT = 8765

def get_latest_production_log() -> Optional[Path]:
    if not TASKS_DIR.exists():
        return None
    logs = list(TASKS_DIR.glob("task-*.log"))
    if not logs:
        return None
    # Sort by mtime descending
    logs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for l in logs:
        try:
            head = l.read_text(encoding="utf-8", errors="ignore")[:1000]
            if "BHOJPURI PRODUCTION PIPELINE" in head or "bho_train" in head:
                return l
        except Exception:
            continue
    return logs[0]

def parse_telemetry():
    telemetry = {
        "status": "IDLE",
        "current_shard": "bho_train_00026.tar",
        "shard_idx": 26,
        "shard_current": 0,
        "shard_total": 5000,
        "shard_pct": 0.0,
        "shard_speed": "0.0 it/s",
        "shard_elapsed": "--:--",
        "shard_eta": "--:--",
        "batch_start_shard": 26,
        "batch_num_shards": 74,
        "batch_completed_shards": 0,
        "batch_samples": 0,
        "batch_total_samples": 370000,
        "batch_pct": 0.0,
        "total_dataset_samples": 130000,
        "total_target_samples": 500000,
        "total_pct": 26.0,
        "local_buffer_gb": 0.015,
        "disk_limit_gb": 2.0,
        "completed_shards": [],
        "active_augmentations_count": 54,
        "raw_tqdm": "",
        "timestamp": time.strftime("%H:%M:%S")
    }

    log_file = get_latest_production_log()
    if not log_file or not log_file.exists():
        return telemetry


    try:
        content = log_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        telemetry["status"] = "RUNNING"

        # Count completed shards in this batch from log
        completed = []
        for line in lines:
            m_fin = re.search(r"Finalized shard:\s*(bho_train_\d+\.tar)\s*\(([\d\.]+)\s*MB,\s*(\d+)\s*samples\)", line)
            if m_fin:
                s_name, s_size, s_count = m_fin.group(1), float(m_fin.group(2)), int(m_fin.group(3))
                completed.append({
                    "name": s_name,
                    "size_mb": s_size,
                    "samples": s_count,
                    "status": "Committed & Evicted (HTTP 200)"
                })

        telemetry["completed_shards"] = completed
        num_completed = len(completed)
        telemetry["batch_completed_shards"] = num_completed

        # Find current active shard synthesis line
        current_shard_name = f"bho_train_{16 + num_completed:05d}.tar"
        for line in reversed(lines):
            m_synth = re.search(r"Synthesizing Shard #(\d+):\s*(bho_train_\d+\.tar)", line)
            if m_synth:
                current_shard_name = m_synth.group(2)
                telemetry["shard_idx"] = int(m_synth.group(1))
                break

        telemetry["current_shard"] = current_shard_name

        # Parse latest tqdm progress line
        for line in reversed(lines):
            if "Shard" in line and "%" in line and "/" in line:
                telemetry["raw_tqdm"] = line.strip()
                # e.g.: Shard 00018:  68%|######7   | 3386/5000 [05:00<01:25, 18.80it/s]
                m_prog = re.search(r"(\d+)%\|.*?\|\s*(\d+)/(\d+)\s*\[([\d:]+)<([\d:]+),\s*([\d\.]+(?:it/s|s/it))\]", line)
                if m_prog:
                    pct = float(m_prog.group(1))
                    curr = int(m_prog.group(2))
                    tot = int(m_prog.group(3))
                    elapsed = m_prog.group(4)
                    eta = m_prog.group(5)
                    speed = m_prog.group(6)

                    telemetry["shard_pct"] = round(pct, 1)
                    telemetry["shard_current"] = curr
                    telemetry["shard_total"] = tot
                    telemetry["shard_elapsed"] = elapsed
                    telemetry["shard_eta"] = eta
                    telemetry["shard_speed"] = speed
                break

        # Calculate batch totals
        curr_in_shard = telemetry["shard_current"]
        total_batch_done = (num_completed * 5000) + curr_in_shard
        telemetry["batch_samples"] = total_batch_done
        telemetry["batch_pct"] = round((total_batch_done / 50000.0) * 100.0, 1)

        total_done = 80000 + total_batch_done
        telemetry["total_dataset_samples"] = total_done
        telemetry["total_pct"] = round((total_done / 500000.0) * 100.0, 1)

        # Check if finished
        if "ALL REQUESTED SHARDS COMPLETED" in content:
            telemetry["status"] = "COMPLETED"

    except Exception as e:
        telemetry["error"] = str(e)

    return telemetry


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            data = parse_telemetry()
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/" or self.path == "/index.html":
            html_path = Path(__file__).parent / "index.html"
            content = html_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # Suppress noisy GET log output
        pass


def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"[Dashboard Server] Live Telemetry Dashboard active at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_server()
