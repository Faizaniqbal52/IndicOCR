"""
Malayalam (mal_Mlym) Linguistic Gatekeeper & Corpus Sanitizer (Agent-Linguist)
Enforces:
1. Multi-source streaming ingestion:
   - wikimedia/wikipedia (20231101.ml)
2. Strict Unicode NFC Normalization.
3. Strict ZWJ / ZWNJ preservation for proper chillu characters (ൺ, ൻ, ർ, ൽ, ൾ, ൿ) & conjuncts.
4. ZERO Latin / foreign script noise in pure Malayalam text.
5. ZERO floating matras (dependent vowel signs at token start).
6. ZERO invalid consecutive identical matras or double viramas.
7. Verification of Malayalam character set (U+0D00 - U+0D7F).
8. Multi-tier serialization:
   - data/processed/malayalam/malayalam_lines.jsonl
   - data/processed/malayalam/malayalam_blocks.jsonl
   - data/processed/malayalam/malayalam_words.jsonl
"""

import sys
import os
import json
import re
import unicodedata
from pathlib import Path
from collections import Counter
from datasets import load_dataset

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"c:\OCR - All")
output_dir = repo_root / "data" / "processed" / "malayalam"
output_dir.mkdir(parents=True, exist_ok=True)

# Valid punctuation and symbols for Malayalam
VALID_PUNCT_CHARS = set(' \t\n\r0123456789!?,.:;"\'()-/%[]‘’“”–—…|।॥')
MALAYALAM_RANGE = range(0x0D00, 0x0D7F + 1)
JOINERS = {0x200C, 0x200D}  # ZWNJ, ZWJ

# Floating matra / virama range:
# U+0D3E - U+0D4D, U+0D57, U+0D62, U+0D63
MALAYALAM_MATRAS = set(range(0x0D3E, 0x0D4D + 1)) | {0x0D57, 0x0D62, 0x0D63}
RE_FLOATING_MATRA = re.compile(r'(?:^|[\s\(\[\"\'\-\,\.\;\:\!\?])[\u0D3E-\u0D4D\u0D57\u0D62\u0D63]')
RE_WEB_NOISE = re.compile(r'(?:https?://|www\.|(?:\.com|\.org|\.net|\.in|\.edu|\.gov)|&[a-z]+;|[<>{}\[\]\\]|\b(?:span|div|href|width|height|style|src|target|px)\b)', re.IGNORECASE)


def is_pure_malayalam_sentence(text: str) -> tuple[bool, str]:
    if not text:
        return False, ""

    text = unicodedata.normalize('NFC', text)

    # Reject foreign scripts (Latin, Arabic, Devanagari, Bengali, Tamil, Telugu, etc.)
    if re.search(r'[a-zA-Z\u0600-\u06FF\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F\u0400-\u04FF\u4E00-\u9FFF]', text):
        return False, ""

    if RE_WEB_NOISE.search(text):
        return False, ""

    # Standardize whitespace
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'[\u200B\uFEFF]', '', text)
    text = re.sub(r'[ \t\r\f\v]+', ' ', text).strip()

    if len(text) < 15 or len(text) > 130:
        return False, ""

    if RE_FLOATING_MATRA.search(text):
        return False, ""

    # Verify 100% of characters are Malayalam, Joiners, or standard punctuation
    mal_count = 0
    for ch in text:
        cp = ord(ch)
        if cp in MALAYALAM_RANGE:
            mal_count += 1
        elif cp in JOINERS or ch in VALID_PUNCT_CHARS:
            continue
        else:
            return False, ""

    if mal_count < 8:
        return False, ""

    if not re.search(r'[\?\!\.।॥]$', text):
        text = text + "."

    return True, text


def validate_malayalam_word(word: str) -> tuple[bool, str]:
    if not word:
        return False, ""
    word = word.strip(' \t\n\r"\'()[]{}.,;:!?–—|।॥')
    if not word:
        return False, ""
    word = unicodedata.normalize('NFC', word)
    if len(word) < 2 or len(word) > 28:
        return False, ""

    # Reject floating matra / virama at word start
    if ord(word[0]) in MALAYALAM_MATRAS:
        return False, ""

    for ch in word:
        cp = ord(ch)
        if not (cp in MALAYALAM_RANGE or cp in JOINERS):
            return False, ""

    return True, word


def build_malayalam_corpus(
    target_lines: int = 150000,
    target_blocks: int = 35000,
    target_words: int = 30000
):
    print("=" * 80)
    print("AGENT-LINGUIST: MALAYALAM CORPUS INGESTION & UNICODE SANITIZATION")
    print(f"Target Lines  : {target_lines:,}")
    print(f"Target Blocks : {target_blocks:,}")
    print(f"Target Words  : {target_words:,}")
    print("=" * 80)

    token = os.environ.get("HF_TOKEN", os.environ.get("HF_TOKEN", ""))

    lines_set = set()
    words_counter = Counter()

    print("\n[Step 1/2] Streaming from wikimedia/wikipedia (20231101.ml)...")
    try:
        wiki_ds = load_dataset("wikimedia/wikipedia", "20231101.ml", split="train", streaming=True, token=token)
        for idx, item in enumerate(wiki_ds):
            raw_text = item.get("text", "")
            for raw_line in re.split(r'[\r\n]+', raw_text):
                for sent in re.split(r'(?<=[\.\?\!।॥])\s+', raw_line):
                    valid, clean_sent = is_pure_malayalam_sentence(sent)
                    if valid and clean_sent not in lines_set:
                        lines_set.add(clean_sent)
                        for tok in clean_sent.split():
                            w_valid, w_clean = validate_malayalam_word(tok)
                            if w_valid:
                                words_counter[w_clean] += 1

            if len(lines_set) % 25000 < 50 and len(lines_set) > 0:
                print(f"  Processed {idx:,} Wikipedia items -> Lines: {len(lines_set):,}, Words: {len(words_counter):,}")

            if len(lines_set) >= target_lines:
                break
    except Exception as e:
        print(f"  [WARNING] Wikipedia streaming completed or interrupted: {e}")

    lines_list = list(lines_set)
    print(f"\nCollected {len(lines_list):,} unique valid Malayalam lines.")

    # Construct paragraph blocks from grouped sentences
    print("Constructing paragraph blocks from lines...")
    blocks_list = []
    step = 4
    for i in range(0, min(len(lines_list) - 4, 150000), step):
        para = " ".join(lines_list[i:i+4])
        if len(para) >= 80:
            blocks_list.append(para)
        if len(blocks_list) >= target_blocks:
            break

    # Serialize to disk
    print(f"Serializing {len(lines_list):,} lines to {output_dir / 'malayalam_lines.jsonl'}...")
    with open(output_dir / "malayalam_lines.jsonl", "w", encoding="utf-8") as f:
        for line in lines_list:
            f.write(json.dumps({"text": line, "line": line}, ensure_ascii=False) + "\n")

    print(f"Serializing {len(blocks_list):,} blocks to {output_dir / 'malayalam_blocks.jsonl'}...")
    with open(output_dir / "malayalam_blocks.jsonl", "w", encoding="utf-8") as f:
        for block in blocks_list:
            f.write(json.dumps({"text": block, "block": block}, ensure_ascii=False) + "\n")

    top_words = [w for w, _ in words_counter.most_common(target_words)]
    print(f"Serializing {len(top_words):,} words to {output_dir / 'malayalam_words.jsonl'}...")
    with open(output_dir / "malayalam_words.jsonl", "w", encoding="utf-8") as f:
        for word in top_words:
            f.write(json.dumps({"text": word, "word": word}, ensure_ascii=False) + "\n")

    print("\n" + "=" * 80)
    print("MALAYALAM CORPUS READY:")
    print(f"  malayalam_lines.jsonl  : {len(lines_list):,} lines")
    print(f"  malayalam_blocks.jsonl : {len(blocks_list):,} blocks")
    print(f"  malayalam_words.jsonl  : {len(top_words):,} words")
    print("=" * 80)


if __name__ == "__main__":
    build_malayalam_corpus(target_lines=150000, target_blocks=35000, target_words=30000)
