"""
Master Multi-Tier Synthetic OCR Generator for Konkani (gom_Deva)
Inherits from HindiMultiTierOCRGenerator to reuse production-hardened CTL shaping,
baseline anchoring, diacritic ownership, and multi-tier layout engines.
Enforces strict column geometry, word-wrapping, and collision prevention.
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


class KonkaniMultiTierOCRGenerator(HindiMultiTierOCRGenerator):
    """
    Konkani (gom_Deva) Synthetic OCR Engine.
    Configured specifically for Goan Konkani typography, Goan cultural archetypes, and linguistic assets.
    """

    def __init__(self, fonts_dir: Path, processed_data_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.data_dir = Path(processed_data_dir)

        from harfbuzz_shaper import FontRegistry, HarfBuzzTokenRenderer
        from degradation_engine import IndianDegradationEngine

        print("[Agent-Shaper] Initializing FontRegistry for Konkani (Devanagari)...")
        self.registry = FontRegistry(self.fonts_dir)
        self.renderer = HarfBuzzTokenRenderer(self.registry)
        self.augmenter = IndianDegradationEngine(seed=42)

        words_path = self.data_dir / "konkani_words.jsonl"
        lines_path = self.data_dir / "konkani_lines.jsonl"
        blocks_path = self.data_dir / "konkani_blocks.jsonl"

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
        self.lang_code = "gom"
        self.script_code = "Deva"
        print(f"[Agent-Shaper] Loaded {len(self.lines_data):,} Konkani lines, {len(self.words_data):,} words, {len(self.blocks_data):,} blocks.")
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
                        if y_cursor >= max_y:
                            return y_cursor
                    current_line = word

            if current_line:
                try:
                    self.renderer.paste_text(canvas, font_name, current_line, (x, y_cursor), font_size=font_size, ink_rgb=ink_rgb)
                except Exception:
                    pass
                y_cursor += line_height
                if y_cursor >= max_y:
                    return y_cursor

            # Inter-sentence subtle spacing
            y_cursor += line_height // 3
            if y_cursor >= max_y:
                return y_cursor

        return y_cursor

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
    # TIER 1: GOAN KONKANI AUTHENTIC ARCHETYPES (WITH ZERO-COLLISION WORD WRAP)
    # =========================================================================
    def generate_literary_magazine_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (252, 249, 242))
        draw = ImageDraw.Draw(canvas)

        draw.rectangle([(40, 40), (page_w - 40, page_h - 40)], outline=(120, 90, 40) if not is_clean else (0, 0, 0), width=2)
        draw.rectangle([(46, 46), (page_w - 46, page_h - 46)], outline=(180, 150, 90) if not is_clean else (100, 100, 100), width=1)

        titles = ["जाग - कोंकणी म्हयनाळें", "गोवा कोंकणी अकादमी पत्रिका", "सुनापरान्त साहित्य विशेषांक", "शणै गोंयबाब स्मृती निबंध"]
        title = random.choice(titles)
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", title, (page_w // 2 - 230, 65), font_size=36, ink_rgb=(40, 20, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "गोंयकारपण आनी अस्मिताय • अंक ४ • वर्स ३२ | मोल: ₹ २५.००", (page_w // 2 - 220, 115), font_size=18, ink_rgb=(80, 70, 60))
        draw.line([(70, 145), (page_w - 70, 145)], fill=(120, 90, 40), width=2)

        self.renderer.paste_text(canvas, "YatraOne-Regular.ttf", "विशेष साहित्य स्तम्भ: समकालीन कोंकणी कविता", (80, 165), font_size=24, ink_rgb=(20, 20, 20))
        draw.line([(80, 200), (500, 200)], fill=(160, 120, 60), width=1)

        verse_lines = self.get_next_lines(6)
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
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "विचार मंथन: कोंकणी भास, समाज आनी संस्कृती", (80, y_cursor), font_size=24, ink_rgb=(10, 10, 10))
        y_cursor += 40

        # 2 Strictly Bounded Columns
        margin_x = 80
        gutter = 40
        col_w = (page_w - 2 * margin_x - gutter) // 2  # ~520 px
        col1_x = margin_x
        col2_x = margin_x + col_w + gutter
        bottom_limit = page_h - 100

        col1_texts = [item['text'] for item in self.get_next_lines(12)]
        col2_texts = [item['text'] for item in self.get_next_lines(12)]

        self.render_wrapped_paragraph(
            canvas, "NotoSansDevanagari.ttf", col1_texts,
            x=col1_x, y_start=y_cursor, max_w=col_w - 10, max_y=bottom_limit,
            font_size=19, line_height=29, ink_rgb=(25, 25, 25)
        )

        draw.line([(col1_x + col_w + gutter // 2, y_cursor), (col1_x + col_w + gutter // 2, bottom_limit - 20)], fill=(180, 170, 160), width=1)

        self.render_wrapped_paragraph(
            canvas, "NotoSansDevanagari.ttf", col2_texts,
            x=col2_x, y_start=y_cursor, max_w=col_w - 10, max_y=bottom_limit,
            font_size=19, line_height=29, ink_rgb=(25, 25, 25)
        )

        # Footnote
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "पान क्रमांक : ४८", (page_w // 2 - 45, page_h - 65), font_size=16, ink_rgb=(100, 100, 100))

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_A_Sahityik_Patrika",
            "lang": self.lang_code,
            "script": self.script_code,
            "title": title,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_official_gazette_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (250, 248, 242))
        draw = ImageDraw.Draw(canvas)

        draw.rectangle([(50, 50), (page_w - 50, page_h - 50)], outline=(0, 0, 0), width=2)
        draw.rectangle([(56, 56), (page_w - 56, page_h - 56)], outline=(0, 0, 0), width=1)

        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "गोवा शासन राजपत्र", (page_w // 2 - 160, 80), font_size=38, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "THE GOA GOVERNMENT GAZETTE", (page_w // 2 - 190, 130), font_size=20, ink_rgb=(30, 30, 30))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "सचिवालय, पर्वरी-गोंय | अधिकृत प्रसिद्धी", (page_w // 2 - 160, 160), font_size=18, ink_rgb=(40, 40, 40))
        draw.line([(80, 195), (page_w - 80, 195)], fill=(0, 0, 0), width=2)

        ref_num = f"अधिसूचना क्रमांक: GOA/REV/{random.randint(2023, 2026)}/{random.randint(1000, 9999)}"
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", ref_num, (90, 215), font_size=18, ink_rgb=(20, 20, 20))
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "दिनांक: १५ ऑगस्ट, २०२६", (page_w - 290, 215), font_size=18, ink_rgb=(20, 20, 20))
        draw.line([(80, 245), (page_w - 80, 245)], fill=(120, 120, 120), width=1)

        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "महसूल आनी नगर नियोजन विभाग: सार्वजनीक सुचोवण", (page_w // 2 - 250, 265), font_size=24, ink_rgb=(0, 0, 0))

        gazette_texts = [item['text'] for item in self.get_next_lines(18)]
        bottom_limit = page_h - 180

        self.render_wrapped_paragraph(
            canvas, "NotoSansDevanagari.ttf", gazette_texts,
            x=90, y_start=315, max_w=page_w - 180, max_y=bottom_limit,
            font_size=20, line_height=32, ink_rgb=(20, 20, 20)
        )

        # Signature and seal
        y_sign = page_h - 140
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "आज्ञेन आनी नांवान,", (page_w - 320, y_sign), font_size=18, ink_rgb=(30, 30, 30))
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "संचालक आनी सचिव (महसूल)", (page_w - 340, y_sign + 30), font_size=20, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "गोवा शासन, सचिवालय, पर्वरी", (page_w - 330, y_sign + 60), font_size=18, ink_rgb=(40, 40, 40))

        draw.ellipse([(140, page_h - 160), (260, page_h - 40)], outline=(30, 60, 130), width=3)
        draw.ellipse([(148, page_h - 152), (252, page_h - 48)], outline=(30, 60, 130), width=1)
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "GOA GOVT", (168, page_h - 118), font_size=16, ink_rgb=(30, 60, 130))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "SEAL", (182, page_h - 95), font_size=16, ink_rgb=(30, 60, 130))

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_B_Official_Gazette",
            "lang": self.lang_code,
            "script": self.script_code,
            "ref_num": ref_num,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_newspaper_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Archetype C: Authentic 3-Column Regional Broadsheet Newspaper.
        Enforces strict column geometry, zero text collision, and professional styling.
        """
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (248, 245, 238))
        draw = ImageDraw.Draw(canvas)

        # 1. Newspaper Masthead
        titles = ["दैनिक सुनापरान्त", "भांगरभूंय - गोंयचें खबरांपत्र", "कोंकणी वार्ता"]
        title = random.choice(titles)
        self.renderer.paste_text(canvas, "YatraOne-Regular.ttf", title, (page_w // 2 - 220, 50), font_size=46, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "पणजी / मडगांव • सोमवार, २० सप्टेंबर २०२६ • अंक १६० | पाने ८ | मोल ₹ ५.००", (page_w // 2 - 260, 115), font_size=18, ink_rgb=(60, 60, 60))
        draw.line([(50, 145), (page_w - 50, 145)], fill=(0, 0, 0), width=3)
        draw.line([(50, 150), (page_w - 50, 150)], fill=(0, 0, 0), width=1)

        # 2. Main Lead Banner Headline
        lead_headline = "गोंयांत पर्यटन आनी पर्यावरणाचे समतोला खातीर नवे नेम जारी"
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", lead_headline, (60, 165), font_size=32, ink_rgb=(0, 0, 0))
        draw.line([(60, 205), (page_w - 60, 205)], fill=(150, 150, 150), width=1)

        # 3. Geometric 3-Column Specifications
        margin_x = 60
        gutter = 30
        num_cols = 3
        # 1240 - 120 = 1120. Total gutter = 2 * 30 = 60. 1120 - 60 = 1060.
        col_w = (page_w - 2 * margin_x - (num_cols - 1) * gutter) // num_cols  # 353 px
        y_start = 220
        max_y = page_h - 90

        col_subheads = [
            "पर्यटन मोसमाची तयारी सुरु",
            "शेती आनी पर्यावरण राखण",
            "शिटूक रावपाचो संदेश"
        ]

        for col_idx in range(num_cols):
            cx = margin_x + col_idx * (col_w + gutter)
            
            # Sub-headline for column
            subhead = col_subheads[col_idx]
            self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", subhead, (cx, y_start), font_size=22, ink_rgb=(10, 30, 80))
            draw.line([(cx, y_start + 30), (cx + col_w - 10, y_start + 30)], fill=(180, 180, 180), width=1)

            # Stream wrapped paragraphs for this column
            col_texts = [item['text'] for item in self.get_next_lines(12)]
            self.render_wrapped_paragraph(
                canvas=canvas,
                font_name="NotoSansDevanagari.ttf",
                text_stream=col_texts,
                x=cx,
                y_start=y_start + 40,
                max_w=col_w - 10,
                max_y=max_y,
                font_size=18,
                line_height=27,
                ink_rgb=(20, 20, 20)
            )

            # Draw vertical column dividing line in the gutter
            if col_idx < num_cols - 1:
                div_x = cx + col_w + gutter // 2
                draw.line([(div_x, y_start), (div_x, max_y)], fill=(190, 190, 190), width=1)

        # Bottom Dateline & Footer Bar
        draw.line([(50, page_h - 75), (page_w - 50, page_h - 75)], fill=(0, 0, 0), width=1)
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "सुनापरान्त मुख्य कार्यालय: पाटो प्लाझा, पणजी-गोंय | मुद्रक आनी प्रकाशक", (page_w // 2 - 250, page_h - 60), font_size=16, ink_rgb=(80, 80, 80))

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_C_Newspaper_Spread",
            "lang": self.lang_code,
            "script": self.script_code,
            "title": title,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_judicial_order_page(self, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        page_w, page_h = 1240, 1754
        canvas = Image.new("RGB", (page_w, page_h), (255, 255, 255) if is_clean else (252, 250, 244))
        draw = ImageDraw.Draw(canvas)

        draw.rectangle([(50, 50), (page_w - 50, page_h - 50)], outline=(40, 40, 40), width=2)

        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "उत्तर गोंय जिल्हा आनी सत्र न्यायालय, पणजी", (page_w // 2 - 270, 80), font_size=32, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "विधिक वाद पत्र (CIVIL PETITION ORDER)", (page_w // 2 - 180, 125), font_size=20, ink_rgb=(40, 40, 40))
        draw.line([(80, 155), (page_w - 80, 155)], fill=(40, 40, 40), width=2)

        case_no = f"दिवाणी खटलो क्र. {random.randint(10, 999)} / {random.randint(2022, 2026)}"
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", case_no, (90, 175), font_size=20, ink_rgb=(20, 20, 20))
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "तारीख: २८ जुलय, २०२६", (page_w - 270, 175), font_size=18, ink_rgb=(20, 20, 20))

        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", "वादी: श्रीमती मारिया फर्नांडीस, रा. म्हापसा, गोंय", (90, 215), font_size=20, ink_rgb=(30, 30, 30))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "--- विरूद्ध ---", (page_w // 2 - 50, 245), font_size=18, ink_rgb=(80, 80, 80))
        self.renderer.paste_text(canvas, "NotoSansDevanagari.ttf", "प्रतिवादी: श्री आंतोन डिसोझा आनी हेर, रा. कलंगूट, गोंय", (90, 275), font_size=20, ink_rgb=(30, 30, 30))
        draw.line([(80, 310), (page_w - 80, 310)], fill=(120, 120, 120), width=1)

        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "हुकूम आनी निकाल पत्र", (page_w // 2 - 100, 330), font_size=24, ink_rgb=(10, 10, 10))

        order_texts = [item['text'] for item in self.get_next_lines(18)]
        bottom_limit = page_h - 180

        self.render_wrapped_paragraph(
            canvas, "NotoSansDevanagari.ttf", order_texts,
            x=90, y_start=380, max_w=page_w - 180, max_y=bottom_limit,
            font_size=20, line_height=32, ink_rgb=(20, 20, 20)
        )

        y_judge = page_h - 140
        self.renderer.paste_text(canvas, "NotoSerifDevanagari.ttf", "जिल्हा आनी सत्र न्यायाधीश", (page_w - 320, y_judge), font_size=22, ink_rgb=(10, 10, 10))
        self.renderer.paste_text(canvas, "Rajdhani-Medium.ttf", "उत्तर गोंय जिल्हा न्यायालय, पणजी", (page_w - 330, y_judge + 35), font_size=18, ink_rgb=(40, 40, 40))

        draw.ellipse([(140, page_h - 160), (260, page_h - 40)], outline=(160, 30, 30), width=3)
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "COURT OF GOA", (158, page_h - 115), font_size=15, ink_rgb=(160, 30, 30))
        self.renderer.paste_text(canvas, "Rajdhani-Bold.ttf", "SEAL", (185, page_h - 95), font_size=15, ink_rgb=(160, 30, 30))

        if is_clean:
            final_img = canvas
            applied_ops = ["pristine_digital_scan"]
        else:
            final_img, applied_ops = self.augmenter.augment_pipeline(canvas)

        meta = {
            "tier": "Tier_1_Full_Page",
            "archetype": "Archetype_D_Judicial_Order",
            "lang": self.lang_code,
            "script": self.script_code,
            "case_no": case_no,
            "is_clean": is_clean,
            "applied_augmentations": applied_ops
        }
        return final_img, meta

    def generate_full_page_sample(self, archetype: Optional[str] = None, is_clean: bool = False) -> Tuple[Image.Image, Dict[str, Any]]:
        archetypes = [
            ("Archetype_A_Sahityik_Patrika", self.generate_literary_magazine_page),
            ("Archetype_B_Official_Gazette", self.generate_official_gazette_page),
            ("Archetype_C_Newspaper_Spread", self.generate_newspaper_page),
            ("Archetype_D_Judicial_Order", self.generate_judicial_order_page),
        ]
        if archetype:
            for name, func in archetypes:
                if name == archetype:
                    return func(is_clean=is_clean)
        _, func = random.choice(archetypes)
        return func(is_clean=is_clean)
