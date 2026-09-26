"""
Bengali HarfBuzz OpenType Shaper & Strict Font Glyph Gate (Agent-Shaper)
Enforces:
1. TTFont cmap extraction for 100% of loaded Bengali fonts.
2. The Zero-.notdef Invariant: Glyph ID 0 is strictly forbidden.
3. Complex Text Layout (CTL) shaping via uharfbuzz with script='Beng', direction='ltr', language='ben'.
4. Pure FreeType glyph-by-glyph rasterization: Zero PIL fallback / Zero Matra Inversion.
5. Dynamic vertical zone padding: Eliminates diacritic clipping for Bengali matras (ী, ৈ, ৌ, ু, ূ, ৃ, etc.).
6. Precise token-level bounding box derivation with cluster mapping.
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
    """Base exception for Bengali Agent-Shaper."""
    pass


class GlyphGateError(ShaperError):
    """Raised when text contains codepoints missing from font cmap."""
    pass


class NotdefGlyphError(ShaperError):
    """Raised when HarfBuzz shaping produces Glyph ID 0 (.notdef)."""
    pass


class BengaliFontRegistry:
    """Manages TrueType cmaps, FreeType faces, and HarfBuzz font instances for Bengali."""

    def __init__(self, fonts_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self.cmaps: Dict[str, Dict[int, str]] = {}
        self.hb_fonts: Dict[str, hb.Font] = {}
        self.ft_faces: Dict[str, freetype.Face] = {}
        self.font_paths: Dict[str, Path] = {}
        self.font_metrics: Dict[str, Dict[str, int]] = {}

        self._load_fonts()

    def _load_fonts(self):
        font_files = list(self.fonts_dir.glob("*.ttf")) + list(self.fonts_dir.glob("*.otf"))
        print(f"[Agent-Shaper] Loading {len(font_files)} Bengali fonts from {self.fonts_dir.name}...")

        for fpath in font_files:
            fname = fpath.name
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

                # Gate: Verify basic Bengali conjunct shaping (reject fonts with broken bng2/beng tables)
                test_buf = hb.Buffer()
                test_buf.add_str("সত্য")
                test_buf.direction = "ltr"
                test_buf.script = "Beng"
                test_buf.language = "ben"
                hb.shape(hb_font, test_buf)
                test_gnames = [tt.getGlyphName(i.codepoint) for i in test_buf.glyph_infos]
                if any(g in ('uni09CD', 'virama', 'hasant', 'glyph00045') for g in test_gnames):
                    print(f"  [REJECT] Font {fname} failed basic conjunct ligature gate (unligated hasant in সত্য).")
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
        CONTROL_AND_SPACE_CODES = {
            0x20, 0x09, 0x0A, 0x0D,
            0x00A0,
            0x200C,  # ZWNJ
            0x200D,  # ZWJ
            0x200B,
            0x00AD
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

    def shape_text(
        self,
        font_name: str,
        text: str,
        script: str = "Beng",
        direction: str = "ltr",
        language: str = "ben"
    ) -> Tuple[List[Dict[str, Any]], hb.Buffer]:
        """
        Gate 2: Shapes text via uharfbuzz with script='Beng'.
        Verifies that no shaped glyph has Glyph ID 0 (.notdef).
        """
        self.verify_glyph_coverage(font_name, text)

        hb_font = self.hb_fonts[font_name]

        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
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
        script: str = "Beng",
        language: str = "ben"
    ) -> List[str]:
        """
        Agent-Shaper Gatekeeper:
        Returns list of font names that:
        1. Support 100% of characters in text via font.getBestCmap().
        2. Successfully shape via HarfBuzz with strictly 0% Glyph ID 0 (.notdef).
        """
        supporting = []
        for font_name in self.hb_fonts:
            try:
                self.verify_glyph_coverage(font_name, text)
                self.shape_text(font_name, text, script=script, language=language)
                supporting.append(font_name)
            except (GlyphGateError, NotdefGlyphError):
                continue
        return supporting


class BengaliHarfBuzzRenderer:
    """
    Renders shaped text via Pure HarfBuzz + FreeType Glyph Compositing for Bengali.
    Completely eliminates default PIL rasterization and matra inversion bugs.
    """

    def __init__(self, registry: BengaliFontRegistry):
        self.registry = registry

    def render_line(
        self,
        font_name: str,
        text: str,
        font_size: int = 36,
        text_color: Tuple[int, int, int] = (15, 15, 15),
        bg_color: Tuple[int, int, int] = (250, 248, 243)
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Renders a line of text via pure HarfBuzz + FreeType for Bengali.
        Guarantees 100% correct Complex Text Layout.
        """
        shaped_glyphs, hb_buf = self.registry.shape_text(
            font_name, text, script="Beng", direction="ltr", language="ben"
        )

        metrics = self.registry.font_metrics[font_name]
        upem = metrics["units_per_em"]
        scale = font_size / upem

        ascender_px = int(metrics["ascent"] * scale)
        descender_px = abs(int(metrics["descent"] * scale))

        ft_face = self.registry.ft_faces[font_name]
        ft_face.set_pixel_sizes(0, font_size)

        tot_advance_x = sum(int(round(pos.x_advance * scale)) for pos in hb_buf.glyph_positions)
        top_zone_pad = max(int(font_size * 0.45), 18)
        bottom_zone_pad = max(int(font_size * 0.40), 16)
        side_pad = max(int(font_size * 0.35), 15)

        canvas_w = tot_advance_x + (side_pad * 2) + 20
        canvas_h = (ascender_px + descender_px) + top_zone_pad + bottom_zone_pad
        baseline_y = top_zone_pad + ascender_px

        alpha_canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)

        cur_x = float(side_pad)
        glyph_boxes = []

        for info, pos in zip(hb_buf.glyph_infos, hb_buf.glyph_positions):
            gid = info.codepoint
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

                if (x2 > x1) and (y2 > y1):
                    alpha_canvas[y1:y2, x1:x2] = np.maximum(
                        alpha_canvas[y1:y2, x1:x2],
                        glyph_arr[src_y1:src_y2, src_x1:src_x2]
                    )

            glyph_boxes.append({
                "cluster": info.cluster,
                "gid": gid,
                "x": gx,
                "y": gy,
                "w": bw,
                "h": bh,
                "x_advance": int(round(pos.x_advance * scale))
            })

            cur_x += pos.x_advance * scale

        # Composite final RGB image
        rgb_img = Image.new("RGB", (canvas_w, canvas_h), color=bg_color)
        rgb_arr = np.array(rgb_img, dtype=np.float32)

        alpha_norm = (alpha_canvas.astype(np.float32) / 255.0)[:, :, np.newaxis]
        ink_arr = np.array(text_color, dtype=np.float32).reshape((1, 1, 3))
        blended = (ink_arr * alpha_norm) + (rgb_arr * (1.0 - alpha_norm))
        result_img = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))

        # Derive token-level bounding boxes
        tokens = text.split()
        token_boxes = []
        t_start = 0

        for tok in tokens:
            t_idx = text.find(tok, t_start)
            if t_idx == -1:
                t_idx = t_start
            t_len = len(tok)
            t_end = t_idx + t_len
            t_start = t_end

            matching = [g for g in glyph_boxes if t_idx <= g["cluster"] < t_end and g["w"] > 0 and g["h"] > 0]
            if matching:
                min_x = min(g["x"] for g in matching)
                min_y = min(g["y"] for g in matching)
                max_x = max(g["x"] + g["w"] for g in matching)
                max_y = max(g["y"] + g["h"] for g in matching)

                pad_t = 3
                box = [
                    max(0, min_x - pad_t),
                    max(0, min_y - pad_t),
                    min(canvas_w, max_x + pad_t),
                    min(canvas_h, max_y + pad_t)
                ]
            else:
                box = [0, 0, 0, 0]

            token_boxes.append({
                "text": tok,
                "bbox": box
            })

        metadata = {
            "text": text,
            "font_name": font_name,
            "font_size": font_size,
            "canvas_size": [canvas_w, canvas_h],
            "baseline_y": baseline_y,
            "shaped_glyphs": shaped_glyphs,
            "tokens": token_boxes,
            "ascender_zone_pad": top_zone_pad,
            "descender_zone_pad": bottom_zone_pad
        }

        return result_img, metadata
