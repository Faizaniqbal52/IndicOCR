import unicodedata
import re
from collections import Counter
from datasets import load_dataset

def clean_corpus_text(t: str) -> str:
    t = unicodedata.normalize('NFC', t)
    t = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', t)
    t = re.sub(r'https?://\S+|www\.\S+', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'[ \t]+', ' ', t)
    return t.strip()

print("Testing Dogri alpaca ingestion...", flush=True)
ds = load_dataset("saillab/alpaca-dogri-cleaned", split="train", streaming=True)
valid_lines = set()
script_range = range(0x0900, 0x097F + 1)
foreign_pattern = re.compile(r'[a-zA-Z\u0600-\u06FF\u0A00-\u0A7F\u0C80-\u0CFF]')

for idx, item in enumerate(ds):
    combined = f"{item.get('instruction', '')} {item.get('input', '')} {item.get('output', '')}".strip()
    for line in combined.split("\n"):
        clean_line = clean_corpus_text(line)
        if not clean_line or foreign_pattern.search(clean_line):
            continue
        if sum(1 for c in clean_line if ord(c) in script_range) < 4:
            continue
        valid_lines.add(clean_line)
        if len(valid_lines) >= 10:
            break
    if len(valid_lines) >= 10:
        break

print(f"Dogri sample lines ({len(valid_lines)}):", flush=True)
for l in list(valid_lines)[:3]:
    print("  ->", l, flush=True)
print("Dogri test successful!", flush=True)
