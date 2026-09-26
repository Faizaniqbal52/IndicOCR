import sys
sys.stdout.reconfigure(encoding='utf-8')
from datasets import load_dataset

token = os.environ.get("HF_TOKEN", "")

# Test Sangraha for Bodo
print("Testing Sangraha for Bodo (brx):")
try:
    ds_brx = load_dataset("ai4bharat/sangraha", data_dir="data/brx", split="train", streaming=True, token=token)
    sample = next(iter(ds_brx))
    print("[SUCCESS] Sangraha Bodo:", sample.get("text", "")[:60])
except Exception as e:
    print("[FAIL] Sangraha Bodo:", e)

# Test Wikipedia for Nepali, Sindhi, Santali, Manipuri
wiki_langs = [
    ("Nepali", "20231101.ne"),
    ("Sindhi", "20231101.sd"),
    ("Santali", "20231101.sat"),
    ("Manipuri", "20231101.mni")
]

for name, cfg in wiki_langs:
    try:
        ds = load_dataset("wikimedia/wikipedia", cfg, split="train", streaming=True, token=token)
        sample = next(iter(ds))
        title = sample.get("title", "")
        text = sample.get("text", "")[:60].replace("\n", " ")
        print(f"[SUCCESS] Wikipedia {name} ({cfg}): {title} -> {text}")
    except Exception as e:
        print(f"[FAIL] Wikipedia {name} ({cfg}): {e}")
