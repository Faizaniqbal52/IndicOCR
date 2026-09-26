# Hindi (`hin`) Corpus Provenance & Reconstruction Ledger

This ledger permanently records the exact origins, repository endpoints, and reconstitution pathways for the Hindi OCR training corpus used in the IndicPixel 1,000,000-sample production run.

---

## 1. Primary Remote Data Sources (Hugging Face Hub)

The Hindi linguistic corpus aggregates 4 multi-genre domains to ensure comprehensive lexical, structural, and typographic coverage:

| Domain | Dataset Identifier | Hugging Face Repository URL | Format & Contents | Sourced Text Type |
|---|---|---|---|---|
| **Poetry & Classical Verse** | **`ReySajju742/Hindi-Poetry-Dataset`** | [hf.co/datasets/ReySajju742/Hindi-Poetry-Dataset](https://huggingface.co/datasets/ReySajju742/Hindi-Poetry-Dataset) | `.csv` | Classical Dohas, Kavita stanzas, and rhyming couplets (Kabir, Rahim, Harivansh Rai Bachchan). |
| **Journalism & Current Affairs** | **`justmalhar/hindi-short-news`** | [hf.co/datasets/justmalhar/hindi-short-news](https://huggingface.co/datasets/justmalhar/hindi-short-news) | `.parquet` | Breaking news, regional reporting, politics, sports, and press releases. |
| **Legal & Administrative** | **`Prarabdha/indian-legal-data-sft1.1-hindi-testing`** | [hf.co/datasets/Prarabdha/indian-legal-data-sft1.1-hindi-testing](https://huggingface.co/datasets/Prarabdha/indian-legal-data-sft1.1-hindi-testing) | `.parquet` | Statutory acts, court judgments, legal provisions, and administrative circulars. |
| **Academic, Technical & General Prose** | **`cfilt/iitb-english-hindi`** | [hf.co/datasets/cfilt/iitb-english-hindi](https://huggingface.co/datasets/cfilt/iitb-english-hindi) | `.parquet` | 1,659,083 multi-domain sentences covering textbooks, government circulars, philosophy, and conversational dialogues. |

---

## 2. Ingestion & Transformation Script Pathway

The data was harvested, sanitized, and balanced using:
- **Processor Script:** [`c:\OCR - All\src\linguist\hindi_processor.py`](file:///c:/OCR%20-%20All/src/linguist/hindi_processor.py)
- **Purity Gatekeeper:** [`c:\OCR - All\src\linguist\unicode_gate.py`](file:///c:/OCR%20-%20All/src/linguist/unicode_gate.py)
- **Typography & Layout Engine:** [`c:\OCR - All\src\shaper\hindi_multi_tier_engine.py`](file:///c:/OCR%20-%20All/src/shaper/hindi_multi_tier_engine.py)

### Pipeline Transformations Applied:
1. **Unicode NFC Normalization:** Normalizes combining characters and diacritical marks.
2. **Joiner Preservation:** Absolute zero stripping of `\u200C` (ZWNJ) and `\u200D` (ZWJ) to preserve half-forms and explicit ligatures.
3. **100% Devanagari Script Purity Invariant:**
   - Scrubbed control codes, unmapped legacy typewriter transcoding artifacts, and HTML entities.
   - Preserved Danda (`।`) and Double Danda (`॥`).
4. **Lexical Partitioning:**
   - `hindi_lines.jsonl`: 150,000 clean lines across 4 domains.
   - `hindi_words.jsonl`: 93,357 isolated vocabulary tokens, numerals, and rare Samyuktaksharas.
   - `hindi_blocks.jsonl`: 10,000 multi-line narrative and administrative blocks.
   - `hindi_linguist_metrics.json`: Full audit demonstrating 11.85% stopword ratio and 46 mined conjunct types.

---

## 3. Remote Synthesized Shard Destination

The resulting 1,000,000 synthesized and augmented OCR samples reside in:
- **Target Repository:** [`Faizaniqbal/IndicPixel-Pan-Indic-OCR`](https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR)
- **Target Subfolder:** `data/hindi/`
- **Shards:** `hin_train_00000.tar` through `hin_train_00199.tar` (200 WebDataset shards @ 5,000 samples each).
- **Format:** WebDataset POSIX `.tar` archives with paired `.png` / `.webp` images and `.json` token-level bounding boxes.
- **Status:** Streamed with live atomic commits and verified HTTP 200 responses.
