# IndicPixel Production Ledger: Bhojpuri (`bho`) OCR Dataset

---

## 1. Dataset & Production Specifications

* **Target Language:** Bhojpuri (`bho`)
* **Target Script:** Devanagari (`Deva`), Direction: `ltr`
* **Target Corpus Volume:** **500,000 verified samples** (100 WebDataset shards @ 5,000 samples/shard)
* **Target Remote Repository:** [`Faizaniqbal/IndicPixel-Pan-Indic-OCR`](https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR)
* **Remote Path in Repo:** `data/bhojpuri/`
* **Local Disk Storage Invariant:** Strictly capped at **$\le$ 2.0 GB** at all times via immediate post-upload local eviction.

### Granularity & Persona Distribution (Per 5,000-Sample Shard)
* **Clean vs. Degraded Ratio:**
  - **30% Pristine Clean Digital Scans:** High-resolution uncorrupted digital text (clean white/natural background, zero photostat noise, zero toner bleed, zero optical blur) for born-digital document & e-book accuracy.
  - **70% Physical In-The-Wild Degradations:** Stochastic chain of 3 to 6 physical operators (raddi paper, newsprint, photostat xerox, ink bleed, folds & lighting, Gaussian blur, affine skew $\pm 2^\circ$, official stamps).
* **Tier 1 (Full-Page Documents):** **2.0% (100 pages / shard)**
  - Archetype A: Literary Society & Cultural Convention Public Notice
  - Archetype B: 3-Column Regional Newspaper Spread
  - Archetype C: Academic / Literary Textbook Chapter
* **Tier 2 (Paragraph & Multi-Line Blocks):** **13.0% (650 blocks / shard)**
* **Tier 3 (Sequence Text Lines - TrOCR / CRNN):** **55.0% (2,750 lines / shard)**
  - 70% Typeset (1,925 lines) across 16 Devanagari OpenType typefaces
  - 30% Kinematic Human Handwriting (825 lines) across 6 authentic personas
* **Tier 4 (Words & Isolated Conjuncts):** **30.0% (1,500 words / shard)**
  - 70% Typeset (1,050 words)
  - 30% Kinematic Human Handwriting (450 words)

---

## 2. Shard Execution & Hub Lifecycle Ledger

| Batch # | Shard Name | Sample Range | Sample Count | Shard Size (MB) | SHA-256 Checksum | Assertions Pass | Hugging Face Upload | Local Eviction | Timestamp (UTC) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `bho_train_00000.tar` | `bho_000000` - `bho_004999` | 5,000 | 103.97 | `3024a3fb479d0810...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 09:50:56 |
| 2 | `bho_train_00001.tar` | `bho_005000` - `bho_009999` | 5,000 | 103.97 | `8efb684db817436a...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 10:03:33 |
| 3 | `bho_train_00002.tar` | `bho_010000` - `bho_014999` | 5,000 | 104.83 | `8e246a1349fa1108...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 10:09:16 |
| 4 | `bho_train_00003.tar` | `bho_015000` - `bho_019999` | 5,000 | 104.95 | `2611c36e07671518...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 10:15:00 |
| 5 | `bho_train_00004.tar` | `bho_020000` - `bho_024999` | 5,000 | 103.89 | `0a11e1ef4d7a4129...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 10:20:43 |
| 6 | `bho_train_00005.tar` | `bho_025000` - `bho_029999` | 5,000 | 104.17 | `21ea1e24552753f5...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 10:27:03 |
| 7 | `bho_train_00006.tar` | `bho_030000` - `bho_034999` | 5,000 | 103.62 | `2f95102dbfc905a6...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 12:34:42 |
| 8 | `bho_train_00007.tar` | `bho_035000` - `bho_039999` | 5,000 | 104.37 | `1dce3ea1902a4eec...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 12:39:43 |
| 9 | `bho_train_00008.tar` | `bho_040000` - `bho_044999` | 5,000 | 104.43 | `d41b813aaf3cc796...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 12:44:44 |
| 10 | `bho_train_00009.tar` | `bho_045000` - `bho_049999` | 5,000 | 104.48 | `060f4cdc34ae7c5f...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 12:50:06 |
| 11 | `bho_train_00010.tar` | `bho_050000` - `bho_054999` | 5,000 | 104.42 | `e72ed68977865cb0...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 12:55:09 |
| 12 | `bho_train_00011.tar` | `bho_055000` - `bho_059999` | 5,000 | 104.44 | `b1dc3d5ea9b3bf7c...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 13:00:01 |
| 13 | `bho_train_00012.tar` | `bho_060000` - `bho_064999` | 5,000 | 104.74 | `c4f64bc1533723dd...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 13:05:18 |
| 14 | `bho_train_00013.tar` | `bho_065000` - `bho_069999` | 5,000 | 104.37 | `1e081cb07051870b...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 13:10:21 |
| 15 | `bho_train_00014.tar` | `bho_070000` - `bho_074999` | 5,000 | 103.02 | `9091de1e909aa3b2...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 13:19:40 |
| 16 | `bho_train_00015.tar` | `bho_075000` - `bho_079999` | 5,000 | 104.67 | `08f80bc5346155ba...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 13:25:18 |
| 17 | `bho_train_00016.tar` | `bho_080000` - `bho_084999` | 5,000 | 105.59 | `239a21ff6ff2de18...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:05:55 |
| 18 | `bho_train_00017.tar` | `bho_085000` - `bho_089999` | 5,000 | 105.74 | `07a4a997be645a9e...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:11:31 |
| 19 | `bho_train_00018.tar` | `bho_090000` - `bho_094999` | 5,000 | 107.05 | `0c2865f21b09aac0...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:17:25 |
| 20 | `bho_train_00019.tar` | `bho_095000` - `bho_099999` | 5,000 | 105.33 | `51eee165412bb695...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:24:01 |
| 21 | `bho_train_00020.tar` | `bho_100000` - `bho_104999` | 5,000 | 106.62 | `497526e861b8a23d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:29:23 |
| 22 | `bho_train_00021.tar` | `bho_105000` - `bho_109999` | 5,000 | 106.05 | `f1416ad4a557772c...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:34:53 |
| 23 | `bho_train_00022.tar` | `bho_110000` - `bho_114999` | 5,000 | 106.10 | `d97bb4a5297fee5b...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:40:28 |
| 24 | `bho_train_00023.tar` | `bho_115000` - `bho_119999` | 5,000 | 105.87 | `87fecc1161fd8d44...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:45:41 |
| 25 | `bho_train_00024.tar` | `bho_120000` - `bho_124999` | 5,000 | 105.94 | `8cbbe1d4bd052a88...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:51:09 |
| 26 | `bho_train_00025.tar` | `bho_125000` - `bho_129999` | 5,000 | 103.76 | `1b83d6fb09f56b02...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-10 14:56:21 |
| 27 | `bho_train_00026.tar` | `bho_130000` - `bho_134999` | 5,000 | 105.59 | `215964892898d415...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 14:44:55 |
| 28 | `bho_train_00027.tar` | `bho_135000` - `bho_139999` | 5,000 | 105.74 | `a39f6cd352200600...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 14:51:29 |
| 29 | `bho_train_00028.tar` | `bho_140000` - `bho_144999` | 5,000 | 107.05 | `d8a3e676fe6e5bc2...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 14:58:01 |
| 30 | `bho_train_00029.tar` | `bho_145000` - `bho_149999` | 5,000 | 105.33 | `188967ffe84615b7...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 15:04:29 |
| 31 | `bho_train_00030.tar` | `bho_150000` - `bho_154999` | 5,000 | 106.62 | `e7e27905943738fa...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 15:10:55 |
| 32 | `bho_train_00031.tar` | `bho_155000` - `bho_159999` | 5,000 | 106.05 | `de411f19f84e38fc...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 15:17:15 |
| 33 | `bho_train_00032.tar` | `bho_160000` - `bho_164999` | 5,000 | 106.10 | `9adf0b5422875843...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-11 15:38:50 |
| 34 | `bho_train_00033.tar` | `bho_165000` - `bho_169999` | 5,000 | 105.59 | `810acfd68cdd6d64...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 15:41:43 |
| 35 | `bho_train_00034.tar` | `bho_170000` - `bho_174999` | 5,000 | 105.74 | `bb14145b695004ff...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 15:48:48 |
| 36 | `bho_train_00035.tar` | `bho_175000` - `bho_179999` | 5,000 | 107.05 | `3713ef4276e39b3d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 15:55:52 |
| 37 | `bho_train_00036.tar` | `bho_180000` - `bho_184999` | 5,000 | 105.33 | `3bf917d4ea9c1557...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:02:10 |
| 38 | `bho_train_00037.tar` | `bho_185000` - `bho_189999` | 5,000 | 106.62 | `f6c9cfd7f3b856a9...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:07:50 |
| 39 | `bho_train_00038.tar` | `bho_190000` - `bho_194999` | 5,000 | 106.05 | `3f984da4dc783320...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:13:39 |
| 40 | `bho_train_00039.tar` | `bho_195000` - `bho_199999` | 5,000 | 106.10 | `f551f84f2c364323...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:19:18 |
| 41 | `bho_train_00040.tar` | `bho_200000` - `bho_204999` | 5,000 | 105.87 | `d299bec464c1e61d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:24:47 |
| 42 | `bho_train_00041.tar` | `bho_205000` - `bho_209999` | 5,000 | 105.94 | `74e783c1892fa951...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:30:21 |
| 43 | `bho_train_00042.tar` | `bho_210000` - `bho_214999` | 5,000 | 103.76 | `736c30d0e072d228...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:35:55 |
| 44 | `bho_train_00043.tar` | `bho_215000` - `bho_219999` | 5,000 | 105.53 | `cf805638e6cef960...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:41:31 |
| 45 | `bho_train_00044.tar` | `bho_220000` - `bho_224999` | 5,000 | 105.47 | `06f48c43933e336f...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:47:04 |
| 46 | `bho_train_00045.tar` | `bho_225000` - `bho_229999` | 5,000 | 106.41 | `bd842772db0d295d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:52:43 |
| 47 | `bho_train_00046.tar` | `bho_230000` - `bho_234999` | 5,000 | 106.62 | `a5f3b3877c7537ab...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 16:58:19 |
| 48 | `bho_train_00047.tar` | `bho_235000` - `bho_239999` | 5,000 | 106.15 | `1e545c994f5d9025...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:03:51 |
| 49 | `bho_train_00048.tar` | `bho_240000` - `bho_244999` | 5,000 | 104.74 | `3224bcc0b82c7403...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:09:30 |
| 50 | `bho_train_00049.tar` | `bho_245000` - `bho_249999` | 5,000 | 105.58 | `dbd098325eeae98f...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:15:06 |
| 51 | `bho_train_00050.tar` | `bho_250000` - `bho_254999` | 5,000 | 108.04 | `83a6507e22f2db9a...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:21:32 |
| 52 | `bho_train_00051.tar` | `bho_255000` - `bho_259999` | 5,000 | 104.83 | `a1037b8078a77da7...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:29:06 |
| 53 | `bho_train_00052.tar` | `bho_260000` - `bho_264999` | 5,000 | 106.99 | `46c31bab5d4e378a...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:36:49 |
| 54 | `bho_train_00053.tar` | `bho_265000` - `bho_269999` | 5,000 | 104.79 | `df773bd4520ce08d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:44:35 |
| 55 | `bho_train_00054.tar` | `bho_270000` - `bho_274999` | 5,000 | 105.46 | `bc8c52f99ac05317...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:52:19 |
| 56 | `bho_train_00055.tar` | `bho_275000` - `bho_279999` | 5,000 | 103.34 | `e982d1b693f4d084...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 17:59:45 |
| 57 | `bho_train_00056.tar` | `bho_280000` - `bho_284999` | 5,000 | 107.12 | `9808f8c01551ffcb...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:06:57 |
| 58 | `bho_train_00057.tar` | `bho_285000` - `bho_289999` | 5,000 | 107.01 | `e73cbeb2a6282c6e...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:14:20 |
| 59 | `bho_train_00058.tar` | `bho_290000` - `bho_294999` | 5,000 | 105.63 | `dcf5118a0e146722...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:21:21 |
| 60 | `bho_train_00059.tar` | `bho_295000` - `bho_299999` | 5,000 | 106.81 | `46b05fb270d4868d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:27:36 |
| 61 | `bho_train_00060.tar` | `bho_300000` - `bho_304999` | 5,000 | 106.22 | `f627b70dc9e0061b...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:33:02 |
| 62 | `bho_train_00061.tar` | `bho_305000` - `bho_309999` | 5,000 | 106.63 | `09f7acf3f37606fd...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:38:23 |
| 63 | `bho_train_00062.tar` | `bho_310000` - `bho_314999` | 5,000 | 105.51 | `5bacfa03d56add6d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:43:41 |
| 64 | `bho_train_00063.tar` | `bho_315000` - `bho_319999` | 5,000 | 105.62 | `27d1ea5360446821...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:48:59 |
| 65 | `bho_train_00064.tar` | `bho_320000` - `bho_324999` | 5,000 | 106.91 | `2dc5055277170cb9...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:54:21 |
| 66 | `bho_train_00065.tar` | `bho_325000` - `bho_329999` | 5,000 | 106.53 | `400609eb5039b964...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 18:59:45 |
| 67 | `bho_train_00066.tar` | `bho_330000` - `bho_334999` | 5,000 | 105.36 | `094883c10a1159a0...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:05:04 |
| 68 | `bho_train_00067.tar` | `bho_335000` - `bho_339999` | 5,000 | 107.59 | `86684b7afd561572...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:10:26 |
| 69 | `bho_train_00068.tar` | `bho_340000` - `bho_344999` | 5,000 | 104.99 | `b281fafe03da4bf0...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:15:43 |
| 70 | `bho_train_00069.tar` | `bho_345000` - `bho_349999` | 5,000 | 105.03 | `28a3b55a100d9d19...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:21:03 |
| 71 | `bho_train_00070.tar` | `bho_350000` - `bho_354999` | 5,000 | 106.27 | `d0a92f4ee15a5ae9...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:26:25 |
| 72 | `bho_train_00071.tar` | `bho_355000` - `bho_359999` | 5,000 | 105.59 | `9659743847241de3...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:31:45 |
| 73 | `bho_train_00072.tar` | `bho_360000` - `bho_364999` | 5,000 | 106.81 | `7511008338ad7e2f...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:37:05 |
| 74 | `bho_train_00073.tar` | `bho_365000` - `bho_369999` | 5,000 | 107.65 | `c6cdcc0b67ffa534...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:47:12 |
| 75 | `bho_train_00074.tar` | `bho_370000` - `bho_374999` | 5,000 | 105.65 | `54a5407ae8c74eec...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:52:36 |
| 76 | `bho_train_00075.tar` | `bho_375000` - `bho_379999` | 5,000 | 105.53 | `b4bfe1a50a860bf1...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 19:57:51 |
| 77 | `bho_train_00076.tar` | `bho_380000` - `bho_384999` | 5,000 | 106.92 | `a38fef0860860cfe...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:03:11 |
| 78 | `bho_train_00077.tar` | `bho_385000` - `bho_389999` | 5,000 | 106.26 | `0cd44ccb7ecab3a7...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:08:32 |
| 79 | `bho_train_00078.tar` | `bho_390000` - `bho_394999` | 5,000 | 104.24 | `b60b5bca96d7dba2...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:13:51 |
| 80 | `bho_train_00079.tar` | `bho_395000` - `bho_399999` | 5,000 | 105.71 | `3620aa773c22cbbe...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:19:11 |
| 81 | `bho_train_00080.tar` | `bho_400000` - `bho_404999` | 5,000 | 105.73 | `234a5becb7ca2f98...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:24:32 |
| 82 | `bho_train_00081.tar` | `bho_405000` - `bho_409999` | 5,000 | 106.86 | `e33c3f513a272d52...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:29:51 |
| 83 | `bho_train_00082.tar` | `bho_410000` - `bho_414999` | 5,000 | 104.83 | `13cee4b0b3a7dedc...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:35:13 |
| 84 | `bho_train_00083.tar` | `bho_415000` - `bho_419999` | 5,000 | 105.82 | `e1d5faaf74213aee...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:40:37 |
| 85 | `bho_train_00084.tar` | `bho_420000` - `bho_424999` | 5,000 | 105.92 | `b2c05d934c995643...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:46:03 |
| 86 | `bho_train_00085.tar` | `bho_425000` - `bho_429999` | 5,000 | 105.47 | `188c323a6a38b074...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:51:21 |
| 87 | `bho_train_00086.tar` | `bho_430000` - `bho_434999` | 5,000 | 106.34 | `690b1cdc7a47a601...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 20:56:44 |
| 88 | `bho_train_00087.tar` | `bho_435000` - `bho_439999` | 5,000 | 104.82 | `441573d0e6b89de3...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:02:05 |
| 89 | `bho_train_00088.tar` | `bho_440000` - `bho_444999` | 5,000 | 104.18 | `5cf1084625e6d3ac...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:07:19 |
| 90 | `bho_train_00089.tar` | `bho_445000` - `bho_449999` | 5,000 | 105.82 | `6e18d728bfc22e70...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:12:43 |
| 91 | `bho_train_00090.tar` | `bho_450000` - `bho_454999` | 5,000 | 104.79 | `f1b3f81436b1b231...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:17:59 |
| 92 | `bho_train_00091.tar` | `bho_455000` - `bho_459999` | 5,000 | 105.98 | `24da997028e6c8cd...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:23:23 |
| 93 | `bho_train_00092.tar` | `bho_460000` - `bho_464999` | 5,000 | 106.87 | `439cefe100dedbd5...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:28:49 |
| 94 | `bho_train_00093.tar` | `bho_465000` - `bho_469999` | 5,000 | 103.62 | `e70a982b5ac24816...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:34:06 |
| 95 | `bho_train_00094.tar` | `bho_470000` - `bho_474999` | 5,000 | 107.61 | `aa54e0addae79c5b...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:39:21 |
| 96 | `bho_train_00095.tar` | `bho_475000` - `bho_479999` | 5,000 | 105.78 | `b431181b3efe4232...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:44:40 |
| 97 | `bho_train_00096.tar` | `bho_480000` - `bho_484999` | 5,000 | 104.87 | `fed6ac2529cebcde...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:49:56 |
| 98 | `bho_train_00097.tar` | `bho_485000` - `bho_489999` | 5,000 | 107.11 | `3453c5769c051274...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 21:55:25 |
| 99 | `bho_train_00098.tar` | `bho_490000` - `bho_494999` | 5,000 | 105.46 | `cba545052373108d...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 22:01:12 |
| 100 | `bho_train_00099.tar` | `bho_495000` - `bho_499999` | 5,000 | 104.05 | `7bf1f663d02b42c3...` | ✅ Pass | ✅ Uploaded HTTP 200 | ✅ Deleted | 2026-09-12 22:07:29 |

---

## 3. Production Lifecycle Guarantees & Operating Status

* **Zero-Defect Verification:** Every shard passes 100% glyph coverage checks (zero `.notdef` boxes), dynamic vertical zone metrics (zero diacritic clipping), and label-box alignment assertions prior to upload.
* **Storage Invariant:** Immediate post-upload eviction ensures local disk footprint stays strictly $\le 2.0\text{ GB}$ (currently **0.015 GB**).
* **Remote Hub Persistence:** All verified shards are committed atomically to [`Faizaniqbal/IndicPixel-Pan-Indic-OCR`](https://huggingface.co/datasets/Faizaniqbal/IndicPixel-Pan-Indic-OCR) under `data/bhojpuri/`.
* **Execution Command Pattern:**
  ```powershell
  python "src/orchestrator/bhojpuri_production_pipeline.py" <start_shard> <num_shards> <samples_per_shard>
  ```

