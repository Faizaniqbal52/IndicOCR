import sys
from datasets import load_dataset

langs = [
    ("nep", "Nepali", "20231101.ne"),
    ("snd", "Sindhi", "20231101.sd"),
    ("sat", "Santali", "20231101.sat"),
    ("mni", "Manipuri", "20231101.mni"),
    ("pa",  "Punjabi",  "20231101.pa"),
    ("kn",  "Kannada",  "20231101.kn"),
    ("brx", "Bodo",     "20231101.brx")
]

print("Checking Wikipedia datasets:")
for code, name, cfg in langs:
    try:
        ds = load_dataset('wikimedia/wikipedia', cfg, split='train', streaming=True)
        sample = next(iter(ds))
        title = sample.get("title", "")
        text = sample.get("text", "")[:60].replace("\n", " ")
        print(f"[OK] {name} ({cfg}): '{title}' -> {text}")
    except Exception as e:
        print(f"[FAIL] {name} ({cfg}): {e}")
