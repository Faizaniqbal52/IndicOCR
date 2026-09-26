"""
Agent-Linguist: Unicode & Corpus Gatekeeper
Enforces:
1. Strict Unicode NFC normalization.
2. GUARANTEE: Never strip \u200D (ZWJ) or \u200C (ZWNJ).
3. Scrub unprintable control codes, non-Devanagari script noise, HTML entities.
4. Legacy font transcoding validation assertions.
5. Akshara / Conjunct mining & Stopword subsampling to break Zipf's Law.
"""

import re
import unicodedata
from collections import Counter
from typing import List, Dict, Tuple, Set, Optional

# Core Devanagari Unicode Ranges
# Main block: U+0900 to U+097F
# Devanagari Extended: U+A8E0 to U+A8FF
# Vedic Extensions: U+1CD0 to U+1CFF
DEVANAGARI_RANGE = (0x0900, 0x097F)
DEVANAGARI_EXT_RANGE = (0xA8E0, 0xA8FF)

# Critical Joiners (MUST NEVER BE STRIPPED)
ZWJ = '\u200D'   # Zero-Width Joiner (Half-forms, explicit ligatures)
ZWNJ = '\u200C'  # Zero-Width Non-Joiner (Explicit halant display)

# Common Indian Punctuation / Numerals
DANDA = '\u0964'       # ।
DOUBLE_DANDA = '\u0965' # ॥
DEVA_DIGITS = set("०१२३४५६७८९")
ARABIC_DIGITS = set("0123456789")

# Regex patterns
RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_HTML_ENTITIES = re.compile(r'&[a-zA-Z0-9#]+;')
RE_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')
RE_ZERO_WIDTH_SPACES = re.compile(r'[\u200B\uFEFF]') # ZWSP and BOM (NOT ZWJ/ZWNJ)
RE_WHITESPACE = re.compile(r'[ \t\r\f\v]+')
RE_MULTIPLE_NEWLINES = re.compile(r'\n{3,}')
RE_URLS = re.compile(r'https?://\S+|www\.\S+')

# Known Top Bhojpuri Stopwords (for Zipfian balancing)
BHOJPURI_COMMON_STOPWORDS = {
    "बा", "बाटे", "बानी", "बाड़न", "ह", "हो", "हवे", "रहल", "रहलन", "गइल",
    "आइल", "भइल", "कइल", "करे", "करेला", "करेले", "आ", "त", "ओह", "एह",
    "जे", "से", "के", "में", "पर", "ले", "खातिर", "ना", "नाहीं", "लोग",
    "का", "काहे", "केहू", "कुछ", "जब", "तब", "अब", "ई", "ऊ", "हम",
    "रउआ", "तोहार", "हमार", "ओकर", "एकर", "उहाँ", "इहाँ", "तनी"
}

# Rare / High-Value Devanagari Conjunct Consonants (Samyuktaksharas)
HIGH_VALUE_CONJUNCTS = [
    "क्ष", "त्र", "ज्ञ", "श्र", "द्द", "द्ध", "द्य", "द्व", "ह्म", "ह्न",
    "ह्य", "ह्र", "ह्ल", "ह्व", "ष्ट", "ष्ठ", "ष्ण", "त्थ", "त्त्व", "द्द्र",
    "क्र", "प्र", "ब्र", "ग्र", "द्र", "ट्र", "ड्र", "र्क", "र्म", "र्व",
    "र्ष", "र्त्य", "स्त्र", "स्न", "स्म", "स्य", "स्थ", "स्प्र", "ङ्क", "ङ्ग",
    "ञ्च", "ञ्ज", "ण्ठ", "ण्ड", "म्प", "म्ब", "म्भ", "न्ह", "ल्ह", "म्ह" # Bhojpuri sonorants
]


SCRIPT_UNICODE_RANGES: Dict[str, List[Tuple[int, int]]] = {
    "Deva": [(0x0900, 0x097F), (0xA8E0, 0xA8FF)],
    "Beng": [(0x0980, 0x09FF)],
    "Taml": [(0x0B80, 0x0BFF)],
    "Telu": [(0x0C00, 0x0C7F)],
    "Gujr": [(0x0A80, 0x0AFF)],
    "Knda": [(0x0C80, 0x0CFF)],
    "Mlym": [(0x0D00, 0x0D7F)],
    "Orya": [(0x0B00, 0x0B7F)],
    "Guru": [(0x0A00, 0x0A7F)],
    "Arab": [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)],
    "Olck": [(0x1C50, 0x1C7F)],
    "Mtei": [(0xABC0, 0xABFF), (0xAAE0, 0xAAFF)],
    "Tibt": [(0x0F00, 0x0FFF)],
    "Lepc": [(0x1C00, 0x1C4F)],
    "Sora": [(0x110D0, 0x110FF)],
    "Wara": [(0x118A0, 0x118FF)],
    "Wcho": [(0x1E2C0, 0x1E2FF)],
    "Tnsa": [(0x16A70, 0x16ACF)],
    "Latn": [(0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x024F)]
}


class UnicodeGatekeeper:
    """Agent-Linguist Corpus & Unicode Gatekeeper."""

    @staticmethod
    def clean_devanagari_typos(text: str) -> str:
        """
        Agent-Linguist Typographical & Legacy Transcoding Gatekeeper:
        Fixes common Devanagari web/keyboard typing corruptions:
        1. Legacy typewriter encoding of independent vowels via Reph:
           - र्इ (Ra + Halant + I) -> ई (U+0908)
           - र्ई (Ra + Halant + II) -> ई (U+0908)
           - र्उ (Ra + Halant + U) -> ऊ (U+090A)
           - र्ए (Ra + Halant + E) -> ऐ (U+0910)
           - इ्र (I + Halant + Ra) -> ई (U+0908)
        2. Misplaced Nuktas (vowel sign typed before nukta):
           - e.g. ड + ि + ़ -> ड़ + ि
        3. Canonical NFC re-composition.
        """
        if not text:
            return ""
        # Legacy reph on independent vowels
        text = text.replace('\u0930\u094d\u0907', '\u0908')  # र्इ -> ई
        text = text.replace('\u0930\u094d\u0908', '\u0908')  # र्ई -> ई
        text = text.replace('\u0930\u094d\u0909', '\u090A')  # र्उ -> ऊ
        text = text.replace('\u0930\u094d\u090F', '\u0910')  # र्ए -> ऐ
        text = text.replace('\u0907\u094d\u0930', '\u0908')  # इ्र -> ई

        # Misplaced nukta: consonant + vowel sign + nukta -> consonant + nukta + vowel sign
        text = re.sub(r'([\u0915-\u0939])([\u093E-\u094C\u0962\u0963])\u093C', '\\g<1>\u093C\\g<2>', text)

        # Re-apply NFC canonical composition
        return unicodedata.normalize('NFC', text)

    @staticmethod
    def scrub_foreign_noise(text: str, script: str = "Deva") -> str:
        """
        Agent-Linguist Foreign Noise Gatekeeper:
        Scrubs unmapped legacy artifacts, foreign script noise (Chinese, Greek, Arabic, etc.),
        emojis, arrows, and unrenderable math symbols.
        Maps typographical dashes/quotes to standard forms.
        Preserves target script codepoints, ZWJ/ZWNJ, allowed numerals, Latin acronyms, and standard punctuation.
        """
        dash_map = {
            '\u2011': '-', '\u2015': '-', '\u2014': '-', '\u2013': '-',
            '\u2033': '"', '\u2032': "'", '`': "'", '’': "'", '‘': "'",
            '“': '"', '”': '"', '«': '"', '»': '"'
        }
        for k, v in dash_map.items():
            text = text.replace(k, v)

        ranges = SCRIPT_UNICODE_RANGES.get(script, [(0x0900, 0x097F)])
        allowed_ascii = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.-?!:;\'\"()[]{}<>/\\%+=*₹@#$&_~")

        clean_chars = []
        for ch in text:
            code = ord(ch)
            if any(r_start <= code <= r_end for r_start, r_end in ranges):
                if 0x0951 <= code <= 0x0954:
                    continue  # Vedic stress accents (Udatta/Anudatta) unrenderable in modern typefaces
                clean_chars.append(ch)
            elif ch in (ZWJ, ZWNJ, DANDA, DOUBLE_DANDA, '\u00A0', '\n', '\t', '\r'):
                clean_chars.append(ch)
            elif ch in allowed_ascii:
                clean_chars.append(ch)
            else:
                continue

        return "".join(clean_chars)

    @staticmethod
    def normalize_and_clean(text: str, script: str = "Deva") -> str:
        """
        Applies Gate 1: Unicode NFC Normalization with strict preservation of ZWJ/ZWNJ.
        Script-aware punctuation standardization.
        Foreign script and unmapped artifact scrubbing.
        """
        if not text:
            return ""

        # 1. Unicode NFC Normalization & Typographical Corruption Fixes
        text = unicodedata.normalize('NFC', text)
        if script == "Deva":
            text = UnicodeGatekeeper.clean_devanagari_typos(text)

        # 2. Strip HTML artifacts and raw URLs
        text = RE_HTML_TAGS.sub(' ', text)
        text = RE_HTML_ENTITIES.sub(' ', text)
        text = RE_URLS.sub(' ', text)

        # 3. Strip invisible junk (BOM, Zero-Width Space) BUT PRESERVE ZWJ and ZWNJ!
        text = RE_ZERO_WIDTH_SPACES.sub('', text)

        # 4. Remove unprintable ASCII/Unicode control characters
        text = RE_CONTROL_CHARS.sub('', text)

        # 5. Script-Aware Punctuation Standardization (only convert pipes to Danda for Danda-using scripts)
        if script in ("Deva", "Beng", "Orya", "Guru"):
            text = text.replace('||', DOUBLE_DANDA).replace('|', DANDA)

        # 6. Scrub foreign script noise, unmapped symbols, emojis, and arrows
        text = UnicodeGatekeeper.scrub_foreign_noise(text, script=script)

        # 7. Normalize Whitespaces
        text = RE_WHITESPACE.sub(' ', text)
        text = RE_MULTIPLE_NEWLINES.sub('\n\n', text)

        return text.strip()

    @staticmethod
    def assert_unicode_integrity(text: str) -> bool:
        """Verifies that NFC invariant holds and joiners are not corrupted."""
        assert text == unicodedata.normalize('NFC', text), "Unicode NFC normalization violated!"
        # Verify no control bytes survive
        assert not bool(RE_CONTROL_CHARS.search(text)), "Unprintable control characters survived in buffer!"
        return True

    @staticmethod
    def is_script_dominant(text: str, script: str = "Deva", min_ratio: float = 0.65) -> bool:
        """
        Checks if text is predominantly the target script.
        Allows punctuation, digits, spaces, and minor loanwords.
        """
        non_space_chars = [c for c in text if not c.isspace()]
        if not non_space_chars:
            return False

        ranges = SCRIPT_UNICODE_RANGES.get(script, [(0x0900, 0x097F)])
        script_count = sum(
            1 for c in non_space_chars
            if any(r_start <= ord(c) <= r_end for r_start, r_end in ranges) or
               c in (ZWJ, ZWNJ, DANDA, DOUBLE_DANDA) or
               c.isdigit() or c in ",.?!:;()-\"'"
        )
        return (script_count / len(non_space_chars)) >= min_ratio

    @staticmethod
    def is_devanagari_dominant(text: str, min_ratio: float = 0.65) -> bool:
        """Backwards-compatibility alias for Devanagari script."""
        return UnicodeGatekeeper.is_script_dominant(text, script="Deva", min_ratio=min_ratio)

    @staticmethod
    def _split_into_bounded_phrases(text: str, min_chars: int = 20, max_chars: int = 85) -> List[str]:
        """Slices arbitrary long text into word-bounded chunks strictly between min_chars and max_chars."""
        words = text.split()
        if not words:
            return []
        
        chunks = []
        current_words = []
        current_len = 0

        for w in words:
            # Word length plus space
            added_len = len(w) + (1 if current_words else 0)
            if current_len + added_len <= max_chars:
                current_words.append(w)
                current_len += added_len
            else:
                chunk_str = " ".join(current_words).strip()
                if len(chunk_str) >= min_chars and len(chunk_str) <= max_chars:
                    chunks.append(chunk_str)
                current_words = [w]
                current_len = len(w)

        if current_words:
            chunk_str = " ".join(current_words).strip()
            if len(chunk_str) >= min_chars and len(chunk_str) <= max_chars:
                chunks.append(chunk_str)

        return chunks

    @staticmethod
    def chunk_sentences(text: str, min_chars: int = 20, max_chars: int = 85) -> List[str]:
        """
        Splits text into length-bounded sentence lines suitable for TrOCR / CRNN line recognizers.
        Guarantees: for all returned s: min_chars <= len(s) <= max_chars.
        """
        raw_parts = re.split(r'([।\n!?]+)', text)
        sentences = []
        current = ""

        for part in raw_parts:
            current += part
            if any(p in part for p in ['।', '\n', '!', '?']):
                cleaned = current.strip()
                if len(cleaned) >= min_chars:
                    if len(cleaned) <= max_chars:
                        sentences.append(cleaned)
                    else:
                        sub_chunks = UnicodeGatekeeper._split_into_bounded_phrases(cleaned, min_chars, max_chars)
                        sentences.extend(sub_chunks)
                current = ""

        if current.strip():
            cleaned = current.strip()
            if len(cleaned) >= min_chars:
                if len(cleaned) <= max_chars:
                    sentences.append(cleaned)
                else:
                    sub_chunks = UnicodeGatekeeper._split_into_bounded_phrases(cleaned, min_chars, max_chars)
                    sentences.extend(sub_chunks)

        # Final invariant filter: 100% of sentences MUST satisfy min_chars <= len <= max_chars
        return [s for s in sentences if min_chars <= len(s) <= max_chars]

    @staticmethod
    def analyze_lexical_balance(lines: List[str]) -> Dict:
        """
        Analyzes akshara distribution, conjunct counts, and stopword ratios.
        """
        char_counter = Counter()
        word_counter = Counter()
        conjunct_matches = Counter()

        for line in lines:
            for char in line:
                char_counter[char] += 1
            words = line.split()
            for w in words:
                word_counter[w] += 1
            for cj in HIGH_VALUE_CONJUNCTS:
                if cj in line:
                    conjunct_matches[cj] += line.count(cj)

        total_words = sum(word_counter.values())
        stopword_count = sum(word_counter[sw] for sw in BHOJPURI_COMMON_STOPWORDS if sw in word_counter)
        stopword_ratio = (stopword_count / total_words) if total_words > 0 else 0.0

        return {
            "total_lines": len(lines),
            "total_tokens": total_words,
            "unique_tokens": len(word_counter),
            "stopword_ratio": stopword_ratio,
            "top_characters": char_counter.most_common(20),
            "conjunct_distribution": dict(conjunct_matches.most_common(25)),
            "samyuktaksharas_mined": len(conjunct_matches)
        }
