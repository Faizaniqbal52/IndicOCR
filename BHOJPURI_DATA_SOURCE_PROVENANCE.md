# Bhojpuri (`bho`) Corpus Provenance & Reconstruction Ledger

This ledger permanently records the exact origins, repository endpoints, and reconstitution pathways for the Bhojpuri OCR training corpus used in the IndicPixel 500,000-sample pilot.

---

## 1. Primary Remote Data Sources (Hugging Face Hub)

| Dataset Identifier | Hugging Face Repository URL | File Format & Location | Description & Contents |
|---|---|---|---|
| **`Satyam810/BhojpuriCorpus`** | [hf.co/datasets/Satyam810/BhojpuriCorpus](https://huggingface.co/datasets/Satyam810/BhojpuriCorpus) | `data/BhojpuriCorpus.csv` (~23.5 MB) | Monolingual Bhojpuri sentences spanning literature, folklore, and local governance. |
| **`1rsh/translate-bhojpuri-hi-karya`** | [hf.co/datasets/1rsh/translate-bhojpuri-hi-karya](https://huggingface.co/datasets/1rsh/translate-bhojpuri-hi-karya) | `data/train-00000-of-00001.parquet` (~12.8 MB) | Bhojpuri–Hindi parallel corpus produced under Project Karya / Microsoft Research. |
| **`ai4bharat/Rural_Women_Bhojpuri`** | [hf.co/datasets/ai4bharat/Rural_Women_Bhojpuri](https://huggingface.co/datasets/ai4bharat/Rural_Women_Bhojpuri) | Audio transcript annotations | Conversational dialectal spoken Bhojpuri transcripts. |

---

## 2. Ingestion & Transformation Script Pathway

The data was harvested and cleansed using:
- **Processor Script:** [`c:\OCR - All\src\linguist\bhojpuri_processor.py`](file:///c:/OCR%20-%20All/src/linguist/bhojpuri_processor.py)
- **Unicode Safety Gate:** [`c:\OCR - All\src\linguist\unicode_gate.py`](file:///c:/OCR%20-%20All/src/linguist/unicode_gate.py)

### Pipeline Transformations Applied:
1. **Unicode NFC Normalization:** Standardized all vowel matras and signs.
2. **Joiner Preservation:** Zero stripping of `\u200D` (ZWJ) and `\u200C` (ZWNJ) to protect complex conjuncts (`क्या`, `प्रकार`, `व्यक्ति`).
3. **Lexical Partitioning:**
   - `bhojpuri_lines.jsonl`: 50,000 sentence lines (20 to 80 characters).
   - `bhojpuri_words.jsonl`: 100,000 vocabulary words with conjunct classifications.
   - `bhojpuri_blocks.jsonl`: 5,000 multi-line narrative blocks for paragraphs and gazettes.

---

## 3. Remote Synthesized Shard Destination

The resulting 500,000 synthesized and augmented OCR samples reside in:
- **Target Repository:** [`Faizaniqbal/IndicPixel-Pan-Indic-OCR`](https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR)
- **Shards:** `bho_train_00000.tar` through `bho_train_00099.tar` (100 WebDataset shards @ 5,000 samples each).
- **Status:** Verified HTTP 200 upload with atomic Hub commits.

---

## 4. Reconstitution Command

If this raw text corpus ever needs to be re-downloaded and rebuilt from scratch:
```powershell
& "C:\Users\ASUS\AppData\Local\Programs\Python\Python312\python.exe" -c "
from huggingface_hub import hf_hub_download
import pandas as pd
from pathlib import Path

csv_path = hf_hub_download(repo_id='Satyam810/BhojpuriCorpus', filename='data/BhojpuriCorpus.csv', repo_type='dataset')
print('Downloaded:', csv_path)
"
```
