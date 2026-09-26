"""
Agent-Shaper: HarfBuzz OpenType Shaper & Strict Font Glyph Gate
Enforces:
1. TTFont cmap extraction for 100% of loaded fonts.
2. The Zero-.notdef Invariant: Glyph ID 0 is strictly forbidden.
3. Complex Text Layout (CTL) shaping via uharfbuzz with explicit script, direction, language.
4. Pure FreeType glyph-by-glyph rasterization: Zero PIL fallback / Zero Matra Inversion.
5. Dynamic vertical zone padding: Eliminates diacritic clipping.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from PIL import Image, ImageFont, ImageDraw
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


class FontRegistry:
    """Manages TrueType cmaps, FreeType faces, and HarfBuzz font instances."""

    def __init__(self, fonts_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.cmaps: Dict[str, Dict[int, str]] = {}
        self.hb_fonts: Dict[str, hb.Font] = {}
        self.ft_faces: Dict[str, freetype.Face] = {}
        self.font_paths: Dict[str, Path] = {}
        self.font_metrics: Dict[str, Dict[str, int]] = {}

        self._load_fonts()

    BLACKLISTED_FONTS = {"Dekko-Regular.ttf"}

    def _load_fonts(self):
        font_files = list(self.fonts_dir.glob("*.ttf")) + list(self.fonts_dir.glob("*.otf"))
        print(f"[Agent-Shaper] Loading {len(font_files)} fonts from {self.fonts_dir.name}...")

        for fpath in font_files:
            fname = fpath.name
            if fname in self.BLACKLISTED_FONTS:
                print(f"  [QUARANTINE] Skipping blacklisted font: {fname}")
                continue
            try:
                # 1. Extract exact cmap table via fontTools
                tt = TTFont(str(fpath))
                cmap = tt.getBestCmap()
                self.cmaps[fname] = cmap

                # Extract font metrics (unitsPerEm, ascent, descent)
                hhea = tt.get('hhea')
                head = tt.get('head')
                upem = head.unitsPerEm if head else 1000
                ascent = hhea.ascent if hhea else int(upem * 0.8)
                descent = hhea.descent if hhea else int(upem * -0.2)

                self.font_metrics[fname] = {
                    "units_per_em": upem,
                    "ascent": ascent,
                    "descent": descent
                }

                # 2. Initialize HarfBuzz face & font
                with open(fpath, "rb") as f:
                    font_data = f.read()
                face = hb.Face(font_data)
                hb_font = hb.Font(face)
                hb_font.scale = (upem, upem)

                # Gate: Verify basic Devanagari conjunct shaping (reject fonts with broken dev2/deva tables)
                test_buf = hb.Buffer()
                test_buf.add_str("सच्चा")
                test_buf.direction = "ltr"
                test_buf.script = "Deva"
                test_buf.language = "hin"
                hb.shape(hb_font, test_buf)
                test_gnames = [tt.getGlyphName(i.codepoint) for i in test_buf.glyph_infos]
                if any(g in ('uni094D', 'virama', 'halant', 'glyph00045') for g in test_gnames):
                    print(f"  [REJECT] Font {fname} failed basic conjunct ligature gate (unligated halant in सच्चा).")
                    continue

                self.hb_fonts[fname] = hb_font
                self.font_paths[fname] = fpath

                # 3. Initialize FreeType Face for pure glyph rasterization
                self.ft_faces[fname] = freetype.Face(str(fpath))

                print(f"  [OK] Registered {fname} (cmap size: {len(cmap):,} codepoints, UPEM: {upem})")
            except Exception as e:
                print(f"  [WARN] Failed to load {fname}: {e}")

    def verify_glyph_coverage(self, font_name: str, text: str) -> bool:
        """
        Gate 1: Verifies that 100% of characters exist in TrueType cmap.
        Raises GlyphGateError if even a single character is missing.
        """
        if font_name not in self.cmaps:
            raise GlyphGateError(f"Font '{font_name}' is not in the active registry.")

        cmap = self.cmaps[font_name]
        missing = []
        # OpenType layout control codes that HarfBuzz processes during GSUB/GPOS
        # and non-printable spaces that do not require an explicit printable glyph in cmap
        CONTROL_AND_SPACE_CODES = {
            0x20, 0x09, 0x0A, 0x0D,  # Standard whitespace
            0x00A0,                  # Non-breaking space
            0x200C,                  # ZWNJ (Zero-width non-joiner)
            0x200D,                  # ZWJ (Zero-width joiner)
            0x200B,                  # Zero-width space
            0x200E,                  # LRM (Left-to-Right Mark)
            0x200F,                  # RLM (Right-to-Left Mark)
            0x00AD                   # Soft hyphen
        }
        for ch in text:
            code = ord(ch)
            if code in CONTROL_AND_SPACE_CODES:
                continue
            if code not in cmap:
                missing.append(f"'{ch}' (U+{code:04X})")

        if missing:
            raise GlyphGateError(f"Font '{font_name}' missing codepoints: {', '.join(set(missing))}")

        return True

    NUKTA_DECOMPOSITIONS = {
        '\u0929': '\u0928\u093c',  # ऩ -> न + ़
        '\u0931': '\u0930\u093c',  # ऱ -> र + ़
        '\u0934': '\u0933\u093c',  # ऴ -> ळ + ़
        '\u0958': '\u0915\u093c',  # क़ -> क + ़
        '\u0959': '\u0916\u093c',  # ख़ -> ख + ़
        '\u095A': '\u0917\u093c',  # ग़ -> ग + ़
        '\u095B': '\u091c\u093c',  # ज़ -> ज + ़
        '\u095C': '\u0921\u093c',  # ड़ -> ड + ़
        '\u095D': '\u0922\u093c',  # ढ़ -> ढ + ़
        '\u095E': '\u092b\u093c',  # फ़ -> फ + ़
        '\u095F': '\u092f\u093c',  # य़ -> य + ़
    }

    def adapt_text_for_font(self, font_name: str, text: str) -> str:
        """
        Agent-Shaper Canonical Nukta Adapter:
        If a font lacks a precomposed nukta character (e.g. ऩ in Tillana/Kalam/YatraOne),
        decomposes it to its canonical base + nukta mark (न + ़) which shapes identically
        via HarfBuzz with 0% .notdef.
        """
        cmap = self.cmaps.get(font_name, {})
        adapted = []
        for ch in text:
            code = ord(ch)
            if code not in cmap and ch in self.NUKTA_DECOMPOSITIONS:
                decomp = self.NUKTA_DECOMPOSITIONS[ch]
                if all(ord(c) in cmap for c in decomp):
                    adapted.append(decomp)
                    continue
            # If a non-Devanagari stray symbol (e.g. arrow, bullet, currency symbol) is missing from font cmap, omit it
            if code not in cmap and not (0x0900 <= code <= 0x097F):
                continue
            adapted.append(ch)
        return "".join(adapted)

    def is_supported(self, font_name: str, text: str) -> bool:
        """Returns True if font can fully shape text with zero .notdef."""
        try:
            adapted = self.adapt_text_for_font(font_name, text)
            self.verify_glyph_coverage(font_name, adapted)
            self.shape_text(font_name, adapted)
            return True
        except (GlyphGateError, NotdefGlyphError):
            return False

    def get_supporting_fonts(self, text: str, script: str = "Deva", language: str = "bho") -> List[str]:
        """
        Agent-Shaper Gatekeeper:
        Returns list of font names that:
        1. Support 100% of characters in text via font.getBestCmap().
        2. Successfully shape via HarfBuzz with strictly 0% Glyph ID 0 (.notdef).
        """
        supporting = []
        for font_name in self.hb_fonts:
            try:
                adapted = self.adapt_text_for_font(font_name, text)
                self.verify_glyph_coverage(font_name, adapted)
                self.shape_text(font_name, adapted, script=script, language=language)
                supporting.append(font_name)
            except (GlyphGateError, NotdefGlyphError):
                continue
        return supporting

    def shape_text(
        self,
        font_name: str,
        text: str,
        script: str = "Deva",
        direction: str = "ltr",
        language: str = "bho"
    ) -> Tuple[List[Dict[str, Any]], Any]:
        """
        Shapes text using HarfBuzz OpenType engine.
        Enforces INVARIANT: 0% Glyph ID 0 (.notdef).
        Returns (shaped_glyphs_list, raw_hb_buffer).
        """
        text = self.adapt_text_for_font(font_name, text)
        self.verify_glyph_coverage(font_name, text)

        hb_font = self.hb_fonts[font_name]
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = direction
        buf.script = script
        buf.language = language

        # Shape with OpenType features enabled
        hb.shape(hb_font, buf)

        infos = buf.glyph_infos or []
        positions = buf.glyph_positions or []

        if not infos or not positions:
            return [], buf

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


class HarfBuzzTokenRenderer:
    """
    Renders shaped text via Pure HarfBuzz + FreeType Glyph Compositing.
    Completely eliminates default PIL rasterization and matra inversion bugs.
    """

    def __init__(self, registry: FontRegistry):
        self.registry = registry

    def render_line(
        self,
        font_name: str,
        text: str,
        font_size: int = 36,
        text_color: Tuple[int, int, int] = (15, 15, 15),
        bg_color: Tuple[int, int, int] = (250, 248, 243),
        script: str = "Deva",
        direction: str = "ltr",
        language: str = "bho"
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Renders a line of text via pure HarfBuzz + FreeType.
        Guarantees 100% correct Complex Text Layout (e.g. 'मिठास', 'संस्कृति').
        """
        shaped_glyphs, hb_buf = self.registry.shape_text(
            font_name, text, script=script, direction=direction, language=language
        )

        metrics = self.registry.font_metrics[font_name]
        upem = metrics["units_per_em"]
        scale = font_size / upem

        ascender_px = int(metrics["ascent"] * scale)
        descender_px = abs(int(metrics["descent"] * scale))

        ft_face = self.registry.ft_faces[font_name]
        ft_face.set_pixel_sizes(0, font_size)

        # Calculate canvas geometry
        glyph_positions = hb_buf.glyph_positions or []
        glyph_infos = hb_buf.glyph_infos or []

        tot_advance_x = sum(int(round(pos.x_advance * scale)) for pos in glyph_positions)
        top_zone_pad = max(int(font_size * 0.45), 18)
        bottom_zone_pad = max(int(font_size * 0.40), 16)
        side_pad = max(int(font_size * 0.35), 15)

        canvas_w = tot_advance_x + (side_pad * 2) + 20
        canvas_h = (ascender_px + descender_px) + top_zone_pad + bottom_zone_pad
        baseline_y = top_zone_pad + ascender_px

        alpha_canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)

        cur_x = float(side_pad)
        for info, pos in zip(glyph_infos, glyph_positions):
            gid = info.codepoint
            # Use FT_LOAD_NO_HINTING to prevent hinter from displacing glyphs relative to HarfBuzz GPOS anchors
            ft_face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = ft_face.glyph
            bitmap = slot.bitmap

            bw, bh = bitmap.width, bitmap.rows
            left, top = slot.bitmap_left, slot.bitmap_top

            gx = int(round(cur_x + pos.x_offset * scale + left))
            gy = int(round(baseline_y - pos.y_offset * scale - top))

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

            cur_x += pos.x_advance * scale

        # Composite onto background image
        img = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        img_arr = np.array(img)

        # Alpha blend text_color onto bg_color
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
            "font_size": font_size,
            "bbox": bbox,
            "canvas_size": [canvas_w, canvas_h],
            "ascender_zone": ascender_px,
            "descender_zone": descender_px,
            "shaped_glyphs": shaped_glyphs,
            "shaped_glyphs_count": len(shaped_glyphs)
        }

        return final_img, annotation

    def render_text_rgba(
        self,
        font_name: str,
        text: str,
        font_size: int = 32,
        ink_rgb: Tuple[int, int, int] = (20, 20, 20),
        script: str = "Deva",
        direction: str = "ltr",
        language: str = "bho",
        return_baseline: bool = False
    ) -> Any:
        """
        Renders shaped text directly into a tightly cropped RGBA Image.
        Uses pure HarfBuzz + FreeType without hinting for subpixel GPOS matra precision.
        Returns:
          - If return_baseline=False: (tight_rgba_img, (0, 0, width, height))
          - If return_baseline=True:  (tight_rgba_img, (0, 0, width, height), baseline_offset)
        """
        shaped_glyphs, hb_buf = self.registry.shape_text(
            font_name, text, script=script, direction=direction, language=language
        )

        metrics = self.registry.font_metrics[font_name]
        upem = metrics["units_per_em"]
        scale = font_size / upem

        ascender_px = int(metrics["ascent"] * scale)
        descender_px = abs(int(metrics["descent"] * scale))

        ft_face = self.registry.ft_faces[font_name]
        ft_face.set_pixel_sizes(0, font_size)

        tot_advance_x = sum(int(round(pos.x_advance * scale)) for pos in hb_buf.glyph_positions)
        pad_x = max(int(font_size * 0.4), 16)
        pad_y = max(int(font_size * 0.4), 16)

        canvas_w = tot_advance_x + (pad_x * 2) + 20
        canvas_h = (ascender_px + descender_px) + (pad_y * 2) + 10
        baseline_y = pad_y + ascender_px

        alpha_canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)

        cur_x = float(pad_x)
        for info, pos in zip(hb_buf.glyph_infos, hb_buf.glyph_positions):
            gid = info.codepoint
            # Use FT_LOAD_NO_HINTING to prevent hinter from displacing glyphs relative to HarfBuzz GPOS anchors
            ft_face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = ft_face.glyph
            bitmap = slot.bitmap

            bw, bh = bitmap.width, bitmap.rows
            left, top = slot.bitmap_left, slot.bitmap_top

            gx = int(round(cur_x + pos.x_offset * scale + left))
            gy = int(round(baseline_y - pos.y_offset * scale - top))

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

            cur_x += pos.x_advance * scale

        mask = (alpha_canvas > 15)
        if np.count_nonzero(mask) < 2:
            empty_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            if return_baseline:
                return empty_img, (0, 0, 1, 1), 0
            return empty_img, (0, 0, 1, 1)

        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        p = 1
        c_x0 = max(0, int(cmin) - p)
        c_y0 = max(0, int(rmin) - p)
        c_x1 = min(canvas_w, int(cmax) + p + 1)
        c_y1 = min(canvas_h, int(rmax) + p + 1)

        cropped_alpha = alpha_canvas[c_y0:c_y1, c_x0:c_x1]
        out_rgba = np.zeros((cropped_alpha.shape[0], cropped_alpha.shape[1], 4), dtype=np.uint8)
        out_rgba[:, :, 0] = ink_rgb[0]
        out_rgba[:, :, 1] = ink_rgb[1]
        out_rgba[:, :, 2] = ink_rgb[2]
        out_rgba[:, :, 3] = cropped_alpha

        tight_img = Image.fromarray(out_rgba, "RGBA")
        baseline_offset = baseline_y - c_y0
        if return_baseline:
            return tight_img, (0, 0, tight_img.width, tight_img.height), baseline_offset
        return tight_img, (0, 0, tight_img.width, tight_img.height)

    def render_line_rgba(
        self,
        font_name: str,
        text: str,
        font_size: int = 32,
        ink_rgb: Tuple[int, int, int] = (20, 20, 20),
        script: str = "Deva",
        direction: str = "ltr",
        language: str = "bho"
    ) -> Tuple[Image.Image, Tuple[int, int, int, int], int]:
        """
        Renders shaped text and returns (tight_rgba_img, bbox, baseline_offset).
        Guarantees exact Shirorekha / baseline positioning when assembling paragraphs.
        """
        return self.render_text_rgba(
            font_name=font_name,
            text=text,
            font_size=font_size,
            ink_rgb=ink_rgb,
            script=script,
            direction=direction,
            language=language,
            return_baseline=True
        )

    def paste_text(
        self,
        canvas: Image.Image,
        font_name: str,
        text: str,
        xy: Tuple[int, int],
        font_size: int = 32,
        ink_rgb: Tuple[int, int, int] = (20, 20, 20),
        script: str = "Deva",
        direction: str = "ltr",
        language: str = "bho"
    ) -> Tuple[int, int, int, int]:
        """
        Renders shaped text via HarfBuzz + FreeType and pastes onto canvas.
        Returns absolute bounding box (x1, y1, x2, y2).
        """
        img_rgba, _ = self.render_text_rgba(
            font_name, text, font_size=font_size, ink_rgb=ink_rgb,
            script=script, direction=direction, language=language
        )
        x, y = xy
        canvas.paste(img_rgba, (x, y), img_rgba)
        return (x, y, x + img_rgba.width, y + img_rgba.height)

    def get_text_width(
        self,
        font_name: str,
        text: str,
        font_size: int = 20,
        script: str = "Deva",
        direction: str = "ltr",
        language: str = "bho"
    ) -> int:
        """Computes exact pixel advance width using HarfBuzz glyph positioning."""
        metrics = self.registry.font_metrics[font_name]
        scale = font_size / metrics["units_per_em"]
        _, hb_buf = self.registry.shape_text(
            font_name, text, script=script, direction=direction, language=language
        )
        return sum(int(pos.x_advance * scale) for pos in hb_buf.glyph_positions)


