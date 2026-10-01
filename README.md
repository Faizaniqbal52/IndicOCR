---
pretty_name: BhartiOCR
language:
- hi
- ur
- bn
- ta
- mr
- te
- gu
- kn
- ml
- or
- pa
- as
- ne
- sa
- sat
- mni
- sd
- brx
- bho
- ks
- gom
- mai
- doi
license: apache-2.0
task_categories:
- image-to-text
tags:
- ocr
- multilingual-ocr
- document-ai
- synthetic-data
- computer-vision
- indian-languages
- pan-indic
- webdataset
- document-understanding
- image-text
- optical-character-recognition
size_categories:
- 10M<n<100M
---

<div align="center">

<img src="assets/hero_banner.png" alt="BhartiOCR Hero Banner" width="100%">

<br/>

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-BhartiOCR-0284c7.svg)](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-10b981.svg)](https://opensource.org/licenses/Apache-2.0)
[![Format: POSIX WebDataset](https://img.shields.io/badge/Format-POSIX%20WebDataset%20(.tar)-f59e0b.svg)](https://github.com/webdataset/webdataset)
[![PyTorch Streaming](https://img.shields.io/badge/PyTorch-Streaming%20DDP%20Ready-6366f1.svg)](https://pytorch.org/)
[![Total Volume](https://img.shields.io/badge/Total%20Volume-13%2C250%2C000%20Samples-8b5cf6.svg)](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR)
[![POSIX Shards](https://img.shields.io/badge/POSIX%20Shards-2%2C650%20Shards-10b981.svg)](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR)
[![Languages](https://img.shields.io/badge/Languages-23%20Pan--Indic%20Languages-38bdf8.svg)](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR)
[![Writing Systems](https://img.shields.io/badge/Writing%20Systems-12%20Distinct%20Scripts-ec4899.svg)](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR)

</div>

# BhartiOCR
### A Multilingual Synthetic OCR and Document Benchmark for Indian Languages

**13.25M image-text pairs · 23 languages · 12 writing systems · 2,650 WebDataset shards**

BhartiOCR is a large-scale synthetic dataset and benchmark designed for research in multilingual Optical Character Recognition (OCR), document layout analysis, and degradation robustness across South Asian languages. The current release (v1.0) contains **13,250,000 paired image-text instances** distributed across **23 languages** and **12 writing systems**. All samples are packaged as WebDataset-compatible POSIX `.tar` archives for direct distributed streaming into modern deep learning frameworks.

---

## 1. Dataset Summary

| Property | Current Release Specification (v1.0) |
|---|---|
| **Dataset Name** | BhartiOCR |
| **Current Version** | v1.0 |
| **Total Samples** | 13,250,000 paired image-text instances |
| **Languages Covered** | 23 (22 Eighth Schedule Constitutional Languages of India + Bhojpuri) |
| **Writing Systems** | 12 distinct scripts (including bidirectional LTR Brahmic and RTL Extended Arabic) |
| **Packaging Format** | 2,650 standardized WebDataset POSIX `.tar` archives |
| **Shard Capacity** | ~5,000 paired samples per archive |
| **Image Encoding** | Lossless WebP (`.webp`) |
| **Annotation Format** | UTF-8 JSON (`.json`) with token-level bounding coordinates |
| **Primary Task** | Multilingual OCR / Document Image-to-Text / Layout Segmentation |
| **Dataset Type** | Synthetic Document AI Benchmark |
| **License** | Apache-2.0 (see [Licensing and Upstream Provenance](#16-licensing)) |
| **Access Policy** | Gated on Hugging Face Hub (requires user agreement) |

---

## 2. Motivation

Optical Character Recognition (OCR) and Vision-Language Models (VLMs) applied to Indian languages frequently fail on real-world printed material. BhartiOCR addresses three recurring challenges in synthetic document generation:

### 2.1 Diacritic and Vertical Layout Truncation
Indian writing systems feature complex non-linear vertical vowel modifiers (*matras*, *halants*, *anusvaras*, *visargas*, and *nuktas*) situated above, below, or across character stems. Standard rasterization pipelines frequently compute tight horizontal bounding boxes that clip ascender and descender strokes, leading to feature degradation during spatial pooling ($H=1$) in convolutional and Transformer backbones. BhartiOCR integrates dynamic font-metric zone calculations ($H_{\text{ascender}} + H_{\text{body}} + H_{\text{descender}}$) with generous padding to prevent boundary clipping.

### 2.2 Complex Text Layout (CTL) and Ligature Integrity
Indic scripts require OpenType shaping engines to compute context-dependent glyph substitutions, consonant conjuncts (*samyuktaksharas*), and explicit half-forms. Naive rasterization tools produce disjointed graphemes or unmapped placeholder boxes (`.notdef` Glyph ID 0). BhartiOCR processes all text through HarfBuzz (`uharfbuzz`) with explicit script tags, language specifiers, and bidirectional text direction (`ltr` / `rtl`).

### 2.3 The Synthetic-to-Real Document Domain Gap
Clean synthetic text renders fail to prepare models for the visual noise, chemical degradation, and mechanical distortions encountered in physical archives, newsprints, court filings, and administrative circulars. BhartiOCR incorporates a 54-operator physical degradation pipeline modeling substrate fibers, ink bleed, photostat thresholding, handling creases, bureaucratic stamps, lighting gradients, and optical sensor noise.

---

## 3. Dataset Scale & Train/Validation/Test Splits

The dataset comprises 13,250,000 instances organized into a standardized 90 / 5 / 5 partition scheme:

| Split | Percentage | Total Samples | Total Shards | Intended Use |
|---|:---:|---:|---:|---|
| **Train** | 90.0% | 11,925,000 | 2,385 | OCR pretraining, fine-tuning, and document layout modeling |
| **Validation** | 5.0% | 662,500 | 132 | Hyperparameter tuning and checkpoint selection |
| **Test** | 5.0% | 662,500 | 133 | Zero-shot and fine-tuned benchmark evaluation |
| **Total** | **100.0%** | **13,250,000** | **2,650** | Complete v1.0 release |

---

## 4. Language and Writing-System Coverage

The v1.0 release encompasses all 22 official Eighth Schedule languages of India plus Bhojpuri:

| Language | Script | ISO 639-3 | Script Code |
|---|---|:---:|:---:|
| **Hindi** | Devanagari | `hin` | `Deva` |
| **Urdu** | Extended Arabic | `urd` | `Arab` |
| **Bengali** | Bengali | `ben` | `Beng` |
| **Tamil** | Tamil | `tam` | `Taml` |
| **Marathi** | Devanagari | `mar` | `Deva` |
| **Telugu** | Telugu | `tel` | `Telu` |
| **Gujarati** | Gujarati | `guj` | `Gujr` |
| **Kannada** | Kannada | `kan` | `Knda` |
| **Malayalam** | Malayalam | `mal` | `Mlym` |
| **Odia** | Odia | `ori` | `Orya` |
| **Punjabi** | Gurmukhi | `pan` | `Guru` |
| **Assamese** | Bengali-Assamese | `asm` | `Beng` |
| **Nepali** | Devanagari | `nep` | `Deva` |
| **Sanskrit** | Devanagari | `san` | `Deva` |
| **Santali** | Ol Chiki | `sat` | `Olck` |
| **Manipuri** | Meetei Mayek | `mni` | `Mtei` |
| **Sindhi** | Extended Arabic | `snd` | `Arab` |
| **Bodo** | Devanagari | `brx` | `Deva` |
| **Bhojpuri** | Devanagari | `bho` | `Deva` |
| **Kashmiri** | Extended Arabic | `kas` | `Arab` |
| **Konkani** | Devanagari | `gom` | `Deva` |
| **Maithili** | Devanagari | `mai` | `Deva` |
| **Dogri** | Devanagari | `doi` | `Deva` |
| **Total** | **12 Writing Systems** | **23** | |

---

## 5. Structural Granularity

To support tasks ranging from word recognition to complete document layout parsing, samples are stratified into four structural tiers:

| Tier | Granularity | Volume Share | Samples | Typ. Resolution ($W \times H$) | Words / Instance | Primary Evaluation Focus |
|---|---|:---:|---:|:---:|:---:|---|
| **Tier 1** | Full-page documents | 2.0% | 265,000 | $1200 \times 1600$ | 80–350 | Multi-column reading order, document layout analysis (DLA) |
| **Tier 2** | Paragraph blocks | 13.0% | 1,722,500 | $800 \times 400$ | 25–80 | Multi-line text block recognition, paragraph-level transcription |
| **Tier 3** | Reading lines | 55.0% | 7,287,500 | $640 \times 72$ | 4–18 | Sequence-to-sequence line recognition (TrOCR, CRNN) |
| **Tier 4** | Tokens & conjuncts | 30.0% | 3,975,000 | $220 \times 54$ | 1–3 | Vocabulary coverage, ligature classification, rare conjunct evaluation |
| **Total** | | **100.0%** | **13,250,000** | | | |

* **Tier 1 (Full-page documents):** Multi-column synthetic compositions simulating newspapers, government gazettes, and book pages with token-level bounding boxes and reading order metadata.
* **Tier 2 (Paragraph blocks):** Justified multi-line formatted text blocks with uniform leading and inter-paragraph margins.
* **Tier 3 (Reading lines):** Continuous syntactic lines, poetic verses, newspaper headlines, and conversational dialogue.
* **Tier 4 (Tokens and conjuncts):** Isolated vocabulary words, numbers, currency symbols, and complex consonant conjuncts.

---

## 6. Script Distribution & Typographic Assets

The 13.25M corpus spans 12 writing systems shaped with over 140 open-source OpenType fonts:

| Script Family | ISO Code | Languages Represented | Total Samples | Sample Fonts Used |
|---|:---:|---|---:|---|
| **Devanagari** | `Deva` | Hindi, Marathi, Nepali, Sanskrit, Bodo, Bhojpuri, Konkani, Maithili, Dogri | 5,250,000 | Noto Sans Devanagari, Sahitya, Halant, Kalam, Asar, Gotu, Rajdhani, Yatra One |
| **Extended Arabic (RTL)** | `Arab` | Urdu, Sindhi, Kashmiri | 2,000,000 | Noto Nastaliq Urdu, Noto Sans Arabic, Gulzar, Lateef, Scheherazade New |
| **Bengali-Assamese** | `Beng` | Bengali, Assamese | 1,500,000 | Noto Sans Bengali, Galada, Mina, Atma, Hind Siliguri, Tiro Bangla |
| **Tamil** | `Taml` | Tamil | 1,000,000 | Noto Sans Tamil, Arima Madurai, Catamaran, Mukta Malar, Pavanam |
| **Telugu** | `Telu` | Telugu | 500,000 | Noto Sans Telugu, Dhurjati, Mandali, Ramabhadra, Suranna, Tenali Ramakrishna |
| **Kannada** | `Knda` | Kannada | 500,000 | Noto Sans Kannada, Baloo Tamma 2, Hubballi, Naganandini, Tiro Kannada |
| **Malayalam** | `Mlym` | Malayalam | 500,000 | Noto Sans Malayalam, Chilanka, Gayathri, Manjari, Meera, Ranga |
| **Gujarati** | `Gujr` | Gujarati | 500,000 | Noto Sans Gujarati, Farsan, Mogra, Rasa, Shrikhand, Mukta Vaani |
| **Odia** | `Orya` | Odia | 500,000 | Noto Sans Odia, Baloo Bhaina 2, Kalinga, Soumyashree, Odia OT |
| **Gurmukhi** | `Guru` | Punjabi | 500,000 | Noto Sans Gurmukhi, Baloo Paaji 2, Mukta Mahee, Saab, Raavi |
| **Ol Chiki** | `Olck` | Santali | 500,000 | Noto Sans Ol Chiki, Guru Gomke, Ol Chiki Classic |
| **Meetei Mayek** | `Mtei` | Manipuri | 500,000 | Noto Sans Meetei Mayek, Eeyek, Meetei Mayek Unicode |

---

## 7. Rendering and Typography Validation Pipeline

Text synthesis uses a script-aware rendering architecture designed to enforce strict typographic and Unicode standards:

```
[Raw Text Corpus]
       │
       ▼
[Unicode NFC Normalization & ZWJ/ZWNJ Preservation]
       │
       ▼
[Corpus Contamination Gate: Foreign Stopword Scrubbing]
       │
       ▼
[Font cmap Validation via fontTools.ttLib.TTFont]
       │
       ▼
[HarfBuzz OpenType CTL Shaping (Script/Direction Tagged)]
       │
       ▼
[FreeType Subpixel Rasterization with Dynamic Zone Padding]
       │
       ▼
[Post-Render Verification: 0 .notdef Glyphs, 0 Canvas Clipping]
```

### 7.1 OpenType CTL Shaping
Text buffers are normalized to Unicode NFC while strictly preserving Zero-Width Joiner (`\u200D`) and Zero-Width Non-Joiner (`\u200C`) sequences. Text is shaped using `uharfbuzz` with explicit script tags (`Deva`, `Beng`, `Taml`, `Arab`, `Mtei`, `Olck`, etc.) and directionality (`ltr` for Brahmic scripts, `rtl` for Extended Arabic).

### 7.2 Font Character-Map Validation
Before shaping, candidate fonts are analyzed with `fontTools.ttLib.TTFont` to extract their Unicode `cmap` table. If any character in a target string lacks a glyph mapping, the string-font pair is rejected. This prevents missing-glyph placeholders (`.notdef` / Glyph ID 0) from entering the generated dataset.

### 7.3 Dynamic Vertical Metric Containment
Vertical bounding canvas dimensions are calculated per font:
$$\text{Height} = \text{Ascender Zone} + \text{Body Zone} + \text{Descender Zone} + \text{Safety Padding}$$
This ensures all upper and lower diacritical markers remain strictly contained within the rasterized canvas.

---

## 8. Master 54-Operator Physical Degradation Pipeline

BhartiOCR incorporates a 4-layer probabilistic physical degradation DAG with **54 documented operators**:
* **12.5% Clean Controls:** Undegraded digital baseline scans.
* **87.5% Compound Degraded Samples:** Transformed through a stochastic sequence of 2 to 5 physical operators.

| Layer | Operator Category | Count | Documented Operators | Probability |
|---|---|:---:|---|:---:|
| **Layer 1** | **Substrates & Paper Types** | 10 | Newsprint pulp, Recycled Kraft, Cream book paper, Ruled notebook paper, Aged acid parchment, Heavy handmade paper, Glazed magazine sheet, Thermal fax paper, Stained ledger paper, Office copy 80gsm | 100% (Base) |
| **Layer 2** | **Printing & Ink Chemistry** | 12 | Capillary ink bleed, Toner micro-voids, Faded typewriter ribbon, Ballpoint pen navy, Carbon black saturation, Dot-matrix pin streaks, Ink feathering, Letterpress halo effect, Thermal drift, Stamp ink bleed, Roller smudge, Under-inking voids | 45%–70% |
| **Layer 3** | **Physical Wear & Handling Defects** | 16 | Paper creases, Bureaucratic circular stamps, Chai/water stains, Moisture droplet blooms, Dog-eared folded corners, Photostat threshold speckles, Staple rust marks, Pin holes, Edge tears, Handling grime, Dust specks, Mildew spots, Crease shadow lines, Surface abrasions, Binding glue stains, Fingerprint smudges | 30%–60% |
| **Layer 4** | **Optical & Sensor Distortions** | 16 | Gaussian defocus blur, Ambient lighting gradient shadow, Sensor chroma noise, Micro-keystone perspective tilt, Barrel optical distortion, Radial vignetting, Flash glare reflection, Motion smear, Under-exposure drop, Over-exposure bloom, JPEG compression blocking, Resolution downsampling, Color temperature shift, Bilinear jitter, Skew angle rotation, Scanner line dropout | 35%–55% |

Each generated sample logs the exact sequence of applied operators in its JSON annotation.

---

## 9. Annotation Format & Schema

Each sample in a WebDataset `.tar` shard contains a paired image (`.webp`) and metadata record (`.json`).

### 9.1 Sample Annotation (Tier 2 Paragraph Block)

```json
{
  "sample_key": "kan_0008644",
  "tier": "Tier_2_Paragraph",
  "lang": "kan",
  "script": "Knda",
  "font_name": "BalooTamma2-Regular.ttf",
  "is_clean": false,
  "canvas_size": [669, 213],
  "text": "ಅದನ್ನು ತಂದು ಶ್ರೀನಿವಾಸನಿಗೆ ಕೊಡುತ್ತಾಳೆ. ಅಂಗಡಿಗೆ ಹಿಂದಿರುಗಿ ಬಂದ ಶ್ರೀನಿವಾಸ ಡಬ್ಬಿಯನ್ನು",
  "tokens": [
    {
      "text": "ಅದನ್ನು",
      "bbox": [24, 16, 110, 68]
    },
    {
      "text": "ತಂದು",
      "bbox": [122, 16, 185, 68]
    },
    {
      "text": "ಶ್ರೀನಿವಾಸನಿಗೆ",
      "bbox": [198, 16, 360, 68]
    }
  ],
  "token_count": 22,
  "applied_augmentations": [
    "Substrate: notebook_ruled",
    "PhysicalDefect: paper_crease",
    "Ink: capillary_bleed",
    "Sensor: optical_defocus"
  ]
}
```

### 9.2 Metadata Field Definitions

| Field Name | Type | Description |
|---|:---:|---|
| `sample_key` | `string` | Globally unique sample identifier formatted as `{lang}_{index:07d}`. |
| `tier` | `string` | Structural granularity tier (`Tier_1_FullPage`, `Tier_2_Paragraph`, `Tier_3_Line`, `Tier_4_Word`). |
| `lang` | `string` | ISO 639-3 three-letter language code. |
| `script` | `string` | ISO 15924 four-letter script code. |
| `font_name` | `string` | OpenType font family utilized for HarfBuzz shaping. |
| `is_clean` | `boolean` | Flag indicating whether the sample belongs to the clean control subset (12.5%). |
| `canvas_size` | `[int, int]` | Canvas dimensions `[width, height]` in pixels. |
| `text` | `string` | Unicode NFC ground truth text transcription. |
| `tokens` | `list[dict]` | Token-level annotations with tight ink bounding boxes `[x0, y0, x1, y1]`. |
| `token_count` | `int` | Total count of annotated tokens in the instance. |
| `applied_augmentations` | `list[string]` | Sequence of physical operators applied from the degradation pipeline. |

Bounding box coordinates use `[x0, y0, x1, y1]` in absolute pixel coordinates where `(x0, y0)` represents the top-left and `(x1, y1)` represents the bottom-right corner.

---

## 10. Data Organization & Shard Topology

Shards are distributed in language-specific directory trees:

```
data/
├── hindi/      # hin_train_{00000..00199}.tar (200 shards, 1.0M samples)
├── urdu/       # urd_train_{00000..00199}.tar (200 shards, 1.0M samples)
├── bengali/    # ben_train_{00000..00199}.tar (200 shards, 1.0M samples)
├── tamil/      # tam_train_{00000..00199}.tar (200 shards, 1.0M samples)
├── marathi/    # mar_train_{00000..00199}.tar (200 shards, 1.0M samples)
├── telugu/     # tel_train_{00000..00099}.tar (100 shards, 500K samples)
├── gujarati/   # guj_train_{00000..00099}.tar (100 shards, 500K samples)
├── kannada/    # kan_train_{00000..00099}.tar (100 shards, 500K samples)
├── malayalam/  # mal_train_{00000..00099}.tar (100 shards, 500K samples)
├── odia/       # ori_train_{00000..00099}.tar (100 shards, 500K samples)
├── punjabi/    # pan_train_{00000..00099}.tar (100 shards, 500K samples)
├── assamese/   # asm_train_{00000..00099}.tar (100 shards, 500K samples)
├── nepali/     # nep_train_{00000..00099}.tar (100 shards, 500K samples)
├── sanskrit/   # san_train_{00000..00099}.tar (100 shards, 500K samples)
├── santali/    # sat_train_{00000..00099}.tar (100 shards, 500K samples)
├── manipuri/   # mni_train_{00000..00099}.tar (100 shards, 500K samples)
├── sindhi/     # snd_train_{00000..00099}.tar (100 shards, 500K samples)
├── bodo/       # brx_train_{00000..00099}.tar (100 shards, 500K samples)
├── bhojpuri/   # bho_train_{00000..00099}.tar (100 shards, 500K samples)
├── kashmiri/   # kas_train_{00000..00099}.tar (100 shards, 500K samples)
├── konkani/    # gom_train_{00000..00049}.tar (50 shards,  250K samples)
├── maithili/   # mai_train_{00000..00049}.tar (50 shards,  250K samples)
└── dogri/      # doi_train_{00000..00049}.tar (50 shards,  250K samples)
```

---

## 11. Distributed Streaming Quickstart (PyTorch / WebDataset)

BhartiOCR shards stream directly over HTTP into PyTorch training loops without local disk extraction:

```python
import webdataset as wds
from torch.utils.data import DataLoader

# Stream Kannada shards directly from Hugging Face Hub
shard_url = "https://huggingface.co/datasets/Faizaniqbal/BhartiOCR/resolve/main/data/kannada/kan_train_{00000..00099}.tar"

dataset = (
    wds.WebDataset(shard_url, resampled=False, shardshuffle=True)
    .shuffle(1000)
    .decode("pil")
    .to_tuple("webp", "json")
)

dataloader = DataLoader(dataset, batch_size=32, num_workers=4)

for images, annotations in dataloader:
    # Forward pass to Vision-Language Model / TrOCR / Donut
    pass
```

---

## 12. Quality Assurance & Validation Statistics

The pipeline enforces an automated verification suite across all generated shards:

| Validation Category | Verification Criterion | Enforcement Mechanism | Measured Failure Rate |
|---|---|---|:---:|
| **Unicode NFC Normalization** | Zero unmapped control codes, joiner preservation | `unicodedata.normalize('NFC', text)` | 0.00% (0 / 13.25M) |
| **Missing Glyph Detection** | Zero `.notdef` tofu glyphs rendered | Pre-render `cmap` table lookup | 0.00% (0 / 13.25M) |
| **CTL Ligature Integrity** | Valid conjunct formation and reordering | HarfBuzz OpenType shaping engine | 0.00% (0 / 13.25M) |
| **Vertical Ink Containment** | Ascenders and descenders strictly within canvas | Font-specific metric padding | 0.00% (0 / 13.25M) |
| **Bounding Box Alignment** | Token bboxes strictly match rendered ink | Ink mask connected-component audit | 0.00% (0 / 13.25M) |
| **Cross-Language Purity** | Zero out-of-domain foreign stopwords | Lexicon exclusion gate per script | 0.00% (0 / 13.25M) |
| **Archive Serialization** | Valid tar format with paired WebP and JSON files | POSIX archive checksum audit | 0.00% (0 / 2,650) |

---

## 13. Data Sources and Provenance

Textual content was sourced from open-access corpora:

| Source | Role | Languages | Primary License | Processing Notes |
|---|---|---|:---:|---|
| **Wikimedia Foundation** | Encyclopedic prose, general vocabulary | Major Indic languages | CC BY-SA 3.0 / 4.0 | Automated markup removal, sentence chunking, stopword filtering |
| **IIT Bombay Parallel Corpus** | Multi-domain sentences, legal and technical text | Hindi | Open Academic | Sentences partitioned into lines and paragraph blocks |
| **Tatoeba Project (Sarvam AI)** | Conversational dialogues, short sentences | Regional languages | CC BY 2.0 FR | Cleaned short-line extraction |
| **GlotCC-V1 (LMU Munich)** | Web crawl text for low-resource languages | Dialects, regional | Open Web / CC0 | Script purity filtering, foreign stopword removal |
| **Public Domain Literature** | Classical verse, poetry dohas | Hindi, Sanskrit, Awadhi | Public Domain | Preserved traditional meter and danda punctuation |

---

## 14. Intended Uses and Out-of-Scope Use

### 14.1 Intended Use Cases
* **OCR Model Pretraining and Fine-Tuning:** Training Vision-Language Models (e.g., Florence-2, Qwen2-VL, Donut, TrOCR) on complex Indic scripts.
* **Document Layout Analysis:** Multi-column reading order and paragraph segmentation research.
* **Synthetic-to-Real Domain Adaptation:** Evaluating model transferability between clean and physically degraded documents.
* **Typographic Robustness Studies:** Benchmarking OCR resilience against ink bleed, font variation, and physical paper damage.

### 14.2 Out-of-Scope Uses
* Evaluating real-world performance solely on synthetic metrics without testing on naturally scanned document collections.
* Automated legal, medical, or administrative decision-making based on OCR predictions without human-in-the-loop review.
* Demographic, identity, or author inference from rendered text contents.

---

## 15. Limitations

* **Synthetic-to-Real Domain Gap:** While the degradation pipeline simulates paper fibers, ink bleeding, and physical defects, synthetic data cannot reproduce all anomalies found in natural historical scans.
* **Text Source Dependence:** Lexical diversity is bounded by the underlying text corpora (Wikipedia, GlotCC, Tatoeba, CFILT).
* **Font Coverage:** Visual diversity is determined by the open-source font pool available per script.
* **Language Volume Differences:** Sample counts vary between major regional languages (1,000,000 samples) and lower-resource languages (250,000 samples).
* **Synthetic Evaluation Interpretation:** Benchmark scores achieved on synthetic test splits should not be interpreted as direct proxies for performance on fragile historical manuscripts.

---

## 16. Licensing and Access

### 16.1 Dataset License
BhartiOCR is released under the **Apache License 2.0**. Use of the dataset is subject to the licensing terms and redistribution requirements of the upstream textual resources used during corpus generation.

### 16.2 Access Policy
The dataset is hosted on the Hugging Face Hub under **gated access**. Users must agree to standard terms and share contact information prior to accessing the files.

---

## 17. Versioning

| Version | Release Date | Samples | Languages | Description |
|---|:---:|:---:|:---:|---|
| **v1.0** | Current | 13,250,000 | 23 | Initial release covering 22 Eighth Schedule languages + Bhojpuri |
| **v1.1** | Planned | 15,250,000 | 27 | Planned expansion to Tier-2 regional languages (see Roadmap) |

---

## 18. Roadmap

The following features are under active development and are not part of the v1.0 release:

* **Regional Language Expansion (v1.1):** Adding 4 Tier-2 Devanagari regional languages—**Awadhi (`awa`)**, **Magahi (`mag`)**, **Chhattisgarhi (`hne`)**, and **Marwari / Rajasthani (`mwr`)** (+2,000,000 samples, target: 27 languages). Cloud smoke test verified.
* **Archival Era Physics Simulation:** Specialized historical degradation profiles simulating 1850s lithographs, 1895 colonial gazettes, 1910s pre-independence literary anthologies, and 1947 newsprint broadsheets.
* **Model Baseline Leaderboard:** Standardized evaluation benchmark assessing OCR performance (CER, WER, Bounding Box IoU) across Florence-2, Qwen2-VL, TrOCR, Nougat, and Donut.
* **Interactive Dataset Inspector:** Hugging Face Space for live WebDataset shard browsing, token bounding box overlay inspection, and ground truth text validation.

---

## 19. Citation

If you utilize BhartiOCR in your research or applications, please cite:

```bibtex
@dataset{bhartiocr_2026,
  author    = {Faizan Iqbal},
  title     = {BhartiOCR: A Multilingual Synthetic OCR and Document Benchmark for Indian Languages},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/Faizaniqbal/BhartiOCR}
}
```

---

## 20. Contact and Feedback

* **Author:** Faizan Iqbal
* **Repository:** [https://huggingface.co/datasets/Faizaniqbal/BhartiOCR](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR)
* For questions, corrections, or reproducibility inquiries, please open a discussion on the [Hugging Face Repository Discussion Board](https://huggingface.co/datasets/Faizaniqbal/BhartiOCR/discussions).
