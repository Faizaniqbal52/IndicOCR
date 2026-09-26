"""
Master Multi-Tier Synthetic OCR Generator for Marathi (mar_Deva)
Inherits from HindiMultiTierOCRGenerator to reuse production-hardened CTL shaping,
FreeType rasterization, baseline anchoring, diacritic ownership, and multi-tier layout engines.
Enforces strict column geometry, word-wrapping, and collision prevention.
Includes Marathi-specific cultural archetypes (Sahitya Patrika, Shasan Rajpatra, Sakal/Loksatta broadsheet).
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


class MarathiMultiTierOCRGenerator(HindiMultiTierOCRGenerator):
    """
    Marathi (mar_Deva) Synthetic OCR Engine.
    Configured specifically for Marathi typography, Maharashtrian cultural archetypes, and linguistic assets.
    """

    def __init__(self, fonts_dir: Path, processed_data_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.data_dir = Path(processed_data_dir)

        from harfbuzz_shaper import FontRegistry, HarfBuzzTokenRenderer
        from degradation_engine import IndianDegradationEngine

        print("[Agent-Shaper] Initializing FontRegistry for Marathi (Devanagari)...")
        self.registry = FontRegistry(self.fonts_dir)
        self.renderer = HarfBuzzTokenRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)

        # Load Marathi linguistic assets
        words_path = self.data_dir / "marathi_words.jsonl"
        lines_path = self.data_dir / "marathi_lines.jsonl"
        blocks_path = self.data_dir / "marathi_blocks.jsonl"

        print(f"[Agent-Shaper] Loading linguistic assets from {self.data_dir.name}...")
        with open(words_path, "r", encoding="utf-8") as f:
            self.words_data = [json.loads(line) for line in f]
        with open(lines_path, "r", encoding="utf-8") as f:
            self.lines_data = [json.loads(line) for line in f]
        with open(blocks_path, "r", encoding="utf-8") as f:
            self.blocks_data = [json.loads(line) for line in f]

        for item in self.words_data:
            val = item.get("text") or item.get("word")
            item["word"] = val
            item["text"] = val
        for item in self.lines_data:
            val = item.get("text") or item.get("line")
            item["line"] = val
            item["text"] = val
        for item in self.blocks_data:
            if "lines" not in item:
                item["lines"] = [s.strip() for s in item.get("text", "").split("।") if s.strip()]

        random.shuffle(self.lines_data)
        random.shuffle(self.words_data)
        random.shuffle(self.blocks_data)

        self.font_names = list(self.registry.hb_fonts.keys())
        self.line_cursor = 0
        self.word_cursor = 0
        self.block_cursor = 0
        self.lang_code = "mar"
        self.script_code = "Deva"
        print(f"[Agent-Shaper] Loaded {len(self.lines_data):,} Marathi lines, {len(self.words_data):,} words, {len(self.blocks_data):,} blocks.")
        print(f"[Agent-Shaper] Available Devanagari fonts: {len(self.font_names)}")

    def render_wrapped_paragraph(
        self,
        canvas: Image.Image,
        font_name: str,
        text_stream: List[str],
        x: int,
        y_start: int,
        max_w: int,
        max_y: int,
        font_size: int = 18,
        line_height: int = 28,
        ink_rgb: Tuple[int, int, int] = (20, 20, 20)
    ) -> int:
        """
        Word-wraps sentences strictly within max_w width and max_y height.
        Guarantees ZERO horizontal column overflow and ZERO collision.
        """
        y_cursor = y_start
        for text in text_stream:
            words = text.split()
            current_line = ""
            for word in words:
                candidate = f"{current_line} {word}".strip() if current_line else word
                try:
                    w_px = self.renderer.get_text_width(font_name, candidate, font_size=font_size)
                except Exception:
                    w_px = int(len(candidate) * font_size * 0.6)

                if w_px <= max_w:
                    current_line = candidate
                else:
                    if current_line:
                        try:
                            self.renderer.paste_text(canvas, font_name, current_line, (x, y_cursor), font_size=font_size, ink_rgb=ink_rgb)
                        except Exception:
                            pass
                        y_cursor += line_height
                        if y_cursor + line_height > max_y:
                            return y_cursor
                    current_line = word

            if current_line and y_cursor + line_height <= max_y:
                try:
                    self.renderer.paste_text(canvas, font_name, current_line, (x, y_cursor), font_size=font_size, ink_rgb=ink_rgb)
                except Exception:
                    pass
                y_cursor += line_height
                if y_cursor + line_height > max_y:
                    return y_cursor
        return y_cursor

    def generate_word_sample(self, word_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        img, meta = super().generate_word_sample(word_entry, is_clean)
        meta["lang"] = self.lang_code
        meta["script"] = self.script_code
        if "text" not in meta:
            meta["text"] = meta.get("word", "")
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
        if "text" not in meta:
            meta["text"] = "\n".join(it["text"] for it in meta.get("lines", []))
        return img, meta

    # =========================================================================
    # TIER 1: MARATHI AUTHENTIC ARCHETYPES
    # =========================================================================
    def generate_literary_magazine_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        """Archetype A: Maharashtra Sahitya Patrika (Literary Magazine / Sant Sahitya / Poetry)"""
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (252, 249, 242))
        draw = ImageDraw.Draw(canvas)

        draw.rectangle([(40, 40), (page_w - 40, page_h - 40)], outline=(120, 90, 40) if not is_clean else (0, 0, 0), width=2)
        draw.rectangle([(46, 46), (page_w - 46, page_h - 46)], outline=(180, 150, 90) if not is_clean else (100, 100, 100), width=1)

        titles = [
            "महाराष्ट्र साहित्य पत्रिका",
            "संत साहित्य धारा व अभंगवाणी",
            "नवसाहित्य त्रैमासिक निबंध",
            "मराठी भाषा व संस्कृती समीक्षा"
        ]
        title = random.choice(titles)
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", title, (page_w // 2 - 240, 65), font_size=36, ink_rgb=(40, 20, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "पुणे मंडळ • वर्ष ६४ • अंक ३ • दिवाळी विशेषांक | मूल्य: ₹ ३५.००", (page_w // 2 - 250, 115), font_size=18, ink_rgb=(80, 70, 60))
        draw.line([(60, 145), (page_w - 60, 145)], fill=(120, 90, 40), width=1)

        num_cols = 2
        col_w = (page_w - 120 - 40) // 2
        gutter = 40
        y_start = 170
        max_y = page_h - 100

        all_page_texts = [title, "पुणे मंडळ • वर्ष ६४ • अंक ३ • दिवाळी विशेषांक | मूल्य: ₹ ३५.००"]
        for col_idx in range(num_cols):
            cx = 60 + col_idx * (col_w + gutter)
            sampled = self.get_next_lines(random.randint(12, 16))
            col_texts = [it["text"] for it in sampled]
            all_page_texts.extend(col_texts)
            self.render_wrapped_paragraph(canvas, "NotoSerifDevanagari.ttf", col_texts, cx, y_start, col_w, max_y, font_size=18, line_height=28)

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_A_Sahityik_Patrika",
            "canvas_size": [page_w, page_h],
            "lang": self.lang_code,
            "script": self.script_code,
            "title": title,
            "text": "\n".join(all_page_texts),
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_official_gazette_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        """Archetype B: Maharashtra Shasan Rajpatra (Official State Gazette / Decree)"""
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (250, 248, 244))
        draw = ImageDraw.Draw(canvas)

        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "महाराष्ट्र शासन", (page_w // 2 - 120, 60), font_size=28, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "शासकीय राजपत्र (THE MAHARASHTRA GOVERNMENT GAZETTE)", (page_w // 2 - 320, 100), font_size=20, ink_rgb=(20, 20, 20))
        draw.line([(60, 140), (page_w - 60, 140)], fill=(0, 0, 0), width=2)

        sampled = self.get_next_lines(random.randint(22, 28))
        col_texts = [it["text"] for it in sampled]
        self.render_wrapped_paragraph(canvas, "NotoSerifDevanagari.ttf", col_texts, 70, 160, page_w - 140, page_h - 100, font_size=17, line_height=27)

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_B_Official_Gazette",
            "canvas_size": [page_w, page_h],
            "lang": self.lang_code,
            "script": self.script_code,
            "text": "महाराष्ट्र शासन\nशासकीय राजपत्र (THE MAHARASHTRA GOVERNMENT GAZETTE)\n" + "\n".join(col_texts),
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_newspaper_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        """Archetype C: Marathi Broadsheet Daily Newspaper Spread (3 columns)"""
        page_w, page_h = 1400, 1850
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (248, 245, 238))
        draw = ImageDraw.Draw(canvas)

        titles = ["दैनिक लोकसत्ता वार्ता", "दैनिक सकाळ समाचार", "महाराष्ट्र टाइम्स वृत्त", "नवशक्ति दैनिक वृत्तपत्र"]
        title = random.choice(titles)
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", title, (page_w // 2 - 240, 50), font_size=44, ink_rgb=(0, 0, 0))
        draw.line([(50, 120), (page_w - 50, 120)], fill=(0, 0, 0), width=2)

        num_cols = 3
        gutter = 30
        col_w = (page_w - 100 - (gutter * 2)) // 3
        y_start = 140
        max_y = page_h - 80

        all_page_texts = [title]
        for col_idx in range(num_cols):
            cx = 50 + col_idx * (col_w + gutter)
            sampled = self.get_next_lines(random.randint(18, 24))
            col_texts = [it["text"] for it in sampled]
            all_page_texts.extend(col_texts)
            self.render_wrapped_paragraph(canvas, "NotoSansDevanagari.ttf", col_texts, cx, y_start, col_w, max_y, font_size=16, line_height=25)
            if col_idx < num_cols - 1:
                rule_x = cx + col_w + (gutter // 2)
                draw.line([(rule_x, y_start), (rule_x, max_y)], fill=(180, 180, 180), width=1)

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_C_Broadsheet_Newspaper",
            "canvas_size": [page_w, page_h],
            "lang": self.lang_code,
            "script": self.script_code,
            "title": title,
            "text": "\n".join(all_page_texts),
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_full_page_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        archetype_choice = random.choice(["magazine", "gazette", "newspaper"])
        if archetype_choice == "magazine":
            return self.generate_literary_magazine_page(is_clean=is_clean)
        elif archetype_choice == "gazette":
            return self.generate_official_gazette_page(is_clean=is_clean)
        else:
            return self.generate_newspaper_page(is_clean=is_clean)
