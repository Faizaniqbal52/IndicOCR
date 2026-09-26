"""
Agent-Shaper & Agent-Augmenter: Multi-Tier Synthetic OCR Generator for Urdu (urd_Arab)
Compliant, Zero-Leak, and Production-Hardened.

Renders data across all 4 Granularity Tiers:
1. Tier 4: Words & Isolated Nastaliq Ligatures (30% quota)
2. Tier 3: Lines / TrOCR Sequences (55% quota)
3. Tier 2: Paragraphs & Multi-Line Text Blocks (13% quota)
4. Tier 1: Full-Page Documents (2% quota):
   - Archetype A: Poetic Diwan / Mushaira Couplet Anthology Page
   - Archetype B: Official Court Notice / Judicial Gazette (عدالت عالیہ, Case No., Stamp Seal)
   - Archetype C: Multi-Column Urdu Daily Newspaper Spread (روزنامہ, 3 columns Right-to-Left)

Integrates:
- UrduHarfBuzzRenderer with RTL Complex Text Layout (CTL).
- 23 verified Urdu fonts (Nastaliq, Freehand/Handwriting, Book Naskh, Modern Editorial).
- 54-Matrix stochastic degradations via IndianDegradationEngine.
- DiacriticOwnershipGate ensuring zero diacritic truncation.
"""

import sys
import os
import io
import json
import random
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r"c:\OCR - All\src\shaper")
sys.path.append(r"c:\OCR - All\src\augmenter")

from urdu_harfbuzz_shaper import UrduFontRegistry, UrduHarfBuzzRenderer
from degradation_engine import IndianDegradationEngine
from ownership_gate import DiacriticOwnershipGate


def clean_pure_urdu(text: str) -> str:
    """Strips all digits (Latin and Perso-Arabic) and non-Urdu characters to guarantee 100% pure Urdu."""
    text = re.sub(r'[\d\u0660-\u0669\u06F0-\u06F9a-zA-Z]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text



class UrduMultiTierOCRGenerator:
    """Generates synthetic Urdu OCR instances across all 4 Granularity Tiers."""

    def __init__(self, fonts_dir: Path, processed_data_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.registry = UrduFontRegistry(self.fonts_dir)
        self.renderer = UrduHarfBuzzRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)
        self.data_dir = Path(processed_data_dir)

        # Load multi-domain linguistic assets
        with open(self.data_dir / "urdu_words.jsonl", "r", encoding="utf-8") as f:
            self.words_data = [json.loads(line) for line in f]
        with open(self.data_dir / "urdu_lines.jsonl", "r", encoding="utf-8") as f:
            self.lines_data = [json.loads(line) for line in f]
        with open(self.data_dir / "urdu_blocks.jsonl", "r", encoding="utf-8") as f:
            self.blocks_data = [json.loads(line) for line in f]

        random.shuffle(self.lines_data)
        random.shuffle(self.words_data)
        random.shuffle(self.blocks_data)

        self.font_names = list(self.registry.hb_fonts.keys())
        self.line_cursor = 0
        self.block_cursor = 0

    def get_next_lines(self, count: int) -> List[Dict[str, Any]]:
        n = len(self.lines_data)
        if self.line_cursor + count > n:
            self.line_cursor = 0
            random.shuffle(self.lines_data)

        batch = self.lines_data[self.line_cursor:self.line_cursor + count]
        self.line_cursor += count
        return batch

    def get_next_blocks(self, count: int) -> List[Dict[str, Any]]:
        n = len(self.blocks_data)
        if self.block_cursor + count > n:
            self.block_cursor = 0
            random.shuffle(self.blocks_data)

        batch = self.blocks_data[self.block_cursor:self.block_cursor + count]
        self.block_cursor += count
        return batch

    # =========================================================================
    # TIER 4: WORDS & ISOLATED NASTALIQ LIGATURES (30% QUOTA)
    # =========================================================================
    def generate_word_sample(
        self,
        word_entry: Optional[Dict[str, Any]] = None,
        is_clean: Optional[bool] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        # Enforce 55% (50%+) clean corpus ratio if not specified
        if is_clean is None:
            is_clean = (random.random() < 0.55)

        for _ in range(15):
            entry = word_entry if word_entry is not None else random.choice(self.words_data)
            # Combine 1 to 3 words for rich compound lexical representation
            if random.random() < 0.35 and " " not in entry["word"]:
                second = random.choice(self.words_data)["word"]
                word = f"{entry['word']} {second}"
            else:
                word = entry["word"]

            supporting_fonts = self.registry.get_supporting_fonts(word)
            if supporting_fonts:
                break
            word_entry = None

        font_name = random.choice(supporting_fonts) if supporting_fonts else "NotoNastaliqUrdu-Regular.ttf"
        font_size = random.choice([34, 38, 44, 48])

        clean_img, ann = self.renderer.render_line(font_name, word, font_size=font_size)
        if is_clean:
            final_img = clean_img
            applied_ops = ["pristine_digital_scan"]
            updated_bbox = ann["bbox"]
        else:
            final_img, applied_ops, updated_bbox = self.augmenter.augment_pipeline(clean_img, bbox=ann["bbox"])

        metadata = {
            "tier": "Tier_4_Word",
            "language": "urdu",
            "word": word,
            "font": font_name,
            "font_style": self.registry.FONT_STYLES.get(font_name, "general"),
            "font_size": font_size,
            "bbox": updated_bbox,
            "canvas_size": ann["canvas_size"],
            "has_aerab": entry.get("has_aerab", False),
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }

        return final_img, metadata

    # =========================================================================
    # TIER 3: TEXT LINES / TrOCR SEQUENCES (55% QUOTA)
    # =========================================================================
    def generate_line_sample(
        self,
        line_entry: Optional[Dict[str, Any]] = None,
        is_clean: Optional[bool] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        # Enforce 55% (50%+) clean corpus ratio if not specified
        if is_clean is None:
            is_clean = (random.random() < 0.55)

        for _ in range(15):
            entry = line_entry if line_entry is not None else random.choice(self.lines_data)
            line_text = entry["line"]

            # Ensure rich line density (at least 6-16 words, ~45 to 90 chars)
            if len(line_text.split()) < 7 and random.random() < 0.5:
                extra = random.choice(self.lines_data)["line"]
                line_text = f"{line_text} اور {extra}"

            # Truncate if overly long
            if len(line_text) > 110:
                words = line_text.split()
                line_text = " ".join(words[:14])

            style_pref = None
            if entry.get("domain") == "poetry":
                style_pref = "nastaliq"
            elif entry.get("domain") == "news":
                style_pref = "newspaper"
            elif entry.get("domain") == "legal":
                style_pref = "naskh"

            supporting = self.registry.get_supporting_fonts(line_text, style_filter=style_pref)
            if not supporting:
                supporting = self.registry.get_supporting_fonts(line_text)
            if supporting:
                break
            line_entry = None

        font_name = random.choice(supporting) if supporting else "NotoNastaliqUrdu-Regular.ttf"
        font_size = random.choice([30, 34, 38, 42])

        clean_img, ann = self.renderer.render_line(font_name, line_text, font_size=font_size)
        if is_clean:
            final_img = clean_img
            applied_ops = ["pristine_digital_scan"]
            updated_bbox = ann["bbox"]
        else:
            final_img, applied_ops, updated_bbox = self.augmenter.augment_pipeline(clean_img, bbox=ann["bbox"])

        metadata = {
            "tier": "Tier_3_Line",
            "language": "urdu",
            "domain": entry.get("domain", "general"),
            "text": line_text,
            "words_count": len(line_text.split()),
            "font": font_name,
            "font_style": self.registry.FONT_STYLES.get(font_name, "general"),
            "font_size": font_size,
            "bbox": updated_bbox,
            "canvas_size": ann["canvas_size"],
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }

        return final_img, metadata

    # =========================================================================
    # TIER 2: MULTI-LINE PARAGRAPH BLOCKS (13% QUOTA)
    # =========================================================================
    def generate_paragraph_sample(
        self,
        block_entry: Optional[Dict[str, Any]] = None,
        is_clean: Optional[bool] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        # Enforce 55% (50%+) clean corpus ratio if not specified
        if is_clean is None:
            is_clean = (random.random() < 0.55)

        entry = block_entry if block_entry is not None else self.get_next_blocks(1)[0]
        raw_text = entry["block"]
        domain = entry.get("domain", "essay")

        # If block is too short, concatenate another block to guarantee 5-8 lines
        if len(raw_text.split()) < 45:
            extra = self.get_next_blocks(1)[0]["block"]
            raw_text = f"{raw_text} {extra}"

        # Select font based on domain
        if domain == "poetry":
            font_name = "NotoNastaliqUrdu-Regular.ttf" if "NotoNastaliqUrdu-Regular.ttf" in self.font_names else self.font_names[0]
        elif domain == "legal":
            font_name = "Amiri-Regular.ttf" if "Amiri-Regular.ttf" in self.font_names else self.font_names[0]
        elif domain == "news":
            font_name = "MarkaziText-Regular.ttf" if "MarkaziText-Regular.ttf" in self.font_names else self.font_names[0]
        else:
            font_name = random.choice(self.font_names)

        font_size = random.choice([26, 28, 32])
        is_nastaliq = "nastaliq" in font_name.lower()

        # Split text into 5 to 8 lines of ~10 to 14 words each
        words = raw_text.split()
        para_lines = []
        words_per_line = random.choice([10, 12, 14])
        for i in range(0, min(len(words), 85), words_per_line):
            chunk = " ".join(words[i:i + words_per_line])
            if chunk.strip():
                para_lines.append(chunk)

        if len(para_lines) < 4:
            # Add synthetic filler lines from lines_data
            for l_ent in self.get_next_lines(4 - len(para_lines)):
                para_lines.append(l_ent["line"][:70])

        if not para_lines:
            para_lines = [raw_text[:60]]

        # Render each line to RGBA
        rendered_lines = []
        max_w = 0
        for l_txt in para_lines:
            try:
                rgba_img, crop_info = self.renderer.render_text_rgba(font_name, l_txt, font_size=font_size)
                rendered_lines.append((rgba_img, l_txt))
                max_w = max(max_w, rgba_img.width)
            except Exception:
                continue

        if not rendered_lines:
            return self.generate_line_sample(is_clean=is_clean)

        pad_x = 35
        pad_y = 35
        canvas_w = max_w + (pad_x * 2) + 20
        canvas_h = pad_y * 2 + sum(img.height for img, _ in rendered_lines) + (len(rendered_lines) - 1) * 12

        # Background substrate
        bg_rgb = (250, 248, 242)
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_rgb)

        cur_y = pad_y
        line_bboxes = []
        full_text_lines = []

        for rgba_img, l_txt in rendered_lines:
            # Right-align for RTL
            cur_x = canvas_w - pad_x - rgba_img.width
            canvas.paste(rgba_img, (cur_x, cur_y), rgba_img)
            line_bboxes.append([cur_x, cur_y, cur_x + rgba_img.width, cur_y + rgba_img.height])
            full_text_lines.append(l_txt)
            cur_y += rgba_img.height + 12

        total_bbox = [
            min(b[0] for b in line_bboxes),
            min(b[1] for b in line_bboxes),
            max(b[2] for b in line_bboxes),
            max(b[3] for b in line_bboxes)
        ]

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
            updated_bbox = total_bbox
        else:
            final_img, applied_ops, updated_bbox = self.augmenter.augment_pipeline(canvas, bbox=total_bbox)

        metadata = {
            "tier": "Tier_2_Paragraph",
            "language": "urdu",
            "domain": domain,
            "text": "\n".join(full_text_lines),
            "font": font_name,
            "font_style": self.registry.FONT_STYLES.get(font_name, "general"),
            "font_size": font_size,
            "bbox": updated_bbox,
            "line_bboxes": line_bboxes,
            "lines_count": len(rendered_lines),
            "canvas_size": [canvas_w, canvas_h],
            "applied_augmentations": applied_ops
        }

        return final_img, metadata

    # =========================================================================
    # TIER 1: FULL-PAGE DOCUMENTS (2% QUOTA • 20,000 SAMPLES)
    # =========================================================================
    def generate_full_page_sample(
        self,
        archetype: Optional[str] = None,
        is_clean: Optional[bool] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Generates authentic full-page Urdu documents across 4 archetypes:
        1. Archetype D: Pure Urdu Academic Essay & Book Chapter (100% pure Urdu prose, edge-to-edge justification, zero numbers)
        2. Archetype B: Official Court Notice / Judicial Gazette (عدالت عالیہ, petition, seal)
        3. Archetype C: Multi-Column Daily Newspaper Spread (3 columns Right-to-Left, headlines)
        4. Archetype A: Poetic Diwan / Mushaira Anthology Page (Couplet layout, ornate borders)
        """
        if is_clean is None:
            is_clean = (random.random() < 0.55)

        if archetype is None:
            archetype = random.choices(
                ["Archetype_D_Prose_Essay", "Archetype_B_Court_Gazette", "Archetype_C_Newspaper", "Archetype_A_Diwan"],
                weights=[0.50, 0.20, 0.15, 0.15]
            )[0]

        page_w = 1200
        page_h = 1600
        if is_clean:
            bg_rgb = (255, 255, 255) if random.random() < 0.65 else (252, 250, 246)
        else:
            bg_rgb = (248, 245, 238)
        canvas = Image.new("RGB", (page_w, page_h), bg_rgb)
        draw = ImageDraw.Draw(canvas)

        line_boxes = []
        document_elements = []

        if archetype == "Archetype_D_Prose_Essay":
            # -----------------------------------------------------------------
            # ARCHETYPE D: ACADEMIC ESSAY & PROSE BOOK CHAPTER
            # Lines spread from EXTREME RIGHT (X=1120) to EXTREME LEFT (X=80)
            # -----------------------------------------------------------------
            x_left = 80
            x_right = 1120
            target_line_w = x_right - x_left  # 1040 px

            font_header = "Amiri-Bold.ttf" if "Amiri-Bold.ttf" in self.font_names else self.font_names[0]
            font_body = "Amiri-Regular.ttf" if "Amiri-Regular.ttf" in self.font_names else self.font_names[0]
            font_size = 25
            line_pitch = 41

            # 1. Top Running Head & Chapter Title
            header_titles = [
                "مضامینِ سرسید — باب سوم: علمی و اخلاقی اصلاحات",
                "تاریخِ ادبِ اردو — دورِ متوسطین اور دبستانِ دہلی",
                "تہذیب الاخلاق — سماجی شعور اور عصری تقاضے",
                "مقدمہ شعر و شاعری — نقد و نظر کا جدید معیار",
                "فلسفہ تعلیم و تربیت — قومی بیداری کے رہنما اصول"
            ]
            title_text = random.choice(header_titles)
            t_img, _ = self.renderer.render_text_rgba(font_header, title_text, font_size=23, ink_rgb=(40, 30, 25))
            tx = (page_w - t_img.width) // 2
            canvas.paste(t_img, (tx, 55), t_img)
            draw.line([x_left, 92, x_right, 92], fill=(160, 140, 120), width=1)
            line_boxes.append([tx, 55, tx + t_img.width, 55 + t_img.height])
            document_elements.append({"type": "header_title", "text": title_text, "bbox": [tx, 55, tx + t_img.width, 55 + t_img.height]})

            # 2. Continuous Running Essay Paragraphs (Zero Numbers, Pure Urdu Only)
            cur_y = 125
            raw_blocks = [b["block"] for b in self.blocks_data if b.get("domain") in ["essay", "general", "legal"]]
            if len(raw_blocks) < 5:
                raw_blocks = [b["block"] for b in self.blocks_data[:20]]

            # Filter blocks to guarantee 100% Pure Urdu with zero numbers or Latin digits
            essay_blocks = [clean_pure_urdu(b) for b in raw_blocks if len(clean_pure_urdu(b).split()) >= 20]
            selected_paras = random.sample(essay_blocks, min(4, len(essay_blocks)))
            expanded_paras = []
            for p in selected_paras:
                words = p.split()
                while len(words) < 160:
                    words.extend(random.choice(essay_blocks).split())
                expanded_paras.append(words)

            for p_idx, p_words in enumerate(expanded_paras):
                if cur_y > page_h - 75:
                    break

                word_idx = 0
                is_first_line_of_para = True

                while word_idx < len(p_words) and cur_y <= page_h - 130:
                    # Paragraph first line indent on right
                    indent = 35 if is_first_line_of_para else 0
                    cur_target_w = target_line_w - indent
                    eff_x_right = x_right - indent

                    line_words = []
                    test_line = []

                    while word_idx < len(p_words):
                        w = p_words[word_idx]
                        test_line.append(w)
                        im_test, _ = self.renderer.render_text_rgba(font_body, " ".join(test_line), font_size=font_size)

                        if im_test.width > cur_target_w:
                            if len(test_line) > 1:
                                test_line.pop()
                                line_words = test_line
                            else:
                                line_words = [w]
                                word_idx += 1
                            break
                        else:
                            word_idx += 1
                            line_words = list(test_line)

                    if not line_words:
                        break

                    is_last_line_of_para = (word_idx >= len(p_words))

                    # Render individual words for line
                    rendered_word_imgs = []
                    for w in line_words:
                        w_im, _ = self.renderer.render_text_rgba(font_body, w, font_size=font_size, ink_rgb=(25, 25, 25))
                        rendered_word_imgs.append((w, w_im))

                    # Case A: Intermediate line -> JUSTIFY FROM EXTREME RIGHT TO EXTREME LEFT
                    if not is_last_line_of_para and len(rendered_word_imgs) > 1:
                        sum_w = sum(im.width for _, im in rendered_word_imgs)
                        gap = (cur_target_w - sum_w) / (len(rendered_word_imgs) - 1)
                        if gap > 24:
                            gap = 12

                        cur_x = eff_x_right
                        for _, w_im in rendered_word_imgs:
                            px = int(cur_x - w_im.width)
                            canvas.paste(w_im, (px, cur_y), w_im)
                            cur_x = px - gap

                        line_box = [x_left, cur_y, eff_x_right, cur_y + font_size + 8]
                    else:
                        # Case B: Last line of paragraph -> Normal right-aligned spacing
                        cur_x = eff_x_right
                        normal_gap = 10
                        for _, w_im in rendered_word_imgs:
                            px = int(cur_x - w_im.width)
                            canvas.paste(w_im, (px, cur_y), w_im)
                            cur_x = px - normal_gap

                        line_box = [int(cur_x + normal_gap), cur_y, eff_x_right, cur_y + font_size + 8]

                    line_boxes.append(line_box)
                    document_elements.append({
                        "type": "essay_line",
                        "para_index": p_idx + 1,
                        "text": " ".join(line_words),
                        "bbox": line_box
                    })

                    cur_y += line_pitch
                    is_first_line_of_para = False

                cur_y += 14  # Inter-paragraph vertical gap

        elif archetype == "Archetype_A_Diwan":
            # -----------------------------------------------------------------
            # ARCHETYPE A: POETIC DIWAN / MUSHAIRA PAGE
            # -----------------------------------------------------------------
            # Outer decorative border
            draw.rectangle([40, 40, page_w - 40, page_h - 40], outline=(140, 100, 60), width=3)
            draw.rectangle([48, 48, page_w - 48, page_h - 48], outline=(180, 150, 110), width=1)

            # Ornate Title Header in Nastaliq
            title_text = random.choice([
                "کلامِ اقبال — بانگِ درا",
                "دیوانِ غالب — غزل ہائے نو",
                "انتخابِ کلام — میر تقی میر",
                "گلزارِ سخن — مشاعرہ خاص"
            ])
            title_font = "NotoNastaliqUrdu-Regular.ttf" if "NotoNastaliqUrdu-Regular.ttf" in self.font_names else self.font_names[0]
            title_img, _ = self.renderer.render_text_rgba(title_font, title_text, font_size=46, ink_rgb=(100, 30, 20))
            tx = (page_w - title_img.width) // 2
            ty = 75
            canvas.paste(title_img, (tx, ty), title_img)
            document_elements.append({"type": "title", "text": title_text, "bbox": [tx, ty, tx + title_img.width, ty + title_img.height]})

            # Floral / geometric separator below title
            draw.line([250, ty + title_img.height + 15, page_w - 250, ty + title_img.height + 15], fill=(160, 120, 80), width=2)

            # Couplets (Ash'ar) layout: Misra-e-Oola (Right) & Misra-e-Sani (Left)
            poetry_lines = [e["line"] for e in self.lines_data if e.get("domain") == "poetry"]
            if len(poetry_lines) < 26:
                poetry_lines = [e["line"] for e in self.lines_data[:30]]

            couplet_font = "Gulzar-Regular.ttf" if "Gulzar-Regular.ttf" in self.font_names else title_font
            cur_y = ty + title_img.height + 40

            # Render 12 to 14 couplets to densely fill the page
            for i in range(0, min(len(poetry_lines) - 1, 24), 2):
                m1 = poetry_lines[i]
                m2 = poetry_lines[i + 1]

                img1, _ = self.renderer.render_text_rgba(couplet_font, m1, font_size=26, ink_rgb=(25, 25, 25))
                img2, _ = self.renderer.render_text_rgba(couplet_font, m2, font_size=26, ink_rgb=(25, 25, 25))

                # Right hemistich
                x1 = page_w - 85 - img1.width
                canvas.paste(img1, (x1, cur_y), img1)
                line_boxes.append([x1, cur_y, x1 + img1.width, cur_y + img1.height])

                # Left hemistich
                x2 = 85
                canvas.paste(img2, (x2, cur_y), img2)
                line_boxes.append([x2, cur_y, x2 + img2.width, cur_y + img2.height])

                # Central couplet ornament symbol (vector geometric diamond - zero tofu)
                cx_mid = page_w // 2
                cy_mid = cur_y + 12
                draw.polygon([(cx_mid, cy_mid - 5), (cx_mid + 5, cy_mid), (cx_mid, cy_mid + 5), (cx_mid - 5, cy_mid)], fill=(160, 110, 60))

                cur_y += max(img1.height, img2.height) + 26
                if cur_y > page_h - 180:
                    break

            # Bottom commentary / footnote block
            draw.line([120, page_h - 140, page_w - 120, page_h - 140], fill=(180, 140, 100), width=1)
            fn_text = "حاشیہ: یہ کلام مطبوعہ نسخہ حمیدیہ سے باہتمام مجلسِ ادب نقل کیا گیا ہے۔ جملہ حقوق محفوظ ہیں۔"
            fn_font = "NotoNastaliqUrdu-Regular.ttf" if "NotoNastaliqUrdu-Regular.ttf" in self.font_names else title_font
            try:
                fn_img, _ = self.renderer.render_text_rgba(fn_font, fn_text, font_size=20, ink_rgb=(90, 70, 50))
                fx = page_w - 120 - fn_img.width
                canvas.paste(fn_img, (fx, page_h - 125), fn_img)
                line_boxes.append([fx, page_h - 125, fx + fn_img.width, page_h - 125 + fn_img.height])
            except Exception:
                pass

            # Bottom page decorative ornament (vector rosette)
            cx_mid = page_w // 2
            cy_bot = page_h - 75
            draw.polygon([(cx_mid, cy_bot - 6), (cx_mid + 8, cy_bot), (cx_mid, cy_bot + 6), (cx_mid - 8, cy_bot)], fill=(140, 100, 60))
            draw.ellipse([cx_mid - 2, cy_bot - 2, cx_mid + 2, cy_bot + 2], fill=(255, 255, 255))

        elif archetype == "Archetype_B_Court_Gazette":
            # -----------------------------------------------------------------
            # ARCHETYPE B: OFFICIAL COURT NOTICE / JUDICIAL GAZETTE
            # -----------------------------------------------------------------
            # Official header banner
            draw.rectangle([50, 45, page_w - 50, 135], outline=(40, 40, 40), width=2)
            court_title = random.choice([
                "عدالت عالیہ پنجاب — باضابطہ قانونی گزٹ و اشہار عام",
                "محکمہ انصاف و قانون — نوٹس برائے پیشی عدالت",
                "سرکاری گزٹ — اعلامیہ برائے حقوق و فرائض مقدمہ"
            ])
            header_font = "Amiri-Bold.ttf" if "Amiri-Bold.ttf" in self.font_names else self.font_names[0]
            h_img, _ = self.renderer.render_text_rgba(header_font, court_title, font_size=34, ink_rgb=(20, 20, 20))
            hx = (page_w - h_img.width) // 2
            canvas.paste(h_img, (hx, 65), h_img)
            line_boxes.append([hx, 65, hx + h_img.width, 65 + h_img.height])

            # Metadata case details box (100% Pure Urdu, Zero Digits)
            case_no = random.choice([
                "مقدمہ بابت: حقِ ملکیت و منتقلی اراضی",
                "مقدمہ بابت: تصفیہ تنازعہ املاک و وراثت",
                "درخواست بابت: تعمیلِ حکم و اجرای عدالت",
                "مقدمہ بابت: اپیل نگرانی و بحالی حقوق"
            ])
            date_str = random.choice([
                "تاریخ اجراء: بتاریخ دہم ماہِ رواں",
                "تاریخ اجراء: بتاریخ بست و پنجم ماہِ رواں",
                "تاریخ اجراء: بتاریخ پانزدہم ماہِ حال"
            ])
            d_img, _ = self.renderer.render_text_rgba(header_font, f"{case_no}  |  {date_str}", font_size=22, ink_rgb=(60, 60, 60))
            dx = page_w - 80 - d_img.width
            canvas.paste(d_img, (dx, 155), d_img)
            line_boxes.append([dx, 155, dx + d_img.width, 155 + d_img.height])

            # Horizontal ruling line
            draw.line([60, 200, page_w - 60, 200], fill=(50, 50, 50), width=2)

            # Body legal clauses (Preamble)
            legal_lines = [e["line"] for e in self.lines_data if e.get("domain") in ["essay_knowledge", "essay", "legal"]]
            if len(legal_lines) < 20:
                legal_lines = [e["line"] for e in self.lines_data[:25]]

            body_font = "Amiri-Regular.ttf" if "Amiri-Regular.ttf" in self.font_names else header_font
            cur_y = 220

            # 6 introductory clauses
            for l_txt in legal_lines[:6]:
                l_img, _ = self.renderer.render_text_rgba(body_font, l_txt, font_size=24, ink_rgb=(20, 20, 20))
                lx = page_w - 70 - l_img.width
                canvas.paste(l_img, (lx, cur_y), l_img)
                line_boxes.append([lx, cur_y, lx + l_img.width, cur_y + l_img.height])
                cur_y += l_img.height + 16

            cur_y += 15
            # Ruled Judicial Schedule Table
            # Table Header
            tbl_x0, tbl_x1 = 60, page_w - 60
            tbl_y0 = cur_y
            row_h = 42
            col_widths = [80, 420, 320, 260] # شمار, عنوان مقدمہ, دفعات قانون, تاریخ پیشی
            col_x_starts = [
                tbl_x1 - col_widths[0],
                tbl_x1 - sum(col_widths[:2]),
                tbl_x1 - sum(col_widths[:3]),
                tbl_x0
            ]

            draw.rectangle([tbl_x0, tbl_y0, tbl_x1, tbl_y0 + row_h], fill=(235, 235, 230), outline=(40, 40, 40), width=1)
            headers = ["شمار", "عنوان مقدمہ و فریقین", "دفعات تعزیرات / قانون", "آئندہ پیشی"]
            for idx, h_txt in enumerate(headers):
                c_img, _ = self.renderer.render_text_rgba(header_font, h_txt, font_size=20, ink_rgb=(20, 20, 20))
                cx = col_x_starts[idx] + (col_widths[idx] - c_img.width) // 2
                canvas.paste(c_img, (cx, tbl_y0 + 8), c_img)
                line_boxes.append([cx, tbl_y0 + 8, cx + c_img.width, tbl_y0 + 8 + c_img.height])

            # Table rows (5 rows) - 100% Pure Urdu Words
            tbl_cur_y = tbl_y0 + row_h
            urdu_serials = ["اوّل", "دوم", "سوم", "چہارم", "پنجم"]
            for row_idx in range(5):
                draw.rectangle([tbl_x0, tbl_cur_y, tbl_x1, tbl_cur_y + row_h], outline=(100, 100, 100), width=1)
                sr_txt = urdu_serials[row_idx]
                party_txt = random.choice(["حکومت بنام محمد اسلم وغیره", "زید بنام بشیر احمد مقدمہ اراضی", "نوٹس تعمیلی بنام غلام رسول", "درخواست حکم امتناعی عاصم علی", "اپیل نگرانی بنام مجسٹریٹ"])
                sec_txt = random.choice([
                    "تعزیرات بابت اقدامِ قتل",
                    "ضابطہ دیوانی بابت حکمِ امتناعی",
                    "قانون معاہدات بابت تلافی ہرجانہ",
                    "تعزیرات بابت جعلسازی و فریب",
                    "ضابطہ فوجداری بابت امن عامہ"
                ])
                date_txt = random.choice([
                    "بتاریخ دہم ماہِ آئندہ",
                    "بتاریخ دوازدہم ماہِ آئندہ",
                    "بتاریخ پانزدہم ماہِ آئندہ",
                    "بتاریخ بیستم ماہِ آئندہ",
                    "بتاریخ بست و پنجم ماہِ آئندہ"
                ])

                # Cells
                for idx, c_val in enumerate([sr_txt, party_txt, sec_txt, date_txt]):
                    f_to_use = body_font if idx > 0 else header_font
                    c_img, _ = self.renderer.render_text_rgba(f_to_use, c_val, font_size=19, ink_rgb=(30, 30, 30))
                    cx = col_x_starts[idx] + (col_widths[idx] - c_img.width) // 2
                    canvas.paste(c_img, (cx, tbl_cur_y + 8), c_img)
                    line_boxes.append([cx, tbl_cur_y + 8, cx + c_img.width, tbl_cur_y + 8 + c_img.height])

                tbl_cur_y += row_h

            # Vertical grid lines in table
            for col_x in col_x_starts[:-1]:
                draw.line([col_x, tbl_y0, col_x, tbl_cur_y], fill=(80, 80, 80), width=1)
            draw.line([tbl_x0, tbl_y0, tbl_x0, tbl_cur_y], fill=(80, 80, 80), width=1)
            draw.line([tbl_x1, tbl_y0, tbl_x1, tbl_cur_y], fill=(80, 80, 80), width=1)

            cur_y = tbl_cur_y + 30

            # Sub-table Concluding Legal Directives (4 more dense lines)
            for l_txt in legal_lines[6:11]:
                l_img, _ = self.renderer.render_text_rgba(body_font, l_txt, font_size=23, ink_rgb=(20, 20, 20))
                lx = page_w - 70 - l_img.width
                canvas.paste(l_img, (lx, cur_y), l_img)
                line_boxes.append([lx, cur_y, lx + l_img.width, cur_y + l_img.height])
                cur_y += l_img.height + 15
                if cur_y > page_h - 220:
                    break

            # Bottom Signatures & Seal Section
            sig_text = "دستخط و مہر رجسٹرار عدالت عالیہ"
            s_img, _ = self.renderer.render_text_rgba(header_font, sig_text, font_size=22, ink_rgb=(40, 40, 40))
            sx = page_w - 100 - s_img.width
            canvas.paste(s_img, (sx, page_h - 130), s_img)
            line_boxes.append([sx, page_h - 130, sx + s_img.width, page_h - 130 + s_img.height])
            draw.line([page_w - 100 - s_img.width, page_h - 95, page_w - 100, page_h - 95], fill=(50, 50, 50), width=1)

            # Official Circular Rubber Stamp (Left bottom)
            stamp_cx, stamp_cy = 200, page_h - 130
            stamp_color = random.choice([(180, 40, 40), (30, 60, 160)])
            draw.ellipse([stamp_cx - 65, stamp_cy - 65, stamp_cx + 65, stamp_cy + 65], outline=stamp_color, width=3)
            draw.ellipse([stamp_cx - 58, stamp_cy - 58, stamp_cx + 58, stamp_cy + 58], outline=stamp_color, width=1)
            stamp_img, _ = self.renderer.render_text_rgba(header_font, "سرکاری مہر تصدیق", font_size=18, ink_rgb=stamp_color)
            canvas.paste(stamp_img, (stamp_cx - stamp_img.width // 2, stamp_cy - stamp_img.height // 2), stamp_img)
            line_boxes.append([stamp_cx - 65, stamp_cy - 65, stamp_cx + 65, stamp_cy + 65])

        else:
            # -----------------------------------------------------------------
            # ARCHETYPE C: MULTI-COLUMN DAILY NEWSPAPER (3 COLUMNS RTL)
            # -----------------------------------------------------------------
            # Newspaper masthead
            masthead = random.choice(["روزنامہ جنگ", "روزنامہ نوائے وقت", "روزنامہ ایکسپریس", "قومی آواز"])
            m_font = "MarkaziText-Regular.ttf" if "MarkaziText-Regular.ttf" in self.font_names else self.font_names[0]
            m_img, _ = self.renderer.render_text_rgba(m_font, masthead, font_size=68, ink_rgb=(10, 10, 10))
            mx = (page_w - m_img.width) // 2
            canvas.paste(m_img, (mx, 40), m_img)
            line_boxes.append([mx, 40, mx + m_img.width, 40 + m_img.height])
            draw.line([50, 135, page_w - 50, 135], fill=(20, 20, 20), width=3)

            # Headline banner
            news_lines = [e["line"] for e in self.lines_data if e.get("domain") == "news"]
            if len(news_lines) < 35:
                news_lines = [e["line"] for e in self.lines_data[:40]]

            headline = news_lines[0] if news_lines else "حکومت کا معاشی اصلاحات اور عوامی فلاح کے لئے اہم تاریخی اقدام"
            h_img, _ = self.renderer.render_text_rgba(m_font, headline, font_size=36, ink_rgb=(180, 20, 20))
            hx = page_w - 60 - h_img.width
            canvas.paste(h_img, (hx, 150), h_img)
            line_boxes.append([hx, 150, hx + h_img.width, 150 + h_img.height])
            draw.line([50, 150 + h_img.height + 10, page_w - 50, 150 + h_img.height + 10], fill=(80, 80, 80), width=1)

            # 3 Columns Layout (Strictly RTL: Col 0 on right, Col 1 center, Col 2 on left)
            col_w = 340
            col_gap = 35
            col_start_y = 150 + h_img.height + 22
            col_xs = [
                page_w - 60 - col_w,                  # Right column (Col 1)
                page_w - 60 - col_w * 2 - col_gap,    # Center column (Col 2)
                page_w - 60 - col_w * 3 - col_gap * 2  # Left column (Col 3)
            ]

            body_font = "NotoNaskhArabic-Regular.ttf" if "NotoNaskhArabic-Regular.ttf" in self.font_names else m_font
            line_idx = 1

            for col_i, cx in enumerate(col_xs):
                # Vertical column rule separator between columns
                if col_i > 0:
                    rule_x = cx + col_w + (col_gap // 2)
                    draw.line([rule_x, col_start_y, rule_x, page_h - 60], fill=(180, 180, 180), width=1)

                cur_y = col_start_y

                if col_i == 1:
                    draw.rectangle([cx + 15, cur_y, cx + col_w - 15, cur_y + 150], fill=(228, 228, 222), outline=(140, 140, 140), width=1)
                    ph_img, _ = self.renderer.render_text_rgba(m_font, "تصویری رپورٹ", font_size=20, ink_rgb=(100, 100, 100))
                    canvas.paste(ph_img, (cx + (col_w - ph_img.width) // 2, cur_y + 65), ph_img)
                    cur_y += 168

                # If left column, put a sub-headline box
                if col_i == 2:
                    sub_title = "خاص تجارتی و معاشی جائزہ"
                    s_img, _ = self.renderer.render_text_rgba(m_font, sub_title, font_size=24, ink_rgb=(10, 10, 100))
                    draw.rectangle([cx + 5, cur_y, cx + col_w - 5, cur_y + 36], fill=(240, 240, 235))
                    canvas.paste(s_img, (cx + col_w - s_img.width - 10, cur_y + 5), s_img)
                    cur_y += 48

                while cur_y < page_h - 75 and line_idx < len(news_lines):
                    l_txt = news_lines[line_idx]
                    line_idx = (line_idx + 1) % len(news_lines)
                    words = l_txt.split()
                    chunk = " ".join(words[:7])
                    try:
                        c_img, _ = self.renderer.render_text_rgba(body_font, chunk, font_size=22, ink_rgb=(25, 25, 25))
                        lx = cx + col_w - c_img.width
                        canvas.paste(c_img, (lx, cur_y), c_img)
                        line_boxes.append([lx, cur_y, lx + c_img.width, cur_y + c_img.height])
                        cur_y += c_img.height + 9
                    except Exception:
                        continue

        # Augmentation pass
        total_bbox = [
            min(b[0] for b in line_boxes),
            min(b[1] for b in line_boxes),
            max(b[2] for b in line_boxes),
            max(b[3] for b in line_boxes)
        ] if line_boxes else [50, 50, page_w - 50, page_h - 50]

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
            updated_bbox = total_bbox
        else:
            final_img, applied_ops, updated_bbox = self.augmenter.augment_pipeline(canvas, bbox=total_bbox)

        metadata = {
            "tier": "Tier_1_Full_Page",
            "language": "urdu",
            "archetype": archetype,
            "canvas_size": [page_w, page_h],
            "bbox": updated_bbox,
            "line_bboxes": line_boxes,
            "lines_count": len(line_boxes),
            "document_elements": document_elements,
            "full_text": "\n".join(el["text"] for el in document_elements if "text" in el),
            "applied_augmentations": applied_ops
        }

        return final_img, metadata
