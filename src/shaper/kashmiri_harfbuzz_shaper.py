"""
Agent-Shaper: Kashmiri HarfBuzz OpenType CTL Shaper & FreeType Glyph Compositor
Specialized for Kashmiri Perso-Arabic Script (Arab), Right-to-Left (RTL) Direction,
Nastaliq Cascades, and Kashmiri Extended Orthography (ٲ, ۆ, ۄ, ؠ, ێ, ٛ, ٚ, ٗ).

Enforces:
1. 100% TrueType cmap extraction for all verified Kashmiri fonts.
2. Invariant: Zero Glyph ID 0 (.notdef / tofu boxes).
3. Explicit RTL OpenType shaping: direction="rtl", script="Arab", language="kas".
4. Proven Left-to-Right FreeType compositing of HarfBuzz visual-ordered buffer.
5. Dynamic vertical zone padding accommodating hanging nuqtas and floating aerab.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
import uharfbuzz as hb
import freetype

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ShaperError(Exception):
    pass


class GlyphGateError(ShaperError):
    pass


class NotdefGlyphError(ShaperError):
    pass


class KashmiriFontRegistry:
    """Manages TrueType cmaps, FreeType faces, and HarfBuzz font instances for Kashmiri typography."""

    CONTROL_AND_SPACE_CODES = {
        0x20, 0x09, 0x0A, 0x0D,
        0x00A0, 0x200C, 0x200D, 0x200B,
        0x200E, 0x200F, 0x061C, 0x00AD
    }

    FONT_STYLES = {
        "Afan_Koshur_Naksh.ttf": "kashmiri_naskh_modern",
        "NotoNastaliqUrdu-Regular.ttf": "nastaliq_cascade",
        "NotoNaskhArabic-Regular.ttf": "naskh_book",
        "Amiri-Regular.ttf": "scholarly_naskh",
        "Amiri-Bold.ttf": "scholarly_bold",
        "Lateef-Regular.ttf": "literary_naskh",
        "NotoSansArabic-Regular.ttf": "modern_sans"
    }

    def __init__(self, fonts_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.cmaps: Dict[str, Dict[int, str]] = {}
        self.hb_fonts: Dict[str, hb.Font] = {}
        self.ft_faces: Dict[str, freetype.Face] = {}
        self.font_paths: Dict[str, Path] = {}
        self.font_metrics: Dict[str, Dict[str, int]] = {}

        self._load_fonts()

    def _load_fonts(self):
        font_files = sorted(list(self.fonts_dir.glob("*.ttf")) + list(self.fonts_dir.glob("*.otf")))
        print(f"[Agent-Shaper] Loading Kashmiri font suite from {self.fonts_dir}...")

        loaded = 0
        for fpath in font_files:
            fname = fpath.name
            try:
                tt = TTFont(str(fpath))
                cmap = tt.getBestCmap()
                if not cmap:
                    continue

                hhea = tt.get('hhea')
                head = tt.get('head')
                upem = head.unitsPerEm if head else 1000
                ascent = hhea.ascent if hhea else int(upem * 0.85)
                descent = hhea.descent if hhea else int(upem * -0.35)

                with open(fpath, "rb") as f:
                    font_data = f.read()
                face = hb.Face(font_data)
                hb_font = hb.Font(face)

                ft_face = freetype.Face(str(fpath))

                self.cmaps[fname] = cmap
                self.hb_fonts[fname] = hb_font
                self.ft_faces[fname] = ft_face
                self.font_paths[fname] = fpath
                self.font_metrics[fname] = {
                    "units_per_em": upem,
                    "ascent": ascent,
                    "descent": descent
                }
                loaded += 1
            except Exception as e:
                print(f"[Agent-Shaper] Skipping unreadable font {fname}: {e}")

        print(f"[Agent-Shaper] Successfully registered {loaded} Kashmiri fonts.")

    def sanitize_kashmiri_text(self, text: str) -> str:
        # Strip rare Quranic annotation signs that are not part of standard Kashmiri orthography
        rare_marks = {0x06EA, 0x06ED, 0x06EB, 0x06DF, 0x06E0, 0x06E2, 0x06E3, 0x06D6, 0x06D7, 0x06D8, 0x06D9, 0x06DA, 0x06DB, 0x06DC}
        return "".join(ch for ch in text if ord(ch) not in rare_marks)

    def verify_glyph_coverage(self, font_name: str, text: str) -> bool:
        if font_name not in self.cmaps:
            raise GlyphGateError(f"Font '{font_name}' not registered.")

        clean_text = self.sanitize_kashmiri_text(text)
        cmap = self.cmaps[font_name]
        missing = []
        for ch in clean_text:
            code = ord(ch)
            if code in self.CONTROL_AND_SPACE_CODES:
                continue
            if code not in cmap:
                missing.append(f"'{ch}' (U+{code:04X})")

        if missing:
            raise GlyphGateError(f"Font '{font_name}' missing Kashmiri codepoints: {', '.join(set(missing))}")

        return True

    def get_supporting_fonts(self, text: str, style_filter: Optional[str] = None) -> List[str]:
        """Returns all registered fonts that have 100% CMAP coverage for the specified text."""
        clean_text = self.sanitize_kashmiri_text(text)
        supporting = []
        for font_name, cmap in self.cmaps.items():
            if style_filter and style_filter.lower() not in self.FONT_STYLES.get(font_name, "").lower():
                continue
            has_all = True
            for ch in clean_text:
                code = ord(ch)
                if code in self.CONTROL_AND_SPACE_CODES:
                    continue
                if code not in cmap:
                    has_all = False
                    break
            if has_all:
                supporting.append(font_name)
        return supporting

    def shape_text(
        self,
        font_name: str,
        text: str,
        script: str = "Arab",
        direction: str = "rtl",
        language: str = "kas"
    ) -> Tuple[List[Dict[str, Any]], Any]:
        clean_text = self.sanitize_kashmiri_text(text)
        self.verify_glyph_coverage(font_name, clean_text)

        hb_font = self.hb_fonts[font_name]
        buf = hb.Buffer()
        buf.add_str(clean_text)
        buf.direction = direction
        buf.script = script
        buf.language = language

        hb.shape(hb_font, buf)

        infos = buf.glyph_infos
        positions = buf.glyph_positions

        shaped_glyphs = []
        for info, pos in zip(infos, positions):
            gid = info.codepoint
            if gid == 0:
                raise NotdefGlyphError(
                    f"HarfBuzz produced .notdef (Glyph 0) in font '{font_name}' for text: '{text}'"
                )

            shaped_glyphs.append({
                "glyph_id": gid,
                "cluster": info.cluster,
                "x_advance": pos.x_advance,
                "y_advance": pos.y_advance,
                "x_offset": pos.x_offset,
                "y_offset": pos.y_offset
            })

        return shaped_glyphs, buf


class KashmiriHarfBuzzRenderer:
    """
    Renders shaped RTL Kashmiri text via HarfBuzz + FreeType Glyph Compositing.
    Correctly composites the visual-ordered HarfBuzz buffer from left to right,
    guaranteeing authentic connected cursive letterforms and zero inverted glyphs.
    """

    def __init__(self, registry: KashmiriFontRegistry):
        self.registry = registry

    def render_line(
        self,
        font_name: str,
        text: str,
        font_size: int = 38,
        text_color: Tuple[int, int, int] = (20, 20, 20),
        bg_color: Tuple[int, int, int] = (246, 242, 234),
        min_width: Optional[int] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        shaped_glyphs, hb_buf = self.registry.shape_text(
            font_name, text, script="Arab", direction="rtl", language="kas"
        )

        metrics = self.registry.font_metrics[font_name]
        upem = metrics["units_per_em"]
        scale = font_size / upem

        ascender_px = int(metrics["ascent"] * scale)
        descender_px = abs(int(metrics["descent"] * scale))

        ft_face = self.registry.ft_faces[font_name]
        ft_face.set_pixel_sizes(0, font_size)

        is_nastaliq = "nastaliq" in self.registry.FONT_STYLES.get(font_name, "").lower()
        top_zone_pad = max(int(font_size * (0.75 if is_nastaliq else 0.45)), 24)
        bottom_zone_pad = max(int(font_size * (0.75 if is_nastaliq else 0.45)), 26)
        side_pad = max(int(font_size * 0.40), 20)

        tot_advance_x = sum(int(pos.x_advance * scale) for pos in hb_buf.glyph_positions)
        content_w = tot_advance_x + (side_pad * 2)
        
        canvas_w = max(content_w, min_width) if min_width else content_w
        canvas_h = (ascender_px + descender_px) + top_zone_pad + bottom_zone_pad
        baseline_y = top_zone_pad + ascender_px

        # Offset to center text if min_width is wider than content
        x_shift = (canvas_w - content_w) // 2 if min_width and min_width > content_w else 0

        alpha_canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)

        # The proven FreeType compositing algorithm (Left-to-Right on visual HarfBuzz buffer)
        cur_x = side_pad + x_shift
        for info, pos in zip(hb_buf.glyph_infos, hb_buf.glyph_positions):
            gid = info.codepoint
            ft_face.load_glyph(gid, freetype.FT_LOAD_RENDER)
            slot = ft_face.glyph
            bitmap = slot.bitmap

            bw, bh = bitmap.width, bitmap.rows
            left, top = slot.bitmap_left, slot.bitmap_top

            x_off = int(pos.x_offset * scale)
            y_off = int(pos.y_offset * scale)

            gx = cur_x + x_off + left
            gy = baseline_y - y_off - top

            if bw > 0 and bh > 0:
                glyph_arr = np.array(bitmap.buffer, dtype=np.uint8).reshape((bh, bw))

                x1, y1 = max(0, gx), max(0, gy)
                x2, y2 = min(canvas_w, gx + bw), min(canvas_h, gy + bh)

                src_x1, src_y1 = x1 - gx, y1 - gy
                src_x2, src_y2 = src_x1 + (x2 - x1), src_y1 + (y2 - y1)

                if src_x2 > src_x1 and src_y2 > src_y1:
                    alpha_canvas[y1:y2, x1:x2] = np.maximum(
                        alpha_canvas[y1:y2, x1:x2],
                        glyph_arr[src_y1:src_y2, src_x1:src_x2]
                    )

            cur_x += int(pos.x_advance * scale)

        # Composite onto RGB background
        img_arr = np.full((canvas_h, canvas_w, 3), bg_color, dtype=np.uint8)
        alpha_norm = (alpha_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
        for c in range(3):
            img_arr[:, :, c] = (
                alpha_norm[:, :, 0] * text_color[c] +
                (1.0 - alpha_norm[:, :, 0]) * img_arr[:, :, c]
            ).astype(np.uint8)

        final_img = Image.fromarray(img_arr, "RGB")

        # Calculate bounding box
        mask = (alpha_canvas > 15)
        if np.count_nonzero(mask) > 4:
            rows = np.any(mask, axis=1)
            cols = np.any(mask, axis=0)
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]
            bbox = [int(cmin), int(rmin), int(cmax) + 1, int(rmax) + 1]
        else:
            bbox = [side_pad, top_zone_pad, canvas_w - side_pad, canvas_h - bottom_zone_pad]

        annotation = {
            "text": text,
            "font": font_name,
            "font_style": self.registry.FONT_STYLES.get(font_name, "general"),
            "font_size": font_size,
            "bbox": bbox,
            "canvas_size": [canvas_w, canvas_h],
            "ascender_zone": ascender_px,
            "descender_zone": descender_px,
            "shaped_glyphs_count": len(shaped_glyphs),
            "alpha_canvas": alpha_canvas
        }

        return final_img, annotation
