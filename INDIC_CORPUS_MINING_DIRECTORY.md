# IndicPixel: Pan-Indic 70-Language & Multi-Author Corpus Directory

## 1. The Multi-Author Diversity Imperative

To build a world-class, zero-defect Pan-Indic OCR dataset (**IndicPixel**), relying on a single data source or author per language is strictly prohibited. Linguistic diversity requires capturing:
* **Lexical Range:** Everyday speech, classical literature, news journalism, technical manuals, administrative/legal notices, and digital conversational text.
* **Syntactic Structures:** Short commands, complex compound sentences, poetry lines, parenthetical clauses, dialogues, and lists.
* **Diacritic & Ligature Stress-Testing:** Rare vowel signs, halant conjuncts, and archaic ligatures that only appear when mining across hundreds of distinct authors and publishing styles.

This master catalog maps out premier, credible repositories across Hugging Face, GitHub, and academic archives covering **all ~70 South Asian languages, regional vernaculars, and indigenous tribal scripts**.

---

## 2. Core Mega-Repositories for Cross-Language Mining

These authoritative repositories form the backbone of our text mining pipeline. They provide multi-author diversity across dozens of languages with direct streaming access (zero local disk footprint):

### A. Meta AI FLORES-200 / NLLB (`facebook/flores`)
* **Hub URL:** [`facebook/flores`](https://huggingface.co/datasets/facebook/flores)
* **Coverage:** **65+ South Asian languages and dialects** (including Bhojpuri, Magahi, Awadhi, Maithili, Chhattisgarhi, Rajasthani, Dogri, Santali, Manipuri, Kashmiri, Sindhi, Balochi, Shina, Balti).
* **Tier:** **Tier 3 (Gold Quality Sentences)**
* **Author Diversity:** Professional multi-domain translation by native linguists across news, science, literature, and culture.
* **Streaming Recipe:**
  ```python
  from datasets import load_dataset
  # Stream gold sentences for any dialect (e.g. Bhojpuri 'bho_Deva', Chhattisgarhi 'hne_Deva')
  ds = load_dataset("facebook/flores", "bho_Deva", split="devtest", streaming=True)
  for row in ds:
      sentence = row["sentence"]
  ```

---

### B. Google MADLAD-400 (`google/madlad-400`)
* **Hub URL:** [`google/madlad-400`](https://huggingface.co/datasets/google/madlad-400)
* **Coverage:** **419 languages**, including almost every regional Indian language and dialect crawled from the open web.
* **Tier:** **Tier 1 (Pages) & Tier 2 (Paragraphs)**
* **Author Diversity:** Thousands of independent web domains, local newspapers, regional forums, and cultural websites.
* **Streaming Recipe:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("google/madlad-400", "new", split="clean", streaming=True) # Newari
  ```

---

### C. AI4Bharat Pretraining & Monolingual Suite (`ai4bharat/sangraha`)
* **Hub URL:** [`ai4bharat/sangraha`](https://huggingface.co/datasets/ai4bharat/sangraha)
* **Coverage:** **22 Constitutional languages** at massive volume (2.5+ Billion tokens).
* **Partitions:**
  - `verified/<lang>`: Curated book literature and verified publications.
  - `unverified/<lang>`: Deduplicated high-confidence classified web text.
* **Tier:** **Tier 1, Tier 2, and Tier 3**

---

### D. Wikimedia Multi-Author Dumps (`wikimedia/wikipedia`, `wikisource`, `wiktionary`)
* **Hub URL:** [`wikimedia/wikipedia`](https://huggingface.co/datasets/wikimedia/wikipedia)
* **Coverage:** **65+ Indic languages/dialects** (including Sanskrit, Maithili, Bhojpuri, Newari, Santali, Tulu, Pali, Awadhi, Doteli, Kashmiri, Sindhi).
* **Tier:**
  - **Wikipedia:** **Tier 1 & Tier 2** (Encyclopedic prose, headings, structured articles).
  - **Wikisource:** **Tier 1 & Tier 3** (Classical drama, poetry, historical manuscripts).
  - **Wiktionary:** **Tier 4** (Pristine lemmatized root vocabulary, parts of speech, inflections).
* **Streaming Recipe:**
  ```python
  from datasets import load_dataset
  # Stream Wikipedia articles across hundreds of crowdsourced authors
  ds = load_dataset("wikimedia/wikipedia", "20231101.bho", split="train", streaming=True)
  ```

---

### E. AI4Bharat Aksharantar (`ai4bharat/Aksharantar`)
* **Hub URL:** [`ai4bharat/Aksharantar`](https://huggingface.co/datasets/ai4bharat/Aksharantar)
* **Coverage:** **21 languages, 26+ million word pairs**.
* **Tier:** **Tier 4 (Tokens & Out-of-Vocabulary Quotas)**
* **Author Diversity:** Massive crowdsourced phonetic transliteration covering modern slang, brand names, place names, and complex proper nouns.

---

### F. StoryWeaver by Pratham Books (`prathambooks/storyweaver`)
* **Coverage:** **30+ Indic languages and indigenous dialects** (including Gondi, Kui, Mundari, Ho, Kokborok, Mizo, Garo, Khasi, Tulu).
* **Tier:** **Tier 2 (Paragraphs) & Tier 3 (Lines)**
* **Author Diversity:** Hundreds of published children's authors, narrative dialogue, storytelling prose, rich punctuation, and emotional dialogue.
* **License:** Open CC-BY 4.0.

---

### G. AI4Bharat Benchmarks (`IndicCOPA`, `IndicQA`, `IndicSentiment`, `Bhasha-Abhijnaanam`)
* **`IndicCOPA`:** Causal reasoning sentence pairs across 19 languages.
* **`IndicQA`:** Question-answering passage reading comprehension across 11 languages.
* **`IndicSentiment`:** User-generated product, movie, and social reviews across 13 languages (authentic informal register).
* **`Bhasha-Abhijnaanam`:** 100% native-script pure sentences across 22 scheduled languages + tribal scripts.

---

## 3. Comprehensive 70-Language South Asian Taxonomy & Source Mapping

Below is the complete 70-language inventory divided by language family and regional branch, with explicit source repositories for multi-author synthesis:

### Group 1: Northern & Dardic / Northwestern (8 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Kashmiri** | `kas` | Perso-Arabic / Naskh | 3.1M Corpus, `sangraha`, `Aksharantar`, `IndicCOPA`, Wikimedia |
| **Urdu** | `urd` | Perso-Arabic / Nastaliq | `sangraha`, `OSCAR`, `samanantar`, `Aksharantar`, `madlad-400` |
| **Sindhi (Arabic)** | `snd_Arab` | Perso-Arabic (52-char) | `sangraha`, `IndicCOPA`, `Aksharantar`, `flores` (`snd_Arab`) |
| **Sindhi (Devanagari)**| `snd_Deva` | Devanagari | `flores`, Sindhi Sahitya Academy publications, `Aksharantar` |
| **Gojri** | `gju` | Perso-Arabic | `flores`, J&K Cultural Academy texts, `madlad-400` |
| **Pahari-Pothwari** | `phr` | Perso-Arabic / Gurmukhi| `madlad-400`, regional folk anthologies, FLORES |
| **Shina** | `scl` | Perso-Arabic | `flores` (`scl_Arab`), Dardic research archives, CIIL Mysore |
| **Balti** | `bft` | Perso-Arabic / Tibetan | `flores` (`bft_Arab`), Himalayan language documentation |

---

### Group 2: Hindi Belt, Central & Western Indo-Aryan (14 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Hindi** | `hin` | Devanagari | `sangraha`, `samanantar` (8.5M), `OSCAR`, `madlad-400`, `Aksharantar` |
| **Bhojpuri** | `bho` | Devanagari | `flores` (`bho_Deva`), Wikimedia (`bho`), `Bhojpuri-NMT`, `madlad-400` |
| **Maithili** | `mai` | Devanagari / Tirhuta | `sangraha`, `IndicCOPA`, `Aksharantar`, Wikimedia (`mai`) |
| **Magahi** | `mag` | Devanagari | `flores` (`mag_Deva`), Magahi Parishad texts, `madlad-400` |
| **Awadhi** | `awa` | Devanagari | `flores` (`awa_Deva`), Wikisource (Ramcharitmanas & classical), `madlad-400` |
| **Braj Bhasha** | `bra` | Devanagari | Wikisource classical literature, Braj Sahitya Academy dumps |
| **Chhattisgarhi** | `hne` | Devanagari | `flores` (`hne_Deva`), Chhattisgarh Rajbhasha Aayog, `madlad-400` |
| **Haryanvi** | `bgc` | Devanagari | `madlad-400` (`bgc`), folk literature corpora, `flores` |
| **Rajasthani** | `raj` | Devanagari | `flores` (`raj_Deva`), Rajasthani Bhasha Academy, `madlad-400` |
| **Marwari** | `mwr` | Devanagari | `flores` (`mwr_Deva`), Wikimedia incubator, `madlad-400` |
| **Malvi** | `mup` | Devanagari | `madlad-400`, Malwa folk literature archives |
| **Garhwali** | `gbm` | Devanagari | `flores` (`gbm_Deva`), Uttarakhand Bhasha Sansthan |
| **Kumaoni** | `kfy` | Devanagari | `flores` (`kfy_Deva`), Kumaon literary archives |
| **Dogri** | `doi` | Devanagari | `sangraha` (`verified/doi`), `Aksharantar`, `Bhasha-Abhijnaanam` |

---

### Group 3: Western & Southern Indo-Aryan (6 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Marathi** | `mar` | Devanagari | `sangraha`, `samanantar` (3.4M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Gujarati** | `guj` | Gujarati | `sangraha`, `samanantar` (3.1M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Konkani** | `gom` | Devanagari / Roman | `sangraha` (`verified/gom`), `IndicCOPA`, `Aksharantar`, Wikimedia |
| **Punjabi** | `pan` | Gurmukhi | `sangraha`, `samanantar` (2.5M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Saraiki** | `skr` | Perso-Arabic | `flores` (`skr_Arab`), `madlad-400`, Saraiki Literary Board |
| **Dhivehi** | `div` | Thaana | `flores` (`div_Thaa`), Wikimedia (`dv`), `madlad-400` |

---

### Group 4: Eastern Indo-Aryan & Himalayan (6 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Bengali** | `ben` | Bengali | `sangraha`, `samanantar` (3.8M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Assamese** | `asm` | Bengali-Assamese | `sangraha`, `samanantar`, `OSCAR`, `Aksharantar`, Wikimedia |
| **Odia** | `ori` | Odia | `sangraha`, `samanantar` (1.2M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Nepali** | `nep` | Devanagari | `sangraha`, `OSCAR`, `madlad-400`, `Aksharantar`, Wikimedia |
| **Bishnupriya Manipuri**| `bpy`| Bengali | Wikimedia (`bpy`), `madlad-400`, literary archives |
| **Chakma** | `ccp` | Chakma / Bengali | `flores` (`ccp_Cakm`), Buddhist tipitaka Chakma corpus |

---

### Group 5: Dravidian Family (10 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Tamil** | `tam` | Tamil | `sangraha`, `samanantar` (5.3M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Telugu** | `tel` | Telugu | `sangraha`, `samanantar` (4.8M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Kannada** | `kan` | Kannada | `sangraha`, `samanantar` (4.1M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Malayalam** | `mal` | Malayalam | `sangraha`, `samanantar` (2.0M), `OSCAR`, `Aksharantar`, Wikimedia |
| **Tulu** | `tcy` | Kannada / Tigalari | Wikimedia (`tcy`), `madlad-400`, Tulu Sahitya Academy |
| **Kodava** | `kfa` | Kannada | Karnataka Kodava Sahitya Academy, `madlad-400` |
| **Badaga** | `bfq` | Tamil / Kannada | CIIL Mysore documentation, Badaga cultural archives |
| **Gondi** | `gon` | Devanagari / Telugu | `storyweaver` (Pratham Books), CGNet Swara corpus |
| **Kui / Kuvi** | `kxu` | Odia / Devanagari | Odisha Tribal Language Academy, CIIL archives |
| **Kurukh (Oraon)** | `kru` | Tolong Siki / Deva | Jharkhand Tribal Welfare Research Institute, `madlad-400` |

---

### Group 6: Tibeto-Burman & Northeastern Indigenous (16 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Manipuri (Meitei Mayek)**| `mni_Mtei`| Meitei Mayek | `sangraha` (`verified/mni`), `Aksharantar`, `Bhasha-Abhijnaanam` |
| **Manipuri (Bengali)** | `mni_Beng`| Bengali | `flores` (`mni_Beng`), Manipur University corpus |
| **Bodo** | `brx` | Devanagari | `sangraha` (`verified/brx`), `Aksharantar`, `Bhasha-Abhijnaanam` |
| **Kokborok (Tripuri)** | `trp` | Bengali / Latin | `storyweaver`, Tripura Tribal Areas Autonomous District Council |
| **Mizo (Lushai)** | `lus` | Latin | `flores` (`lus_Latn`), Wikimedia (`lus`), Mizo Academy of Letters |
| **Garo** | `grt` | Latin / Bengali | `storyweaver`, Meghalaya State Language Board |
| **Khasi** (Austroasiatic)| `kha`| Latin | `flores` (`kha_Latn`), Wikimedia incubator, Khasi Authors Society |
| **Ao Naga** | `njo` | Latin | Ao Baptist Arogo Mungdang archives, `storyweaver` |
| **Angami Naga** | `njm` | Latin | Ura Academy (Kohima), Angami literature board |
| **Lotha Naga** | `njh` | Latin | Lotha Literature Committee, Nagaland state publications |
| **Konyak** | `nbe` | Latin | Konyak Baptist Bumeinok Bangjum archives |
| **Karbi** | `mjw` | Latin / Assamese | Karbi Lammet Amei (Karbi Sahitya Sabha) |
| **Lepcha** | `lep` | Lepcha script | Sikkim Indigenous Language Board, `flores` |
| **Limbu** | `lif` | Sirijanga script | Sikkim Limbu Language Committee, Nepal academy |
| **Newari (Nepal Bhasa)**| `new` | Devanagari / Prachalit| Wikimedia (`new`), `madlad-400`, Nepal Bhasa Parishad |
| **Tibetan (Bhoti / Ladakhi)**| `bod` | Tibetan script | `flores` (`bod_Tibt`), Wikisource (`bo`), Buddhist Digital Resource Center (BDRC) |

---

### Group 7: Austroasiatic (Munda) Family (5 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Santali (Ol Chiki)** | `sat_Olck`| Ol Chiki | `sangraha` (`verified/sat`), `IndicCOPA`, `Aksharantar`, `flores` |
| **Santali (Devanagari)**| `sat_Deva`| Devanagari | `sangraha`, Bihar/Jharkhand tribal literature dumps |
| **Mundari** | `unr` | Devanagari / Mundari Bani| `storyweaver`, Mundari Sahitya Parishad, CIIL |
| **Ho** | `hoc` | Warang Citi / Devanagari| `storyweaver`, Tata Steel Tribal Cultural Society archives |
| **Kharia** | `khr` | Devanagari | Jharkhand Bhasha Sansthan, CIIL documentation |

---

### Group 8: Classical, Scriptural & Ancient (5 Languages)
| Language | ISO / Code | Primary Script | Multi-Author Source Repositories |
| :--- | :--- | :--- | :--- |
| **Sanskrit** | `san` | Devanagari | `sangraha` (`verified/san`), `OSCAR`, `IndicCOPA`, Wikisource (`sa`) |
| **Pali** | `pli` | Devanagari / Burmese | Tipitaka Pali Canon digital project, VRI Vipassana Research Institute |
| **Prakrit / Ardhamagadhi**| `pra` | Devanagari | Jain Agamas digital corpus, Prakrit Bharati Academy |
| **Avestan** | `ave` | Avestan script | Avesta Digital Archive (SOAS) |
| **Sinhala** | `sin` | Sinhala | `flores` (`sin_Sinh`), `madlad-400`, Wikimedia (`si`) |

---

## 4. Multi-Author Ingestion Protocol (Quality & Deduplication Gate)

When aggregating across multiple diverse repositories for any language:

1. **Strict Unicode NFC Gate:**
   - Normalizes varied decomposition standards from different web publishers into standard NFC Unicode codepoints.
2. **ZWJ / ZWNJ Preservation Gate:**
   - Prohibits regex cleaners from stripping `\u200C` and `\u200D` (mandatory for conjunct ligatures in Kashmiri, Bengali, Malayalam, and Devanagari).
3. **Multi-Source Line Shuffling:**
   - Interleaves text samples across authors (e.g. 25% Wikipedia, 25% FLORES, 25% Sangraha books, 25% Aksharantar tokens) to eliminate author-specific stylistic bias.
4. **HarfBuzz CMAP Font Validation:**
   - Discards any text line if the target language font lacks full coverage in `font.getBestCmap()`. Zero `.notdef` tofu boxes permitted.
5. **Streaming Disk Control:**
   - Uses HTTP streaming iterators (`streaming=True`) so local disk usage stays strictly $\le 1.0\text{ GB}$ throughout synthesis.
