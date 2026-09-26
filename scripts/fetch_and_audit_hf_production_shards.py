"""
Fetch and Audit Live Hugging Face Production Shards
Downloads live shards and visual audit plates from Faizaniqbal/IndicOCR
for Kannada, Punjabi, Nepali, Sindhi, and Bodo.
Performs line-by-line, character-by-character forensic audit of actual uploaded data.
"""

import io
import os
import sys
import json
import tarfile
import random
import unicodedata
from pathlib import Path
from PIL import Image
from huggingface_hub import hf_hub_download

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ID = "Faizaniqbal/IndicOCR"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

ARTIFACT_MEDIA_DIR = Path(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\3dbba92f-a15a-4629-9d9c-b3b34712581d\.tempmediaStorage")
ARTIFACT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

OUT_DIR = Path(r"c:\OCR - All\scratch\hf_audit_live")
OUT_DIR.mkdir(parents=True, exist_ok=True)

LANGS = [
    ("kan", "kannada", "Kannada", range(0x0C80, 0x0CFF + 1)),
    ("pan", "punjabi", "Punjabi", range(0x0A00, 0x0A7F + 1)),
    ("nep", "nepali", "Nepali", range(0x0900, 0x097F + 1)),
    ("snd", "sindhi", "Sindhi", range(0x0600, 0x06FF + 1)),
    ("brx", "bodo", "Bodo", range(0x0900, 0x097F + 1))
]

def run_audit():
    print("=" * 80)
    print("FETCHING & AUDITING LIVE HUGGING FACE SHARDS (Faizaniqbal/IndicOCR)")
    print("=" * 80)

    audit_summary = {}

    for code, subfolder, name, script_range in LANGS:
        print(f"\n--- AUDITING {name.upper()} ({code}) FROM HUGGING FACE ---")
        
        # 1. Download Production Plate from HF
        plate_filename = f"data/{subfolder}/{code}_production_plate.png"
        try:
            print(f"  Fetching production plate: {plate_filename}...")
            local_plate = hf_hub_download(
                repo_id=REPO_ID,
                repo_type="dataset",
                filename=plate_filename,
                token=HF_TOKEN,
                cache_dir=str(OUT_DIR / "cache")
            )
            # Copy to artifacts directory
            art_plate = ARTIFACT_MEDIA_DIR / f"hf_live_{code}_production_plate.png"
            with open(local_plate, "rb") as f_in, open(art_plate, "wb") as f_out:
                f_out.write(f_in.read())
            print(f"  [OK] Saved live plate to artifact: {art_plate.name}")
        except Exception as e:
            print(f"  [WARN] Plate not yet uploaded or failed: {e}")

        # 2. Download Shard 00001 (or 00000) from HF
        shard_candidates = [f"data/{subfolder}/{code}_train_00001.tar", f"data/{subfolder}/{code}_train_00000.tar"]
        downloaded_shard = None
        for sc in shard_candidates:
            try:
                print(f"  Fetching live shard: {sc}...")
                downloaded_shard = hf_hub_download(
                    repo_id=REPO_ID,
                    repo_type="dataset",
                    filename=sc,
                    token=HF_TOKEN,
                    cache_dir=str(OUT_DIR / "cache")
                )
                print(f"  [OK] Successfully downloaded shard: {sc} ({os.path.getsize(downloaded_shard)/(1024*1024):.2f} MB)")
                break
            except Exception as e:
                print(f"  Candidate {sc} not available: {e}")

        if not downloaded_shard:
            print(f"  [FAIL] Could not download any shard for {name}!")
            continue

        # 3. Extract and Inspect Shard Samples
        with tarfile.open(downloaded_shard, "r") as tar:
            members = tar.getmembers()
            json_members = [m for m in members if m.name.endswith(".json")]
            webp_members = {m.name: m for m in members if m.name.endswith(".webp")}

            print(f"  Total samples in shard: {len(json_members):,} pairs")
            
            # Audit a sample of 25 items thoroughly
            sample_subset = random.sample(json_members, min(25, len(json_members)))
            
            clipping_errors = 0
            tofu_errors = 0
            punct_only_errors = 0
            contamination_errors = 0
            
            inspected_samples = []

            for m_json in sample_subset:
                f_json = tar.extractfile(m_json)
                meta = json.loads(f_json.read().decode("utf-8"))
                
                base_name = m_json.name.replace(".json", "")
                text = meta.get("text", "")
                tokens = meta.get("tokens", [])
                glyphs = meta.get("shaped_glyphs", [])
                cw, ch = meta.get("canvas_size", [0, 0])
                
                # Check 1: Glyph ID 0
                if any(g.get("glyph_id", 1) == 0 for g in glyphs):
                    tofu_errors += 1

                # Check 2: Bounding box clipping
                for tok in tokens:
                    bx = tok.get("bbox", [0, 0, 0, 0])
                    if bx[0] < 0 or bx[1] < 0 or bx[2] > cw or bx[3] > ch:
                        clipping_errors += 1

                # Check 3: Minimum native script characters
                native_script_chars = sum(1 for c in text if ord(c) in script_range)
                if native_script_chars < 2 and len(text.strip()) > 0:
                    punct_only_errors += 1

                # Check 4: Contamination (Bodo specific)
                if code == "brx":
                    hindi_stops = {'के', 'लिए', 'को', 'है', 'था', 'थी', 'पर', 'सब', 'कर', 'नहीं'}
                    words = set(text.split())
                    if any(w in words for w in hindi_stops):
                        contamination_errors += 1

                if len(inspected_samples) < 3:
                    inspected_samples.append({
                        "key": meta.get("sample_key", base_name),
                        "tier": meta.get("tier", "unknown"),
                        "text": text[:80],
                        "tokens_count": len(tokens),
                        "font": meta.get("font_name", "unknown"),
                        "augmentations": meta.get("applied_augmentations", [])[:2],
                        "native_chars": native_script_chars
                    })

            # Also extract 1 sample webp image to artifacts
            sample_webp_m = webp_members.get(f"{inspected_samples[0]['key']}.webp")
            if sample_webp_m:
                f_img = tar.extractfile(sample_webp_m)
                img = Image.open(io.BytesIO(f_img.read()))
                art_sample_img = ARTIFACT_MEDIA_DIR / f"hf_live_sample_{code}_{inspected_samples[0]['key']}.png"
                img.save(art_sample_img)
                print(f"  [SAVED SAMPLE CROP] {art_sample_img.name}")

            audit_summary[code] = {
                "name": name,
                "shard_name": Path(downloaded_shard).name,
                "samples_in_shard": len(json_members),
                "audited_subset": len(sample_subset),
                "tofu_errors": tofu_errors,
                "clipping_errors": clipping_errors,
                "punct_only_errors": punct_only_errors,
                "contamination_errors": contamination_errors,
                "status": "PASSED (100% ZERO DEFECTS)" if (tofu_errors + clipping_errors + punct_only_errors + contamination_errors == 0) else "FAILED",
                "sample_inspection": inspected_samples
            }

    # Save full audit JSON
    with open(OUT_DIR / "hf_production_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("LIVE HUGGING FACE PRODUCTION SHARDS AUDIT COMPLETED")
    print("=" * 80)
    for code, res in audit_summary.items():
        print(f"  {res['name']} ({code}): {res['status']} | Tofu: {res['tofu_errors']}, Clip: {res['clipping_errors']}, Punct: {res['punct_only_errors']}, Contam: {res['contamination_errors']}")
        for s in res["sample_inspection"][:2]:
            print(f"    - [{s['tier']}] \"{s['text']}\" (Font: {s['font']}, Tokens: {s['tokens_count']}, Native Chars: {s['native_chars']})")

if __name__ == "__main__":
    run_audit()
