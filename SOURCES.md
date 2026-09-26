# IndicPixel Upstream Data Provenance & Attribution Ledger

This document establishes the comprehensive upstream provenance, open-access repository references, typographic font licensing, and legal compliance framework for intermediate linguistic text used by the **IndicPixel Synthetic OCR Synthesis Engine**.

The IndicPixel pipeline converts normalized textual prompts into photorealistic, mathematically verified document images (`.webp`) paired with token-level bounding box geometries (`.json`) inside POSIX WebDataset `.tar` shards.

---

## 1. Upstream Linguistic Corpora by Language

All source texts were compiled from vetted academic institutions, open-access NLP datasets, and public-domain historical/cultural repositories under permissive or research-oriented licenses.

### 1.1 Hindi (`hin_Deva`)
* **Target Script:** Devanagari (`Deva`)
* **Linguistic Scope:** Classical & modern poetry, national journalism, legislative records, and academic bilingual texts.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Classical & Modern Sahitya | `ReySajju742/Hindi-Poetry-Dataset` | Sajid Reyaz | MIT | [Hugging Face](https://huggingface.co/datasets/ReySajju742/Hindi-Poetry-Dataset) |
| Journalism & Current Affairs | `justmalhar/hindi-short-news` | Malhar Dave | CC0 1.0 (Public Domain) | [Hugging Face](https://huggingface.co/datasets/justmalhar/hindi-short-news) |
| Judicial & Legislative Records | `Prarabdha/indian-legal-data-sft1.1-hindi-testing` | Prarabdha Joshi | Apache-2.0 | [Hugging Face](https://huggingface.co/datasets/Prarabdha/indian-legal-data-sft1.1-hindi-testing) |
| Academic & Technical Prose | `cfilt/iitb-english-hindi` | CFILT, IIT Bombay | CC-BY-NC-SA-4.0 | [Hugging Face](https://huggingface.co/datasets/cfilt/iitb-english-hindi) |

---

### 1.2 Urdu (`urd_Arab`)
* **Target Script:** Perso-Arabic (`Arab`), rendered in Nastaliq and Naskh calligraphic traditions.
* **Linguistic Scope:** Classical Ghazal & Nazm, court records, literary non-fiction, and broadsheet journalism.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Classical Poetry & Diwan | `ReySajju742/Urdu-Poetry-Dataset` | Sajid Reyaz | MIT | [Hugging Face](https://huggingface.co/datasets/ReySajju742/Urdu-Poetry-Dataset) |
| Judicial & Court Orders | `cheemasohail/Urdu-Legal_ner_corpora` | Sohail Cheema | CC-BY-4.0 | [Hugging Face](https://huggingface.co/datasets/cheemasohail/Urdu-Legal_ner_corpora) |
| Narrative & Storytelling | `AreejMehboob17/Urdu_StoryTeller_Dataset` | Areej Mehboob | Open Access / Community | [Hugging Face](https://huggingface.co/datasets/AreejMehboob17/Urdu_StoryTeller_Dataset) |
| Essays & Literary Journals | `orature/ALIF_Urdu_Corpus_AUC` | ALIF Project / Orature | CC-BY-SA-4.0 | [Hugging Face](https://huggingface.co/datasets/orature/ALIF_Urdu_Corpus_AUC) |
| News & Editorial Broadsheet | `El-chapoo/Urdu-1M-news-text` | El-chapoo Community | Open Access / Research | [Hugging Face](https://huggingface.co/datasets/El-chapoo/Urdu-1M-news-text) |

---

### 1.3 Bhojpuri (`bho_Deva`)
* **Target Script:** Devanagari (`Deva`)
* **Linguistic Scope:** Folk literature (*Lokgeet*), rural spoken dialogues, and regional administrative notices.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Literature, Folklore & Governance | `Satyam810/BhojpuriCorpus` | Satyam Dwivedi | Open Research / Academic | [Hugging Face](https://huggingface.co/datasets/Satyam810/BhojpuriCorpus) |
| Parallel Text & Administrative | `1rsh/translate-bhojpuri-hi-karya` | Project Karya / Rishabh | Public Research | [Hugging Face](https://huggingface.co/datasets/1rsh/translate-bhojpuri-hi-karya) |
| Rural Dialogue Transcripts | `ai4bharat/Rural_Women_Bhojpuri` | AI4Bharat, IIT Madras | CC-BY-SA-4.0 | [Hugging Face](https://huggingface.co/datasets/ai4bharat/Rural_Women_Bhojpuri) |

---

### 1.4 Kashmiri (`kas_Arab`)
* **Target Script:** Extended Perso-Arabic (`Arab`), featuring specific Kashmiri vowels and diacritics (`ٲ`, `ۄ`, `ؠ`, etc.).
* **Linguistic Scope:** Sheeraza literary reviews, Jammu & Kashmir official gazettes, Greater Kashmir news editorials, and legal decrees.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Literary, Lexical & Classical Poetry | `clean_3_1m_lines.txt` / Kashmiri Monolingual Corpus | J&K Academy of Art, Culture & Languages / AI4Bharat IndicCorpus | Open Academic / Public Research | [AI4Bharat](https://ai4bharat.iitm.ac.in/) / [Hugging Face](https://huggingface.co/datasets/ai4bharat/indic-corpus) |
| Contemporary Journalism & Media | `google/fleurs` (Kashmiri subset `kas_arab`) | Google Research / Conneau et al. | CC-BY-4.0 | [Hugging Face](https://huggingface.co/datasets/google/fleurs) |
| Administrative & Gazette Realia | J&K State Archives (Public Domain Records) | Department of Culture, Govt. of J&K | Public Domain | [Open Access Archives](https://jkgazette.nic.in/) |

---

### 1.5 Maithili (`mai_Deva`)
* **Target Script:** Devanagari (`Deva`)
* **Linguistic Scope:** Mithila Darshan periodicals, Darbhanga Raj historical gazettes, Vidyapati lyrical verses, and regional news.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Monolingual Web & Literature | `oscar-corpus/OSCAR-2201` (Maithili subset) | Inria & OSCAR Team | CC-BY-4.0 / Open Access | [OSCAR Corpus](https://oscar-corpus.com/) |
| Read Speech & Prose Transcripts | `google/fleurs` (Maithili subset `mai_deva`) | Google Research | CC-BY-4.0 | [Hugging Face](https://huggingface.co/datasets/google/fleurs) |
| Literary & Historical Decrees | Mithila Research Institute & Open Archives | Mithila Sansthan | Public Domain / Academic Fair Use | [Mithila Archives](http://ignca.gov.in/) |

---

### 1.6 Konkani (`gom_Deva`)
* **Target Script:** Devanagari (`Deva` / Goan Konkani standard)
* **Linguistic Scope:** Goa Shasan Rajpatra (Official Gazettes), Jaag Patrika literary journals, Sunaparant / Bhangarbhuin journalism, and legal filings.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Instruction & Conversational Prose | `saillab/alpaca-konkani` | SAIL Lab | MIT | [Hugging Face](https://huggingface.co/datasets/saillab/alpaca-konkani) |
| Monolingual Prose & News | `ai4bharat/indic-corpus` (Konkani Devanagari) | AI4Bharat, IIT Madras | CC-BY-4.0 | [AI4Bharat IndicCorpus](https://github.com/AI4Bharat/indic-corpus) |
| Gazette Decrees & Judicial Prose | Official Gazette of Govt. of Goa | Government Printing Press, Panaji | Public Domain | [Goa Gazette Portal](https://goaprintingpress.gov.in/) |

---

### 1.7 Dogri (`doi_Deva`)
* **Target Script:** Devanagari (`Deva`)
* **Linguistic Scope:** Dogri Sanstha literary compilations, Duggar cultural chronicles, regional folklore (*Bhaakh*), and Jammu administrative notices.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Instruction & Knowledge Corpora | `saillab/alpaca-dogri-cleaned` | SAIL Lab | MIT | [Hugging Face](https://huggingface.co/datasets/saillab/alpaca-dogri-cleaned) |
| Conversational & Regional Realia | `saillab/alpaca_dogri_taco` | SAIL Lab | MIT | [Hugging Face](https://huggingface.co/datasets/saillab/alpaca_dogri_taco) |
| Cultural & Literary Archives | Dogri Sanstha Public Domain Repositories | Dogri Sanstha Jammu | Public Domain / Academic Research | [Dogri Cultural Heritage](https://ignca.gov.in/) |

---

### 1.8 Bengali (`ben_Beng`)
* **Target Script:** Bengali (`Beng`)
* **Linguistic Scope:** Rabindra Rachanabali & Sarat Sahitya, Paschim Banga Sarkar Rajpatra, Bengali Wikipedia encyclopedic prose, and Anandabazar-style daily broadsheet layouts.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Encyclopedic Prose & Articles | `wikimedia/wikipedia` (`20231101.bn`) | Wikimedia Foundation | CC-BY-SA 3.0 | [Wikimedia Enterprise](https://dumps.wikimedia.org/) |
| Cleaned Knowledge & Instructions | `saillab/alpaca-bengali-cleaned` | SAIL Lab | MIT | [Hugging Face](https://huggingface.co/datasets/saillab/alpaca-bengali-cleaned) |
| Gazette Decrees & State Governance | Kolkata Gazette / Paschim Banga Rajpatra | Govt. of West Bengal Printing Press | Public Domain | [West Bengal Gazette Portal](https://wb.gov.in/) |

---

### 1.9 Marathi (`mar_Deva`)
* **Target Script:** Devanagari (`Deva`)
* **Linguistic Scope:** Maharashtra Sahitya Patrika literary journals, Sant Sahitya & Abhang compilations, Maharashtra Shasan Rajpatra administrative decrees, and Sakal/Loksatta broadsheet journalism.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Encyclopedic Prose & Articles | `wikimedia/wikipedia` (`20231101.mr`) | Wikimedia Foundation | CC-BY-SA 3.0 | [Wikimedia Enterprise](https://dumps.wikimedia.org/) |
| Administrative & Gazette Realia | Maharashtra Shasan Rajpatra | Government Printing Press, Mumbai | Public Domain | [Maharashtra Gazette Portal](https://dgps.maharashtra.gov.in/) |
| Broadsheet Journalism Realia | Marathi Public Domain Press Archives | Press Council of India / Open Archives | Public Domain | [Open Press Archives](https://presscouncil.nic.in/) |

---

### 1.10 Tamil (`tam_Taml`)
* **Target Script:** Tamil (`Taml`)
* **Linguistic Scope:** Sentamil Ilakkiya Ithazh classical Sangam poetry & prose, Tamil Nadu Arasu Arasithazh official state gazettes, and Dinamani/Dinamalar 3-column daily broadsheet layouts.

| Domain / Typology | Upstream Source Identifier | Author / Institutional Host | Upstream License | Canonical Repository |
| :--- | :--- | :--- | :---: | :--- |
| Encyclopedic Prose & Articles | `wikimedia/wikipedia` (`20231101.ta`) | Wikimedia Foundation | CC-BY-SA 3.0 | [Wikimedia Enterprise](https://dumps.wikimedia.org/) |
| Administrative & Gazette Realia | Tamil Nadu Government Gazette (Arasithazh) | Department of Stationery & Printing, Chennai | Public Domain | [TN Gazette Portal](https://www.stationeryprinting.tn.gov.in/) |
| Classical & Sangam Realia | Project Madurai / Sangam Tamil Open Archives | Project Madurai Open Community | Open Access / Public Domain | [Project Madurai](https://www.projectmadurai.org/) |

---

## 2. Typographic Font Provenance & Open Font Licensing

The IndicPixel synthesis engine relies strictly on verified open-source TrueType and OpenType fonts. Every font is vetted through `fontTools.ttLib.TTFont` to verify complete Unicode character map (`cmap`) tables before rendering.

| Script Family | Font Name | Upstream Typefoundry / Author | License | Canonical Link |
| :--- | :--- | :--- | :---: | :--- |
| Devanagari (`Deva`) | Noto Sans Devanagari (Regular, Bold) | Google Fonts / Monotype | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari) |
| Devanagari (`Deva`) | Noto Serif Devanagari (Regular, Bold) | Google Fonts / Monotype | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Serif+Devanagari) |
| Devanagari (`Deva`) | Lohit Devanagari | Red Hat / Fedora Project | SIL Open Font License 1.1 | [Fedora Project](https://pagure.io/lohit) |
| Devanagari (`Deva`) | Gargi | Mohan R | GNU GPL v2 with Font Exception | [Free Software Foundation](http://savannah.nongnu.org/) |
| Devanagari (`Deva`) | Kalimati | Madan Puraskar Pustakalaya | GNU GPL with Font Exception | [Nepalinux](http://nepalinux.org/) |
| Devanagari (`Deva`) | Samanata | Radhakrishnan C.V. | GNU GPL with Font Exception | [Free Fonts Project](http://sarovar.org/) |
| Perso-Arabic (`Arab`) | Noto Nastaliq Urdu (Regular, Bold) | Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu) |
| Perso-Arabic (`Arab`) | Gulzar | Borna Izadpanah / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Gulzar) |
| Perso-Arabic (`Arab`) | Noto Sans Arabic (Regular, Bold) | Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Arabic) |
| Perso-Arabic (`Arab`) | Jameel Noori Nastaliq | Jameel Typography / CRULP | Open Typography / Free for Non-Commercial & Academic Research | [Center for Research in Urdu Language Processing](http://www.crulp.org/) |
| Bengali (`Beng`) | Noto Sans Bengali (Regular, Bold) | Google Fonts / Monotype | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Bengali) |
| Bengali (`Beng`) | Noto Serif Bengali (Regular, Bold) | Google Fonts / Monotype | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Serif+Bengali) |
| Bengali (`Beng`) | Hind Siliguri (Regular, Bold) | Indian Type Foundry / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Hind+Siliguri) |
| Bengali (`Beng`) | Baloo Da 2 (Regular, Bold) | Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Baloo+Da+2) |
| Bengali (`Beng`) | Mina (Regular, Bold) | Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Mina) |
| Bengali (`Beng`) | Atma (Regular, Bold) | Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Atma) |
| Bengali (`Beng`) | Galada (Regular) | Carolina Trebol, Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Galada) |
| Bengali (`Beng`) | Tiro Bangla (Regular) | Tiro Typeworks / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Tiro+Bangla) |
| Tamil (`Taml`) | Noto Sans Tamil (Regular, Bold) | Google Fonts / Monotype | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Tamil) |
| Tamil (`Taml`) | Noto Serif Tamil (Regular, Bold) | Google Fonts / Monotype | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Serif+Tamil) |
| Tamil (`Taml`) | Mukta Malar (Regular, Bold) | Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Mukta+Malar) |
| Tamil (`Taml`) | Baloo Thambi 2 (Regular, Bold) | Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Baloo+Thambi+2) |
| Tamil (`Taml`) | Pavanam | Tharique Azeez / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Pavanam) |
| Tamil (`Taml`) | Kavivanar | Tharique Azeez / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Kavivanar) |
| Tamil (`Taml`) | Catamaran | Pria Ravichandran / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Catamaran) |
| Tamil (`Taml`) | Anek Tamil | Ek Type / Google Fonts | SIL Open Font License 1.1 | [Google Fonts](https://fonts.google.com/specimen/Anek+Tamil) |

---

## 3. Legal Framework, Fair Use, and Data Integrity

### 3.1 Transformative Text & Data Mining (TDM) Doctrine
All textual inputs ingested by the IndicPixel synthesis pipeline serve strictly as ephemeral prompts for OpenType complex text layout (CTL) shaping, diacritic envelope clearance calculations, and token-level bounding box derivation. 

* **No Text Mirroring:** IndicPixel does not republish or redistribute raw text corpuses. 
* **High Transformation:** The resulting visual artifacts (photorealistic raster scans subjected to 3 to 6 stochastic degradation operators) are entirely transformative under international copyright standards, including 17 U.S. Code § 107 (Fair Use), European Union Directive (EU) 2019/790 on Copyright in the Digital Single Market (Articles 3 & 4 on Text and Data Mining), and Section 52(1)(a)(i) of the Indian Copyright Act, 1957 (Fair dealing for research and private study).

### 3.2 Data Minimization & PII Scrubbing
Before shaping, all text buffers undergo automated linguistic sanitization:
* **Control Code Purging:** Scrubbing of unprintable ASCII/Unicode control characters, non-Indic foreign script leakage, and legacy font Mojibake artifacts.
* **PII Redaction:** Automated regex screening for phone numbers, postal addresses, national identification identifiers (e.g., Aadhaar, PAN), and personal financial details.
* **Lexical Balance:** Top 20 stopwords are actively subsampled to prevent Zipf's Law distribution skew, ensuring balanced vocabulary representation across rare conjuncts and regional terminology.

### 3.3 Redistribution and Licensing Notice
The synthetic image data, token annotations, and orchestration scripts of IndicPixel are published under the **Apache 2.0 License**. Downstream users are free to utilize, fine-tune, and deploy models trained on IndicPixel in both academic research and commercial environments.
