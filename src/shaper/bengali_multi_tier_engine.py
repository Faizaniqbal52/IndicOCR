"""
Master Multi-Tier Synthetic OCR Generator for Bengali (ben_Beng)
Renders data across all 4 Granularity Tiers:
1. Tier 4: Words & Rare Bengali Conjuncts (30% quota)
2. Tier 3: Lines / TrOCR Sequences (55% quota)
3. Tier 2: Paragraphs & Multi-Line Text Blocks (13% quota)
4. Tier 1: Full-Page Documents (2% quota):
   - Archetype A: Sahityik Patrika (Literary Journal & Poetry Page)
   - Archetype B: Sarkar Rajpatra (Official State Gazette / Legal Decree)
   - Archetype C: Broadsheet Daily Newspaper Spread (3 columns Left-to-Right with vertical dividing rules)
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

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / "augmenter"))

from bengali_harfbuzz_shaper import BengaliFontRegistry, BengaliHarfBuzzRenderer
from degradation_engine import IndianDegradationEngine
from ownership_gate import DiacriticOwnershipGate


class BengaliMultiTierOCRGenerator:
    """Generates synthetic Bengali OCR instances across all 4 Granularity Tiers."""

    def __init__(self, fonts_dir: Path, processed_data_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.data_dir = Path(processed_data_dir)

        print("[Agent-Shaper] Initializing BengaliFontRegistry...")
        self.registry = BengaliFontRegistry(self.fonts_dir)
        self.renderer = BengaliHarfBuzzRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)

        # Load Bengali linguistic assets
        print(f"[Agent-Shaper] Loading linguistic assets from {self.data_dir.name}...")
        with open(self.data_dir / "bengali_words.jsonl", "r", encoding="utf-8") as f:
            self.words_data = [json.loads(line) for line in f]
        with open(self.data_dir / "bengali_lines.jsonl", "r", encoding="utf-8") as f:
            self.lines_data = [json.loads(line) for line in f]
        with open(self.data_dir / "bengali_blocks.jsonl", "r", encoding="utf-8") as f:
            self.blocks_data = [json.loads(line) for line in f]

        for item in self.words_data:
            val = item.get("text") or item.get("word")
            item["word"] = val
            item["text"] = val
        for item in self.lines_data:
            val = item.get("text") or item.get("line")
            item["line"] = val
            item["text"] = val

        random.shuffle(self.lines_data)
        random.shuffle(self.words_data)
        random.shuffle(self.blocks_data)

        self.font_names = list(self.registry.hb_fonts.keys())
        self.line_cursor = 0
        self.block_cursor = 0
        self.word_cursor = 0
        self.lang_code = "ben"
        self.script_code = "Beng"

        print(f"[Agent-Shaper] Loaded {len(self.lines_data):,} Bengali lines, {len(self.words_data):,} words, {len(self.blocks_data):,} blocks.")
        print(f"[Agent-Shaper] Available Bengali fonts: {len(self.font_names)}")

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
    # TIER 4: WORDS & ISOLATED BENGALI CONJUNCTS (30% QUOTA)
    # =========================================================================
    def generate_tier_4_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        n_words = len(self.words_data)
        if self.word_cursor >= n_words:
            self.word_cursor = 0
            random.shuffle(self.words_data)

        item = self.words_data[self.word_cursor]
        self.word_cursor += 1
        word_text = item["word"]

        supporting = self.registry.get_supporting_fonts(word_text)
        font_name = random.choice(supporting) if supporting else random.choice(self.font_names)
        font_size = random.choice([32, 38, 44, 48])

        img, meta = self.renderer.render_line(
            font_name=font_name,
            text=word_text,
            font_size=font_size
        )

        applied_ops = []
        if not is_clean:
            res = self.augmenter.augment_pipeline(img)
            img, applied_ops = res[0], res[1]

        out_meta = {
            "tier": "Tier_4_Word",
            "lang": self.lang_code,
            "script": self.script_code,
            "font_name": font_name,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops,
            "canvas_size": list(img.size),
            "text": word_text,
            "tokens": meta["tokens"],
            "num_tokens": 1,
            "shaped_glyphs": meta.get("shaped_glyphs", [])
        }
        return img, out_meta

    # =========================================================================
    # TIER 3: SEQUENCE LINES (55% QUOTA)
    # =========================================================================
    def generate_tier_3_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        line_item = self.get_next_lines(1)[0]
        line_text = line_item["text"]

        supporting = self.registry.get_supporting_fonts(line_text)
        attempts = 0
        while not supporting and attempts < 10:
            line_item = self.get_next_lines(1)[0]
            line_text = line_item["text"]
            supporting = self.registry.get_supporting_fonts(line_text)
            attempts += 1

        font_name = random.choice(supporting) if supporting else random.choice(self.font_names)
        font_size = random.choice([26, 30, 34, 38])

        img, meta = self.renderer.render_line(
            font_name=font_name,
            text=line_text,
            font_size=font_size
        )

        applied_ops = []
        if not is_clean:
            res = self.augmenter.augment_pipeline(img)
            img, applied_ops = res[0], res[1]

        out_meta = {
            "tier": "Tier_3_Line",
            "lang": self.lang_code,
            "script": self.script_code,
            "font_name": font_name,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops,
            "canvas_size": list(img.size),
            "text": line_text,
            "tokens": meta["tokens"],
            "num_tokens": len(meta["tokens"]),
            "shaped_glyphs": meta.get("shaped_glyphs", [])
        }
        return img, out_meta

    # =========================================================================
    # TIER 2: PARAGRAPHS & MULTI-LINE TEXT BLOCKS (13% QUOTA)
    # =========================================================================
    def generate_tier_2_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        block_item = self.get_next_blocks(1)[0]
        block_text = block_item["text"]

        # Split into 3 to 5 sentences
        sentences = [s.strip() for s in re.split(r'(?<=[।॥\?\!])\s+', block_text) if s.strip()]
        if len(sentences) < 2:
            sentences = [block_text]

        supporting = self.registry.get_supporting_fonts(block_text)
        font_name = random.choice(supporting) if supporting else random.choice(self.font_names)
        font_size = random.choice([22, 26, 30])

        rendered_lines = []
        max_w = 0
        total_h = 0

        for sent in sentences[:5]:
            try:
                l_img, l_meta = self.renderer.render_line(font_name=font_name, text=sent, font_size=font_size)
                rendered_lines.append((l_img, l_meta))
                max_w = max(max_w, l_img.width)
                total_h += l_img.height + 6
            except Exception:
                continue

        if not rendered_lines:
            return self.generate_tier_3_sample(is_clean=is_clean)

        canvas_w = max_w + 30
        canvas_h = total_h + 30
        bg_col = (250, 248, 243)
        canvas = Image.new("RGB", (canvas_w, canvas_h), color=bg_col)

        y_offset = 15
        all_tokens = []
        full_text = []

        for l_img, l_meta in rendered_lines:
            canvas.paste(l_img, (15, y_offset))
            for tok in l_meta["tokens"]:
                bx = tok["bbox"]
                if bx != [0, 0, 0, 0]:
                    all_tokens.append({
                        "text": tok["text"],
                        "bbox": [bx[0] + 15, bx[1] + y_offset, bx[2] + 15, bx[3] + y_offset]
                    })
            full_text.append(l_meta["text"])
            y_offset += l_img.height + 6

        applied_ops = []
        if not is_clean:
            res = self.augmenter.augment_pipeline(canvas)
            canvas, applied_ops = res[0], res[1]

        out_meta = {
            "tier": "Tier_2_Paragraph",
            "lang": self.lang_code,
            "script": self.script_code,
            "font_name": font_name,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops,
            "canvas_size": list(canvas.size),
            "text": " ".join(full_text),
            "tokens": all_tokens,
            "num_tokens": len(all_tokens),
            "line_count": len(rendered_lines)
        }
        return canvas, out_meta

    # =========================================================================
    # TIER 1: FULL-PAGE DOCUMENTS (2% QUOTA)
    # =========================================================================
    def generate_tier_1_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        archetype = random.choice([
            "Archetype_A_Sahityik_Patrika",
            "Archetype_B_Sarkar_Rajpatra",
            "Archetype_C_Newspaper_Spread"
        ])

        canvas_w, canvas_h = 1240, 1754  # A4 150 DPI
        bg_color = (250, 248, 243)
        canvas = Image.new("RGB", (canvas_w, canvas_h), color=bg_color)
        draw = ImageDraw.Draw(canvas)

        font_name = random.choice(self.font_names)
        all_tokens = []
        text_accumulator = []

        # Masthead Header
        header_text = "আনন্দবাজার পত্রিকা" if "Newspaper" in archetype else ("সাহিত্যিক পর্যালোচনা" if "Sahityik" in archetype else "পশ্চিমবঙ্গ সরকার রাজ্যপত্র")
        h_img, h_meta = self.renderer.render_line(font_name=font_name, text=header_text, font_size=42)
        h_x = (canvas_w - h_img.width) // 2
        canvas.paste(h_img, (h_x, 60))
        for tok in h_meta["tokens"]:
            bx = tok["bbox"]
            all_tokens.append({"text": tok["text"], "bbox": [bx[0] + h_x, bx[1] + 60, bx[2] + h_x, bx[3] + 60]})
        text_accumulator.append(header_text)

        draw.line([(60, 140), (canvas_w - 60, 140)], fill=(40, 40, 40), width=3)

        # Multi-column Layout
        col_w = 340
        gut = 30
        x_start = 60
        y_start = 170

        lines_batch = self.get_next_lines(45)
        l_idx = 0

        for col in range(3):
            cx = x_start + col * (col_w + gut)
            cy = y_start
            while cy < 1620 and l_idx < len(lines_batch):
                sent = lines_batch[l_idx]["text"]
                l_idx += 1
                try:
                    line_img, line_meta = self.renderer.render_line(font_name=font_name, text=sent, font_size=20)
                    if line_img.width > col_w:
                        line_img = line_img.crop((0, 0, col_w, line_img.height))
                    canvas.paste(line_img, (cx, cy))
                    for tok in line_meta["tokens"]:
                        bx = tok["bbox"]
                        if bx[2] <= col_w:
                            all_tokens.append({"text": tok["text"], "bbox": [bx[0] + cx, bx[1] + cy, bx[2] + cx, bx[3] + cy]})
                    text_accumulator.append(sent)
                    cy += line_img.height + 6
                except Exception:
                    continue

            # Vertical divider
            if col < 2:
                div_x = cx + col_w + (gut // 2)
                draw.line([(div_x, y_start), (div_x, 1640)], fill=(180, 180, 180), width=1)

        draw.line([(60, 1660), (canvas_w - 60, 1660)], fill=(40, 40, 40), width=2)

        applied_ops = []
        if not is_clean:
            res = self.augmenter.augment_pipeline(canvas)
            canvas, applied_ops = res[0], res[1]

        out_meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": archetype,
            "lang": self.lang_code,
            "script": self.script_code,
            "font_name": font_name,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops,
            "canvas_size": [canvas_w, canvas_h],
            "text": " ".join(text_accumulator),
            "tokens": all_tokens,
            "num_tokens": len(all_tokens),
            "line_count": l_idx
        }
        return canvas, out_meta

    generate_full_page_sample = generate_tier_1_sample
    generate_paragraph_sample = generate_tier_2_sample
    generate_line_sample = generate_tier_3_sample
    generate_word_sample = generate_tier_4_sample

    # =========================================================================
    # MULTI-TIER MASTER SAMPLER
    # =========================================================================
    def generate_sample(self, is_clean: Optional[bool] = None) -> Tuple[Image.Image, Dict[str, Any]]:
        """Samples according to 70% degraded vs 30% clean and 2%/13%/55%/30% tiers."""
        if is_clean is None:
            is_clean = (random.random() < 0.30)

        rand_tier = random.random()
        if rand_tier < 0.02:
            return self.generate_tier_1_sample(is_clean=is_clean)
        elif rand_tier < 0.15:
            return self.generate_tier_2_sample(is_clean=is_clean)
        elif rand_tier < 0.70:
            return self.generate_tier_3_sample(is_clean=is_clean)
        else:
            return self.generate_tier_4_sample(is_clean=is_clean)
