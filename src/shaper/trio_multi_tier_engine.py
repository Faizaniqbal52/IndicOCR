"""
Multi-Tier Synthetic OCR Generators for:
1. Odia (ori_Orya)
2. Assamese (asm_Beng)
3. Sanskrit (san_Deva)

Each generator supports all 4 Granularity Tiers:
- Tier 4: Words & Isolated Tokens (30% quota)
- Tier 3: Lines / TrOCR Sequences (55% quota)
- Tier 2: Paragraphs & Multi-Line Blocks (13% quota)
- Tier 1: Full-Page Document Archetypes (2% quota):
    * Odia: Odisha Rajapatra (Gazette), Utkal Sahitya (Journal), Samaja (Broadsheet)
    * Assamese: Asom Rajpatra (Gazette), Asom Sahitya Sabha (Journal), Asomiya Pratidin (Broadsheet)
    * Sanskrit: Samskrita Bharati (Journal), Veda Samhita (Manuscript), Sudharma (Daily Newspaper)
"""

import sys
import os
import io
import json
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image, ImageDraw

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / "augmenter"))

from generic_harfbuzz_shaper import ScriptFontRegistry, UniversalHarfBuzzRenderer
from degradation_engine import IndianDegradationEngine


class BaseTrioOCRGenerator:
    def __init__(self, lang_code: str, script_code: str, lang_tag: str, fonts_dir: Path, data_dir: Path, archetypes: List[str]):
        self.lang_code = lang_code
        self.script_code = script_code
        self.lang_tag = lang_tag
        self.fonts_dir = Path(fonts_dir)
        self.data_dir = Path(data_dir)
        self.archetypes = archetypes

        self.registry = ScriptFontRegistry(self.fonts_dir, script_code, lang_tag)
        self.renderer = UniversalHarfBuzzRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)

        # Load linguistic files
        with open(self.data_dir / f"{lang_code}_words.jsonl", "r", encoding="utf-8") as f:
            self.words_data = [json.loads(line) for line in f]
        with open(self.data_dir / f"{lang_code}_lines.jsonl", "r", encoding="utf-8") as f:
            self.lines_data = [json.loads(line) for line in f]
        with open(self.data_dir / f"{lang_code}_blocks.jsonl", "r", encoding="utf-8") as f:
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

    # TIER 4: WORDS (30% QUOTA)
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

        img, meta = self.renderer.render_line(font_name=font_name, text=word_text, font_size=font_size)
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
            "word": word_text,
            "tokens": meta["tokens"],
            "num_tokens": 1,
            "shaped_glyphs": meta.get("shaped_glyphs", [])
        }
        return img, out_meta

    # TIER 3: LINES (55% QUOTA)
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

        img, meta = self.renderer.render_line(font_name=font_name, text=line_text, font_size=font_size)
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

    # TIER 2: PARAGRAPHS (13% QUOTA)
    def generate_tier_2_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        block_item = self.get_next_blocks(1)[0]
        block_text = block_item["text"]

        sentences = [s.strip() for s in re.split(r'(?<=[\.\?\!।॥])\s+', block_text) if s.strip()]
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
        canvas = Image.new("RGB", (canvas_w, canvas_h), color=(250, 248, 243))
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
            "text": "\n".join(full_text),
            "tokens": all_tokens,
            "num_tokens": len(all_tokens),
            "num_lines": len(rendered_lines)
        }
        return canvas, out_meta

    # TIER 1: FULL PAGES (2% QUOTA)
    def generate_tier_1_sample(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1000, 1400
        canvas = Image.new("RGB", (page_w, page_h), color=(252, 250, 245))
        draw = ImageDraw.Draw(canvas)

        title_text = random.choice(self.archetypes)
        supporting = self.registry.get_supporting_fonts(title_text)
        font_name = random.choice(supporting) if supporting else random.choice(self.font_names)
        title_font_size = 32
        body_font_size = 18

        all_tokens = []
        full_text = []
        t_w = self.renderer.get_text_width(font_name, title_text, font_size=title_font_size)
        title_x = max(40, (page_w - t_w) // 2)
        title_y = 50

        try:
            t_img, t_meta = self.renderer.render_line(font_name=font_name, text=title_text, font_size=title_font_size)
            canvas.paste(t_img, (title_x, title_y))
            for tok in t_meta["tokens"]:
                bx = tok["bbox"]
                if bx != [0, 0, 0, 0]:
                    all_tokens.append({
                        "text": tok["text"],
                        "bbox": [bx[0] + title_x, bx[1] + title_y, bx[2] + title_x, bx[3] + title_y]
                    })
            full_text.append(title_text)
        except Exception:
            pass

        draw.line([(40, 110), (page_w - 40, 110)], fill=(80, 80, 80), width=2)
        draw.line([(40, 114), (page_w - 40, 114)], fill=(120, 120, 120), width=1)

        # 2 Column layout
        col_w = (page_w - 120) // 2
        col1_x = 40
        col2_x = 40 + col_w + 40
        draw.line([(col1_x + col_w + 20, 130), (col1_x + col_w + 20, page_h - 60)], fill=(200, 200, 200), width=1)

        blocks = self.get_next_blocks(6)
        curr_y1 = 130
        curr_y2 = 130

        for idx, blk in enumerate(blocks):
            lines = [l.strip() for l in blk["text"].split("।") if len(l.strip()) > 15][:4]
            if not lines:
                lines = [l.strip() for l in blk["text"].split(".") if len(l.strip()) > 15][:4]
            col_x = col1_x if idx % 2 == 0 else col2_x
            curr_y = curr_y1 if idx % 2 == 0 else curr_y2

            for l_txt in lines:
                if curr_y > page_h - 80:
                    break
                trimmed_txt = l_txt[:45] + "।"
                try:
                    l_img, l_meta = self.renderer.render_line(font_name=font_name, text=trimmed_txt, font_size=body_font_size)
                    canvas.paste(l_img, (col_x, curr_y))
                    for tok in l_meta["tokens"]:
                        bx = tok["bbox"]
                        if bx != [0, 0, 0, 0]:
                            all_tokens.append({
                                "text": tok["text"],
                                "bbox": [bx[0] + col_x, bx[1] + curr_y, bx[2] + col_x, bx[3] + curr_y]
                            })
                    full_text.append(trimmed_txt)
                    curr_y += l_img.height + 4
                except Exception:
                    continue

            if idx % 2 == 0:
                curr_y1 = curr_y + 15
            else:
                curr_y2 = curr_y + 15

        applied_ops = []
        if not is_clean:
            res = self.augmenter.augment_pipeline(canvas)
            canvas, applied_ops = res[0], res[1]

        out_meta = {
            "tier": "Tier_1_FullPage",
            "lang": self.lang_code,
            "script": self.script_code,
            "font_name": font_name,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops,
            "canvas_size": list(canvas.size),
            "text": "\n".join(full_text),
            "tokens": all_tokens,
            "num_tokens": len(all_tokens)
        }
        return canvas, out_meta

    generate_full_page_sample = generate_tier_1_sample
    generate_paragraph_sample = generate_tier_2_sample
    generate_line_sample = generate_tier_3_sample
    generate_word_sample = generate_tier_4_sample

    def generate_sample_by_tier(self, tier: str, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        if tier == "word":
            return self.generate_tier_4_sample(is_clean=is_clean)
        elif tier == "line":
            return self.generate_tier_3_sample(is_clean=is_clean)
        elif tier == "paragraph":
            return self.generate_tier_2_sample(is_clean=is_clean)
        elif tier == "full_page":
            return self.generate_tier_1_sample(is_clean=is_clean)
        else:
            return self.generate_tier_3_sample(is_clean=is_clean)


class OdiaMultiTierOCRGenerator(BaseTrioOCRGenerator):
    def __init__(self, fonts_dir: Path, data_dir: Path):
        archetypes = [
            "ଓଡ଼ିଶା ରାଜପତ୍ର | ସାଧାରଣ ପ୍ରଶାସନ ଓ ସଂସଦୀୟ ବ୍ୟାପାର ବିଭାଗ",
            "ଉତ୍କଳ ସାହିତ୍ୟ ପତ୍ରିକା | ପ୍ରାଚୀନ ଓ ଆଧୁନିକ ଓଡ଼ିଆ ସାହିତ୍ୟ",
            "ସମାଜ ଦୈନିକ ଖବରକାଗଜ | ରାଜ୍ୟ ତଥା ଜାତୀୟ ମୁଖ୍ୟ ସମ୍ବାଦ"
        ]
        super().__init__("odia", "Orya", "ori", fonts_dir, data_dir, archetypes)


class AssameseMultiTierOCRGenerator(BaseTrioOCRGenerator):
    def __init__(self, fonts_dir: Path, data_dir: Path):
        archetypes = [
            "অসম ৰাজপত্ৰ | প্ৰশাসনীয় সংস্কাৰ আৰু অধিসূচনা বিভাগ",
            "অসম সাহিত্য সভা পত্ৰিকা | অসমীয়া ভাষা সাহিত্য আৰু কৃষ্টি",
            "অসমীয়া প্ৰতিদিন বাতৰিকাকত | ৰাজ্যিক আৰু ৰাষ্ট্ৰীয় প্ৰধান বাতৰি"
        ]
        super().__init__("assamese", "Beng", "asm", fonts_dir, data_dir, archetypes)


class SanskritMultiTierOCRGenerator(BaseTrioOCRGenerator):
    def __init__(self, fonts_dir: Path, data_dir: Path):
        archetypes = [
            "संस्कृतभारती पत्रिका | प्राच्यविद्या संशोधनम् तथा दार्शनिक विमर्शः",
            "वेदशास्त्र संहिता | उपनिषद् भाष्यम् तथा वैदिक वाङ्मयम्",
            "सुधर्मा संस्कृत दैनिक वृत्तपत्रम् | राष्ट्रिय वार्ता विशेषाङ्कः"
        ]
        super().__init__("sanskrit", "Deva", "san", fonts_dir, data_dir, archetypes)
