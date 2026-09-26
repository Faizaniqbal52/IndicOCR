---
license: apache-2.0
task_categories:
- image-to-text
- visual-question-answering
- document-question-answering
language:
- hin
- urd
- ben
- tam
- mar
- tel
- guj
- mal
- ori
- asm
- san
- kan
- pan
- nep
- snd
- brx
- sat
- mni
- bho
- mai
- gom
- kas
- doi
tags:
- ocr
- indic-ocr
- multilingual-ocr
- pan-indic
- document-ai
- document-understanding
- document-layout-analysis
- synthetic-dataset
- webdataset
- tr-ocr
- donut
- layoutlmv3
- nougat
- surya-ocr
- vision-language-models
- text-recognition
- devanagari
- bengali-assamese
- gurmukhi
- gujarati
- odia
- tamil
- telugu
- kannada
- malayalam
- perso-arabic
- ol-chiki
- meetei-mayek
- pytorch
size_categories:
- 10M<n<100M
configs:
- config_name: hindi
  data_files: "data/hindi/*.tar"
- config_name: urdu
  data_files: "data/urdu/*.tar"
- config_name: bengali
  data_files: "data/bengali/*.tar"
- config_name: tamil
  data_files: "data/tamil/*.tar"
- config_name: marathi
  data_files: "data/marathi/*.tar"
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
- config_name: kannada
  data_files: "data/kannada/*.tar"
- config_name: punjabi
  data_files: "data/punjabi/*.tar"
- config_name: nepali
  data_files: "data/nepali/*.tar"
- config_name: sindhi
  data_files: "data/sindhi/*.tar"
- config_name: bodo
  data_files: "data/bodo/*.tar"
- config_name: santali
  data_files: "data/santali/*.tar"
- config_name: manipuri
  data_files: "data/manipuri/*.tar"
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

<img src="assets/hero_banner.png" alt="IndicOCR Hero Banner" width="100%">

<br/>

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-IndicOCR-0284c7.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-10b981.svg)](https://opensource.org/licenses/Apache-2.0)
[![Format: POSIX WebDataset](https://img.shields.io/badge/Format-POSIX%20WebDataset%20(.tar)-f59e0b.svg)](https://github.com/webdataset/webdataset)
[![PyTorch Streaming](https://img.shields.io/badge/PyTorch-Streaming%20DDP%20Ready-6366f1.svg)](https://pytorch.org/)
[![Verified Volume](https://img.shields.io/badge/Verified%20Volume-13%2C250%2C000%20Samples-8b5cf6.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![POSIX Shards](https://img.shields.io/badge/POSIX%20Shards-2%2C650%20Shards-10b981.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![Languages](https://img.shields.io/badge/Languages-23%20Pan--Indic%20Languages-38bdf8.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)
[![Scripts](https://img.shields.io/badge/Scripts-12%20Distinct%20Writing%20Systems-ec4899.svg)](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)

**Large-scale multilingual OCR and document dataset across 23 Pan-Indic languages and 12 writing systems.**

</div>

---

## 1. Overview

**IndicOCR (IndicPixel)** is a large-scale multilingual Optical Character Recognition (OCR) and document dataset covering the South Asian linguistic landscape. The dataset provides dense document coverage across **23 official and literary languages** representing **12 distinct writing systems**.

### Dataset Specifications:
* **Scale & Scope:** Over **13,250,000 verified OCR pairs** organized into **2,650 standardized POSIX WebDataset shards** (`.tar`), enabling distributed multi-GPU streaming without local disk bottlenecks.
* **4-Tier Document Hierarchy:** Encompasses complete structural representation from isolated tokens to complex multi-column documents:
  * **Tier 1: Full-Page Document Spreads (2%)** — Multi-column administrative, literary, and broadsheet layouts with word-level bounding box ground truth.
  * **Tier 2: Multi-Line Paragraph Blocks (13%)** — Wrapped multi-line natural reading sequences.
  * **Tier 3: Reading Lines (55%)** — Core continuous text sentences with token-level bounding coordinates.
  * **Tier 4: Isolated Tokens & Complex Conjuncts (30%)** — Rare samyuktaksharas, ligatures, numerals, and vocabulary words.
* **Complex Text Layout (CTL) Fidelity:** Native HarfBuzz OpenType shaping and FreeType rasterization with font-level metrics to prevent diacritic truncation and glyph clipping across all scripts.
* **Realistic Document Degradation:** High-fidelity simulation of scan wear, bleed-through, paper textures, non-uniform illumination, folds, and compression artifacts for real-world document generalization.

---

## 2. Dataset Portfolio & Linguistic Coverage

| Language | Script | ISO 639-3 | Verified Samples | POSIX Shards | Granularity Tiers | Document Archetypes |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **Hindi** | Devanagari (`Deva`) | `hin` | **1,000,000** | 200 | Words, Lines, Paragraphs, Pages | Literary, Gazettes, Broadsheets |
| **Urdu** | Perso-Arabic (`Arab`) | `urd` | **1,000,000** | 200 | Words, Lines, Paragraphs, Pages | Classical Poetry, Legal Decrees, Newspapers |
| **Bengali** | Bengali (`Beng`) | `ben` | **1,000,000** | 200 | Words, Lines, Paragraphs, Pages | Periodicals, State Gazettes, Dailies |
| **Tamil** | Tamil (`Taml`) | `tam` | **1,000,000** | 200 | Words, Lines, Paragraphs, Pages | Sangam Literary, Official Gazettes, Newsprint |
| **Marathi** | Devanagari (`Deva`) | `mar` | **1,000,000** | 200 | Words, Lines, Paragraphs, Pages | State Gazettes, Periodicals, Newsprint |
| **Telugu** | Telugu (`Telu`) | `tel` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Rajapatram, Literary Journals, Broadsheets |
| **Gujarati** | Gujarati (`Gujr`) | `guj` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | State Gazettes, Dailies, Cultural Reviews |
| **Kannada** | Kannada (`Knda`) | `kan` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Karnataka Rajyapatra, Literary Reviews, Dailies |
| **Malayalam** | Malayalam (`Mlym`) | `mal` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Kerala Gazettes, Sahitya Masika, Broadsheets |
| **Odia** | Odia (`Orya`) | `ori` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Odisha Rajapatra, Utkal Sahitya, Samaja |
| **Punjabi** | Gurmukhi (`Guru`) | `pan` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Punjab Gazette, Literary Reviews, Ajit Dailies |
| **Assamese** | Assamese (`Beng`) | `asm` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Asom Rajpatra, Sahitya Sabha, Pratidin |
| **Nepali** | Devanagari (`Deva`) | `nep` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Nepal Rajpatra, Gorkhapatra, Literary Reviews |
| **Sanskrit** | Devanagari (`Deva`) | `san` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Samskrita Bharati, Veda Samhita, Sudharma |
| **Sindhi** | Extended Perso-Arabic (`Arab`) | `snd` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Sindh Gazette, Cultural Reviews, Ibrat Dailies |
| **Bodo** | Devanagari (`Deva`) | `brx` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Bodoland Gazette, Literary Publications, News |
| **Santali** | Ol Chiki (`Olck`) | `sat` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Cultural Gazettes, Official Notices, Dailies |
| **Manipuri** | Meetei Mayek (`Mtei`) | `mni` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Manipur Gazette, Literary Reviews, Poknapham |
| **Bhojpuri** | Devanagari (`Deva`) | `bho` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Folk Literature, Gram Panchayat Notices |
| **Kashmiri** | Perso-Arabic (`Arab`) | `kas` | **500,000** | 100 | Words, Lines, Paragraphs, Pages | Cultural Reviews, Regional Decrees |
| **Konkani** | Devanagari (`Deva`) | `gom` | **250,000** | 50 | Words, Lines, Paragraphs, Pages | State Gazettes, Cultural Publications |
| **Maithili** | Devanagari (`Deva`) | `mai` | **250,000** | 50 | Words, Lines, Paragraphs, Pages | Regional Notices, Literary Periodicals |
| **Dogri** | Devanagari (`Deva`) | `doi` | **250,000** | 50 | Words, Lines, Paragraphs, Pages | Literary Digests, Regional Gazette Notices |
| **TOTAL** | **12 Writing Systems** | **23 Languages** | **13,250,000** | **2,650** | **4 Structural Tiers** | **Pan-Indic Administrative & Literary** |

---

## 3. Structural Specification & Annotation Format

Each sample is packaged inside standardized WebDataset `.tar` archives containing paired lossless image files (`.webp`) and comprehensive metadata descriptors (`.json`):

```json
{
  "sample_key": "kan_0008644",
  "tier": "Tier_2_Paragraph",
  "lang": "kan",
  "script": "Knda",
  "font_name": "BalooTamma2-Regular.ttf",
  "is_clean": false,
  "canvas_size": [669, 213],
  "text": "ಅದನ್ನು ತಂದು ಶ್ರೀನಿವಾಸನಿಗೆ ಕೊಡುತ್ತಾಳೆ. ಅಂಗಡಿಗೆ ಹಿಂದಿರುಗಿ\nಬಂದ ಶ್ರೀನಿವಾಸ ಡಬ್ಬಿಯನ್ನು",
  "tokens": [
    {"text": "ಅದನ್ನು", "bbox": [24, 16, 110, 68]},
    {"text": "ತಂದು", "bbox": [122, 16, 185, 68]},
    {"text": "ಶ್ರೀನಿವಾಸನಿಗೆ", "bbox": [198, 16, 360, 68]}
  ],
  "token_count": 22,
  "applied_augmentations": [
    "#04 Substrate: notebook_ruled",
    "#40 Keystone Tilt"
  ]
}
```

### Metadata Fields:
* `sample_key` *(string)*: Unique globally indexed identifier across shards.
* `tier` *(string)*: Structural tier (`Tier_1_FullPage`, `Tier_2_Paragraph`, `Tier_3_Line`, `Tier_4_Word`).
* `lang` *(string)*: ISO 639-3 language identifier.
* `script` *(string)*: ISO 15924 script tag.
* `font_name` *(string)*: Typographic font family utilized for CTL rendering.
* `canvas_size` *(list of int)*: `[width, height]` in pixels.
* `text` *(string)*: Canonical ground truth text in Unicode NFC normalization.
* `tokens` *(list of dict)*: Word-level bounding boxes `[x0, y0, x1, y1]` tightly enclosing ink boundaries.
* `token_count` *(int)*: Total word/token count.
* `applied_augmentations` *(list of string)*: Stochastic physical degradation operators applied.

---

## 4. Distributed Streaming Quickstart (PyTorch / WebDataset)

The dataset is formatted for direct streaming directly into GPU memory without prior disk extraction:

```python
import webdataset as wds
from torch.utils.data import DataLoader

# Example: Stream Kannada shards directly from Hugging Face Hub
shard_url = "https://huggingface.co/datasets/Faizaniqbal/IndicOCR/resolve/main/data/kannada/kan_train_{00000..00099}.tar"

dataset = (
    wds.WebDataset(shard_url, resampled=False, shardshuffle=True)
    .shuffle(1000)
    .decode("pil")
    .to_tuple("webp", "json")
)

dataloader = DataLoader(dataset, batch_size=32, num_workers=4)

for images, metadata in dataloader:
    # Forward pass to Vision-Language Model / TrOCR / Donut / LayoutLMv3
    pass
```

---

## 5. Licensing & Citation

IndicPixel is released under the **Apache 2.0 License** for open commercial and academic research.

```bibtex
@dataset{indicpixel_2026,
  author    = {Faizan Iqbal},
  title     = {IndicPixel: A Large-Scale Foundational Multilingual Document AI and OCR Benchmark for Pan-Indic Languages},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/Faizaniqbal/IndicOCR}
}
```
