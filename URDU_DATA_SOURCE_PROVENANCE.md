# Urdu (`urd`) Corpus Provenance & Reconstruction Ledger

This ledger permanently records the exact origins, repository endpoints, and reconstitution pathways for the Urdu OCR training corpus used in the IndicPixel 1,000,000-sample production run.

---

## 1. Primary Remote Data Sources (Hugging Face Hub)

The Urdu linguistic corpus aggregates 5 multi-genre domains to ensure comprehensive lexical, structural, and typographic coverage:

| Domain | Dataset Identifier | Hugging Face Repository URL | Format & Contents | Sourced Text Type |
|---|---|---|---|---|
| **Poetry** | **`ReySajju742/Urdu-Poetry-Dataset`** & **`synthetic-urdu-poetry-dataset`** | [hf.co/datasets/ReySajju742/Urdu-Poetry-Dataset](https://huggingface.co/datasets/ReySajju742/Urdu-Poetry-Dataset) | `.csv` | Classical Ghazals, Nazms, and Ash'ar couplets (Diwan layout). |
| **Legal & Admin** | **`cheemasohail/Urdu-Legal_ner_corpora`** | [hf.co/datasets/cheemasohail/Urdu-Legal_ner_corpora](https://huggingface.co/datasets/cheemasohail/Urdu-Legal_ner_corpora) | `.txt` | Statutory case filings, penal code, court judgments, and gazette circulars. |
| **Narrative** | **`AreejMehboob17/Urdu_StoryTeller_Dataset`** | [hf.co/datasets/AreejMehboob17/Urdu_StoryTeller_Dataset](https://huggingface.co/datasets/AreejMehboob17/Urdu_StoryTeller_Dataset) | `.parquet` | Fiction, storytelling excerpts, dialogue, and historical prose. |
| **Essays & Non-Fiction** | **`orature/ALIF_Urdu_Corpus_AUC`** | [hf.co/datasets/orature/ALIF_Urdu_Corpus_AUC](https://huggingface.co/datasets/orature/ALIF_Urdu_Corpus_AUC) | `.parquet` | Academic treatises, essays, science, philosophy, and history (ALIF AUC). |
| **Journalism & News** | **`El-chapoo/Urdu-1M-news-text`** | [hf.co/datasets/El-chapoo/Urdu-1M-news-text](https://huggingface.co/datasets/El-chapoo/Urdu-1M-news-text) | `.parquet` | Contemporary journalism (BBC, Dawn, Express), headlines, domestic & world news. |

---

## 2. Ingestion & Transformation Script Pathway

The data was harvested, sanitized, and balanced using:
- **Processor Script:** [`c:\OCR - All\src\linguist\urdu_processor.py`](file:///c:/OCR%20-%20All/src/linguist/urdu_processor.py)
- **Purity Gatekeeper:** [`c:\OCR - All\src\linguist\unicode_gate.py`](file:///c:/OCR%20-%20All/src/linguist/unicode_gate.py)
- **Shaping & Rendering:** [`c:\OCR - All\src\shaper\harfbuzz_shaper.py`](file:///c:/OCR%20-%20All/src/shaper\harfbuzz_shaper.py)

### Pipeline Transformations Applied:
1. **Unicode NFC Normalization:** Normalizes combining characters and diacritical marks.
2. **Joiner Preservation:** Absolute zero stripping of `\u200C` (ZWNJ) and `\u200D` (ZWJ) to preserve Perso-Arabic ligatures and word boundaries.
3. **100% Script Purity Invariant:**
   - 0 English/Latin characters (`a-z`, `A-Z`).
   - 0 Digits (`0-9`, Eastern Arabic-Indic `۰-۹`, Arabic `٠-٩`).
   - Strict preservation of all 40 authentic Urdu alphabet characters (including `پ`, `ٹ`, `چ`, `ڈ`, `ڑ`, `ژ`, `ک`, `گ`, `ں`, `ہ`, `ھ`, `ء`, `ی`, `ے`).
4. **Lexical Partitioning:**
   - `urdu_lines.jsonl`: 75,000 clean lines across 5 domains.
   - `urdu_words.jsonl`: 150,000 isolated vocabulary tokens and conjuncts.
   - `urdu_blocks.jsonl`: 10,000 multi-line narrative and administrative blocks.
   - `urdu_pages.jsonl`: Archetypes A (Diwan), B (Court Gazette), C (Newspaper), and D (Prose Essay).

---

## 3. Remote Synthesized Shard Destination

The resulting 1,000,000 synthesized and augmented OCR samples reside in:
- **Target Repository:** [`Faizaniqbal/IndicPixel-Pan-Indic-OCR`](https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR)
- **Target Subfolder:** `data/urdu/`
- **Shards:** `urd_train_00000.tar` through `urd_train_00199.tar` (200 WebDataset shards @ 5,000 samples each).
- **Format:** WebDataset POSIX `.tar` archives with paired `.png` / `.webp` images and `.json` token-level bounding boxes.
- **Status:** Streamed with live atomic commits and verified HTTP 200 responses.
