import os, sys, re, unicodedata
from collections import Counter
from datasets import load_dataset

log_path = 'scripts/corpus_contamination_full_report.txt'

HINDI_STOPWORDS_IN_DEVA = {
    'के', 'लिए', 'को', 'है', 'था', 'थी', 'थीं', 'पर', 'तू', 'सब', 'कर', 'नहीं', 'मंजिल',
    'होता', 'होती', 'होते', 'करना', 'करने', 'अपनी', 'अपने', 'अपना', 'बहुत', 'साथ',
    'लेकिन', 'किंतु', 'परंतु', 'क्योंकि', 'इसलिए', 'उन्होंने', 'उसने', 'जिसने', 'कि'
}

SINDHI_LETTERS = set('ٻڄڏڳڱڌٿٺڦڻڙڪي')
URDU_EXCLUSIVES = set('ٹڈڑے')

with open(log_path, 'w', encoding='utf-8') as out:
    def log(msg):
        out.write(msg + "\n")
        out.flush()

    log("=" * 80)
    log("COMPREHENSIVE PAN-INDIC CORPUS CONTAMINATION AUDIT (7 LANGUAGES)")
    log("=" * 80 + "\n")

    # 1. BODO
    log(">>> [1/7] AUDITING: BODO (alayaran/bodo-monolingual-dataset)")
    try:
        ds = load_dataset("alayaran/bodo-monolingual-dataset", split="train", streaming=True)
        total, contaminated = 0, 0
        samples = []
        for item in ds:
            total += 1
            if total > 500:
                break
            text = item.get("text", "").strip()
            words = set(text.split())
            hits = words.intersection(HINDI_STOPWORDS_IN_DEVA)
            if len(hits) >= 2:
                contaminated += 1
                if len(samples) < 3:
                    samples.append((text[:100], hits))
        log(f"  Total Lines Sampled: {total}")
        log(f"  Hindi Contaminated Lines: {contaminated} ({contaminated/total*100:.2f}%)")
        for s, hits in samples:
            log(f"    - Flagged [hits: {hits}]: {s}...")
    except Exception as e:
        log(f"  Error Bodo: {e}")

    # 2. NEPALI
    log("\n>>> [2/7] AUDITING: NEPALI (wikimedia/wikipedia 20231101.ne)")
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.ne", split="train", streaming=True)
        total, hindi_hits = 0, 0
        for item in ds:
            total += 1
            if total > 100:
                break
            for line in item.get("text", "").split("\n"):
                line = line.strip()
                if len(line) < 20:
                    continue
                words = set(line.split())
                hits = words.intersection({'होता', 'होती', 'होते', 'करना', 'करने', 'लेकिन', 'क्योंकि', 'इसलिए'})
                if len(hits) >= 2:
                    hindi_hits += 1
        log(f"  Total Articles Sampled: {total}")
        log(f"  Suspicious Hindi-style Lines: {hindi_hits}")
    except Exception as e:
        log(f"  Error Nepali: {e}")

    # 3. SINDHI
    log("\n>>> [3/7] AUDITING: SINDHI (wikimedia/wikipedia 20231101.sd)")
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.sd", split="train", streaming=True)
        total, pure_urdu, authentic_sindhi = 0, 0, 0
        for item in ds:
            total += 1
            if total > 100:
                break
            for line in item.get("text", "").split("\n"):
                line = line.strip()
                if len(line) < 20:
                    continue
                has_sindhi = any(c in SINDHI_LETTERS for c in line)
                has_urdu_ex = any(c in URDU_EXCLUSIVES for c in line)
                if has_sindhi:
                    authentic_sindhi += 1
                elif has_urdu_ex and not has_sindhi:
                    pure_urdu += 1
        log(f"  Total Articles Sampled: {total}")
        log(f"  Authentic Sindhi Lines (contains distinct Sindhi glyphs): {authentic_sindhi}")
        log(f"  Urdu-only Lines (missing Sindhi characters): {pure_urdu}")
    except Exception as e:
        log(f"  Error Sindhi: {e}")

    # 4. MANIPURI
    log("\n>>> [4/7] AUDITING: MANIPURI (wikimedia/wikipedia 20231101.mni)")
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.mni", split="train", streaming=True)
        total, mtei_lines, beng_lines = 0, 0, 0
        for item in ds:
            total += 1
            if total > 100:
                break
            for line in item.get("text", "").split("\n"):
                line = line.strip()
                if len(line) < 15:
                    continue
                mtei_chars = sum(1 for c in line if 0xABC0 <= ord(c) <= 0xABFF)
                beng_chars = sum(1 for c in line if 0x0980 <= ord(c) <= 0x09FF)
                if mtei_chars >= 5:
                    mtei_lines += 1
                elif beng_chars >= 5:
                    beng_lines += 1
        log(f"  Total Articles Sampled: {total}")
        log(f"  Meetei Mayek Lines: {mtei_lines}")
        log(f"  Bengali Script Lines: {beng_lines}")
    except Exception as e:
        log(f"  Error Manipuri: {e}")

    # 5. SANTALI
    log("\n>>> [5/7] AUDITING: SANTALI (wikimedia/wikipedia 20231101.sat)")
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.sat", split="train", streaming=True)
        total, olck_lines, foreign_lines = 0, 0, 0
        for item in ds:
            total += 1
            if total > 100:
                break
            for line in item.get("text", "").split("\n"):
                line = line.strip()
                if len(line) < 15:
                    continue
                olck_chars = sum(1 for c in line if 0x1C50 <= ord(c) <= 0x1C7F)
                if olck_chars >= 5:
                    olck_lines += 1
                else:
                    foreign_lines += 1
        log(f"  Total Articles Sampled: {total}")
        log(f"  Ol Chiki Lines: {olck_lines}")
        log(f"  Non-Ol Chiki Lines: {foreign_lines}")
    except Exception as e:
        log(f"  Error Santali: {e}")

    # 6. PUNJABI
    log("\n>>> [6/7] AUDITING: PUNJABI (wikimedia/wikipedia 20231101.pa)")
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.pa", split="train", streaming=True)
        total, guru_lines, foreign = 0, 0, 0
        for item in ds:
            total += 1
            if total > 100:
                break
            for line in item.get("text", "").split("\n"):
                line = line.strip()
                if len(line) < 15:
                    continue
                guru_chars = sum(1 for c in line if 0x0A00 <= ord(c) <= 0x0A7F)
                if guru_chars >= 5:
                    guru_lines += 1
                else:
                    foreign += 1
        log(f"  Total Articles Sampled: {total}")
        log(f"  Gurmukhi Lines: {guru_lines}")
        log(f"  Foreign Script Lines: {foreign}")
    except Exception as e:
        log(f"  Error Punjabi: {e}")

    # 7. KANNADA
    log("\n>>> [7/7] AUDITING: KANNADA (wikimedia/wikipedia 20231101.kn)")
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.kn", split="train", streaming=True)
        total, knda_lines, foreign = 0, 0, 0
        for item in ds:
            total += 1
            if total > 100:
                break
            for line in item.get("text", "").split("\n"):
                line = line.strip()
                if len(line) < 15:
                    continue
                knda_chars = sum(1 for c in line if 0x0C80 <= ord(c) <= 0x0CFF)
                if knda_chars >= 5:
                    knda_lines += 1
                else:
                    foreign += 1
        log(f"  Total Articles Sampled: {total}")
        log(f"  Kannada Lines: {knda_lines}")
        log(f"  Foreign Script Lines: {foreign}")
    except Exception as e:
        log(f"  Error Kannada: {e}")

    log("\n" + "=" * 80)
    log("AUDIT COMPLETE: All 7 language corpora analyzed.")
    log("=" * 80)

print("Finished writing to scripts/corpus_contamination_full_report.txt")
