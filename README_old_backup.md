---
license: apache-2.0
task_categories:
- image-to-text
- visual-question-answering
language:
- bho
- ur
tags:
- ocr
- synthetic-dataset
- indic-ocr
- devanagari
- perso-arabic
- nastaliq
- naskh
- bhojpuri
- urdu
- webdataset
- tr-ocr
- layoutlm
- donut
- document-ai
size_categories:
- 1M<n<10M
configs:
- config_name: bhojpuri
  data_files: "data/bhojpuri/*.tar"
- config_name: urdu
  data_files: "data/urdu/*.tar"
---

# IndicPixel: Pan-Indic High-Fidelity Synthetic OCR Dataset

**IndicPixel** is an open-access, zero-defect, high-fidelity synthetic multilingual OCR dataset engine designed to overcome the critical low-resource data barrier across 22 Scheduled Indian languages. 

Rather than relying on sterile synthetic renders or noisy web-scraped document crops, IndicPixel generates photorealistic, mathematically verified document pairs across 4 hierarchical granularity tiers with strict font-shaping validation and a comprehensive 54-operator degradation taxonomy.

---

## 🌐 Dataset Overview & Language Coverage

| Language | Script | ISO Code | Target Quota | Current Status | Repository Path | Storage Size |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **Bhojpuri** | Devanagari (`Deva`) | `bho` | **500,000 samples** | ✅ **100% Complete** (100/100 Shards) | `data/bhojpuri/` | ~10.5 GB |
| **Urdu** | Perso-Arabic (`Arab` / Nastaliq & Naskh) | `ur` / `urd` | **1,000,000 samples** | ✅ **100% Complete** (200/200 Shards) | `data/urdu/` | ~15.25 GB |
| **Hindi** | Devanagari (`Deva`) | `hi` / `hin` | **1,000,000 samples** | 🚀 **Next in Pipeline** (Tier A) | `data/hindi/` | ~15.0 GB (est.) |
| **Pan-Indic Published** | Multi-Script | — | **1,500,000 samples** | ✅ **1,500,000 Samples Live** | `data/` | **~25.75 GB** |

All samples are serialized into standard POSIX WebDataset `.tar` shards (~5,000 samples / shard) containing paired lossless compressed images (`.png` / `.webp`) and token-level ground truth metadata (`.json`).

---

## 📊 Hierarchical Granularity Matrix

IndicPixel structures document generation across 4 distinct visual granularity tiers to simultaneously support token recognizers, line readers, and multimodal document understanding models:

| Tier | Granularity | Canvas Size | Document Layout & Archetypes | Target Models |
| :--- | :--- | :---: | :--- | :--- |
| **Tier 1** | **Full Pages** | $1200 \times 1600$ px | **Archetype A:** Literary Diwan & Couplets<br>**Archetype B:** Official Gazette & Circulars<br>**Archetype C:** Multi-Column Newsprint<br>**Archetype D:** Dense Academic Prose | LayoutLMv3, Donut, Surya OCR, Nougat |
| **Tier 2** | **Paragraphs** | $800 \times 400$ px | Justified multi-line prose, dialogue excerpts, section blocks | Block OCR, Layout Analysis |
| **Tier 3** | **Sequence Lines** | $800 \times 60$ px | Single horizontal lines of typeset text and kinematic handwriting | TrOCR, CRNN, Sequence Recognizers |
| **Tier 4** | **Words & Tokens** | $150 \times 50$ px | Isolated lexical tokens, rare conjuncts, complex ligatures | CTC Decoders, Lexicon Miners |

### Quality & Balance Ratios
* **Clean Scan vs. Degradation Ratio:**
  * **Urdu (`urd`):** **55% Pristine Digital Scans** on clean/warm paper; **45% Stochastic In-The-Wild Degradations**.
  * **Bhojpuri (`bho`):** **30% Pristine Digital Scans**; **70% Physical Degradation Chains**.
* **Typography vs. Handwriting:**
  * **Typeset Print:** Rendered across authentic OpenType fonts (26 Perso-Arabic Nastaliq/Naskh fonts; 16 Devanagari fonts).
  * **Handwriting Kinematics:** Synthesized across distinct biological personas simulating pen pressure, muscle tremors, and baseline drift.

---

## 🔬 Zero-Defect Pipeline Invariants

Every shard in this repository is strictly pre-screened through internal gatekeeper agents prior to publication:

1. **Zero Glyph ID 0 (`.notdef` / Tofu Boxes):**  
   Every text-font pair is validated against the font's OpenType `cmap` table via `fontTools` and shaped strictly through `uharfbuzz`. Default PIL font rasterization fallbacks and unmapped `.notdef` glyphs are prohibited.
2. **Zero Diacritic Clipping:**  
   Dynamic vertical zone padding (`ascender_zone`, `body_zone`, `descender_zone`) is calculated per font metrics. Upper diacritics (*matras, pesh, zabar, zer, tashdeed*) and lower descenders (*nuqtas, zair, conjuncts*) have 100% ink clearance.
3. **Diacritic Ownership Gate:**  
   100% of a token's raster ink is guaranteed to reside inside its polygon/box coordinates, preventing bounding box clipping during model training.
4. **100% Script Purity (Urdu):**  
   Strict Unicode NFC normalization. Zero Latin alphabet noise, zero Arabic/Western digits in prose batches, and full preservation of all 40 authentic Urdu Unicode characters (including `\u200C` ZWNJ and `\u200D` ZWJ).

---

## 🧪 54-Operator Degradation Taxonomy

IndicPixel applies a stochastic chain of 2 to 6 degradation operators per non-clean sample:

* **Category A: Procedural Substrates (12):** Clean White, Aged Paper, Book Page, Newsprint, Ruled Notebook, Parchment, Weathered Manila, Coffee-Stained, Old Book, Recycled Pulp, Cream, Ivory.
* **Category B: Physical Degradations (14):** Ink Bleed, Toner Erosion, Non-Uniform Shadow Gradient, Photostat Xerox Clipping, Optical Blur, Handheld Motion Blur, Mobile JPEG Compression, 3D Ridge Crease, 3D Diagonal Fold, Aged Patina & Stain, Carbon Copy Artifacts, Scanner Border Smudges, Subtle Skew Jitter, Official Stamp Imprints.
* **Category C: Ancient Scripture Decay (11):** Sepia Wash, Moisture Blotches, Palm Leaf Ribs, Insect Wormholes, Craquelure, Water Tidemarks, Iron Gall Ink Corrosion, Temple Lamp Soot, Vermilion/Sindoor Stains, Fungal Mildew, Frayed Margins.
* **Category D: Sensor & Geometry (11):** Planar Rotation, Horizontal Shear, Keystone Tilt, Perspective Homography, Overexposure Washout, Underexposure Darkness, High Contrast Binarization, Low Contrast Washout, Gaussian Sensor Noise, Salt & Pepper Dust, Faded Print.
* **Category E: Handwriting Kinematics (6):** Elastic TPS Mesh, Slant & Shear Variation, Stroke Pressure Dynamics, Baseline Waviness Drift, Pen Lift Discontinuity, Multi-Persona Profiling.

---

## 📚 Linguistic Domain Architecture & Text Typology

To ensure OCR and Document AI models trained on IndicPixel generalize robustly across historical archives, legal filings, modern periodicals, and literature, textual prompts are curated across distinct multi-genre domain taxonomies tailored to each language's cultural and administrative landscape:

### 1. Urdu (`urd` / Perso-Arabic Script)
* **Classical & Modern Poetry (Diwan Layouts):** Ghazals, Nazms, Rubaiyat, and couplets (Ash'ar) formatted in balanced dual-hemistich alignments (*Misra-e-Oola* and *Misra-e-Sani*). This domain tests intricate Nastaliq calligraphic stacking, non-linear vertical ligature cascades, and complex Perso-Arabic poetic diacritics (*Aerab*).
* **Legal, Court & Statutory Records:** Administrative court judgments, statutory penal codes, sworn affidavits, and official government gazette circulars. Features dense bureaucratic terminology, formal punctuation, and structured institutional letterheads.
* **Literary Narrative & Folk Fiction:** Long-form prose excerpts, historical folklore, dialogue-heavy story arcs, and cultural allegories capturing idiomatic conversational grammar and diverse Perso-Arabic vocabulary.
* **Academic Treatises & Non-Fiction (ALIF):** Dense scholarly essays spanning history, philosophy, natural sciences, technology, and literary criticism, formatted in margin-to-margin academic paragraph prose.
* **Contemporary Journalism & Newsprint:** Breaking news reporting, international affairs, business headlines, and editorial opinion pieces representing modern typeset newsprint layouts with multi-tier headline hierarchies.

### 2. Bhojpuri (`bho` / Devanagari Script)
* **Folk Literature & Cultural Heritage:** Traditional Bhojpuri folklore, oral storytelling, Lokgeet (folk ballads), and rural cultural narratives preserving unique regional vocabulary and grammatical structures.
* **Parallel Conversational & Civic Text:** Real-world conversational dialogs, civic announcements, rural education material, and bilingual Hindi–Bhojpuri administrative registers.
* **Spoken Dialectal Transcripts:** Phonetically transcribed conversational recordings capturing colloquial rural speech patterns, idiomatic regional phrasing, and informal Devanagari syntactical nuances.

---

### 🔗 Upstream Attribution & Source Provenance
All textual training data is sourced ethically from public research corpora, open-access linguistic repositories, and cultural archives across 22 Scheduled Indian languages. To maintain repository clarity and full licensing compliance, all upstream source datasets, external repository links, and attribution notices are consolidated into:  
👉 **[`SOURCES.md`](./SOURCES.md)**

---

## 🚀 Usage with Python & WebDataset

You can stream the dataset directly into PyTorch without downloading tens of gigabytes to disk:

```python
import webdataset as wds
from PIL import Image
import io

# 1. Stream Urdu Shards (All 200 Shards: 00000 to 00199)
urdu_url = "https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR/resolve/main/data/urdu/urd_train_{00000..00199}.tar"

dataset_urdu = (
    wds.WebDataset(urdu_url)
    .decode("pil")
    .to_tuple("png", "json")
)

for img, meta in dataset_urdu:
    print(f"Sample ID: {meta['sample_id']}")
    print(f"Text     : {meta['text']}")
    print(f"Tier     : {meta['tier']}")
    print(f"Boxes    : {len(meta.get('bboxes', []))} tokens")
    break

# 2. Stream Bhojpuri Shards (Shards 00000 to 00099)
bhojpuri_url = "https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR/resolve/main/data/bhojpuri/bho_train_{00000..00099}.tar"

dataset_bho = (
    wds.WebDataset(bhojpuri_url)
    .decode("pil")
    .to_tuple("webp", "json")
)
```

---

## 📄 License & Citation

This dataset is distributed under the **Apache 2.0 License**.

```bibtex
@dataset{indicpixel_2026,
  author    = {Faizan Iqbal},
  title     = {IndicPixel: Pan-Indic High-Fidelity Synthetic OCR Dataset},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR}
}
```
