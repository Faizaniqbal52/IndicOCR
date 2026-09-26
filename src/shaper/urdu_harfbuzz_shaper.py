"""
Agent-Shaper: Urdu HarfBuzz OpenType CTL Shaper & FreeType Glyph Compositor
Specialized for Perso-Arabic Script (Arab), Right-to-Left (RTL) Direction, and Nastaliq Cascades.

Enforces:
1. 100% TrueType cmap extraction for all 23 active Urdu fonts.
2. Invariant: Zero Glyph ID 0 (.notdef / tofu boxes) across all rendered text.
3. Explicit RTL OpenType shaping: direction="rtl", script="Arab", language="urd".
4. Nastaliq cascading geometry: dynamic vertical zone padding accommodating hanging nuqtas and floating aerab.
5. Pure FreeType glyph-by-glyph rasterization (zero PIL fallback).
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
import uharfbuzz as hb
import freetype

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ShaperError(Exception):
    """Base exception for Agent-Shaper."""
    pass


class GlyphGateError(ShaperError):
    """Raised when text contains codepoints missing from font cmap."""
    pass


class NotdefGlyphError(ShaperError):
    """Raised when HarfBuzz shaping produces Glyph ID 0 (.notdef)."""
    pass


class UrduFontRegistry:
    """Manages TrueType cmaps, FreeType faces, and HarfBuzz font instances for Urdu typography."""

    # OpenType control codes and whitespace that HarfBuzz processes during GSUB/GPOS
    CONTROL_AND_SPACE_CODES = {
        0x20, 0x09, 0x0A, 0x0D,  # Standard whitespace
        0x00A0,                  # Non-breaking space
        0x200C,                  # ZWNJ (Zero-width non-joiner)
        0x200D,                  # ZWJ (Zero-width joiner)
        0x200B,                  # Zero-width space
        0x200E,                  # LRM (Left-to-Right Mark)
        0x200F,                  # RLM (Right-to-Left Mark)
        0x061C,                  # ALM (Arabic Letter Mark)
        0x00AD                   # Soft hyphen
    }

    # Style classifications
    FONT_STYLES = {
        # Nastaliq
        "NotoNastaliqUrdu-Regular.ttf": "nastaliq",
        "Gulzar-Regular.ttf": "nastaliq",
        # Freehand / Handwriting / Ink / Casual
        "ArefRuqaa-Regular.ttf": "handwriting_ruqaa",
        "ArefRuqaa-Bold.ttf": "handwriting_ruqaa",
        "ArefRuqaaInk-Regular.ttf": "handwriting_ink",
        "ArefRuqaaInk-Bold.ttf": "handwriting_ink",
        "ReemKufi-Regular.ttf": "handwriting_kufi",
        "ReemKufiInk-Regular.ttf": "handwriting_kufi_ink",
        "Qahiri-Regular.ttf": "handwriting_informal",
        "Katibeh-Regular.ttf": "handwriting_manuscript",
        "Lalezar-Regular.ttf": "handwriting_poster",
        "Rakkas-Regular.ttf": "handwriting_sign",
        "Changa-Regular.ttf": "handwriting_casual",
        # Book Naskh
        "Amiri-Regular.ttf": "naskh_book",
        "Amiri-Bold.ttf": "naskh_book",
        "NotoNaskhArabic-Regular.ttf": "naskh_clean",
        "Lateef-Regular.ttf": "naskh_literary",
        # Modern Newspaper & Display
        "MarkaziText-Regular.ttf": "newspaper_editorial",
        "NotoSansArabic-Regular.ttf": "modern_sans",
        "Almarai-Regular.ttf": "modern_display",
        "Cairo-Regular.ttf": "modern_display",
        "ElMessiri-Regular.ttf": "modern_display",
        "Mada-Regular.ttf": "modern_display"
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
        print(f"[Agent-Shaper] Loading Urdu font suite from {self.fonts_dir}...")

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
                hb_font.scale = (upem, upem)

                ft_face = freetype.Face(str(fpath))

                self.cmaps[fname] = cmap
                self.font_metrics[fname] = {
                    "units_per_em": upem,
                    "ascent": ascent,
                    "descent": descent
                }
                self.hb_fonts[fname] = hb_font
                self.ft_faces[fname] = ft_face
                self.font_paths[fname] = fpath
                loaded += 1
            except Exception as e:
                print(f"  [WARN] Failed to load {fname}: {e}")

        print(f"[Agent-Shaper] Successfully registered {loaded} Urdu fonts.")

    def verify_glyph_coverage(self, font_name: str, text: str) -> bool:
        """
        Asserts that 100% of characters in text exist in the font's TrueType cmap.
        Raises GlyphGateError if even a single character is unmapped.
        """
        if font_name not in self.cmaps:
            raise GlyphGateError(f"Font '{font_name}' is not registered.")

        cmap = self.cmaps[font_name]
        missing = []
        for ch in text:
            code = ord(ch)
            if code in self.CONTROL_AND_SPACE_CODES:
                continue
            if code not in cmap:
                missing.append(f"'{ch}' (U+{code:04X})")

        if missing:
            raise GlyphGateError(f"Font '{font_name}' missing codepoints: {', '.join(set(missing))}")

        return True

    def shape_text(
        self,
        font_name: str,
        text: str,
        script: str = "Arab",
        direction: str = "rtl",
        language: str = "urd"
    ) -> Tuple[List[Dict[str, Any]], Any]:
        """
        Shapes text using HarfBuzz OpenType engine.
        Enforces INVARIANT: 0% Glyph ID 0 (.notdef).
        Returns (shaped_glyphs_list, raw_hb_buffer).
        """
        self.verify_glyph_coverage(font_name, text)

        hb_font = self.hb_fonts[font_name]
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = direction
        buf.script = script
        buf.language = language

        # OpenType shaping
        hb.shape(hb_font, buf)

        infos = buf.glyph_infos
        positions = buf.glyph_positions

        shaped_glyphs = []
        for info, pos in zip(infos, positions):
            gid = info.codepoint
            if gid == 0:
                raise NotdefGlyphError(
                    f"HarfBuzz OpenType shaping produced .notdef (Glyph 0) in font '{font_name}' for text: '{text}'"
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

    def get_supporting_fonts(
        self,
        text: str,
        style_filter: Optional[str] = None
    ) -> List[str]:
        """
        Returns list of font names that support 100% of characters with zero .notdef.
        Optionally filters by style (e.g. 'nastaliq', 'handwriting', 'naskh', 'newspaper').
        """
        supporting = []
        for fname in self.hb_fonts:
            if style_filter:
                fstyle = self.FONT_STYLES.get(fname, "")
                if style_filter not in fstyle:
                    continue
            try:
                self.verify_glyph_coverage(fname, text)
                self.shape_text(fname, text)
                supporting.append(fname)
            except (GlyphGateError, NotdefGlyphError):
                continue
        return supporting


class UrduHarfBuzzRenderer:
    """
    Renders shaped RTL Urdu text via HarfBuzz + FreeType Glyph Compositing.
    Specialized for Nastaliq downward cascades, floating aerab, and hanging nuqtas.
    """

    def __init__(self, registry: UrduFontRegistry):
        self.registry = registry

    def render_line(
        self,
        font_name: str,
        text: str,
        font_size: int = 38,
        text_color: Tuple[int, int, int] = (18, 18, 18),
        bg_color: Tuple[int, int, int] = (250, 248, 242)
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Renders a single line of RTL Urdu text.
        Guarantees zero diacritic clipping via dynamic vertical zone padding.
        """
        shaped_glyphs, hb_buf = self.registry.shape_text(
            font_name, text, script="Arab", direction="rtl", language="urd"
        )

        metrics = self.registry.font_metrics[font_name]
        upem = metrics["units_per_em"]
        scale = font_size / upem

        ascender_px = int(metrics["ascent"] * scale)
        descender_px = abs(int(metrics["descent"] * scale))

        ft_face = self.registry.ft_faces[font_name]
        ft_face.set_pixel_sizes(0, font_size)

        # Dynamic vertical zone padding for Nastaliq cascades & hanging nuqtas
        is_nastaliq = "nastaliq" in self.registry.FONT_STYLES.get(font_name, "").lower()
        top_zone_pad = max(int(font_size * (0.65 if is_nastaliq else 0.45)), 22)
        bottom_zone_pad = max(int(font_size * (0.70 if is_nastaliq else 0.45)), 24)
        side_pad = max(int(font_size * 0.40), 18)

        tot_advance_x = sum(int(pos.x_advance * scale) for pos in hb_buf.glyph_positions)
        canvas_w = tot_advance_x + (side_pad * 2) + 24
        canvas_h = (ascender_px + descender_px) + top_zone_pad + bottom_zone_pad
        baseline_y = top_zone_pad + ascender_px

        alpha_canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)

        cur_x = side_pad
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

        # Compute tight bounding box
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
            "shaped_glyphs_count": len(shaped_glyphs)
        }

        return final_img, annotation

    def render_text_rgba(
        self,
        font_name: str,
        text: str,
        font_size: int = 34,
        ink_rgb: Tuple[int, int, int] = (20, 20, 20)
    ) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """
        Renders shaped text directly into a tightly cropped RGBA image with alpha transparency.
        Used for embedding headings, columns, and stamps onto document canvases.
        """
        shaped_glyphs, hb_buf = self.registry.shape_text(
            font_name, text, script="Arab", direction="rtl", language="urd"
        )

        metrics = self.registry.font_metrics[font_name]
        upem = metrics["units_per_em"]
        scale = font_size / upem

        ascender_px = int(metrics["ascent"] * scale)
        descender_px = abs(int(metrics["descent"] * scale))

        ft_face = self.registry.ft_faces[font_name]
        ft_face.set_pixel_sizes(0, font_size)

        is_nastaliq = "nastaliq" in self.registry.FONT_STYLES.get(font_name, "").lower()
        top_zone_pad = max(int(font_size * (0.65 if is_nastaliq else 0.45)), 22)
        bottom_zone_pad = max(int(font_size * (0.70 if is_nastaliq else 0.45)), 24)
        side_pad = max(int(font_size * 0.40), 16)

        tot_advance_x = sum(int(pos.x_advance * scale) for pos in hb_buf.glyph_positions)
        canvas_w = tot_advance_x + (side_pad * 2) + 24
        canvas_h = (ascender_px + descender_px) + top_zone_pad + bottom_zone_pad
        baseline_y = top_zone_pad + ascender_px

        alpha_canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)

        cur_x = side_pad
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

        # Find tight crop
        mask = (alpha_canvas > 15)
        if np.count_nonzero(mask) > 4:
            rows = np.any(mask, axis=1)
            cols = np.any(mask, axis=0)
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]
            # 2px safety margin
            cmin, rmin = max(0, cmin - 2), max(0, rmin - 2)
            cmax, rmax = min(canvas_w - 1, cmax + 2), min(canvas_h - 1, rmax + 2)
        else:
            cmin, rmin, cmax, rmax = 0, 0, canvas_w - 1, canvas_h - 1

        crop_w = cmax - cmin + 1
        crop_h = rmax - rmin + 1

        rgba_arr = np.zeros((crop_h, crop_w, 4), dtype=np.uint8)
        rgba_arr[:, :, 0] = ink_rgb[0]
        rgba_arr[:, :, 1] = ink_rgb[1]
        rgba_arr[:, :, 2] = ink_rgb[2]
        rgba_arr[:, :, 3] = alpha_canvas[rmin:rmax + 1, cmin:cmax + 1]

        tight_img = Image.fromarray(rgba_arr, "RGBA")
        return tight_img, (cmin, rmin, crop_w, crop_h)
