# INDICPIXEL: ZERO-DEFECT PAN-INDIC OCR PRODUCTION MANUAL & POST-MORTEM
**Lead Systems Architecture, Strict Invariants, Degradation Registry, and Post-Mortem Encyclopedia**

---

## 1. PROJECT PHILOSOPHY & MANDATE

IndicPixel is the premier, zero-defect multilingual synthetic OCR and Document AI benchmark across Pan-Indic scripts.
* **Absolute Zero Tolerance**: Zero tofu boxes (`.notdef` / Glyph ID 0), zero diacritic clipping, zero canvas overflow, zero painted debug boxes on image rasters, and zero memory/disk leaks.
* **Volume Tiers**:
  * Flagship High-Resource Languages: **1,000,000 samples** (200 WebDataset shards)
  * Standard & Regional Languages: **500,000 samples** (100 WebDataset shards)
  * Targeted Rare Dialects: **250,000 samples** (50 WebDataset shards)
* **Compute Separation**:
  * Synthesis is **100% CPU-based** (HarfBuzz OpenType shaping + FreeType rendering + OpenCV paper physics).
  * GPU quota on Kaggle/Cloud is preserved (0.0 GPU hours consumed). All cloud synthesis runs in CPU mode with unlimited hours.

---

## 2. THE 4-TIER DOCUMENT GRANULARITY MATRIX

Every 5,000-sample WebDataset `.tar` shard MUST strictly preserve the following 4-tier distribution:

| Granularity Tier | Share per Shard | Sample Count | Target Document AI / OCR Objective |
| :--- | :---: | :---: | :--- |
| **Tier 4: Words & Isolated Tokens** | **30%** | **1,500** | Word-level recognition, lexicons, rare conjunct dictionaries |
| **Tier 3: Reading Sequence Lines** | **55%** | **2,750** | TrOCR, line-level attention, CTC decoding, text recognition |
| **Tier 2: Paragraph Text Blocks** | **13%** | **650** | Multi-line reading order, line-break handling, layout modeling |
| **Tier 1: Full-Page Document Spreads** | **2%** | **100** | Full-page Document AI (LayoutLMv3, Donut, Nougat, Broadsheets) |

### Archetype Document Spreads (Tier 1 Architecture):
* **Archetype A: Sahitya / Literary Journal Spread**: Elegant two-column spread with ornamental header, centered section title, and multi-line body paragraphs.
* **Archetype B: Official Government Gazette / Rajapatra**: Dense formal administrative document, bilingual header, Ashok Chakra / state crest placeholder, circular bureaucratic stamps, two-column notification blocks.
* **Archetype C: Broadsheet Daily Newspaper Spread**: Multi-column newsprint layout with vertical column rules, bold headlines, datelines, and article columns.

---

## 3. THE MASTER 54-OPERATOR DEGRADATION TAXONOMY

Every degraded sample receives a stochastic DAG chain of **3 to 6 physical operators**.
* **Clean Baseline Anchor**: Exactly 12.5% (1 in 8 samples) are saved with clean white scan physics (`#01 Clean White Scan Baseline`).
* **Degraded Renders**: Exactly 87.5% receive active degradation.

```
Category A: 12 Procedural Document Substrates (Paper Physics)
  #01 Clean White Scan Baseline      #07 Weathered / Damp Paper
  #02 Aged Indian Acid Paper (1890)   #08 Coffee Stained & Chai Ring Blotches
  #03 Book Page (Cream Pulp)          #09 Old Library Book (Edge Burn & Tanning)
  #04 Yellow Newsprint (Raddi Paper)  #10 Recycled Kraft Paper with Fibers
  #05 Ruled Student Notebook Lines    #11 Fine Cream Stationery
  #06 Ancient Vellum / Parchment      #12 Antique Ivory Parchment

Category B: 14 Physical Print & Bureaucratic Degradations (Indian Realism)
  #13 Capillary Ink Bleed             #20 Dot Matrix Ribbon Degradation
  #14 Toner Erosion & Micro-Voids     #21 Offset Press Ink Smudge
  #15 Non-Uniform Shadow Gradient     #22 Aged Patina Oxidation
  #16 Xerox Photostat High-Clip       #23 Low-Resolution Mobile Sensor Quantization
  #17 Optical Defocus Blur            #24 Scanner Bed Border Shadow
  #18 Handheld Motion Blur            #25 Physical Diagonal Paper Crease
  #19 Carbon Copy Bleedthrough        #26 Official Indian Bureaucratic Stamps (Purple/Red/Blue)

Category C: 11 Ancient Scripture & Historical Manuscript Cycles
  #27 Sepia Iron-Gall Wash           #33 Iron-Gall Ink Acid Corrosion
  #28 Moisture Water Blotches         #34 Temple Lamp Oil / Soot Shadow
  #29 Palm-Leaf Manuscript Ribs       #35 Vermilion / Sindoor Ritual Powder Smudges
  #30 Manuscript Wormholes / Perfs    #36 Fungal Mildew Colonies
  #31 Lacquer Craquelure Fissures     #37 Frayed & Chipped Document Margins
  #32 Water Immersion Tidemarks

Category D: 11 Geometric, Optical & Sensor Transformations
  #38 Micro-Planar Rotation (±1.2°)   #44 High-Contrast Photostat Clipping
  #39 Horizontal Shear (±1.5°)        #45 Low-Contrast Ribbon Washout
  #40 Keystone Handheld Tilt          #46 High-ISO Sensor Chroma Noise
  #41 Perspective Warp (Micro)        #47 Photostat Glass Dust & Dirt Specks
  #42 Overexposure Light Flare        #48 Faded Print Ribbon Exhaustion
  #43 Underexposure Deep Shadow

Category E: 6 Kinematic Handwriting & Human Deformations
  #49 Elastic Paper Mesh Deformation  #52 Sinusoidal Baseline Drift
  #50 Kinematic Slant (±2.5°)         #53 Natural Pen Lift Discontinuity
  #51 Variable Stroke Pressure        #54 Multi-Persona Complex Kinematics
```

---

## 4. POST-MORTEM: EVERY MISTAKE MADE & PERMANENT SOLUTIONS

### MISTAKE 1: Diacritic Truncation & CNN H=1 Breakdown
* **Symptom**: Top matras (e.g. Hindi *ikkar/ikaron*, Gurmukhi *tippi/bindi*) or bottom *halant/ottulu* cut off by canvas edge. In CNN feature extractors where pooling height reaches $H=1$, clipped features collapse into noise.
* **Root Cause**: Fixed padding or baseline PIL rendering without checking font ascent/descent metrics.
* **Permanent Fix**: Dynamic vertical zone calculation from font metrics:
  ```python
  asc_px = int(math.ceil(metrics["ascender"] * font_size))
  desc_px = int(math.ceil(metrics["descender"] * font_size))
  pad_top = max(int(font_size * 0.45), 18)
  pad_bottom = max(int(font_size * 0.40), 16)
  ch = asc_px + desc_px + pad_top + pad_bottom
  ```

### MISTAKE 2: Tofu Boxes / Glyph ID 0 Rendered
* **Symptom**: Black rectangle / hollow box `.notdef` rendered when a font lacks a specific glyph.
* **Root Cause**: Fallback to default PIL rasterization or blindly passing unvalidated Unicode strings.
* **Permanent Fix**: Strict HarfBuzz OpenType CTL shaping + cmap gate:
  ```python
  infos, positions = hb.shape(font, buf)
  assert all(info.codepoint != 0 for info in infos), "Glyph ID 0 detected!"
  ```

### MISTAKE 3: Stripping ZWJ (`\u200D`) and ZWNJ (`\u200C`)
* **Symptom**: Explicit conjuncts or half-forms collapse into full consonants with visible viramas.
* **Root Cause**: `cmap` filtering: `ord(c) in cmap or c == ' '`. OpenType fonts often handle ZWJ/ZWNJ in GSUB feature tables, NOT as visible glyphs in `cmap`.
* **Permanent Fix**: Explicit joiner preservation whitelist:
  ```python
  text = "".join(c for c in text if ord(c) in cmap or c in (' ', '\u200C', '\u200D'))
  ```

### MISTAKE 4: Cross-Script Heading Contamination
* **Symptom**: An Odia character (`\u0B24`) accidentally embedded in an Assamese archetype title string, causing shaping failures.
* **Root Cause**: Copy-pasting boilerplate archetype strings between language generators without validating Unicode codepoints against the target script block.
* **Permanent Fix**: Script isolation validation pass on all archetype strings before pipeline start:
  ```python
  assert all(ord(c) in script_range or ord(c) < 128 for c in archetype_title)
  ```

### MISTAKE 5: Right-Margin Canvas Overflow in Full-Page Layouts
* **Symptom**: In multi-column spreads, 218 tokens in Kannada had `bbox[2] > 1000px` (e.g. 1048px). The image was clipped by PIL, but bounding boxes pointed outside the canvas.
* **Root Cause**: Slicing sentences by character count (`s[:45]`) instead of measuring physical pixel advance widths. In wide scripts like Kannada, 45 characters exceeded column width ($440\text{px}$).
* **Permanent Fix**: Pixel-constrained word wrapping with dynamic advance tracking:
  ```python
  max_col_w = col_w - 20 # 420px max inside a 440px column
  # Wrap words greedily until cumulative line advance <= max_col_w
  # Enforce hard post-render assertion:
  assert all(tok["bbox"][2] <= page_w and tok["bbox"][3] <= page_h for tok in all_tokens)
  ```

### MISTAKE 6: Bounding Box Drift Under Uncompensated Geometric Warps
* **Symptom**: Applying $8^\circ$ rotation or $14^\circ$ slant shifted text pixels by 30–50px, but bounding boxes in JSON remained at unrotated coordinates. Also caused text corners to clip the frame.
* **Root Cause**: Geometric ops in OpenCV transformed the image array without affine-transforming the bounding box polygons.
* **Permanent Fix**:
  1. Constrain uncompensated rotations to micro-skew ($\pm 1.0^\circ$ to $\pm 1.5^\circ$), where IoU $> 96\%$.
  2. Apply dynamic border padding (`cv2.copyMakeBorder`) before rotation to eliminate edge clipping.

### MISTAKE 7: Silent `try/except: pass` Blocks
* **Symptom**: Broken samples or skipped shards silently disappear without logging root causes.
* **Permanent Fix**: Fail fast. Log exact codepoint, font, and tier on exception, isolate the failing module, and fix the root cause immediately.

### MISTAKE 8: Local & Cloud Disk Exhaustion
* **Symptom**: Disk filling up with 20–50 GB of unevicted `.tar` shards, causing OS out-of-space crash.
* **Permanent Fix**: Stream-and-evict protocol:
  ```python
  # Immediately upon verified upload (HTTP 200), unlink local shard:
  shard_path.unlink(missing_ok=True)
  assert local_storage_consumption_gb <= 1.0
  ```

### MISTAKE 9: Exposing Internal Development State on Public Hub
* **Symptom**: Labeling languages as "100% complete" vs "scaling to 500k" or mentioning "Kaggle cloud staging" on Hugging Face dataset cards.
* **Permanent Fix**: Every published language is presented uniformly as `Available` with its verified sample volume. Zero mentions of Kaggle, internal roadmaps, or draft staging in public documentation.

### MISTAKE 10: Redundant Language Staging & Ledger Amnesia
* **Symptom**: Attempting to stage, push, or audit languages that have ALREADY been fully synthesized and committed to Hugging Face (e.g. treating Bhojpuri, Kashmiri, Dogri, Konkani, Maithili as "unstarted").
* **Root Cause**: Relying on temporary conversational context rather than querying live remote repository state (`Faizaniqbal/IndicOCR`) and local ledger files (`MASTER_PAN_INDIC_LEDGER.md`).
* **Permanent Fix**: 
  1. Mandatory live query against Hugging Face repository before preparing or staging any worker.
  2. Hardcoded `COMPLETED_LANGS` redundancy guard in `deploy_kaggle_production_fleet.py` and `kaggle_queue_dispatcher.py` that immediately aborts any operation on completed languages.
  3. Every newly completed language must have its individual markdown ledger (`<LANG>_PRODUCTION_LEDGER.md`) synchronized immediately upon completion.

---

## 5. PRE-COMMIT QUALITY ASSERTION CHECKLIST

Before any shard or batch is marked as valid, it MUST pass these 5 assertions:
1. `assert all(glyph_id != 0 for glyph_id in shaped_glyphs)` (Zero `.notdef` tofu boxes).
2. `assert all(0 <= tok['bbox'][0] < tok['bbox'][2] <= canvas_w for tok in tokens)` (Zero horizontal overflow).
3. `assert all(0 <= tok['bbox'][1] < tok['bbox'][3] <= canvas_h for tok in tokens)` (Zero vertical overflow).
4. `assert applied_augmentations_count >= 2 or is_clean` (Zero un-augmented sterile renders).
5. `assert local_buffer_size_gb <= 1.0` (Zero disk accumulation).

---

## 6. KAGGLE CLOUD FLEET ARCHITECTURE

### Hardware Constraints & Advantages:
* **Mode**: CPU mode (`"enable_gpu": false`).
* **Quota Consumed**: **0.0 GPU hours** (30-hour weekly GPU quota remains 100% intact).
* **Hardware Specs per Kernel**: **4 vCPUs**, **30 GB RAM**, **20 GB SSD disk**.
* **Kaggle Concurrency**: Up to **30 concurrent batch kernels** simultaneously.

### Optimum Production Fleet (5 to 6 Simultaneous Kernels):
* **Kernel 1**: Kannada (`kan_Knda`) — 500,000 samples (4 vCPUs)
* **Kernel 2**: Punjabi (`pan_Guru`) — 500,000 samples (4 vCPUs)
* **Kernel 3**: Nepali (`nep_Deva`) — 500,000 samples (4 vCPUs)
* **Kernel 4**: Sindhi (`snd_Arab`) — 500,000 samples (4 vCPUs)
* **Kernel 5**: Bodo (`brx_Deva`) — 500,000 samples (4 vCPUs)
* **Kernel 6**: Santali (`sat_Olck`) or High-Volume Dravidian Extension (4 vCPUs)

### Throughput & Scaling:
* Single Kernel: ~110 samples/sec $\rightarrow$ 500,000 samples in **~1 hour 15 minutes**.
* Fleet (6 Kernels in Parallel): **~660 samples/sec combined** $\rightarrow$ **3,000,000 samples completed in ~75 minutes**.

---

## 7. THE NON-NEGOTIABLE LAWS: THE ITERATIVE 5,000-SAMPLE SMOKE TEST & VISUAL AUDIT GATEWAY

### LAW 1: NEVER TRUST CODE ALONE — VISUAL PROOF IS SUPREME
* Automated tests passing is necessary but NEVER sufficient.
* We must inspect the actual rendered rasters, character ligatures, paper textures, and composite before/after plates with human eyes.
* On the basis of visible output quality, we decide whether a dataset is worthy of training state-of-the-art Document AI models or not.

### LAW 2: THE 5,000-SAMPLE SMOKE TEST PROTOCOL
Before any language is authorized for full-scale 500,000-sample production, it MUST undergo an isolated **5,000-sample smoke test (exactly 1 complete shard)**:
1. **Tier Ratios**: Exactly 1,500 words (30%), 2,750 lines (55%), 650 paragraphs (13%), and 100 full-page spreads (2%).
2. **Font Coverage**: Evenly distributed across all verified OpenType fonts.
3. **Degradation Range**: All 54 operators sampled across the stochastic chain (12.5% clean baseline, 87.5% degraded).
4. **Text Purity**:
   - Zero English or foreign script contamination.
   - Zero Wikipedia template/citation residue (`[1]`, `{{...}}`, `<tag>`, URLs).
   - Natural phrase lengths and complete sentence boundaries.

### LAW 3: THE MANDATORY 5-STEP FORENSIC AUDIT & FIX LOOP
For every smoke test batch:
1. **Deploy Smoke Test**: Run the 5,000-sample test on Kaggle in isolated CPU mode.
2. **Download Locally**: Retrieve the `.tar` shard, individual sample PNGs, and composite before/after inspection plates.
3. **Forensic Autopsy**: Programmatically verify:
   - Glyph ID 0 rate == 0.00%.
   - Token canvas overflow == 0 (all $x_2 \le W$ and $y_2 \le H$).
   - Diacritic clipping == 0.
   - Ink legibility under degradation.
4. **Generate Comprehensive Defect Report**: Document every single flaw, edge-case failure, and area of improvement.
5. **Apply Fix & Re-Verify**: Patch the generator/augmentation code. Run another smoke test if needed until 100% defect-free.
6. **Final Gate**: Only after 100% defect-free certification does the language qualify for the full-scale 500,000-sample production fleet.

---

## 8. AUTHORITATIVE 23-LANGUAGE PRODUCTION FLEET STATUS (LIVE ON HUGGING FACE)

Repository: [`Faizaniqbal/IndicOCR`](https://huggingface.co/datasets/Faizaniqbal/IndicOCR)  
**Total Live Remote Samples:** `12,285,000` samples across `2,457` WebDataset `.tar` shards across **23 languages**.

| # | Language | Code | Script Tag | Verified Fonts | Live Shards | Live Samples | Target Quota | Status |
| :-: | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | **Hindi** | `hin` | `Deva` | NotoSans, NotoSerif, RozhaOne, YatraOne, TiroDevanagari | 200 | 1,000,000 | 200 | 🏆 **100% COMPLETE** |
| 2 | **Urdu** | `urd` | `Arab` | NotoNastaliqUrdu, Gulzar, Lateef, NotoSansArabic | 200 | 1,000,000 | 200 | 🏆 **100% COMPLETE** |
| 3 | **Bengali** | `ben` | `Beng` | NotoSansBengali, NotoSerifBengali, TiroBangla, Galada | 200 | 1,000,000 | 200 | 🏆 **100% COMPLETE** |
| 4 | **Tamil** | `tam` | `Taml` | NotoSansTamil, NotoSerifTamil, MuktaMalar, Catamaran | 200 | 1,000,000 | 200 | 🏆 **100% COMPLETE** |
| 5 | **Marathi** | `mar` | `Deva` | NotoSans, NotoSerif, RozhaOne, YatraOne, TiroDevanagari | 200 | 1,000,000 | 200 | 🏆 **100% COMPLETE** |
| 6 | **Telugu** | `tel` | `Telu` | NotoSansTelugu, NotoSerifTelugu, Ramabhadra, Mandali | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 7 | **Gujarati** | `guj` | `Gujr` | NotoSansGujarati, NotoSerifGujarati, Rasa, Mogra | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 8 | **Kannada** | `kan` | `Knda` | NotoSansKannada, NotoSerifKannada, BalooTamma2, AnekKannada | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 9 | **Malayalam** | `mal` | `Mlym` | NotoSansMalayalam, NotoSerifMalayalam, Gayathri, Chilanka | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 10 | **Odia** | `ori` | `Orya` | NotoSansOriya, NotoSerifOriya | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 11 | **Assamese** | `asm` | `Beng` | NotoSansBengali, NotoSerifBengali, TiroBangla | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 12 | **Nepali** | `nep` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 13 | **Sanskrit** | `san` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne, RozhaOne | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 14 | **Santali** | `sat` | `Olck` | NotoSansOlChiki | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 15 | **Bhojpuri** | `bho` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne, RozhaOne | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 16 | **Kashmiri** | `kas` | `Arab` | NotoSansArabic, NotoNaskhArabic, Lateef | 100 | 500,000 | 100 | 🏆 **100% COMPLETE** |
| 17 | **Dogri** | `doi` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne, RozhaOne | 50 | 250,000 | 50 | 🏆 **100% COMPLETE** |
| 18 | **Konkani** | `gom` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne, RozhaOne | 50 | 250,000 | 50 | 🏆 **100% COMPLETE** |
| 19 | **Maithili** | `mai` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne, RozhaOne | 50 | 250,000 | 50 | 🏆 **100% COMPLETE** |
| 20 | **Manipuri** | `mni` | `Mtei` | NotoSansMeeteiMayek | 97 | 485,000 | 100 | 🔄 **IN PROGRESS (97/100)** |
| 21 | **Sindhi** | `snd` | `Arab` | NotoSansArabic, NotoNaskhArabic, Lateef | 50 | 250,000 | 100 | 🔄 **IN PROGRESS (50/100)** |
| 22 | **Punjabi** | `pan` | `Guru` | NotoSansGurmukhi, NotoSerifGurmukhi, AnekGurmukhi | 45 | 225,000 | 100 | 🔄 **IN PROGRESS (45/100)** |
| 23 | **Bodo** | `brx` | `Deva` | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | 35 | 175,000 | 100 | 🔄 **IN PROGRESS (35/100)** |

---

## 9. GENUINE NEXT-WAVE EXPANSION FLEET (ZERO-SHARD TARGETS)

These languages have **0 shards** currently committed on Hugging Face and represent the genuine next-wave expansion targets:

| Priority | Code | Language | Script | Verified Fonts Pool | Target Corpus Source | Est. Native Speakers | Status |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **P1** | **`awa`** | **Awadhi** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Wikipedia `20231101.awa` (Ramcharitmanas, literature) | ~38 Million | **Staged (0 Shards)** |
| **P2** | **`new`** | **Newari (Nepal Bhasa)** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Wikipedia `20231101.new` (72k+ articles) | ~1.2 Million | **Staged (0 Shards)** |
| **P3** | **`tcy`** | **Tulu** | Kannada Script (`Knda`) | NotoSansKannada, NotoSerifKannada, BalooTamma2, AnekKannada | Wikipedia `20231101.tcy` | ~2 Million | **Staged (0 Shards)** |
| **P4** | **`anp`** | **Angika** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Wikipedia `20231101.anp` | ~15 Million | **Staged (0 Shards)** |
| **P5** | **`mag`** | **Magahi** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Wikipedia `20231101.mag` | ~13 Million | Candidate |
| **P6** | **`hne`** | **Chhattisgarhi** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Wikipedia `20231101.hne` | ~18 Million | Candidate |
| **P7** | **`mwr`** | **Marwari / Rajasthani** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Wikipedia `20231101.mwr` | ~25 Million | Candidate |
| **P8** | **`bgc`** | **Haryanvi** | Devanagari (`Deva`) | NotoSansDevanagari, NotoSerifDevanagari, YatraOne | Saillab / OSCAR Hindi-dialects | ~10 Million | Candidate |

---

## 10. MANDATORY PRE-PRODUCTION GATEWAY (NO DIRECT HF PUSHES)

Under NO circumstances is any new language worker permitted to push shards directly to Hugging Face without passing through the 3-step verification gateway:

```
[Phase 1: Local Forensic Audit Pass]
   ├── 1. Font cmap script codepoint assertion (>= 20 codepoints in target range).
   ├── 2. Native script alphabet gate (>= 2 letters + matras per line; no punctuation-only).
   ├── 3. HarfBuzz CTL Shaping verification (Zero Glyph ID 0 / .notdef tofu).
   ├── 4. Dynamic vertical zone bounding box assertion (Zero diacritic clipping).
   └── 5. 4-Tier test render (Word, Line, Paragraph, Full Page) through 54-op degradation DAG.
          │
          ▼
[Phase 2: Isolated Kaggle Smoke Test (1 Shard / 5,000 Samples)]
   ├── Run strictly in CPU mode (0.0 GPU hours consumed).
   ├── Output held locally in /kaggle/working/ (ZERO remote commits to HF).
   └── Generate composite before/after proof plates for visual human inspection.
          │
          ▼
[Phase 3: Visual Inspection & Human Approval]
   ├── Human review of composite plates across all 4 tiers.
   ├── Verification of ligature formation, ink bleed, and paper textures.
   └── ONLY upon human approval: Deploy to Kaggle Production Fleet with live HF streaming.
```

