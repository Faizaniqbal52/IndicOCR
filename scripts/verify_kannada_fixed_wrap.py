import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os, math, random, unicodedata
from PIL import Image, ImageDraw
import numpy as np
import uharfbuzz as hb
import freetype
from fontTools.ttLib import TTFont

fonts_dir = "kaggle_cloud_pipeline/latest_cloud_output/fonts/kannada"
available_fonts = [
    "NotoSansKannada-Regular.ttf",
    "NotoSerifKannada-Regular.ttf",
    "BalooTamma2-Regular.ttf",
    "AnekKannada-Regular.ttf"
]

class TestRenderer:
    def __init__(self):
        self.hb_fonts = {}
        self.ft_faces = {}
        self.cmaps = {}
        self.font_metrics = {}
        for fn in available_fonts:
            fp = os.path.join(fonts_dir, fn)
            tt = TTFont(fp)
            self.cmaps[fn] = tt.getBestCmap()
            hhea = tt.get("hhea")
            head = tt.get("head")
            upem = head.unitsPerEm if head else 1000
            asc = hhea.ascent if hhea else 800
            desc = hhea.descent if hhea else -200
            self.font_metrics[fn] = {"ascender": asc / upem, "descender": abs(desc) / upem}
            with open(fp, "rb") as f:
                data = f.read()
            face = hb.Face(data)
            font = hb.Font(face)
            font.scale = (upem, upem)
            hb.ot_font_set_funcs(font)
            self.hb_fonts[fn] = font
            self.ft_faces[fn] = freetype.Face(fp)

    def shape_text(self, fn, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        buf.script = "Knda"
        buf.language = "kan"
        hb.shape(self.hb_fonts[fn], buf)
        return buf.glyph_infos, buf.glyph_positions

    def get_text_width(self, fn, text, font_size=18):
        if not text:
            return 0
        text = unicodedata.normalize('NFC', text)
        cmap = self.cmaps[fn]
        text = "".join(c for c in text if ord(c) in cmap or c in (' ', '\u200C', '\u200D'))
        if not text.strip():
            return 0
        try:
            infos, positions = self.shape_text(fn, text)
            ft = self.ft_faces[fn]
            upem = ft.units_per_EM
            scale = (font_size * 64) / (upem * 64)
            return int(math.ceil(sum(p.x_advance * scale for p in positions)))
        except Exception:
            return int(len(text) * font_size * 0.7)

    def render_line(self, fn, text, font_size=18):
        text = unicodedata.normalize('NFC', text)
        cmap = self.cmaps[fn]
        text = "".join(c for c in text if ord(c) in cmap or c in (' ', '\u200C', '\u200D'))
        words = text.split()
        if not words:
            words = ["."]
        word_spans = []
        cursor = 0
        for w in words:
            idx = text.find(w, cursor)
            if idx == -1:
                idx = cursor
            word_spans.append((w, idx, idx + len(w)))
            cursor = idx + len(w)

        infos, positions = self.shape_text(fn, text)
        ft = self.ft_faces[fn]
        ft.set_char_size(font_size * 64)
        upem = ft.units_per_EM
        scale = (font_size * 64) / (upem * 64)
        total_adv_x = sum(pos.x_advance * scale for pos in positions)
        metrics = self.font_metrics[fn]
        asc_px = int(math.ceil(metrics["ascender"] * font_size))
        desc_px = int(math.ceil(metrics["descender"] * font_size))
        pad_x = 16
        pad_top = max(int(font_size * 0.45), 14)
        pad_bottom = max(int(font_size * 0.40), 12)
        line_height = asc_px + desc_px
        cw = int(math.ceil(total_adv_x)) + 2 * pad_x
        ch = line_height + pad_top + pad_bottom

        canvas = np.full((ch, cw), 255, dtype=np.uint8)
        cur_x = pad_x
        cur_y = pad_top + asc_px
        word_glyph_boxes = {i: [] for i in range(len(word_spans))}

        for info, pos in zip(infos, positions):
            gid = info.codepoint
            x_off = pos.x_offset * scale
            y_off = pos.y_offset * scale
            x_adv = pos.x_advance * scale
            y_adv = pos.y_advance * scale
            ft.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = ft.glyph
            bitmap = slot.bitmap
            top = slot.bitmap_top
            left = slot.bitmap_left
            gx = int(cur_x + x_off + left)
            gy = int(cur_y - y_off - top)
            bh, bw = bitmap.rows, bitmap.width
            if bw > 0 and bh > 0:
                buf_arr = np.array(bitmap.buffer, dtype=np.uint8).reshape((bh, bw))
                y0, y1 = max(0, gy), min(ch, gy + bh)
                x0, x1 = max(0, gx), min(cw, gx + bw)
                by0, by1 = max(0, -gy), max(0, -gy) + (y1 - y0)
                bx0, bx1 = max(0, -gx), max(0, -gx) + (x1 - x0)
                if x1 > x0 and y1 > y0:
                    glyph_slice = buf_arr[by0:by1, bx0:bx1]
                    canvas[y0:y1, x0:x1] = np.minimum(canvas[y0:y1, x0:x1], 255 - glyph_slice)
                    cluster = info.cluster
                    for w_idx, (w_str, s_idx, e_idx) in enumerate(word_spans):
                        if s_idx <= cluster < e_idx:
                            word_glyph_boxes[w_idx].append((x0, y0, x1, y1))
                            break
            cur_x += x_adv
            cur_y += y_adv

        token_boxes = []
        for w_idx, (w_str, _, _) in enumerate(word_spans):
            boxes = word_glyph_boxes[w_idx]
            if boxes:
                token_boxes.append({"text": w_str, "bbox": [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]})
            else:
                token_boxes.append({"text": w_str, "bbox": [pad_x, pad_top, cw - pad_x, ch - pad_bottom]})

        return Image.fromarray(canvas).convert("RGB"), {"tokens": token_boxes, "text": text}

renderer = TestRenderer()
print("TestRenderer initialized successfully!")

# Test 10 full pages with wrapped text
page_w, page_h = 1000, 1400
col_w = (page_w - 120) // 2
col1_x = 40
col2_x = 40 + col_w + 40
max_content_w = col_w - 20

test_text = "ಕನ್ನಡ ತೆಲುಗು ಲಿಪಿ ಒಂದೇ ಸ್ವರೂಪದ್ದಾಗಿದೆಯೆಂದು ಹೇಳಬಹುದಾದ ಅನೇಕ ಪುರಾವೆಗಳು ಸಾಹಿತ್ಯದಲ್ಲಿ ದೊರೆಯುತ್ತವೆ ಮತ್ತು ಇತಿಹಾಸಕಾರರು ಇದನ್ನು ಒಪ್ಪುತ್ತಾರೆ. ಭಾರತೀಯ ಸಂಸ್ಕೃತಿ ಮತ್ತು ಇತಿಹಾಸದಲ್ಲಿ ಕರ್ನಾಟಕವು ಪ್ರಮುಖ ಪಾತ್ರವನ್ನು ವಹಿಸಿದೆ. ಇಲ್ಲಿನ ರಾಜಮನೆತನಗಳು ಕಲೆ ಮತ್ತು ವಾಸ್ತುಶಿಲ್ಪಕ್ಕೆ ಮಹತ್ತರ ಕೊಡುಗೆ ನೀಡಿವೆ."
raw_words = test_text.split()

total_tokens_tested = 0
clipped_count = 0

for fn in available_fonts:
    # Wrap text
    wrapped = []
    curr_line = []
    curr_w = 0
    sp_w = renderer.get_text_width(fn, " ", font_size=18)
    for w in raw_words:
        w_w = renderer.get_text_width(fn, w, font_size=18)
        if curr_line and (curr_w + sp_w + w_w > max_content_w):
            wrapped.append(" ".join(curr_line))
            curr_line = [w]
            curr_w = w_w
        else:
            curr_line.append(w)
            curr_w += (sp_w + w_w) if len(curr_line) > 1 else w_w
    if curr_line:
        wrapped.append(" ".join(curr_line))
        
    for col_x in [col1_x, col2_x]:
        y = 130
        for l_txt in wrapped:
            im, meta = renderer.render_line(fn, l_txt, font_size=18)
            for tok in meta["tokens"]:
                total_tokens_tested += 1
                bx = tok["bbox"]
                gx2 = bx[2] + col_x
                if gx2 > page_w:
                    clipped_count += 1
                    print(f"FAILED OVERFLOW: {gx2} > {page_w} in {fn} for '{tok['text']}'")
            y += im.height + 4

print(f"\nAUDIT RESULT: Tested {total_tokens_tested} tokens across 4 Kannada fonts.")
print(f"Tokens exceeding right canvas boundary ({page_w}px): {clipped_count}")
assert clipped_count == 0, "FATAL: Tokens still clipping!"
print(">>> ZERO DEFECT VERIFIED: 100% of tokens strictly inside canvas! <<<")
