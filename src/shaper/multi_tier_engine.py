"""
Multi-Tier Synthetic OCR Generator for Bhojpuri (Compliant & Production-Hardened)
Renders data across all 4 Granularity Tiers:
1. Tier 4: Words & Isolated Samyuktaksharas
2. Tier 3: Lines (TrOCR / CRNN Sequence Recognizers)
3. Tier 2: Paragraphs & Multi-Line Text Blocks
4. Tier 1: Full-Page Documents:
   - Archetype A: Literary Society & Cultural Convention Notice (Non-Govt / Compliant Public Notice, Ruled Table, Society Seal)
   - Archetype B: Multi-Column Regional Newspaper Spread (Full 3-column text fill, Headlines, Byline, Photo Box & Caption)
"""

import sys
import os
import io
import json
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r"c:\OCR - All\src\shaper")
sys.path.append(r"c:\OCR - All\src\augmenter")

from harfbuzz_shaper import FontRegistry, HarfBuzzTokenRenderer
from degradation_engine import IndianDegradationEngine
from ownership_gate import DiacriticOwnershipGate


class MultiTierOCRGenerator:
    """Generates synthetic OCR instances across all 4 Granularity Tiers."""

    def __init__(self, fonts_dir: Path, processed_data_dir: Path):
        self.registry = FontRegistry(fonts_dir)
        self.renderer = HarfBuzzTokenRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)
        self.data_dir = Path(processed_data_dir)

        # Load linguistic assets
        with open(self.data_dir / "bhojpuri_words.jsonl", "r", encoding="utf-8") as f:
            self.words_data = [json.loads(line) for line in f]
        with open(self.data_dir / "bhojpuri_lines.jsonl", "r", encoding="utf-8") as f:
            self.lines_data = [json.loads(line) for line in f]
        with open(self.data_dir / "bhojpuri_blocks.jsonl", "r", encoding="utf-8") as f:
            self.blocks_data = [json.loads(line) for line in f]

        random.shuffle(self.lines_data)
        random.shuffle(self.words_data)
        random.shuffle(self.blocks_data)

        self.font_names = list(self.registry.hb_fonts.keys())
        self.line_cursor = 0

    def get_next_lines(self, count: int) -> List[Dict[str, Any]]:
        """Consumes a sliding batch of lines from the 50,000-line corpus without repeating."""
        n = len(self.lines_data)
        if self.line_cursor + count > n:
            self.line_cursor = 0
            random.shuffle(self.lines_data)

        batch = self.lines_data[self.line_cursor:self.line_cursor + count]
        self.line_cursor += count
        return batch

    # =========================================================================
    # TIER 4: WORDS & ISOLATED CONJUNCTS
    # =========================================================================
    def generate_word_sample(self, word_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        for _ in range(10):
            entry = word_entry if word_entry is not None else random.choice(self.words_data)
            word = entry["word"]
            supporting_fonts = self.registry.get_supporting_fonts(word)
            if supporting_fonts:
                break
            word_entry = None  # Resample if given entry has no supporting fonts

        font_name = random.choice(supporting_fonts) if supporting_fonts else "NotoSansDevanagari.ttf"
        font_size = random.choice([32, 38, 44, 48])

        clean_img, ann = self.renderer.render_line(font_name, word, font_size=font_size)
        if is_clean:
            final_img = clean_img
            applied_ops = ["pristine_digital_scan"]
            updated_bbox = ann["bbox"]
        else:
            final_img, applied_ops, updated_bbox = self.augmenter.augment_pipeline(clean_img, bbox=ann["bbox"])

        metadata = {
            "tier": "Tier_4_Word",
            "word": word,
            "word_type": entry.get("type", "lexical"),
            "font": font_name,
            "font_size": font_size,
            "bbox": updated_bbox,
            "canvas_size": ann["canvas_size"],
            "ascender_zone": ann["ascender_zone"],
            "descender_zone": ann["descender_zone"],
            "shaped_glyphs": ann.get("shaped_glyphs", []),
            "applied_augmentations": applied_ops,
            "is_clean": is_clean
        }
        return final_img, metadata

    # =========================================================================
    # TIER 3: TEXT LINES (TrOCR / Sequence Recognizers)
    # =========================================================================
    def generate_line_sample(self, line_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        for _ in range(10):
            entry = line_entry if line_entry is not None else self.get_next_lines(1)[0]
            text = entry["text"]
            supporting_fonts = self.registry.get_supporting_fonts(text)
            if supporting_fonts:
                break
            line_entry = None  # Resample if given entry has no supporting fonts

        font_name = random.choice(supporting_fonts) if supporting_fonts else "NotoSerifDevanagari.ttf"
        font_size = random.choice([26, 30, 34, 38])

        clean_img, ann = self.renderer.render_line(font_name, text, font_size=font_size)
        if is_clean:
            final_img = clean_img
            applied_ops = ["pristine_digital_scan"]
            updated_bbox = ann["bbox"]
        else:
            final_img, applied_ops, updated_bbox = self.augmenter.augment_pipeline(clean_img, bbox=ann["bbox"])

        metadata = {
            "tier": "Tier_3_Line",
            "text": text,
            "font": font_name,
            "font_size": font_size,
            "bbox": updated_bbox,
            "canvas_size": ann["canvas_size"],
            "ascender_zone": ann["ascender_zone"],
            "descender_zone": ann["descender_zone"],
            "shaped_glyphs": ann.get("shaped_glyphs", []),
            "applied_augmentations": applied_ops,
            "is_clean": is_clean
        }
        return final_img, metadata

    # =========================================================================
    # TIER 2: PARAGRAPHS & MULTI-LINE TEXT BLOCKS (Pure HarfBuzz + FreeType)
    # =========================================================================
    def generate_paragraph_sample(self, block_entry: Optional[Dict[str, Any]] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        for _ in range(10):
            if block_entry is None:
                sampled = self.get_next_lines(random.randint(3, 6))
                lines = [it["text"] for it in sampled]
                block_id = f"dyn_block_{random.randint(10000, 99999)}"
            else:
                lines = block_entry["lines"]
                block_id = block_entry.get("block_id", "block_0")

            combined_text = " ".join(lines)
            supporting_fonts = self.registry.get_supporting_fonts(combined_text)
            if supporting_fonts:
                break
            block_entry = None  # Resample if given entry has no supporting fonts

        font_name = random.choice(supporting_fonts) if supporting_fonts else "NotoSerifDevanagari.ttf"
        font_size = random.choice([26, 30, 34])

        rendered_lines = []
        max_w = 0
        line_height = int(font_size * 1.55)

        for l in lines:
            img_rgba, _ = self.renderer.render_text_rgba(font_name, l, font_size=font_size)
            rendered_lines.append((l, img_rgba))
            max_w = max(max_w, img_rgba.width)

        pad_x = 25
        pad_y = 25
        canvas_w = max_w + (pad_x * 2)
        canvas_h = (len(lines) * line_height) + (pad_y * 2)

        bg_color = (255, 255, 255) if is_clean else (250, 248, 243)
        img = Image.new("RGB", (canvas_w, canvas_h), bg_color)

        y_cursor = pad_y
        line_annotations = []
        for idx, (l, line_img) in enumerate(rendered_lines):
            img.paste(line_img, (pad_x, y_cursor), line_img)
            line_annotations.append({
                "line_index": idx,
                "text": l,
                "bbox": [pad_x, y_cursor, pad_x + line_img.width, y_cursor + line_img.height]
            })
            y_cursor += line_height

        if is_clean:
            final_img = img
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(img)

        metadata = {
            "tier": "Tier_2_Paragraph",
            "block_id": block_id,
            "font": font_name,
            "font_size": font_size,
            "canvas_size": [canvas_w, canvas_h],
            "lines": line_annotations,
            "applied_augmentations": applied_ops,
            "is_clean": is_clean
        }
        return final_img, metadata

    # =========================================================================
    # TIER 1: FULL PAGES (ARCHETYPE A: CULTURAL SOCIETY / PUBLIC NOTICE)
    # [Dynamic Line-Stitching: Zero Paragraph Block Repetition]
    # =========================================================================
    def generate_public_notice_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (252, 250, 245))
        draw = ImageDraw.Draw(canvas)

        page_elements = []

        # 1. Literary Society Header (Pure HarfBuzz)
        cx = page_w // 2
        society_titles = [
            "अखिल भारतीय भोजपुरी साहित्य परिषद",
            "पूर्वांचल लोक कला आ साहित्य अकादमी",
            "भोजपुरी भाषा संस्थान एवं शोध केन्द्र",
            "काशी-मगध भोजपुरी सांस्कृतिक मंच"
        ]
        s_title = random.choice(society_titles)
        ref_num = f"भोस/{random.randint(2024, 2026)}/अधि-{random.randint(10, 99)}"
        reg_num = f"{random.randint(100, 999)}/{random.randint(2018, 2025)}"

        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", s_title, (cx - 260, 50), font_size=30, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", f"केन्द्रीय कार्यालय, राजेंद्र नगर, पटना | पंजीकृत संख्या: {reg_num}", (cx - 240, 95), font_size=20, ink_rgb=(60, 60, 60))
        draw.line([(80, 135), (page_w - 80, 135)], fill=(0, 0, 0), width=2)
        draw.line([(80, 139), (page_w - 80, 139)], fill=(0, 0, 0), width=1)

        # 2. Reference & Date
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", f"विज्ञप्ति संख्या: {ref_num}", (90, 160), font_size=22, ink_rgb=(20, 20, 20))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "दिनांक: 09 सितम्बर 2026", (page_w - 320, 160), font_size=22, ink_rgb=(20, 20, 20))

        # 3. Subject Line (Dynamic)
        subject_line = random.choice([
            "विषय: 42वां वार्षिक भोजपुरी साहित्य सम्मेलन आ सम्मान समारोह के संबंध में।",
            "विषय: लोकगीत आ बिदेसिया नाट्य महोत्सव के आयोजन आ प्रतिनिधि बैठक सूचना।",
            "विषय: भोजपुरी भाषा के मानकीकरण आ शब्दकोश संकलन कार्यशाला के संबंध में।"
        ])
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", subject_line, (90, 205), font_size=26, ink_rgb=(15, 15, 15))
        draw.line([(90, 245), (960, 245)], fill=(80, 80, 80), width=1)

        # 4. Dynamic Body Paragraphs (using freshly consumed lines)
        y_cursor = 270
        body_lines = self.get_next_lines(8)
        for item in body_lines:
            try:
                b = self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", item["text"], (90, y_cursor), font_size=22, ink_rgb=(25, 25, 25))
                page_elements.append({"type": "body_line", "text": item["text"], "bbox": list(b)})
                y_cursor += 38
            except Exception:
                continue

        # 5. Ruled Schedule & Agenda Table
        y_cursor += 25
        table_x = 90
        table_w = page_w - 180
        table_top = y_cursor
        row_h = 44

        # Table Header
        draw.rectangle([(table_x, table_top), (table_x + table_w, table_top + row_h)], fill=(235, 230, 220), outline=(0, 0, 0), width=1)
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "सत्र", (table_x + 15, table_top + 10), font_size=22, ink_rgb=(0, 0, 0))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "कार्यक्रम / परिचर्चा के विषय", (table_x + 90, table_top + 10), font_size=22, ink_rgb=(0, 0, 0))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "वक्ता / अध्यक्ष", (table_x + 650, table_top + 10), font_size=22, ink_rgb=(0, 0, 0))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "समय", (table_x + 880, table_top + 10), font_size=22, ink_rgb=(0, 0, 0))

        # Table Rows
        table_rows = [
            ("प्रथम", "उद्घाटन सत्र: भोजपुरी भाषा के ऐतिहासिक विकास", "डॉ. रामेश्वर सिंह", "पूर्वाह्न 10:00"),
            ("द्वितीय", "बिदेसिया परंपरा आ भिखारी ठाकुर के नाटक चर्चा", "प्रो. शंभुनाथ मिश्र", "दोपहर 12:30"),
            ("तृतीय", "कवि सम्मेलन आ युवा रचनाकार सम्मान", "कवि मंडल सदस्य", "अपराह्न 03:00")
        ]

        for r_idx, (c1, c2, c3, c4) in enumerate(table_rows):
            ry = table_top + ((r_idx + 1) * row_h)
            draw.rectangle([(table_x, ry), (table_x + table_w, ry + row_h)], outline=(0, 0, 0), width=1)
            self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", c1, (table_x + 20, ry + 10), font_size=20, ink_rgb=(20, 20, 20))
            self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", c2, (table_x + 90, ry + 10), font_size=20, ink_rgb=(20, 20, 20))
            self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", c3, (table_x + 650, ry + 10), font_size=20, ink_rgb=(20, 20, 20))
            self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", c4, (table_x + 890, ry + 10), font_size=20, ink_rgb=(20, 20, 20))

        # 6. Concluding Notes (Freshly consumed)
        y_cursor = table_top + (len(table_rows) + 1) * row_h + 35
        closing_lines = self.get_next_lines(3)
        for item in closing_lines:
            try:
                self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", item["text"], (90, y_cursor), font_size=22, ink_rgb=(25, 25, 25))
                y_cursor += 36
            except Exception:
                continue

        # 7. Signature Block
        y_cursor += 45
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", "हस्ताक्षर / Authorized Signatory", (page_w - 380, y_cursor), font_size=20, ink_rgb=(100, 100, 100))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "महासचिव / General Secretary", (page_w - 380, y_cursor + 35), font_size=22, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", s_title, (page_w - 380, y_cursor + 65), font_size=20, ink_rgb=(30, 30, 30))

        # 8. Physical Degradation
        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            img_bgr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
            img_bgr = self.augmenter.apply_official_stamp(img_bgr)
            img_bgr = self.augmenter.apply_paper_substrate(img_bgr, paper_type="raddi")
            img_bgr = self.augmenter.apply_shadow_gradient(img_bgr)
            img_bgr, _ = self.augmenter.apply_subtle_skew(img_bgr, max_angle_deg=0.8)
            final_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            applied_ops = ["society_stamp", "raddi_paper", "shadow_gradient", "subtle_skew"]

        metadata = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Literary_Society_Public_Notice",
            "canvas_size": [page_w, page_h],
            "language": "bho",
            "script": "Deva",
            "applied_augmentations": applied_ops,
            "is_clean": is_clean
        }
        return final_img, metadata

    # =========================================================================
    # TIER 1: FULL PAGES (ARCHETYPE B: 3-COLUMN REGIONAL NEWSPAPER SPREAD)
    # [Dynamic Word-Wrapping & Continuous Stream Fill]
    # =========================================================================
    def generate_newspaper_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (250, 248, 242))
        draw = ImageDraw.Draw(canvas)

        # 1. Masthead
        paper_names = ["भोजपुरी दैनिक समाचार", "पूर्वांचल दर्पण", "गंगा-गंडक पत्रिका", "बिदेसिया जनसंदेश"]
        p_name = random.choice(paper_names)
        vol_issue = f"वर्ष {random.randint(5, 25)}, अंक {random.randint(100, 350)}  |  मूल्य: ₹ ५.००"

        self.renderer.paste_text(canvas, "YatraOne-Regular.ttf", p_name, (page_w // 2 - 200, 35), font_size=46, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", vol_issue, (page_w - 300, 95), font_size=16, ink_rgb=(50, 50, 50))
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", "पटना • आरा • बक्सर • वाराणसी • छपरा", (60, 95), font_size=16, ink_rgb=(50, 50, 50))
        draw.line([(60, 125), (page_w - 60, 125)], fill=(0, 0, 0), width=3)

        # 2. Main Banner Headline (Drawn dynamically)
        headline_line = self.get_next_lines(1)[0]["text"]
        subheadline_line = self.get_next_lines(1)[0]["text"]
        for _ in range(10):
            if self.registry.get_supporting_fonts(headline_line[:65]):
                break
            headline_line = self.get_next_lines(1)[0]["text"]

        for _ in range(10):
            if self.registry.get_supporting_fonts(subheadline_line[:75]):
                break
            subheadline_line = self.get_next_lines(1)[0]["text"]

        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", headline_line[:65], (60, 140), font_size=28, ink_rgb=(0, 0, 0))
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", subheadline_line[:75], (60, 185), font_size=20, ink_rgb=(40, 40, 40))
        draw.line([(60, 220), (page_w - 60, 220)], fill=(80, 80, 80), width=1)

        # 3. 3-Column Geometry
        margin_x = 60
        gutter = 28
        col_w = (page_w - (2 * margin_x) - (2 * gutter)) // 3
        col_top = 240
        col_bottom = 1700
        line_pitch = 28

        for c_idx in range(3):
            col_x = margin_x + (c_idx * (col_w + gutter))
            y_curr = col_top

            # Section Header badge
            sec_name = ["विशेष रपट (Special Report)", "सांस्कृतिक मंच (Culture)", "साहित्य चर्चा (Literature)"][c_idx]
            draw.rectangle([(col_x, y_curr), (col_x + col_w, y_curr + 30)], fill=(225, 222, 215))
            draw.rectangle([(col_x + 10, y_curr + 9), (col_x + 20, y_curr + 19)], fill=(40, 40, 40))
            self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", sec_name, (col_x + 26, y_curr + 4), font_size=20, ink_rgb=(0, 0, 0))
            y_curr += 42

            # Dynamically stream lines until column is filled
            while y_curr < col_bottom - 30:
                sentence = self.get_next_lines(1)[0]["text"]
                try:
                    self.registry.verify_glyph_coverage("NotoSerifDevanagari.ttf", sentence)
                except Exception:
                    continue
                words = sentence.split()
                buf = ""
                for w in words:
                    test_buf = (buf + " " + w).strip()
                    w_px = self.renderer.get_text_width("NotoSerifDevanagari.ttf", test_buf, font_size=20)
                    if w_px <= col_w - 8:
                        buf = test_buf
                    else:
                        if buf:
                            self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (col_x, y_curr), font_size=20, ink_rgb=(20, 20, 20))
                            y_curr += line_pitch
                            if y_curr >= col_bottom - 30:
                                break
                        buf = w
                if buf and y_curr < col_bottom - 30:
                    self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (col_x, y_curr), font_size=20, ink_rgb=(20, 20, 20))
                    y_curr += line_pitch + 8

            # Column separator line
            if c_idx < 2:
                div_x = col_x + col_w + (gutter // 2)
                draw.line([(div_x, col_top), (div_x, col_bottom)], fill=(180, 180, 180), width=1)

        # 4. Realistic Newsprint Degradation
        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            img_bgr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
            img_bgr = self.augmenter.apply_paper_substrate(img_bgr, paper_type="newsprint")
            img_bgr = self.augmenter.apply_ink_bleed_or_toner_loss(img_bgr)
            img_bgr = self.augmenter.apply_optical_blur(img_bgr)
            img_bgr = self.augmenter.apply_shadow_gradient(img_bgr)
            final_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            applied_ops = ["newsprint_paper", "ink_bleed", "optical_blur", "shadow_gradient"]

        metadata = {
            "tier": "Tier_1_Full_Page",
            "archetype": "3_Column_Newspaper_Spread",
            "canvas_size": [page_w, page_h],
            "columns": 3,
            "language": "bho",
            "script": "Deva",
            "applied_augmentations": applied_ops,
            "is_clean": is_clean
        }
        return final_img, metadata

    # =========================================================================
    # TIER 1: FULL PAGES (ARCHETYPE C: ACADEMIC / LITERARY TEXTBOOK SPREAD)
    # [Single / Two-Column Textbook with Chapter Headings & Footnotes]
    # =========================================================================
    def generate_textbook_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (252, 250, 244))
        draw = ImageDraw.Draw(canvas)

        # 1. Running Header & Page Number
        chapter_num = random.randint(1, 15)
        page_num = random.randint(24, 280)
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", f"अध्याय {chapter_num} : भोजपुरी साहित्य के आलोचनात्मक इतिहास", (100, 60), font_size=18, ink_rgb=(80, 80, 80))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", f"पृष्ठ {page_num}", (page_w - 180, 60), font_size=20, ink_rgb=(60, 60, 60))
        draw.line([(100, 95), (page_w - 100, 95)], fill=(120, 120, 120), width=1)

        # 2. Section Heading
        section_titles = [
            "खण्ड २: लोकनाट्य परंपरा आ भिखारी ठाकुर के काव्य चेतना",
            "खण्ड ३: मध्यकालीन संत साहित्य आ कबीर के भोजपुरी पद",
            "खण्ड ४: पूर्वांचल के लोकगाथा आ सामाजिक संघर्ष के स्वर"
        ]
        sec_title = random.choice(section_titles)
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", sec_title, (100, 130), font_size=26, ink_rgb=(10, 10, 10))

        # 3. Main Body Lines (Single wide column with justified flow)
        y_curr = 185
        col_w = page_w - 200
        line_pitch = 34
        footnote_y = 1520

        while y_curr < footnote_y - 40:
            sentence = self.get_next_lines(1)[0]["text"]
            words = sentence.split()
            buf = ""
            for w in words:
                test_buf = (buf + " " + w).strip()
                w_px = self.renderer.get_text_width("NotoSerifDevanagari.ttf", test_buf, font_size=22)
                if w_px <= col_w - 10:
                    buf = test_buf
                else:
                    if buf:
                        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (100, y_curr), font_size=22, ink_rgb=(25, 25, 25))
                        y_curr += line_pitch
                        if y_curr >= footnote_y - 40:
                            break
                    buf = w
            if buf and y_curr < footnote_y - 40:
                self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", buf, (100, y_curr), font_size=22, ink_rgb=(25, 25, 25))
                y_curr += line_pitch + 10

        # 4. Footnote Section
        draw.line([(100, footnote_y), (400, footnote_y)], fill=(80, 80, 80), width=1)
        fn_lines = self.get_next_lines(2)
        fn_y = footnote_y + 15
        for f_idx, fn in enumerate(fn_lines):
            fn_text = f"[{f_idx+1}] {fn['text'][:70]}..."
            self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", fn_text, (100, fn_y), font_size=16, ink_rgb=(70, 70, 70))
            fn_y += 28

        # 5. Paper Aging & Sensor Degradation
        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            img_bgr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
            img_bgr = self.augmenter.apply_paper_substrate(img_bgr, paper_type="cream_unlined")
            img_bgr = self.augmenter.apply_shadow_gradient(img_bgr)
            img_bgr = self.augmenter.apply_optical_blur(img_bgr)
            final_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            applied_ops = ["cream_paper", "shadow_gradient", "optical_blur"]

        metadata = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Academic_Textbook_Chapter",
            "canvas_size": [page_w, page_h],
            "language": "bho",
            "script": "Deva",
            "applied_augmentations": applied_ops,
            "is_clean": is_clean
        }
        return final_img, metadata

    def generate_full_page(self, archetype: Optional[str] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        """Stochastically routes full-page synthesis across the 3 compliant archetypes."""
        if archetype is None:
            archetype = random.choice([
                "Literary_Society_Public_Notice",
                "3_Column_Newspaper_Spread",
                "Academic_Textbook_Chapter"
            ])

        if archetype == "Literary_Society_Public_Notice":
            return self.generate_public_notice_page(is_clean=is_clean)
        elif archetype == "3_Column_Newspaper_Spread":
            return self.generate_newspaper_page(is_clean=is_clean)
        else:
            return self.generate_textbook_page(is_clean=is_clean)

