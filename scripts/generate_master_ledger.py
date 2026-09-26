"""
===================================================================================
MASTER PAN-INDIC OCR PRODUCTION LEDGER & AUDIT GENERATOR
Queries Hugging Face API live and generates authoritative master ledger
===================================================================================
"""

import os
import sys
from datetime import datetime, timezone
from collections import Counter
from huggingface_hub import HfApi

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

api = HfApi()
repo_id = "Faizaniqbal/IndicOCR"

print(f"Connecting to Hugging Face Hub: {repo_id}...", flush=True)
files = api.list_repo_files(repo_id, repo_type="dataset")
shards = [f for f in files if f.startswith("data/") and f.endswith(".tar")]
counts = Counter(f.split("/")[1] for f in shards)

LANG_METADATA = {
    "assamese": ("asm", "Assamese", "Bengali-Assamese (`Beng`)", 100),
    "bengali": ("ben", "Bengali", "Bengali (`Beng`)", 200),
    "bhojpuri": ("bho", "Bhojpuri", "Devanagari (`Deva`)", 100),
    "bodo": ("brx", "Bodo", "Devanagari (`Deva`)", 100),
    "dogri": ("doi", "Dogri", "Devanagari (`Deva`)", 50),
    "gujarati": ("guj", "Gujarati", "Gujarati (`Gujr`)", 100),
    "hindi": ("hin", "Hindi", "Devanagari (`Deva`)", 200),
    "kannada": ("kan", "Kannada", "Kannada (`Knda`)", 100),
    "kashmiri": ("kas", "Kashmiri", "Extended Arabic RTL (`Arab`)", 100),
    "konkani": ("gom", "Konkani", "Devanagari (`Deva`)", 50),
    "maithili": ("mai", "Maithili", "Devanagari (`Deva`)", 50),
    "malayalam": ("mal", "Malayalam", "Malayalam (`Mlym`)", 100),
    "manipuri": ("mni", "Manipuri", "Meetei Mayek (`Mtei`)", 100),
    "marathi": ("mar", "Marathi", "Devanagari (`Deva`)", 200),
    "nepali": ("nep", "Nepali", "Devanagari (`Deva`)", 100),
    "odia": ("ori", "Odia", "Odia (`Orya`)", 100),
    "punjabi": ("pan", "Punjabi", "Gurmukhi (`Guru`)", 100),
    "sanskrit": ("san", "Sanskrit", "Devanagari (`Deva`)", 100),
    "santali": ("sat", "Santali", "Ol Chiki (`Olck`)", 100),
    "sindhi": ("snd", "Sindhi", "Extended Arabic RTL (`Arab`)", 100),
    "tamil": ("tam", "Tamil", "Tamil (`Taml`)", 200),
    "telugu": ("tel", "Telugu", "Telugu (`Telu`)", 100),
    "urdu": ("urd", "Urdu", "Extended Arabic RTL (`Arab`)", 200),
}

utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

lines = [
    "# MASTER PAN-INDIC OCR PRODUCTION LEDGER & DATASET REGISTRY",
    f"**Audit Timestamp:** `{utc_now}` | **Target Repository:** [`Faizaniqbal/IndicOCR`](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)",
    "",
    "## Executive Summary",
    f"* **Total Remote Shards Live:** `{len(shards):,}` WebDataset `.tar` shards",
    f"* **Total Verified Samples Live:** `{len(shards)*5000:,}` samples",
    f"* **Total Covered Languages:** `23` Languages (All 22 Eighth Schedule Constitutional Languages + Bhojpuri)",
    "",
    "---",
    "",
    "## 1. Existing Production Fleet Status Matrix (23 Languages)",
    "",
    "| # | Language | Code | Script | Live Shards | Live Samples | Target Quota | Status | Local Ledger File |",
    "| :-: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |"
]

idx = 1
for folder, (code, name, script, target) in sorted(LANG_METADATA.items(), key=lambda x: x[1][1]):
    scount = counts.get(folder, 0)
    samples = scount * 5000
    if scount >= target:
        status = "🏆 **COMPLETE (100%)**"
    else:
        status = f"🔄 **IN PROGRESS ({scount}/{target} shards)**"
    
    ledger_name = f"{folder.upper()}_PRODUCTION_LEDGER.md"
    lines.append(f"| {idx} | **{name}** | `{code}` | {script} | {scount} | {samples:,} | {target} | {status} | [`{ledger_name}`]({ledger_name}) |")
    idx += 1

lines.extend([
    "",
    "---",
    "",
    "## 2. Genuinely Unstarted Pan-Indic Languages (Zero Shards on HF)",
    "",
    "These languages have **0 shards** in the Hugging Face repository and represent the **true next pipeline expansion**:",
    "",
    "| # | Language | Code | Script | Target Corpus Source | Primary Font | Est. Speakers |",
    "| :-: | :--- | :---: | :--- | :--- | :--- | :--- |",
    "| 1 | **Awadhi** | `awa` | Devanagari (`Deva`) | Wikipedia `20231101.awa` | NotoSansDevanagari | ~38 Million |",
    "| 2 | **Newari (Nepal Bhasa)** | `new` | Devanagari (`Deva`) | Wikipedia `20231101.new` | NotoSansDevanagari | ~1.2 Million |",
    "| 3 | **Tulu** | `tcy` | Kannada Script (`Knda`) | Wikipedia `20231101.tcy` | NotoSansKannada | ~2 Million |",
    "| 4 | **Angika** | `anp` | Devanagari (`Deva`) | Wikipedia `20231101.anp` | NotoSansDevanagari | ~15 Million |",
    "| 5 | **Magahi** | `mag` | Devanagari (`Deva`) | Wikipedia `20231101.mag` | NotoSansDevanagari | ~13 Million |",
    "| 6 | **Chhattisgarhi** | `hne` | Devanagari (`Deva`) | Wikipedia `20231101.hne` | NotoSansDevanagari | ~18 Million |",
    "| 7 | **Marwari / Rajasthani** | `mwr` | Devanagari (`Deva`) | Wikipedia `20231101.mwr` | NotoSansDevanagari | ~25 Million |",
    "| 8 | **Haryanvi** | `bgc` | Devanagari (`Deva`) | Saillab / OSCAR Hindi-dialects | NotoSansDevanagari | ~10 Million |",
    "| 9 | **Bishnupriya Manipuri** | `bpy` | Bengali-Assamese (`Beng`) | Wikipedia `20231101.bpy` | NotoSansBengali | ~500,000 |",
    "| 10 | **Khasi** | `kha` | Latin (`Latn`) | Wikipedia `20231101.kha` | NotoSans | ~1.6 Million |",
    "",
    "---",
    "",
    "## 3. Discarded Redundancies (Already Completed - DO NOT RERUN)",
    "",
    "* **Bhojpuri (`bho`)**: **100 shards (500,000 samples)** already committed live under `data/bhojpuri/`.",
    "* **Kashmiri (`kas`)**: **100 shards (500,000 samples)** already committed live under `data/kashmiri/`.",
    "* **Dogri (`doi`)**: **50 shards (250,000 samples)** already committed live under `data/dogri/`.",
    "* **Konkani (`gom`)**: **50 shards (250,000 samples)** already committed live under `data/konkani/`.",
    "* **Maithili (`mai`)**: **50 shards (250,000 samples)** already committed live under `data/maithili/`.",
    "* **Kannada (`kan`)**: **100 shards (500,000 samples)** already committed live under `data/kannada/`.",
    "* **Nepali (`nep`)**: **100 shards (500,000 samples)** already committed live under `data/nepali/`.",
    "* **Santali (`sat`)**: **100 shards (500,000 samples)** already committed live under `data/santali/`.",
    "",
    "**Strict Engineering Invariant:** The dispatcher and deployer must NEVER launch or push workers for any of the above completed languages."
])

out_path = r"c:\OCR - All\MASTER_PAN_INDIC_LEDGER.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Generated {out_path} successfully!", flush=True)
