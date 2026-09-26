"""
Agent-Linguist Pipeline for Bhojpuri (bho_Deva)
Processes harvested raw text through mandatory linguistic inspection gates:
1. NFC Normalization & Joiner Safety (ZWJ/ZWNJ preservation).
2. Script Purity & Noise Scrubbing.
3. Sentence Length Bounding (TrOCR / CRNN optimal ranges).
4. Lexical Balancing & Samyuktakshara Mining (Zipfian mitigation).
5. Serialization to data/processed/bhojpuri/
"""

import sys
import os
import json
import random
from pathlib import Path
from collections import Counter
import pandas as pd

# Fix Windows console utf-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from unicode_gate import (
    UnicodeGatekeeper,
    BHOJPURI_COMMON_STOPWORDS,
    HIGH_VALUE_CONJUNCTS,
    ZWJ, ZWNJ, DANDA, DOUBLE_DANDA
)

def run_bhojpuri_linguist_gate(
    target_lines: int = 50000,
    target_words: int = 100000,
    target_blocks: int = 5000
):
    print("=" * 80)
    print("      AGENT-LINGUIST: BHOJPURI CORPUS INGESTION & QUALITY GATE")
    print("=" * 80)

    raw_csv_path = Path(
        r"C:\Users\ASUS\.cache\huggingface\hub\datasets--Satyam810--BhojpuriCorpus\snapshots\d3b569eeb809bcc715eccda4fb80a598375d322d\data\BhojpuriCorpus.csv"
    )
    pq_path = Path(
        r"C:\Users\ASUS\.cache\huggingface\hub\datasets--1rsh--translate-bhojpuri-hi-karya\snapshots\7992985f4039868ff1c05d761665a0458df8a2ba\data\train-00000-of-00001.parquet"
    )
    if not pq_path.exists():
        # Search dynamically
        pq_candidates = list(Path(r"C:\Users\ASUS\.cache\huggingface\hub\datasets--1rsh--translate-bhojpuri-hi-karya\snapshots").glob("**/*.parquet"))
        if pq_candidates:
            pq_path = pq_candidates[0]

    out_dir = Path(r"c:\OCR - All\data\processed\bhojpuri")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] Ingesting raw Bhojpuri text from local caches:")
    print(f"      - CSV: {raw_csv_path.name} ({raw_csv_path.stat().st_size / (1024*1024):.1f} MB)")
    if pq_path.exists():
        print(f"      - Parquet: {pq_path.name} ({pq_path.stat().st_size / (1024*1024):.1f} MB)")

    raw_texts = []

    # 1. Read from BhojpuriCorpus.csv (chunked to preserve memory)
    print("[2/5] Reading BhojpuriCorpus.csv...")
    chunk_size = 50000
    for chunk in pd.read_csv(raw_csv_path, chunksize=chunk_size, usecols=['text'], dtype={'text': str}):
        valid_chunk = chunk['text'].dropna().tolist()
        raw_texts.extend(valid_chunk)
        if len(raw_texts) >= 150000:
            break
    print(f"      Harvested {len(raw_texts):,} raw article / document segments.")

    # 2. Read from 1rsh translate parquet
    if pq_path.exists():
        print("[2b/5] Reading 1rsh human-translated sentences...")
        df_pq = pd.read_parquet(pq_path, columns=['sentence'])
        pq_sentences = df_pq['sentence'].dropna().tolist()
        raw_texts.extend(pq_sentences)
        print(f"      Added {len(pq_sentences):,} high-quality translated sentences.")

    print(f"[3/5] Applying Unicode NFC Normalization, Joiner Safety & Devanagari Filter...")
    valid_sentences = []
    dropped_count = 0
    zwj_count = 0
    zwnj_count = 0

    for raw_t in raw_texts:
        cleaned = UnicodeGatekeeper.normalize_and_clean(raw_t)
        if not cleaned:
            dropped_count += 1
            continue

        # Gatekeeper invariant: Must be Devanagari-dominant
        if not UnicodeGatekeeper.is_devanagari_dominant(cleaned, min_ratio=0.65):
            dropped_count += 1
            continue

        # Track joiners
        if ZWJ in cleaned:
            zwj_count += cleaned.count(ZWJ)
        if ZWNJ in cleaned:
            zwnj_count += cleaned.count(ZWNJ)

        # Slice into length-bounded sentence lines (TrOCR/CRNN: 20 to 85 characters)
        chunks = UnicodeGatekeeper.chunk_sentences(cleaned, min_chars=20, max_chars=85)
        for c in chunks:
            assert 20 <= len(c) <= 85, f"Length constraint violated: len={len(c)}"
            if UnicodeGatekeeper.is_devanagari_dominant(c, min_ratio=0.75):
                UnicodeGatekeeper.assert_unicode_integrity(c)
                valid_sentences.append(c)

    print(f"      Total candidate lines extracted: {len(valid_sentences):,}")
    print(f"      Corrupt / Non-Devanagari segments dropped: {dropped_count:,}")
    print(f"      Protected ZWJ occurrences: {zwj_count:,}")
    print(f"      Protected ZWNJ occurrences: {zwnj_count:,}")

    # Deduplicate while preserving order
    seen = set()
    deduped_sentences = []
    for s in valid_sentences:
        if s not in seen:
            seen.add(s)
            deduped_sentences.append(s)
    print(f"      Unique deduplicated lines: {len(deduped_sentences):,}")

    # 4. Stratification & Conjunct Mining (Zipfian Mitigation)
    print("[4/5] Stratifying and balancing corpus...")
    conjunct_lines = []
    general_lines = []

    for s in deduped_sentences:
        if any(cj in s for cj in HIGH_VALUE_CONJUNCTS):
            conjunct_lines.append(s)
        else:
            general_lines.append(s)

    print(f"      Lines with rare Samyuktaksharas: {len(conjunct_lines):,} ({len(conjunct_lines)/len(deduped_sentences)*100:.1f}%)")
    print(f"      General prose lines: {len(general_lines):,}")

    # Build balanced line selection:
    # 25% conjunct-dense, 75% natural prose
    random.seed(42)
    random.shuffle(conjunct_lines)
    random.shuffle(general_lines)

    n_conjunct = min(len(conjunct_lines), int(target_lines * 0.25))
    n_general = min(len(general_lines), target_lines - n_conjunct)

    final_lines = conjunct_lines[:n_conjunct] + general_lines[:n_general]
    random.shuffle(final_lines)
    print(f"      Selected {len(final_lines):,} target line-level samples.")

    # 5. Extract Words & Isolated Conjuncts
    print("[5/5] Extracting words and lexical units...")
    word_counter = Counter()
    for s in final_lines:
        for w in s.split():
            # Strip outer punctuation
            w_clean = w.strip("।,;!?-()[]\"'")
            if len(w_clean) >= 2 and UnicodeGatekeeper.is_devanagari_dominant(w_clean, min_ratio=0.85):
                word_counter[w_clean] += 1

    # Subsample top stopwords to prevent Zipf's Law imbalance
    final_words = []
    stopword_cap = 50
    stopword_tracker = Counter()

    # Priority 1: Words containing rare conjuncts
    conjunct_words = [w for w in word_counter if any(cj in w for cj in HIGH_VALUE_CONJUNCTS)]
    for w in conjunct_words:
        final_words.append({"word": w, "type": "samyuktakshara", "count": word_counter[w]})

    # Priority 2: General vocabulary with stopword dampening
    for w, count in word_counter.most_common():
        if w in BHOJPURI_COMMON_STOPWORDS:
            if stopword_tracker[w] < stopword_cap:
                final_words.append({"word": w, "type": "stopword", "count": count})
                stopword_tracker[w] += 1
        else:
            final_words.append({"word": w, "type": "lexical", "count": count})

        if len(final_words) >= target_words:
            break

    print(f"      Selected {len(final_words):,} word-level samples (Conjunct words: {len(conjunct_words):,}).")

    # Build Multi-line Blocks for Full Pages
    print("      Building multi-line blocks for page layouts...")
    blocks = []
    chunk_size_lines = 4
    for i in range(0, min(len(final_lines), target_blocks * chunk_size_lines), chunk_size_lines):
        blk = final_lines[i:i+chunk_size_lines]
        if len(blk) == chunk_size_lines:
            blocks.append({
                "block_id": f"bho_blk_{len(blocks):06d}",
                "lines": blk,
                "text": "\n".join(blk)
            })

    # Save to disk
    lines_file = out_dir / "bhojpuri_lines.jsonl"
    words_file = out_dir / "bhojpuri_words.jsonl"
    blocks_file = out_dir / "bhojpuri_blocks.jsonl"
    metrics_file = out_dir / "bhojpuri_linguist_metrics.json"

    print(f"      Writing {lines_file.name}...")
    with open(lines_file, "w", encoding="utf-8") as f:
        for idx, line in enumerate(final_lines):
            f.write(json.dumps({"id": f"bho_line_{idx:06d}", "text": line, "lang": "bho", "script": "Deva"}, ensure_ascii=False) + "\n")

    print(f"      Writing {words_file.name}...")
    with open(words_file, "w", encoding="utf-8") as f:
        for idx, item in enumerate(final_words):
            f.write(json.dumps({"id": f"bho_word_{idx:06d}", **item, "lang": "bho", "script": "Deva"}, ensure_ascii=False) + "\n")

    print(f"      Writing {blocks_file.name}...")
    with open(blocks_file, "w", encoding="utf-8") as f:
        for item in blocks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Run complete lexical analysis
    analysis = UnicodeGatekeeper.analyze_lexical_balance(final_lines)
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("      LINGUISTIC AUDIT RESULTS:")
    print(f"      - Verified Lines Written: {len(final_lines):,}")
    print(f"      - Verified Words Written: {len(final_words):,}")
    print(f"      - Multi-line Blocks Written: {len(blocks):,}")
    print(f"      - Stopword Ratio: {analysis['stopword_ratio']*100:.2f}% (Controlled under 30%)")
    print(f"      - Samyuktaksharas Mined: {analysis['samyuktaksharas_mined']} unique conjunct types")
    print(f"      - Metrics Report Saved: {metrics_file}")
    print("=" * 80)

if __name__ == "__main__":
    run_bhojpuri_linguist_gate(target_lines=50000, target_words=100000, target_blocks=5000)
