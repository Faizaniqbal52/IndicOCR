import os, sys

target_file = "c:/OCR - All/kaggle_cloud_pipeline/indicpixel_kaggle_cloud_pipeline.py"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Unicode joiner whitelist
old_cmap_line = 'text = "".join(c for c in text if ord(c) in cmap or c == \' \')'
new_cmap_line = 'text = "".join(c for c in text if ord(c) in cmap or c in (\' \', \'\\u200C\', \'\\u200D\'))'
assert old_cmap_line in content, "old_cmap_line not found"
content = content.replace(old_cmap_line, new_cmap_line)

# 2. Add get_text_width to GenericHarfBuzzRenderer before render_line
get_text_width_code = '''    def get_text_width(self, font_name: str, text: str, font_size: int = 18) -> int:
        if not text:
            return 0
        text = unicodedata.normalize('NFC', text)
        cmap = self.cmaps[font_name]
        text = "".join(c for c in text if ord(c) in cmap or c in (' ', '\\u200C', '\\u200D'))
        if not text.strip():
            return 0
        try:
            infos, positions = self.shape_text(font_name, text)
            ft = self.ft_faces[font_name]
            upem = ft.units_per_EM
            scale = (font_size * 64) / (upem * 64)
            return int(math.ceil(sum(p.x_advance * scale for p in positions)))
        except Exception:
            return int(len(text) * font_size * 0.75)

    def render_line(self, font_name: str, text: str, font_size: int = 32):'''

old_render_line_def = '    def render_line(self, font_name: str, text: str, font_size: int = 32):'
assert old_render_line_def in content, "old_render_line_def not found"
content = content.replace(old_render_line_def, get_text_width_code, 1)

# 3. Replace render_full_page with pixel-accurate word-wrapping & post-render boundary assertions
old_render_full_page = '''    def render_full_page(self, font_name: str, archetypes: List[str], blocks_corpus: List[str], lang_code: str):
        page_w, page_h = 1000, 1400
        canvas = Image.new("RGB", (page_w, page_h), color=(252, 250, 245))
        draw = ImageDraw.Draw(canvas)
        title_text = random.choice(archetypes)
        all_tokens = []
        full_text = []
        all_glyphs = []
        title_y = 50

        try:
            t_img, t_meta = self.render_line(font_name, title_text, font_size=32)
            title_x = max(40, (page_w - t_img.width) // 2)
            canvas.paste(t_img, (title_x, title_y))
            for tok in t_meta["tokens"]:
                bx = tok["bbox"]
                all_tokens.append({
                    "text": tok["text"],
                    "bbox": [bx[0] + title_x, bx[1] + title_y, bx[2] + title_x, bx[3] + title_y]
                })
            full_text.append(title_text)
            all_glyphs.extend(t_meta.get("shaped_glyphs", []))
        except Exception:
            pass

        draw.line([(40, 110), (page_w - 40, 110)], fill=(80, 80, 80), width=2)
        draw.line([(40, 114), (page_w - 40, 114)], fill=(140, 140, 140), width=1)

        # 2 Column layout
        col_w = (page_w - 120) // 2
        col1_x = 40
        col2_x = 40 + col_w + 40
        draw.line([(col1_x + col_w + 20, 130), (col1_x + col_w + 20, page_h - 60)], fill=(210, 210, 210), width=1)

        curr_y1 = 130
        curr_y2 = 130
        sample_blocks = random.sample(blocks_corpus, min(6, len(blocks_corpus))) if blocks_corpus else [""]
        for idx, blk in enumerate(sample_blocks):
            col_x = col1_x if idx % 2 == 0 else col2_x
            curr_y = curr_y1 if idx % 2 == 0 else curr_y2
            sentences = [s.strip() for s in re.split(r'(?<=[\.\?\!।॥])\s+', blk) if s.strip()][:4]
            for s in sentences:
                if curr_y > page_h - 80:
                    break
                s_trim = s[:45] + "."
                try:
                    l_img, l_meta = self.render_line(font_name, s_trim, font_size=18)
                    canvas.paste(l_img, (col_x, curr_y))
                    for tok in l_meta["tokens"]:
                        bx = tok["bbox"]
                        all_tokens.append({
                            "text": tok["text"],
                            "bbox": [bx[0] + col_x, bx[1] + curr_y, bx[2] + col_x, bx[3] + curr_y]
                        })
                    full_text.append(s_trim)
                    all_glyphs.extend(l_meta.get("shaped_glyphs", []))
                    curr_y += l_img.height + 4
                except Exception:
                    continue
            if idx % 2 == 0:
                curr_y1 = curr_y + 15
            else:
                curr_y2 = curr_y + 15

        meta = {
            "tier": "Tier_1_FullPage",
            "text": "\\n".join(full_text),
            "font_name": font_name,
            "canvas_size": [page_w, page_h],
            "tokens": all_tokens,
            "token_count": len(all_tokens),
            "word_count": len(all_tokens),
            "shaped_glyphs": all_glyphs[:50]
        }
        return canvas, meta'''

new_render_full_page = '''    def render_full_page(self, font_name: str, archetypes: List[str], blocks_corpus: List[str], lang_code: str):
        page_w, page_h = 1000, 1400
        canvas = Image.new("RGB", (page_w, page_h), color=(252, 250, 245))
        draw = ImageDraw.Draw(canvas)
        title_text = random.choice(archetypes)
        all_tokens = []
        full_text = []
        all_glyphs = []
        title_y = 50

        # Auto-scale title font size if too wide
        title_font_size = 32
        t_w = self.get_text_width(font_name, title_text, font_size=title_font_size)
        if t_w > page_w - 120:
            title_font_size = max(20, int(title_font_size * (page_w - 120) / max(t_w, 1)))

        try:
            t_img, t_meta = self.render_line(font_name, title_text, font_size=title_font_size)
            title_x = max(40, (page_w - t_img.width) // 2)
            canvas.paste(t_img, (title_x, title_y))
            for tok in t_meta["tokens"]:
                bx = tok["bbox"]
                all_tokens.append({
                    "text": tok["text"],
                    "bbox": [bx[0] + title_x, bx[1] + title_y, bx[2] + title_x, bx[3] + title_y]
                })
            full_text.append(title_text)
            all_glyphs.extend(t_meta.get("shaped_glyphs", []))
        except Exception:
            pass

        draw.line([(40, 110), (page_w - 40, 110)], fill=(80, 80, 80), width=2)
        draw.line([(40, 114), (page_w - 40, 114)], fill=(140, 140, 140), width=1)

        # 2 Column layout
        # col_w = (1000 - 120) // 2 = 440px. Max line content width constrained to 415px
        col_w = (page_w - 120) // 2
        col1_x = 40
        col2_x = 40 + col_w + 40
        max_col_content_w = col_w - 25
        draw.line([(col1_x + col_w + 20, 130), (col1_x + col_w + 20, page_h - 60)], fill=(210, 210, 210), width=1)

        curr_y1 = 130
        curr_y2 = 130
        sample_blocks = random.sample(blocks_corpus, min(8, len(blocks_corpus))) if blocks_corpus else [""]
        for idx, blk in enumerate(sample_blocks):
            col_x = col1_x if idx % 2 == 0 else col2_x
            curr_y = curr_y1 if idx % 2 == 0 else curr_y2
            raw_words = [w.strip() for w in blk.split() if w.strip()]
            if not raw_words:
                continue

            # Pixel-accurate word wrapping
            wrapped_lines = []
            curr_line_words = []
            curr_line_w = 0
            space_w = self.get_text_width(font_name, " ", font_size=18)

            for w in raw_words:
                w_w = self.get_text_width(font_name, w, font_size=18)
                if curr_line_words and (curr_line_w + space_w + w_w > max_col_content_w):
                    wrapped_lines.append(" ".join(curr_line_words))
                    curr_line_words = [w]
                    curr_line_w = w_w
                else:
                    curr_line_words.append(w)
                    curr_line_w += (space_w + w_w) if len(curr_line_words) > 1 else w_w

            if curr_line_words:
                wrapped_lines.append(" ".join(curr_line_words))

            for s_line in wrapped_lines[:6]:
                if curr_y > page_h - 80:
                    break
                try:
                    l_img, l_meta = self.render_line(font_name, s_line, font_size=18)
                    canvas.paste(l_img, (col_x, curr_y))
                    for tok in l_meta["tokens"]:
                        bx = tok["bbox"]
                        all_tokens.append({
                            "text": tok["text"],
                            "bbox": [bx[0] + col_x, bx[1] + curr_y, bx[2] + col_x, bx[3] + curr_y]
                        })
                    full_text.append(s_line)
                    all_glyphs.extend(l_meta.get("shaped_glyphs", []))
                    curr_y += l_img.height + 4
                except Exception:
                    continue

            if idx % 2 == 0:
                curr_y1 = curr_y + 15
            else:
                curr_y2 = curr_y + 15

        # STRICT ASSERTION: verify 100% of tokens are strictly within page canvas boundaries
        for tok in all_tokens:
            bx = tok["bbox"]
            assert bx[0] >= 0 and bx[1] >= 0, f"Negative bbox: {bx}"
            assert bx[2] <= page_w, f"Token overflow on right edge: {bx[2]} > {page_w} for '{tok['text']}'"
            assert bx[3] <= page_h, f"Token overflow on bottom edge: {bx[3]} > {page_h} for '{tok['text']}'"

        meta = {
            "tier": "Tier_1_FullPage",
            "text": "\\n".join(full_text),
            "font_name": font_name,
            "canvas_size": [page_w, page_h],
            "tokens": all_tokens,
            "token_count": len(all_tokens),
            "word_count": len(all_tokens),
            "shaped_glyphs": all_glyphs[:50]
        }
        return canvas, meta'''

assert old_render_full_page in content, "old_render_full_page not found"
content = content.replace(old_render_full_page, new_render_full_page, 1)

# 4. Update geometric operators in Master54DegradationEngine to micro-transforms with border padding
old_rotation = '''    def op_38_planar_rotation(self, img_bgr: np.ndarray) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        ang = random.choice([-8.0, 8.0, -5.0, 5.0])
        M = cv2.getRotationMatrix2D((w // 2, h // 2), ang, 1.0)
        return cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)'''

new_rotation = '''    def op_38_planar_rotation(self, img_bgr: np.ndarray) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        ang = random.choice([-1.2, 1.2, -0.8, 0.8])
        pad = 12
        padded = cv2.copyMakeBorder(img_bgr, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
        ph, pw = padded.shape[:2]
        M = cv2.getRotationMatrix2D((pw // 2, ph // 2), ang, 1.0)
        rotated = cv2.warpAffine(padded, M, (pw, ph), borderMode=cv2.BORDER_REPLICATE)
        return rotated[pad:pad+h, pad:pad+w]'''

assert old_rotation in content, "old_rotation not found"
content = content.replace(old_rotation, new_rotation, 1)

old_shear = '''    def op_39_horizontal_shear(self, img_bgr: np.ndarray) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        s = math.tan(math.radians(random.uniform(-5.0, 5.0)))
        M = np.array([[1.0, s, -s * (h / 2)], [0.0, 1.0, 0.0]], dtype=np.float32)
        return cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)'''

new_shear = '''    def op_39_horizontal_shear(self, img_bgr: np.ndarray) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        s = math.tan(math.radians(random.uniform(-1.5, 1.5)))
        M = np.array([[1.0, s, -s * (h / 2)], [0.0, 1.0, 0.0]], dtype=np.float32)
        return cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)'''

assert old_shear in content, "old_shear not found"
content = content.replace(old_shear, new_shear, 1)

old_slant = '''    def op_50_kinematic_slant(self, img_bgr: np.ndarray) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        slant = math.tan(math.radians(random.choice([-10.0, 10.0, -14.0, 14.0])))
        M = np.array([[1.0, slant, -slant * (h / 2)], [0.0, 1.0, 0.0]], dtype=np.float32)
        return cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)'''

new_slant = '''    def op_50_kinematic_slant(self, img_bgr: np.ndarray) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        slant = math.tan(math.radians(random.choice([-2.5, 2.5, -3.0, 3.0])))
        M = np.array([[1.0, slant, -slant * (h / 2)], [0.0, 1.0, 0.0]], dtype=np.float32)
        return cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)'''

assert old_slant in content, "old_slant not found"
content = content.replace(old_slant, new_slant, 1)

# 5. Add hard token bbox canvas assertions in synthesize_stream
old_assertions = '''                    # Pre-commit zero-defect assertions
                    assert meta["token_count"] > 0, f"Token count 0 in {sample_key}"
                    glyphs = meta.get("shaped_glyphs", [])
                    if glyphs:
                        assert all(g.get("glyph_id", 1) != 0 for g in glyphs), f"Glyph ID 0 detected in {sample_key}"
                    if not is_clean:
                        assert len(applied_ops) >= 2, f"Augmentations < 2 in {sample_key}"'''

new_assertions = '''                    # Pre-commit zero-defect assertions
                    assert meta["token_count"] > 0, f"Token count 0 in {sample_key}"
                    glyphs = meta.get("shaped_glyphs", [])
                    if glyphs:
                        assert all(g.get("glyph_id", 1) != 0 for g in glyphs), f"Glyph ID 0 detected in {sample_key}"
                    if not is_clean:
                        assert len(applied_ops) >= 2, f"Augmentations < 2 in {sample_key}"
                    cw_chk, ch_chk = meta["canvas_size"]
                    for tok in meta["tokens"]:
                        bx = tok["bbox"]
                        assert bx[0] >= 0 and bx[1] >= 0, f"Negative bbox: {bx} in {sample_key}"
                        assert bx[2] <= cw_chk, f"BBox width breach: {bx[2]} > {cw_chk} in {sample_key} for '{tok['text']}'"
                        assert bx[3] <= ch_chk, f"BBox height breach: {bx[3]} > {ch_chk} in {sample_key} for '{tok['text']}'"'''

assert old_assertions in content, "old_assertions not found"
content = content.replace(old_assertions, new_assertions, 1)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched indicpixel_kaggle_cloud_pipeline.py with all zero-defect fixes!")
