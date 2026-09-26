"""
Master Multi-Tier Synthetic OCR Generator for Maithili (mai_Deva)
Inherits from HindiMultiTierOCRGenerator to reuse production-hardened CTL shaping,
baseline anchoring, diacritic ownership, and multi-tier layout engines.
"""

import sys
import os
import io
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageDraw

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / "augmenter"))

from hindi_multi_tier_engine import HindiMultiTierOCRGenerator


class MaithiliMultiTierOCRGenerator(HindiMultiTierOCRGenerator):
    """
    Maithili (mai_Deva) Synthetic OCR Engine.
    Configured specifically for Maithili typography, Mithila cultural archetypes, and linguistic assets.
    """

    def __init__(self, fonts_dir: Path, processed_data_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.data_dir = Path(processed_data_dir)

        # Import dependencies
        from harfbuzz_shaper import FontRegistry, HarfBuzzTokenRenderer
        from degradation_engine import IndianDegradationEngine

        print("[Agent-Shaper] Initializing FontRegistry for Maithili (Devanagari)...")
        self.registry = FontRegistry(self.fonts_dir)
        self.renderer = HarfBuzzTokenRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)

        # Load Maithili linguistic assets
        words_path = self.data_dir / "maithili_words.jsonl"
        lines_path = self.data_dir / "maithili_lines.jsonl"
        blocks_path = self.data_dir / "maithili_blocks.jsonl"

        print(f"[Agent-Shaper] Loading linguistic assets from {self.data_dir.name}...")
        with open(words_path, "r", encoding="utf-8") as f:
            self.words_data = [json.loads(line) for line in f]
        with open(lines_path, "r", encoding="utf-8") as f:
            self.lines_data = [json.loads(line) for line in f]
        with open(blocks_path, "r", encoding="utf-8") as f:
            self.blocks_data = [json.loads(line) for line in f]

        random.shuffle(self.lines_data)
        random.shuffle(self.words_data)
        random.shuffle(self.blocks_data)

        self.font_names = list(self.registry.hb_fonts.keys())
        self.line_cursor = 0
        self.lang_code = "mai"
        self.script_code = "Deva"
        print(f"[Agent-Shaper] Loaded {len(self.lines_data):,} Maithili lines, {len(self.words_data):,} words, {len(self.blocks_data):,} blocks.")
        print(f"[Agent-Shaper] Available Devanagari fonts: {len(self.font_names)}")

    def generate_word_sample(self, word_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_word_sample(word_entry, is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        return img, meta

    def generate_line_sample(self, line_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_line_sample(line_entry, is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        return img, meta

    def generate_paragraph_sample(self, block_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_paragraph_sample(block_entry, is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        return img, meta

    # =========================================================================
    # TIER 1: MAITHILI AUTHENTIC ARCHETYPES
    # =========================================================================
    def generate_literary_magazine_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (252, 249, 242))
        draw = ImageDraw.Draw(canvas)

        draw.rectangle([(40, 40), (page_w - 40, page_h - 40)], outline=(120, 90, 40) if not is_clean else (0, 0, 0), width=2)
        draw.rectangle([(46, 46), (page_w - 46, page_h - 46)], outline=(180, 150, 90) if not is_clean else (100, 100, 100), width=1)

        titles = ["समकालीन मैथिली साहित्य", "मिथिला भारती त्रैमासिक", "मैथिली काव्य धारा", "विदेह साहित्य सम्हार"]
        title = random.choice(titles)
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", title, (page_w // 2 - 220, 65), font_size=36, ink_rgb=(40, 20, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "वर्ष २८ • अंक ३ • मिथिला विशेषांक | मूल्य: ₹ ३०.००", (page_w // 2 - 200, 115), font_size=18, ink_rgb=(80, 70, 60))
        draw.line([(70, 145), (page_w - 70, 145)], fill=(120, 90, 40), width=2)

        self.renderer.paste_text(canvas, "YatraOne-Regular.ttf", "विशेष काव्य स्तम्भ: अमर विद्यापति रचनावली", (80, 165), font_size=24, ink_rgb=(20, 20, 20))
        draw.line([(80, 200), (480, 200)], fill=(160, 120, 60), width=1)

        verse_lines = self.get_next_lines(8)
        y_cursor = 225
        for idx, item in enumerate(verse_lines):
            try:
                line_txt = f"✦ {item['text']} ✦" if idx % 2 == 0 else f"    {item['text']}"
                self.renderer.paste_text(canvas, "Tillana-Regular.ttf" if idx % 2 == 0 else "Sahitya-Regular.ttf",
                                         line_txt, (120, y_cursor), font_size=22, ink_rgb=(30, 20, 15))
                y_cursor += 36
            except Exception:
                continue

        draw.line([(100, y_cursor + 15), (page_w - 100, y_cursor + 15)], fill=(180, 150, 100), width=1)
        y_cursor += 35
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "आलोचनात्मक विमर्श: मैथिली भाषा एवं संस्कृति", (80, y_cursor), font_size=24, ink_rgb=(10, 10, 10))
        y_cursor += 40

        col_w = (page_w - 160 - 30) // 2
        col1_x = 80
        col2_x = col1_x + col_w + 30
        bottom_limit = page_h - 100

        y_c1 = y_cursor
        while y_c1 < bottom_limit - 40:
            sentence = self.get_next_lines(1)[0]["text"]
            words = sentence.split()
            buf = ""
            for w in words:
                test_buf = (buf + " " + w).strip()
                try:
                    w_px = self.renderer.get_text_width("NotoSerifDevanagari.ttf", test_buf, font_size=20)
                except Exception:
                    w_px = len(test_buf) * 12
                if w_px > col_w:
                    if buf:
                        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (col1_x, y_c1), font_size=20, ink_rgb=(15, 15, 15))
                        y_c1 += 28
                    buf = w
                else:
                    buf = test_buf
            if buf and y_c1 < bottom_limit - 30:
                self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (col1_x, y_c1), font_size=20, ink_rgb=(15, 15, 15))
                y_c1 += 34

        y_c2 = y_cursor
        while y_c2 < bottom_limit - 40:
            sentence = self.get_next_lines(1)[0]["text"]
            words = sentence.split()
            buf = ""
            for w in words:
                test_buf = (buf + " " + w).strip()
                try:
                    w_px = self.renderer.get_text_width("NotoSerifDevanagari.ttf", test_buf, font_size=20)
                except Exception:
                    w_px = len(test_buf) * 12
                if w_px > col_w:
                    if buf:
                        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (col2_x, y_c2), font_size=20, ink_rgb=(15, 15, 15))
                        y_c2 += 28
                    buf = w
                else:
                    buf = test_buf
            if buf and y_c2 < bottom_limit - 30:
                self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (col2_x, y_c2), font_size=20, ink_rgb=(15, 15, 15))
                y_c2 += 34

        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "पृष्ठ संख्या : १४२", (page_w // 2 - 50, page_h - 60), font_size=16, ink_rgb=(100, 100, 100))

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        return final_img, {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_A_Sahityik_Patrika",
            "title": title,
            "applied_augmentations": applied_ops,
            "is_clean": is_clean,
            "lang": self.lang_code,
            "script": self.script_code
        }

    def generate_official_gazette_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_official_gazette_page(is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        return img, meta

    def generate_newspaper_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_newspaper_page(is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        return img, meta

    def generate_judicial_order_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_judicial_order_page(is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        return img, meta

    def generate_full_page_sample(self, archetype_choice: Optional[str] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        archetypes = [
            "Archetype_A_Sahityik_Patrika",
            "Archetype_B_Official_Gazette",
            "Archetype_C_Newspaper_Spread",
            "Archetype_D_Judicial_Order"
        ]
        chosen = archetype_choice if archetype_choice in archetypes else random.choice(archetypes)
        if chosen == "Archetype_A_Sahityik_Patrika":
            return self.generate_literary_magazine_page(is_clean)
        elif chosen == "Archetype_B_Official_Gazette":
            return self.generate_official_gazette_page(is_clean)
        elif chosen == "Archetype_C_Newspaper_Spread":
            return self.generate_newspaper_page(is_clean)
        else:
            return self.generate_judicial_order_page(is_clean)
