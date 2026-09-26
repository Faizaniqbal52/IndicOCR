import os
from huggingface_hub import HfApi
from dotenv import load_dotenv

load_dotenv('c:/OCR - All/.env')
api = HfApi(token=os.getenv('HF_TOKEN'))
repo = 'Faizaniqbal/IndicOCR'

readme_text = """---
license: apache-2.0
task_categories:
- image-to-text
- visual-question-answering
- document-question-answering
language:
- hin
- urd
- ben
- mar
- tam
- tel
- guj
- mal
- ori
- asm
- san
- bho
- mai
- gom
- kas
- doi
tags:
- ocr
- synthetic-dataset
- indic-ocr
- devanagari
- perso-arabic
- bengali
- tamil
- telugu
- gujarati
- malayalam
- odia
- assamese
- sanskrit
- webdataset
- tr-ocr
- layoutlmv3
- donut
- document-ai
size_categories:
- 1M<n<10M
configs:
- config_name: hindi
  data_files: "data/hindi/*.tar"
- config_name: urdu
  data_files: "data/urdu/*.tar"
- config_name: bengali
  data_files: "data/bengali/*.tar"
- config_name: marathi
  data_files: "data/marathi/*.tar"
- config_name: tamil
  data_files: "data/tamil/*.tar"
- config_name: telugu
  data_files: "data/telugu/*.tar"
- config_name: gujarati
  data_files: "data/gujarati/*.tar"
- config_name: malayalam
  data_files: "data/malayalam/*.tar"
- config_name: odia
  data_files: "data/odia/*.tar"
- config_name: assamese
  data_files: "data/assamese/*.tar"
- config_name: sanskrit
  data_files: "data/sanskrit/*.tar"
- config_name: bhojpuri
  data_files: "data/bhojpuri/*.tar"
- config_name: kashmiri
  data_files: "data/kashmiri/*.tar"
- config_name: maithili
  data_files: "data/maithili/*.tar"
- config_name: konkani
  data_files: "data/konkani/*.tar"
- config_name: dogri
  data_files: "data/dogri/*.tar"
---

<div align="center">

<img src="https://huggingface.co/datasets/Faizaniqbal/IndicOCR/resolve/main/assets/hero_banner.png" alt="IndicPixel Hero Banner" width="100%">

<br/>

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-IndicOCR-0284c7.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-10b981.svg)](https://opensource.org/licenses/Apache-2.0)
[![Format: POSIX WebDataset](https://img.shields.io/badge/Format-POSIX%20WebDataset%20(.tar)-f59e0b.svg)](https://github.com/webdataset/webdataset)
[![PyTorch Streaming](https://img.shields.io/badge/PyTorch-Streaming%20DDP%20Ready-6366f1.svg)](https://pytorch.org/)
[![Verified Volume](https://img.shields.io/badge/Verified%20Volume-8%2C685%2C000%2B%20Samples-8b5cf6.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![POSIX Shards](https://img.shields.io/badge/POSIX%20Shards-1%2C737%2B%20Shards-10b981.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![Live Languages](https://img.shields.io/badge/Live%20Languages-16%20Languages-38bdf8.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)

**The premier large-scale, high-fidelity multilingual OCR & Document AI dataset across Pan-Indic languages and scripts.**

</div>

---

## Overview

**IndicPixel (IndicOCR)** is a comprehensive, open-access multilingual Document AI and synthetic OCR benchmark engineered to advance text recognition across South Asian languages and scripts.

### Dataset Portfolio (8.68M+ Samples | 1,737 Shards | 16 Languages)
- **Dataset Volume:** **8,685,000+ verified OCR pairs** packaged across **1,737 POSIX WebDataset shards** (`.tar`), streamed losslessly with companion JSON metadata.
- **Language Coverage:** Hindi, Urdu, Bengali, Tamil, Marathi, Telugu, Gujarati, Malayalam, Bhojpuri, Kashmiri, Konkani, Maithili, Dogri, Odia, Assamese, and Sanskrit.
- **Zero-Defect Quality Assertions:** 0.00% `.notdef` tofu rate (Glyph ID 0), 0.00% diacritic clipping rate, 54-operator stochastic physical degradation taxonomy, and full word/token bounding box ground truth.

The dataset addresses key challenges in Indic OCR:
- **Complex Script Support:** Natural rendering of conjunct stacking, subjoined consonants (ottulu/matras), and cascading ligatures across Devanagari, Perso-Arabic, Bengali, Assamese, Tamil, Telugu, Gujarati, Malayalam, Odia, and regional scripts.
- **Granular Document Hierarchy:** Spanning 4 standardized granularity tiers: Isolated Tokens (30%), Reading Sequence Lines (55%), Paragraph Blocks (13%), and Full-Page Document Spreads (2%).
- **Real-World Environmental Degradations:** High-fidelity simulation of scan artifacts, physical paper textures, ink bleed, non-uniform shadows, perspective transforms, and print variations via the master 54-operator degradation taxonomy.
- **Streaming WebDataset Format:** Lossless WebP images with character- and token-level ground truth bounding boxes packaged into standardized `.tar` archives for direct distributed GPU streaming.

---

## Dataset Portfolio & Language Coverage

| Language | Script | ISO 639-3 | Verified Samples | Shards | Payload Format | Archetype Styles | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| **Hindi** | Devanagari (`Deva`) | `hin` | **1,000,000** | 200 | WebDataset `.tar` | Literary, Gazettes, Broadsheet Newspapers | `Available` |
| **Urdu** | Perso-Arabic (`Arab` / Nastaliq & Naskh) | `urd` | **1,000,000** | 200 | WebDataset `.tar` | Classical Poetry, Legal Decrees, Broadsheets | `Available` |
| **Bengali** | Bengali (`Beng`) | `ben` | **1,000,000** | 200 | WebDataset `.tar` | Literary Magazines, State Gazettes, Dailies | `Available` |
| **Tamil** | Tamil (`Taml`) | `tam` | **1,000,000** | 200 | WebDataset `.tar` | Sangam Literary, Official Gazettes, Newspapers | `Available` |
| **Marathi** | Devanagari (`Deva`) | `mar` | **1,000,000** | 200 | WebDataset `.tar` | State Gazettes, Newsprint, Literary Periodicals | `Available` |
| **Telugu** | Telugu (`Telu`) | `tel` | **500,000** | 100 | WebDataset `.tar` | Rajapatram, Literary Journals, Broadsheets | `Available` |
| **Gujarati** | Gujarati (`Gujr`) | `guj` | **500,000** | 100 | WebDataset `.tar` | State Gazettes, Daily Newspapers, Periodicals | `Available` |
| **Malayalam** | Malayalam (`Mlym`) | `mal` | **500,000** | 100 | WebDataset `.tar` | Kerala Gazettes, Sahitya Masika, Broadsheets | `Available` |
| **Bhojpuri** | Devanagari (`Deva`) | `bho` | **500,000** | 100 | WebDataset `.tar` | Folk Literature, Gram Panchayat Notices | `Available` |
| **Kashmiri** | Perso-Arabic (`Arab`) | `kas` | **500,000** | 100 | WebDataset `.tar` | Cultural Reviews, Regional Decrees | `Available` |
| **Konkani** | Devanagari (`Deva`) | `gom` | **250,000** | 50 | WebDataset `.tar` | State Gazettes, Cultural Publications | `Available` |
| **Maithili** | Devanagari (`Deva`) | `mai` | **250,000** | 50 | WebDataset `.tar` | Regional Notices, Literary Periodicals | `Available` |
| **Dogri** | Devanagari (`Deva`) | `doi` | **250,000** | 50 | WebDataset `.tar` | Literary Digests, Regional Gazette Notices | `Available` |
| **Odia** | Odia (`Orya`) | `ori` | **155,000+** | 31+ | WebDataset `.tar` | Odisha Rajapatra, Utkal Sahitya, Samaja | `Available` |
| **Assamese** | Assamese (`Beng`) | `asm` | **155,000+** | 31+ | WebDataset `.tar` | Asom Rajpatra, Sahitya Sabha, Pratidin | `Available` |
| **Sanskrit** | Devanagari (`Deva`) | `san` | **125,000+** | 25+ | WebDataset `.tar` | Samskrita Bharati, Veda Samhita, Sudharma | `Available` |

---

## Data Structure & Format

Each sample is stored in WebDataset `.tar` shards containing dual lossless image and JSON metadata files:

```json
{
  "sample_key": "ori_0012500",
  "tier": "Tier_3_Line",
  "lang": "ori",
  "script": "Orya",
  "font_name": "NotoSansOriya-Regular.ttf",
  "is_clean": false,
  "canvas_size": [850, 80],
  "text": "ଭାରତୀୟ ସମ୍ବିଧାନର ଅଷ୍ଟମ ଅନୁସୂଚୀରେ ବାଇଶିଟି ଭାଷା ଅନ୍ତର୍ଭୁକ୍ତ ଅଟେ।",
  "tokens": [
    {"text": "ଭାରତୀୟ", "bbox": [15, 12, 110, 68]},
    {"text": "ସମ୍ବିଧାନର", "bbox": [120, 12, 225, 68]}
  ],
  "num_tokens": 7
}
```

---

## Quickstart & Streaming with PyTorch

The dataset is formatted for direct high-throughput streaming via [WebDataset](https://github.com/webdataset/webdataset):

```python
import webdataset as wds
from torch.utils.data import DataLoader

# Example: Stream Odia shards directly from Hugging Face Hub
shard_url = "https://huggingface.co/datasets/Faizaniqbal/IndicOCR/resolve/main/data/odia/ori_train_{00000..00030}.tar"

dataset = (
    wds.WebDataset(shard_url, resampled=False, shardshuffle=True)
    .shuffle(1000)
    .decode("pil")
    .to_tuple("webp", "json")
)

dataloader = DataLoader(dataset, batch_size=32, num_workers=4)

for images, metadata in dataloader:
    # Forward pass to Vision-Encoder-Decoder / LayoutLM / TrOCR
    pass
```

---

## Licensing & Citation

The dataset is distributed under the **Apache 2.0 License**.

```bibtex
@dataset{indicpixel_2026,
  author    = {Faizan Iqbal},
  title     = {IndicPixel: Pan-Indic High-Fidelity Synthetic Multilingual OCR Dataset},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/Faizaniqbal/IndicOCR}
}
```
"""

with open('c:/OCR - All/README.md', 'w', encoding='utf-8') as f:
    f.write(readme_text.strip() + '\n')

print('Wrote clean local README.md')

commit = api.upload_file(
    path_or_fileobj='c:/OCR - All/README.md',
    path_in_repo='README.md',
    repo_id=repo,
    repo_type='dataset',
    commit_message='docs: clean and professionalize public dataset card'
)
print('Pushed to Hugging Face successfully:', commit)
