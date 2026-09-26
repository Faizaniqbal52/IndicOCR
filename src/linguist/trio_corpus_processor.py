"""
Agent-Linguist Corpus Processor & Unicode Sanitizer for:
1. Odia (ori_Orya) - wikimedia/wikipedia (20231101.or)
2. Assamese (asm_Beng) - wikimedia/wikipedia (20231101.as)
3. Sanskrit (san_Deva) - wikimedia/wikipedia (20231101.sa)

Enforces:
- Strict Unicode NFC Normalization.
- Zero Latin / foreign script noise.
- Strict ZWJ / ZWNJ preservation for proper conjunct shaping.
- Zero floating matras (dependent vowel signs at token start).
- Tri-partite serialization: lines, blocks, words.
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
token = os.environ.get("HF_TOKEN", os.environ.get("HF_TOKEN", ""))
VALID_PUNCT_CHARS = set(' \t\n\r0123456789!?,.:;"\'()-/%[]‘’“”–—…|।॥')
JOINERS = {0x200C, 0x200D}

# Config per language
LANG_SPECS = {
    "odia": {
        "wiki_id": "20231101.or",
        "script_range": range(0x0B00, 0x0B7F + 1),
        "matras": set(range(0x0B3E, 0x0B4D + 1)) | {0x0B56, 0x0B57},
        "re_matra": re.compile(r'(?:^|[\s\(\[\"\'\-\,\.\;\:\!\?])[\u0B3E-\u0B4D\u0B56\u0B57]'),
        "foreign_pattern": re.compile(r'[a-zA-Z\u0600-\u06FF\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0B80-\u0BFF\u0C00-\u0C7F\u0D00-\u0D7F]'),
        "target_lines": 150000,
        "target_blocks": 35000,
        "target_words": 30000
    },
    "assamese": {
        "wiki_id": "20231101.as",
        "script_range": range(0x0980, 0x09FF + 1),
        "matras": set(range(0x09BE, 0x09CD + 1)) | {0x09D7},
        "re_matra": re.compile(r'(?:^|[\s\(\[\"\'\-\,\.\;\:\!\?])[\u09BE-\u09CD\u09D7]'),
        "foreign_pattern": re.compile(r'[a-zA-Z\u0600-\u06FF\u0900-\u097F\u0A00-\u0A7F\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0D00-\u0D7F]'),
        "target_lines": 150000,
        "target_blocks": 35000,
        "target_words": 30000
    },
    "sanskrit": {
        "wiki_id": "20231101.sa",
        "script_range": range(0x0900, 0x097F + 1),
        "matras": set(range(0x093E, 0x094F + 1)) | {0x0955, 0x0956, 0x0957},
        "re_matra": re.compile(r'(?:^|[\s\(\[\"\'\-\,\.\;\:\!\?])[\u093E-\u094F\u0955-\u0957]'),
        "foreign_pattern": re.compile(r'[a-zA-Z\u0600-\u06FF\u0980-\u09FF\u0A00-\u0A7F\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0D00-\u0D7F]'),
        "target_lines": 150000,
        "target_blocks": 35000,
        "target_words": 30000
    }
}


def sanitize_sentence(text: str, spec: dict) -> tuple[bool, str]:
    if not text:
        return False, ""
    text = unicodedata.normalize('NFC', text)
    if spec["foreign_pattern"].search(text):
        return False, ""
    # Standardize whitespace & drop controls
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'[\u200B\uFEFF]', '', text)
    text = re.sub(r'[ \t\r\f\v]+', ' ', text).strip()
    if len(text) < 15 or len(text) > 130:
        return False, ""
    if spec["re_matra"].search(text):
        return False, ""
    script_count = 0
    for ch in text:
        cp = ord(ch)
        if cp in spec["script_range"]:
            script_count += 1
        elif cp in JOINERS or ch in VALID_PUNCT_CHARS:
            continue
        else:
            return False, ""
    if script_count < 8:
        return False, ""
    if not re.search(r'[\?\!\.।॥]$', text):
        text = text + "।" if spec["wiki_id"].endswith((".or", ".sa", ".as")) else text + "."
    return True, text


def sanitize_word(word: str, spec: dict) -> tuple[bool, str]:
    if not word:
        return False, ""
    word = word.strip(' \t\n\r"\'()[]{}.,;:!?–—|।॥')
    if not word:
        return False, ""
    word = unicodedata.normalize('NFC', word)
    if len(word) < 2 or len(word) > 28:
        return False, ""
    if ord(word[0]) in spec["matras"]:
        return False, ""
    for ch in word:
        cp = ord(ch)
        if not (cp in spec["script_range"] or cp in JOINERS):
            return False, ""
    return True, word


def build_corpus_for_lang(lang_key: str):
    spec = LANG_SPECS[lang_key]
    out_dir = repo_root / "data" / "processed" / lang_key
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"AGENT-LINGUIST: INGESTING {lang_key.upper()} ({spec['wiki_id']})")
    print(f"Target Lines: {spec['target_lines']:,} | Blocks: {spec['target_blocks']:,} | Words: {spec['target_words']:,}")
    print("=" * 80)

    lines_set = set()
    words_counter = Counter()

    try:
        ds = load_dataset("wikimedia/wikipedia", spec["wiki_id"], split="train", streaming=True, token=token)
        for idx, item in enumerate(ds):
            raw = item.get("text", "")
            for raw_line in re.split(r'[\r\n]+', raw):
                for sent in re.split(r'(?<=[\.\?\!।॥])\s+', raw_line):
                    valid, clean_sent = sanitize_sentence(sent, spec)
                    if valid and clean_sent not in lines_set:
                        lines_set.add(clean_sent)
                        for tok in clean_sent.split():
                            w_valid, w_clean = sanitize_word(tok, spec)
                            if w_valid:
                                words_counter[w_clean] += 1

            if len(lines_set) % 25000 < 50 and len(lines_set) > 0:
                print(f"  [{lang_key.upper()}] Processed {idx:,} articles -> Lines: {len(lines_set):,}, Words: {len(words_counter):,}")

            if len(lines_set) >= spec["target_lines"]:
                break
    except Exception as e:
        print(f"  [NOTICE] Wikipedia stream ended or reached target: {e}")

    lines_list = list(lines_set)
    print(f"  [{lang_key.upper()}] Total unique lines: {len(lines_list):,}")

    # Build paragraph blocks
    blocks_list = []
    step = 4
    for i in range(0, min(len(lines_list) - 4, 150000), step):
        para = " ".join(lines_list[i:i+4])
        if len(para) >= 80:
            blocks_list.append(para)
        if len(blocks_list) >= spec["target_blocks"]:
            break

    # Save lines
    l_file = out_dir / f"{lang_key}_lines.jsonl"
    with open(l_file, "w", encoding="utf-8") as f:
        for l in lines_list:
            f.write(json.dumps({"text": l, "line": l}, ensure_ascii=False) + "\n")

    # Save blocks
    b_file = out_dir / f"{lang_key}_blocks.jsonl"
    with open(b_file, "w", encoding="utf-8") as f:
        for b in blocks_list:
            f.write(json.dumps({"text": b, "block": b}, ensure_ascii=False) + "\n")

    # Save words
    top_words = [w for w, _ in words_counter.most_common(spec["target_words"])]
    w_file = out_dir / f"{lang_key}_words.jsonl"
    with open(w_file, "w", encoding="utf-8") as f:
        for w in top_words:
            f.write(json.dumps({"text": w, "word": w}, ensure_ascii=False) + "\n")

    print(f"  [OK] Saved {lang_key}: {len(lines_list):,} lines, {len(blocks_list):,} blocks, {len(top_words):,} words to {out_dir}\n")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for k in ["odia", "assamese", "sanskrit"]:
            build_corpus_for_lang(k)
    else:
        build_corpus_for_lang(target)
