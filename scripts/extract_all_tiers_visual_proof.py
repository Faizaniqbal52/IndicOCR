"""
Extract All 4 Tiers for All 5 Languages from Live Hugging Face Shards
Saves 1 image per tier (Full Page, Paragraph, Line, Word) for:
- Kannada
- Punjabi
- Nepali
- Sindhi
- Bodo
"""

import io
import os
import sys
import json
import tarfile
from pathlib import Path
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = Path(r"c:\OCR - All\scratch\hf_audit_live\cache")
ARTIFACT_DIR = Path(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\3dbba92f-a15a-4629-9d9c-b3b34712581d\.tempmediaStorage")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

LANG_MAP = {
    "kan_train_00001.tar": "Kannada",
    "pan_train_00001.tar": "Punjabi",
    "nep_train_00001.tar": "Nepali",
    "snd_train_00001.tar": "Sindhi",
    "brx_train_00001.tar": "Bodo"
}

TIERS = ["Tier_1_FullPage", "Tier_2_Paragraph", "Tier_3_Line", "Tier_4_Word"]

def extract_all_tiers():
    tar_files = list(CACHE_DIR.glob("**/*.tar"))
    extracted_records = {}

    for tf in sorted(tar_files):
        if tf.name not in LANG_MAP:
            continue
        lang_name = LANG_MAP[tf.name]
        prefix = tf.name.split("_")[0]
        extracted_records[lang_name] = {}

        print(f"\nExtracting all 4 tiers for {lang_name} from {tf.name}...")
        with tarfile.open(tf, "r") as tar:
            members = tar.getmembers()
            webp_dict = {m.name: m for m in members if m.name.endswith(".webp")}
            json_members = [m for m in members if m.name.endswith(".json")]

            found_tiers = set()
            for m_json in json_members:
                if len(found_tiers) == 4:
                    break
                meta = json.loads(tar.extractfile(m_json).read().decode("utf-8"))
                tier = meta.get("tier")
                if tier in TIERS and tier not in found_tiers:
                    base_key = m_json.name.replace(".json", "")
                    webp_name = f"{base_key}.webp"
                    if webp_name in webp_dict:
                        img_bytes = tar.extractfile(webp_dict[webp_name]).read()
                        img = Image.open(io.BytesIO(img_bytes))
                        out_filename = f"hf_proof_{prefix}_{tier}.png"
                        out_path = ARTIFACT_DIR / out_filename
                        img.save(out_path)
                        found_tiers.add(tier)
                        extracted_records[lang_name][tier] = {
                            "file": out_filename,
                            "key": base_key,
                            "text": meta.get("text", "")[:60],
                            "tokens": meta.get("token_count", 0),
                            "font": meta.get("font_name", "unknown"),
                            "dimensions": meta.get("canvas_size", [0, 0]),
                            "augmentations": meta.get("applied_augmentations", [])
                        }
                        print(f"  [FOUND {tier}] {out_filename} ({meta.get('canvas_size')} px, {meta.get('token_count')} tokens)")

    out_json = ARTIFACT_DIR / "all_tiers_extraction_manifest.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(extracted_records, f, indent=2, ensure_ascii=False)
    print("\nManifest written to all_tiers_extraction_manifest.json")

if __name__ == "__main__":
    extract_all_tiers()
