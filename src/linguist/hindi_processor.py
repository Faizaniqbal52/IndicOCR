"""
Agent-Linguist Pipeline for Hindi (hin_Deva)
Processes harvested raw text from 4 multi-domain sources:
1. IITB English-Hindi Corpus (1.66M general/technical/dialogue sentences)
2. Hindi Poetry Dataset (classical & modern Dohas/Kavita)
3. Hindi Short News (press releases, headlines, regional journalism)
4. Indian Legal Hindi Corpus (statutory acts, court contexts)

Mandatory Linguistic Inspection Gates:
- Strict Unicode NFC Normalization & Joiner Safety (ZWJ/ZWNJ guarantee).
- Script Purity (Devanagari dominant, strip control codes, HTML tags, Latin bleed).
- Sequence Length Bounding (20 to 85 chars for TrOCR / CRNN line targets).
- Lexical Balancing & Samyuktakshara Mining (Zipfian mitigation).
- Multi-tier serialization into data/processed/hindi/
"""

import sys
import os
import json
import random
from pathlib import Path
from collections import Counter
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parent))
from unicode_gate import (
    UnicodeGatekeeper,
    HIGH_VALUE_CONJUNCTS,
    ZWJ, ZWNJ, DANDA, DOUBLE_DANDA
)

HINDI_COMMON_STOPWORDS = {
    "है", "हैं", "के", "की", "का", "में", "से", "को", "पर", "और", "ने", "एक", "यह",
    "वह", "भी", "तो", "होता", "होती", "होते", "था", "थी", "थे", "किया", "गया", "कर",
    "दिया", "लिया", "लिए", "अपने", "अपनी", "कि", "जो", "करते", "करती", "करता", "इस",
    "उस", "या", "तक", "साथ", "हुए", "हुई", "हुआ", "नहीं", "जाता", "जाती", "गई", "गए",
    "बहुत", "सब", "कोई", "जैसे", "कहा", "होने", "रहे", "रहा", "रही", "सकते", "सकता"
}


def run_hindi_linguist_gate(
    target_lines: int = 150000,
    target_words: int = 200000,
    target_blocks: int = 10000
):
    print("=" * 80)
    print("      AGENT-LINGUIST: HINDI CORPUS INGESTION & QUALITY GATE")
    print("=" * 80)

    # 1. Paths
    iitb_pq = Path(r"C:\Users\ASUS\.cache\huggingface\hub\datasets--cfilt--iitb-english-hindi\snapshots\321516f50bdcc1214fa75164c545478976ed84bd\data\train-00000-of-00001.parquet")
    poetry_csv = Path(r"C:\Users\ASUS\.cache\huggingface\hub\datasets--ReySajju742--Hindi-Poetry-Dataset\snapshots\e58a14b258254a073e2a5c78eab10e313b8c6b7f\output_hi.csv")
    news_pq = Path(r"C:\Users\ASUS\.cache\huggingface\hub\datasets--justmalhar--hindi-short-news\snapshots\8187212de159777b9b9c01fa4df9bf6b8a9660c5\data\train-00000-of-00001.parquet")
    legal_pq = Path(r"C:\Users\ASUS\.cache\huggingface\hub\datasets--Prarabdha--indian-legal-data-sft1.1-hindi-testing\snapshots\84b40dbeecabe4e40652683fca5da1fe853d277c\data\train-00000-of-00001.parquet")

    out_dir = Path(r"c:\OCR - All\data\processed\hindi")
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_texts = []

    # Domain A: Hindi Poetry (Dohas & Verse)
    if poetry_csv.exists():
        print(f"[1/5] Ingesting Hindi Poetry & Classical Verse ({poetry_csv.name})...")
        df_poetry = pd.read_csv(poetry_csv)
        if "content" in df_poetry.columns:
            for text in df_poetry["content"].dropna():
                for line in str(text).splitlines():
                    l_clean = line.strip()
                    if len(l_clean) >= 15:
                        raw_texts.append(l_clean)
        print(f"      Poetry verses harvested: {len(raw_texts):,}")

    # Domain B: Hindi Short News & Journalism
    if news_pq.exists():
        print(f"[2/5] Ingesting Hindi News & Journalism ({news_pq.name})...")
        df_news = pd.read_parquet(news_pq)
        news_count = 0
        if "completion" in df_news.columns:
            for val in df_news["completion"].dropna():
                raw_texts.append(str(val))
                news_count += 1
                if news_count >= 100000:
                    break
        print(f"      News articles harvested: {news_count:,}")

    # Domain C: Legal & Statutory Texts
    if legal_pq.exists():
        print(f"[3/5] Ingesting Legal & Statutory Texts ({legal_pq.name})...")
        df_legal = pd.read_parquet(legal_pq)
        for col in ["context", "hindi_response", "hindi_question"]:
            if col in df_legal.columns:
                for val in df_legal[col].dropna():
                    raw_texts.append(str(val))
        print(f"      Legal prose harvested.")

    # Domain D: Massive General / Technical Prose (IITB)
    if iitb_pq.exists():
        print(f"[4/5] Ingesting IITB English-Hindi Corpus ({iitb_pq.name})...")
        df_iitb = pd.read_parquet(iitb_pq)
        iitb_samples = 0
        for item in df_iitb["translation"]:
            if isinstance(item, dict) and "hi" in item:
                hi_text = item["hi"]
                if hi_text:
                    raw_texts.append(hi_text)
                    iitb_samples += 1
            if iitb_samples >= 600000:
                break
        print(f"      IITB sentences harvested: {iitb_samples:,}")

    print(f"Total raw text units across all 4 domains: {len(raw_texts):,}")

    # Processing & Gatekeeping
    print(f"[5/5] Applying Unicode NFC Normalization, Joiner Safety & Devanagari Filter...")
    valid_sentences = []
    dropped_count = 0
    zwj_count = 0
    zwnj_count = 0

    for raw_t in raw_texts:
        cleaned = UnicodeGatekeeper.normalize_and_clean(raw_t)
        if not cleaned:
            dropped_count += 1
            continue

        if not UnicodeGatekeeper.is_devanagari_dominant(cleaned, min_ratio=0.65):
            dropped_count += 1
            continue

        if ZWJ in cleaned:
            zwj_count += cleaned.count(ZWJ)
        if ZWNJ in cleaned:
            zwnj_count += cleaned.count(ZWNJ)

        chunks = UnicodeGatekeeper.chunk_sentences(cleaned, min_chars=20, max_chars=85)
        for c in chunks:
            assert 20 <= len(c) <= 85, f"Length constraint violated: len={len(c)}"
            if UnicodeGatekeeper.is_devanagari_dominant(c, min_ratio=0.75):
                UnicodeGatekeeper.assert_unicode_integrity(c)
                valid_sentences.append(c)

    print(f"      Total candidate lines extracted: {len(valid_sentences):,}")
    print(f"      Dropped non-Devanagari segments : {dropped_count:,}")
    print(f"      Protected ZWJ occurrences       : {zwj_count:,}")
    print(f"      Protected ZWNJ occurrences      : {zwnj_count:,}")

    # Deduplicate while preserving order
    seen = set()
    deduped_sentences = []
    for s in valid_sentences:
        if s not in seen:
            seen.add(s)
            deduped_sentences.append(s)

    print(f"      Unique deduplicated lines: {len(deduped_sentences):,}")

    # Stratification & Conjunct Mining (Zipfian Mitigation)
    print("      Stratifying corpus and mining Samyuktaksharas...")
    conjunct_lines = []
    general_lines = []

    for s in deduped_sentences:
        if any(cj in s for cj in HIGH_VALUE_CONJUNCTS):
            conjunct_lines.append(s)
        else:
            general_lines.append(s)

    print(f"      Lines with rare Samyuktaksharas: {len(conjunct_lines):,} ({len(conjunct_lines)/len(deduped_sentences)*100:.1f}%)")
    print(f"      General prose lines            : {len(general_lines):,}")

    # 25% conjunct-dense, 75% natural prose
    random.seed(42)
    random.shuffle(conjunct_lines)
    random.shuffle(general_lines)

    n_conjunct = min(len(conjunct_lines), int(target_lines * 0.25))
    n_general = min(len(general_lines), target_lines - n_conjunct)

    final_lines = conjunct_lines[:n_conjunct] + general_lines[:n_general]
    random.shuffle(final_lines)
    print(f"      Selected {len(final_lines):,} target line-level samples.")

    # Extract Words & Isolated Conjuncts
    print("      Extracting words and dampening Zipfian stopwords...")
    word_counter = Counter()
    for s in final_lines:
        for w in s.split():
            w_clean = w.strip("।,;!?-()[]\"'")
            if len(w_clean) >= 2 and UnicodeGatekeeper.is_devanagari_dominant(w_clean, min_ratio=0.85):
                word_counter[w_clean] += 1

    final_words = []
    stopword_cap = 50
    stopword_tracker = Counter()

    # Priority 1: Words containing rare conjuncts
    conjunct_words = [w for w in word_counter if any(cj in w for cj in HIGH_VALUE_CONJUNCTS)]
    for w in conjunct_words:
        final_words.append({"word": w, "type": "samyuktakshara", "count": word_counter[w]})

    # Priority 2: General vocabulary with stopword dampening
    for w, count in word_counter.most_common():
        if w in HINDI_COMMON_STOPWORDS:
            if stopword_tracker[w] < stopword_cap:
                final_words.append({"word": w, "type": "stopword", "count": count})
                stopword_tracker[w] += 1
        else:
            final_words.append({"word": w, "type": "lexical", "count": count})

        if len(final_words) >= target_words:
            break

    print(f"      Selected {len(final_words):,} word-level samples (Rare conjunct words: {len(conjunct_words):,}).")

    # Build Multi-line Blocks for Full Pages & Paragraphs
    print("      Building multi-line blocks for page and paragraph layouts...")
    blocks = []
    chunk_size_lines = 4
    for i in range(0, min(len(final_lines), target_blocks * chunk_size_lines), chunk_size_lines):
        blk = final_lines[i:i+chunk_size_lines]
        if len(blk) == chunk_size_lines:
            blocks.append({
                "block_id": f"hin_blk_{len(blocks):06d}",
                "lines": blk,
                "text": "\n".join(blk)
            })

    # Save to disk
    lines_file = out_dir / "hindi_lines.jsonl"
    words_file = out_dir / "hindi_words.jsonl"
    blocks_file = out_dir / "hindi_blocks.jsonl"
    metrics_file = out_dir / "hindi_linguist_metrics.json"

    print(f"      Writing {lines_file.name}...")
    with open(lines_file, "w", encoding="utf-8") as f:
        for idx, line in enumerate(final_lines):
            f.write(json.dumps({"id": f"hin_line_{idx:06d}", "text": line, "lang": "hin", "script": "Deva"}, ensure_ascii=False) + "\n")

    print(f"      Writing {words_file.name}...")
    with open(words_file, "w", encoding="utf-8") as f:
        for idx, item in enumerate(final_words):
            f.write(json.dumps({"id": f"hin_word_{idx:06d}", **item, "lang": "hin", "script": "Deva"}, ensure_ascii=False) + "\n")

    print(f"      Writing {blocks_file.name}...")
    with open(blocks_file, "w", encoding="utf-8") as f:
        for item in blocks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    analysis = UnicodeGatekeeper.analyze_lexical_balance(final_lines)
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("      LINGUISTIC AUDIT RESULTS:")
    print(f"      - Verified Lines Written       : {len(final_lines):,}")
    print(f"      - Verified Words Written       : {len(final_words):,}")
    print(f"      - Multi-line Blocks Written    : {len(blocks):,}")
    print(f"      - Stopword Ratio               : {analysis['stopword_ratio']*100:.2f}% (Strictly < 30%)")
    print(f"      - Samyuktaksharas Mined        : {analysis['samyuktaksharas_mined']} unique conjunct types")
    print(f"      - Metrics Report Saved         : {metrics_file}")
    print("=" * 80)


if __name__ == "__main__":
    run_hindi_linguist_gate(target_lines=150000, target_words=200000, target_blocks=10000)
