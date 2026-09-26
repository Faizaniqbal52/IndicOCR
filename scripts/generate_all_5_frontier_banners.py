"""
Frontier Lab Master Banner Engine (v5)
Renders 5 distinct gallery-grade thematic banners for IndicPixel / IndicOCR:
1. Theme 1: "The Linguistic Continuum" (DeepMind / Swiss International Style)
2. Theme 2: "Velvet Editorial" (Parisian Minimalist / Haute Typographie Specimen - Fixed)
3. Theme 3: "Neural Document Blueprint" (Linear / NASA Technical Telemetry)
4. Theme 4: "Heritage Saffron & Obsidian" (Contemporary Deep Tech India / Sarvam AI / Bhashini)
5. Theme 5: "The Frontier Synthesis" (The Ultimate Fusion: Heritage Gold, Velvet Analog Grain, Precision Vision Coordinates)

Resolution: 2400 x 700 px (Retina 2x).
Zero buzzwords, zero unproven claims, 100% meaningful architectural structure.
"""

import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(r"c:\OCR - All")
ASSETS_DIR = REPO_ROOT / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_MEDIA_DIR = Path(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\3dbba92f-a15a-4629-9d9c-b3b34712581d\.tempmediaStorage")
BRAIN_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

SCRIPTS = [
    {"name": "Devanagari", "char": "अ", "font": Path(r"c:\OCR - All\fonts\devanagari\NotoSansDevanagari.ttf"), "code": "Deva", "lang": "hin/mar"},
    {"name": "Bengali", "char": "অ", "font": Path(r"c:\OCR - All\fonts\bengali\NotoSansBengali-Regular.ttf"), "code": "Beng", "lang": "ben/asm"},
    {"name": "Tamil", "char": "அ", "font": Path(r"c:\OCR - All\fonts\tamil\NotoSansTamil-Regular.ttf"), "code": "Taml", "lang": "tam"},
    {"name": "Telugu", "char": "అ", "font": Path(r"c:\OCR - All\fonts\telugu\NotoSansTelugu-Regular.ttf"), "code": "Telu", "lang": "tel"},
    {"name": "Kannada", "char": "ಅ", "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\latest_cloud_output\fonts\kannada\NotoSansKannada-Regular.ttf"), "code": "Knda", "lang": "kan"},
    {"name": "Gurmukhi", "char": "ਅ", "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\latest_cloud_output\fonts\punjabi\NotoSansGurmukhi-Regular.ttf"), "code": "Guru", "lang": "pan"},
    {"name": "Gujarati", "char": "અ", "font": Path(r"c:\OCR - All\fonts\gujarati\NotoSansGujarati-Regular.ttf"), "code": "Gujr", "lang": "guj"},
    {"name": "Malayalam", "char": "അ", "font": Path(r"c:\OCR - All\fonts\malayalam\NotoSansMalayalam-Regular.ttf"), "code": "Mlym", "lang": "mal"},
    {"name": "Odia", "char": "ଅ", "font": Path(r"c:\OCR - All\fonts\odia\NotoSansOriya-Regular.ttf"), "code": "Orya", "lang": "ori"},
    {"name": "Perso-Arabic", "char": "آ", "font": Path(r"c:\OCR - All\fonts\urdu\NotoNaskhArabic-Regular.ttf"), "code": "Arab", "lang": "urd/snd"},
    {"name": "Ol Chiki", "char": "ᱚ", "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\smoke_fleet_v11_output\fonts\sat\NotoSansOlChiki-Regular.ttf"), "code": "Olck", "lang": "sat"},
    {"name": "Meetei Mayek", "char": "ꯃ", "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\smoke_fleet_v11_output\fonts\mni\NotoSansMeeteiMayek-Regular.ttf"), "code": "Mtei", "lang": "mni"},
]

def get_font(name: str, size: int, fallback: str = "arial.ttf") -> ImageFont.FreeTypeFont:
    win_dir = Path("C:/Windows/Fonts")
    for f in [name, fallback, "segoeui.ttf", "arial.ttf"]:
        p = win_dir / f
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()

# =============================================================================
# THEME 1: "The Linguistic Continuum" (DeepMind / Swiss International Style)
# =============================================================================
def generate_theme1():
    W, H = 2400, 700
    img = Image.new("RGBA", (W, H), (9, 12, 18, 255))
    draw = ImageDraw.Draw(img)

    # Subtle Sub-Pixel Grid (Very soft, non-intrusive alpha=5)
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 5), width=1)
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 5), width=1)

    # Ambient Glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(-120, -100), (850, 450)], fill=(56, 189, 248, 16))
    gd.ellipse([(1450, 80), (2500, 750)], fill=(245, 158, 11, 14))
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Bezel
    draw.rounded_rectangle([2, 2, W - 3, H - 3], radius=24, outline=(71, 85, 105, 220), width=2)
    draw.rounded_rectangle([4, 4, W - 5, H - 5], radius=22, outline=(255, 255, 255, 14), width=1)

    font_brand = get_font("segoeuib.ttf", 64, "arialbd.ttf")
    font_desc = get_font("segoeui.ttf", 22, "arial.ttf")
    font_mono = get_font("consola.ttf", 15, "courier.ttf")
    font_num = get_font("segoeuib.ttf", 38, "arialbd.ttf")
    font_lbl = get_font("segoeuib.ttf", 14, "arialbd.ttf")
    font_meta = get_font("segoeui.ttf", 14, "arial.ttf")

    # Brand
    bx, by = 90, 75
    draw.text((bx, by), "INDICPIXEL", fill=(248, 250, 252, 255), font=font_brand)
    draw.text((bx + 400, by + 14), "[23 SOUTH ASIAN LANGUAGES • 12 SCRIPTS]", fill=(56, 189, 248, 230), font=font_mono)
    draw.text((bx + 400, by + 38), "POSIX WEBDATASET SPECIFICATION", fill=(148, 163, 184, 200), font=font_mono)

    draw.text((bx, by + 86),
              "Multilingual synthetic optical document corpus covering official and literary languages of South Asia.",
              fill=(226, 232, 240, 230), font=font_desc)

    # The Script Horizon
    horizon_y = 175
    hx_start, hx_end = 1200, 2310
    draw.line([(hx_start, horizon_y), (hx_end, horizon_y)], fill=(51, 65, 85, 200), width=1)

    spacing = (hx_end - hx_start) // 12
    for i, s in enumerate(SCRIPTS):
        gx = hx_start + i * spacing + 12
        gy = horizon_y - 62
        bw, bh = 58, 64
        box_x, box_y = gx - 8, gy - 6
        draw.rectangle([box_x, box_y, box_x + bw, box_y + bh], outline=(30, 41, 59, 180), width=1)
        # Laser cyan corner ticks
        draw.line([(box_x, box_y), (box_x + 8, box_y)], fill=(56, 189, 248, 230), width=2)
        draw.line([(box_x, box_y), (box_x, box_y + 8)], fill=(56, 189, 248, 230), width=2)
        draw.line([(box_x + bw, box_y + bh), (box_x + bw - 8, box_y + bh)], fill=(56, 189, 248, 230), width=2)
        draw.line([(box_x + bw, box_y + bh), (box_x + bw, box_y + bh - 8)], fill=(56, 189, 248, 230), width=2)

        if s["font"].exists():
            try:
                gf = ImageFont.truetype(str(s["font"]), 34)
                draw.text((gx, gy), s["char"], fill=(248, 250, 252, 255), font=gf)
            except Exception:
                pass
        draw.text((gx - 4, horizon_y + 12), s["code"], fill=(100, 116, 139, 230), font=font_mono)

    # 5 Metric Columns
    cols = [
        ("12,000,000+", "VERIFIED OCR SAMPLES", "Dense Document Corpus"),
        ("2,400+", "POSIX SHARDS (.TAR)", "Distributed Streaming"),
        ("23", "PAN-INDIC LANGUAGES", "Constitutional Scope"),
        ("12", "WRITING SYSTEMS", "HarfBuzz OpenType CTL"),
        ("4 TIERS", "GRANULARITY HIERARCHY", "Pages • Paras • Lines • Words")
    ]
    cy = 440
    cw = 425
    for i, (val, lbl, sub) in enumerate(cols):
        cx = bx + i * (cw + 24)
        if i > 0:
            draw.line([(cx - 12, cy + 10), (cx - 12, cy + 115)], fill=(30, 41, 59, 220), width=1)
        draw.text((cx, cy), val, fill=(248, 250, 252, 255), font=font_num)
        draw.text((cx, cy + 54), lbl, fill=(56, 189, 248, 230), font=font_lbl)
        draw.text((cx, cy + 80), sub, fill=(148, 163, 184, 210), font=font_meta)

    draw.text((bx, 642), "Apache 2.0 Open Data  •  POSIX WebDataset Standard  •  Word-Level Bounding Boxes  •  Zero .notdef Glyphs",
              fill=(100, 116, 139, 220), font=font_meta)
    
    out_path = ASSETS_DIR / "banner_theme1_continuum.png"
    img.convert("RGB").save(out_path, format="PNG", quality=95)
    return img

# =============================================================================
# THEME 2: "Velvet Editorial" (Parisian Haute Typographie / Minimalist Specimen)
# =============================================================================
def generate_theme2():
    W, H = 2400, 700
    img = Image.new("RGBA", (W, H), (15, 16, 20, 255))
    draw = ImageDraw.Draw(img)

    # Subtle Analog Film Grain
    np.random.seed(42)
    noise = np.random.normal(0, 3.0, (H, W)).astype(np.float32)
    noise_img = Image.fromarray(np.clip(noise + 128, 0, 255).astype(np.uint8), mode="L")
    noise_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    noise_rgba.paste((255, 255, 255, 5), (0, 0), noise_img)
    img = Image.alpha_composite(img, noise_rgba)
    draw = ImageDraw.Draw(img)

    # Subtle Background Sculptural Watermark (Devanagari 'अ' rendered with very gentle alpha=16)
    bg_font_path = Path(r"c:\OCR - All\fonts\devanagari\NotoSansDevanagari.ttf")
    if bg_font_path.exists():
        try:
            big_font = ImageFont.truetype(str(bg_font_path), 540)
            draw.text((1780, 60), "अ", fill=(255, 255, 255, 16), font=big_font)
        except Exception:
            pass

    draw.rounded_rectangle([2, 2, W - 3, H - 3], radius=22, outline=(65, 70, 80, 210), width=1)

    font_brand = get_font("georgiab.ttf", 64, "timesbd.ttf")
    font_sub = get_font("georgia.ttf", 26, "times.ttf")
    font_body = get_font("segoeui.ttf", 20, "arial.ttf")
    font_small = get_font("segoeui.ttf", 15, "arial.ttf")
    font_num = get_font("georgiab.ttf", 36, "timesbd.ttf")
    font_lbl = get_font("segoeuib.ttf", 13, "arialbd.ttf")

    x_start = 110
    draw.text((x_start, 75), "IndicPixel", fill=(245, 239, 230, 255), font=font_brand)
    # Vermilion Seal Pip
    draw.ellipse([x_start + 325, 110, x_start + 338, 123], fill=(225, 29, 72, 255))

    draw.text((x_start, 155), "A Typographic & Document Corpus across South Asian Scripts",
              fill=(214, 204, 190, 240), font=font_sub)

    draw.text((x_start, 205),
              "Organized into 12,000,000 verified samples across 23 languages and 12 distinct writing systems.\n"
              "Synthesized with native HarfBuzz Complex Text Layout shaping and full structural ground truth.",
              fill=(156, 163, 175, 220), font=font_body)

    # Dividing Rule
    draw.line([(1260, 75), (1260, 580)], fill=(45, 48, 56, 210), width=1)

    # Right Column: The 4 Document Tiers Specimen
    rx = 1330
    draw.text((rx, 80), "DOCUMENT HIERARCHY SPECIMEN", fill=(225, 29, 72, 240), font=font_lbl)

    tiers = [
        ("Tier I", "Full-Page Spread", "Multi-column archival and broadsheet layouts (2%)"),
        ("Tier II", "Paragraph Block", "Wrapped continuous natural reading sequences (13%)"),
        ("Tier III", "Reading Sentence", "Isolated syntactic text with token bounding boxes (55%)"),
        ("Tier IV", "Isolated Token", "Rare conjuncts, numerals, and vocabulary words (30%)")
    ]

    for i, (t_num, t_name, t_desc) in enumerate(tiers):
        ty = 130 + i * 58
        draw.text((rx, ty), t_num, fill=(245, 239, 230, 250), font=font_lbl)
        draw.text((rx + 75, ty), "—", fill=(100, 116, 139, 180), font=font_small)
        draw.text((rx + 105, ty), t_name, fill=(245, 239, 230, 240), font=font_small)
        draw.text((rx + 290, ty), t_desc, fill=(148, 163, 184, 200), font=font_small)

    # Bottom Metric Band (Evenly spaced to avoid collision)
    metrics = [
        ("12,000,000", "TOTAL SAMPLES"),
        ("2,400+", "WEBDATASET SHARDS"),
        ("23", "LANGUAGES"),
        ("12", "WRITING SYSTEMS"),
        ("APACHE 2.0", "OPEN DATA")
    ]
    my = 480
    col_spacing = 220
    for i, (val, lbl) in enumerate(metrics):
        mx = x_start + i * col_spacing
        draw.text((mx, my), val, fill=(245, 239, 230, 255), font=font_num)
        draw.text((mx, my + 50), lbl, fill=(156, 163, 175, 200), font=font_lbl)

    draw.text((x_start, 638), "POSIX WebDataset  •  Word & Line Level Bounding Coordinates  •  Zero Glyph Clipping",
              fill=(100, 116, 139, 200), font=font_small)

    out_path = ASSETS_DIR / "banner_theme2_velvet.png"
    img.convert("RGB").save(out_path, format="PNG", quality=95)
    return img

# =============================================================================
# THEME 3: "Neural Document Blueprint" (Linear / NASA Technical Telemetry)
# =============================================================================
def generate_theme3():
    W, H = 2400, 700
    img = Image.new("RGBA", (W, H), (7, 16, 34, 255))
    draw = ImageDraw.Draw(img)

    # Blueprint Grid
    grid_c = (56, 189, 248, 12)
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=grid_c, width=1)
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=grid_c, width=1)

    # Perimeter ticks
    for x in range(0, W, 96):
        draw.line([(x, 0), (x, 7)], fill=(56, 189, 248, 140), width=1)
        draw.line([(x, H - 7), (x, H)], fill=(56, 189, 248, 140), width=1)
    for y in range(0, H, 96):
        draw.line([(0, y), (7, y)], fill=(56, 189, 248, 140), width=1)
        draw.line([(W - 7, y), (W, y)], fill=(56, 189, 248, 140), width=1)

    draw.rectangle([2, 2, W - 3, H - 3], outline=(56, 189, 248, 90), width=1)

    font_mono_title = get_font("consola.ttf", 52, "courier.ttf")
    font_mono_sub = get_font("consola.ttf", 20, "courier.ttf")
    font_mono_meta = get_font("consola.ttf", 14, "courier.ttf")
    font_val = get_font("consola.ttf", 36, "courier.ttf")

    draw.text((80, 36), "SPEC_ID: IND-PX-12M // SUBSYSTEM: MULTILINGUAL_DOCUMENT_OCR // REV: 2026.4",
              fill=(56, 189, 248, 200), font=font_mono_meta)

    draw.text((80, 75), "INDICPIXEL::SYNTHETIC_CORPUS", fill=(248, 250, 252, 255), font=font_mono_title)
    draw.text((80, 142), "VOLUME = 12,000,000 OCR PAIRS  |  SHARDS = 2,400 POSIX .TAR",
              fill=(163, 230, 53, 230), font=font_mono_sub)
    draw.text((80, 180), "COVERAGE: 23 SOUTH ASIAN LANGUAGES  |  12 WRITING SYSTEMS  |  CTL: HARFBUZZ",
              fill=(148, 163, 184, 220), font=font_mono_meta)

    # Document AI Anatomy Wireframe
    wx, wy = 1380, 75
    ww, wh = 920, 345
    draw.rectangle([wx, wy, wx + ww, wy + wh], outline=(56, 189, 248, 120), width=1)
    draw.text((wx + 16, wy + 12), "RAY_CAST_PROJECTION // BOUNDING_BOX_TELEMETRY", fill=(56, 189, 248, 180), font=font_mono_meta)

    # Simulated column 1: Document lines
    col1_x, col1_y = wx + 30, wy + 42
    draw.rectangle([col1_x, col1_y, col1_x + 380, col1_y + 270], outline=(30, 58, 95, 200), width=1)
    draw.text((col1_x + 10, col1_y + 10), "TIER 1: PAGE_SPREAD [2400x3200]", fill=(100, 116, 139, 200), font=font_mono_meta)
    
    for line_idx in range(6):
        ly = col1_y + 45 + line_idx * 35
        draw.rectangle([col1_x + 15, ly, col1_x + 365, ly + 24], outline=(56, 189, 248, 70), width=1)
        draw.rectangle([col1_x + 20, ly + 3, col1_x + 95, ly + 21], outline=(163, 230, 53, 180), fill=(163, 230, 53, 25), width=1)
        draw.rectangle([col1_x + 105, ly + 3, col1_x + 210, ly + 21], outline=(56, 189, 248, 140), width=1)
        draw.rectangle([col1_x + 220, ly + 3, col1_x + 355, ly + 21], outline=(56, 189, 248, 140), width=1)

    # Simulated column 2: Token Inspection
    col2_x = wx + 440
    draw.rectangle([col2_x, col1_y, col2_x + 450, col1_y + 270], outline=(30, 58, 95, 200), width=1)
    draw.text((col2_x + 10, col1_y + 10), "TIER 4: TOKEN_INSPECTION [CHAR_LEVEL]", fill=(100, 116, 139, 200), font=font_mono_meta)
    
    sample_font = Path(r"c:\OCR - All\fonts\devanagari\NotoSansDevanagari.ttf")
    if sample_font.exists():
        try:
            big_f = ImageFont.truetype(str(sample_font), 110)
            draw.text((col2_x + 160, col1_y + 60), "क्ष", fill=(248, 250, 252, 255), font=big_f)
            draw.line([(col2_x + 40, col1_y + 80), (col2_x + 410, col1_y + 80)], fill=(239, 68, 68, 180), width=1)
            draw.line([(col2_x + 40, col1_y + 185), (col2_x + 410, col1_y + 185)], fill=(56, 189, 248, 180), width=1)
            draw.text((col2_x + 20, col1_y + 72), "SHR", fill=(239, 68, 68, 200), font=font_mono_meta)
            draw.text((col2_x + 20, col1_y + 178), "BSL", fill=(56, 189, 248, 200), font=font_mono_meta)
        except Exception:
            pass

    metrics_tech = [
        ("[01]", "12.0M SAMPLES", "TOTAL INVENTORY"),
        ("[02]", "2,400 SHARDS", "POSIX WEBDATASET"),
        ("[03]", "23 LANGUAGES", "INDIC COVERAGE"),
        ("[04]", "12 SCRIPTS", "WRITING SYSTEMS"),
        ("[05]", "4 TIERS", "GRANULARITY")
    ]
    for i, (idx, val, lbl) in enumerate(metrics_tech):
        bx = 80 + i * 448
        by = 460
        draw.rectangle([bx, by, bx + 420, by + 130], outline=(30, 58, 95, 180), width=1)
        draw.text((bx + 16, by + 12), idx, fill=(163, 230, 53, 220), font=font_mono_meta)
        draw.text((bx + 16, by + 40), val, fill=(248, 250, 252, 255), font=font_val)
        draw.text((bx + 16, by + 92), lbl, fill=(100, 116, 139, 220), font=font_mono_meta)

    draw.text((80, 646), "COMPATIBILITY: TrOCR • Donut • Nougat • LayoutLMv3 • Surya // LICENSE: Apache 2.0",
              fill=(100, 116, 139, 220), font=font_mono_meta)

    out_path = ASSETS_DIR / "banner_theme3_blueprint.png"
    img.convert("RGB").save(out_path, format="PNG", quality=95)
    return img

# =============================================================================
# THEME 4: "Heritage Saffron & Obsidian" (Contemporary Deep Tech India)
# =============================================================================
def generate_theme4():
    W, H = 2400, 700
    img = Image.new("RGBA", (W, H), (10, 11, 16, 255))
    draw = ImageDraw.Draw(img)

    # Architectural Jali Micro-Lattice (Whisper-quiet alpha=4)
    jali = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jd = ImageDraw.Draw(jali)
    step = 54
    for x in range(0, W, step):
        for y in range(0, H, step):
            jd.polygon([(x + step//2, y), (x + step, y + step//2), (x + step//2, y + step), (x, y + step//2)],
                       outline=(255, 255, 255, 4), width=1)
    img = Image.alpha_composite(img, jali)
    draw = ImageDraw.Draw(img)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(-100, -80), (820, 420)], fill=(234, 88, 12, 18))
    gd.ellipse([(1400, -100), (2500, 500)], fill=(245, 158, 11, 16))
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([2, 2, W - 3, H - 3], radius=22, outline=(245, 158, 11, 150), width=1)
    draw.rounded_rectangle([4, 4, W - 5, H - 5], radius=20, outline=(51, 65, 85, 140), width=1)

    font_brand = get_font("segoeuib.ttf", 66, "arialbd.ttf")
    font_sub_brand = get_font("segoeui.ttf", 26, "arial.ttf")
    font_desc = get_font("segoeui.ttf", 21, "arial.ttf")
    font_val = get_font("segoeuib.ttf", 40, "arialbd.ttf")
    font_lbl = get_font("segoeuib.ttf", 14, "arialbd.ttf")
    font_meta = get_font("segoeui.ttf", 14, "arial.ttf")

    x_start, y_start = 90, 75
    draw.text((x_start, y_start), "INDICPIXEL", fill=(248, 250, 252, 255), font=font_brand)
    
    # Saffron Pillar Line
    draw.rectangle([x_start + 410, y_start + 26, x_start + 414, y_start + 66], fill=(245, 158, 11, 255))
    draw.text((x_start + 430, y_start + 28), "Pan-Indic Document & Vision Corpus", fill=(245, 158, 11, 250), font=font_sub_brand)

    draw.text((x_start, y_start + 88),
              "Preserving linguistic complexity across 23 South Asian languages and 12 writing systems.\n"
              "12,000,000 verified document samples with word & line bounding coordinates in standard WebDataset format.",
              fill=(226, 232, 240, 230), font=font_desc)

    # 12-Script Seal
    seal_x, seal_y = 1380, 65
    seal_w, seal_h = 920, 320
    seal_bg = Image.new("RGBA", (seal_w, seal_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seal_bg)
    sd.rounded_rectangle([0, 0, seal_w - 1, seal_h - 1], radius=16,
                         fill=(18, 20, 29, 210), outline=(245, 158, 11, 120), width=1)
    sd.text((24, 14), "CONSTITUTIONAL & REGIONAL WRITING SYSTEMS", fill=(245, 158, 11, 230), font=font_lbl)
    img.paste(seal_bg, (seal_x, seal_y), seal_bg)
    draw = ImageDraw.Draw(img)

    cols = 6
    tw, th = 140, 120
    for idx, s in enumerate(SCRIPTS):
        c = idx % cols
        r = idx // cols
        tx = seal_x + 22 + c * (tw + 8)
        ty = seal_y + 44 + r * (th + 10)

        t_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        td = ImageDraw.Draw(t_img)
        td.rounded_rectangle([0, 0, tw - 1, th - 1], radius=10,
                             fill=(24, 27, 40, 230), outline=(51, 65, 85, 140), width=1)
        if s["font"].exists():
            try:
                g_font = ImageFont.truetype(str(s["font"]), 36)
                gb = td.textbbox((0, 0), s["char"], font=g_font)
                gw = gb[2] - gb[0]
                td.text(((tw - gw) // 2, 10), s["char"], fill=(251, 191, 36, 255), font=g_font)
            except Exception:
                pass
        nb = td.textbbox((0, 0), s["name"], font=font_meta)
        td.text(((tw - (nb[2] - nb[0])) // 2, 64), s["name"], fill=(248, 250, 252, 240), font=font_meta)
        cb = td.textbbox((0, 0), s["code"], font=font_lbl)
        td.text(((tw - (cb[2] - cb[0])) // 2, 90), s["code"], fill=(148, 163, 184, 200), font=font_lbl)

        img.paste(t_img, (tx, ty), t_img)
        draw = ImageDraw.Draw(img)

    # 5 Unified Cards with colored top bars
    cards = [
        ("12,000,000+", "VERIFIED SAMPLES", "Document Corpus", (245, 158, 11)),
        ("2,400+", "WEBDATASET SHARDS", "Streaming .tar", (52, 211, 153)),
        ("23", "LANGUAGES", "Constitutional Scope", (56, 189, 248)),
        ("12", "WRITING SYSTEMS", "OpenType Complex Text", (167, 139, 250)),
        ("4", "GRANULARITY TIERS", "Pages • Paras • Lines • Words", (244, 114, 182))
    ]
    card_w = 416
    card_h = 165
    cy = 435
    for i, (val, lbl, sub, col) in enumerate(cards):
        cx = x_start + i * (card_w + 32)
        c_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(c_img)
        cd.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=14,
                             fill=(18, 20, 29, 220), outline=col + (120,), width=1)
        cd.rounded_rectangle([16, 0, card_w - 16, 3], radius=2, fill=col + (230,))
        cd.text((22, 25), val, fill=(248, 250, 252, 255), font=font_val)
        cd.text((22, 85), lbl, fill=col + (240,), font=font_lbl)
        cd.text((22, 115), sub, fill=(148, 163, 184, 210), font=font_meta)
        img.paste(c_img, (cx, cy), c_img)
        draw = ImageDraw.Draw(img)

    draw.text((x_start, 638), "Apache 2.0 Open Data  •  POSIX WebDataset Standard  •  Zero .notdef Glyphs  •  HarfBuzz Shaped",
              fill=(100, 116, 139, 220), font=font_meta)

    out_path = ASSETS_DIR / "banner_theme4_heritage.png"
    img.convert("RGB").save(out_path, format="PNG", quality=95)
    return img

# =============================================================================
# THEME 5: "The Frontier Synthesis" (Ultimate Fusion: Heritage Gold & Precision AI)
# =============================================================================
def generate_theme5_synthesis():
    W, H = 2400, 720
    # Transparent master canvas for true floating drop-shadow on light/dark mode
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    margin_x, margin_y = 24, 16
    cw, ch = W - 2 * margin_x, H - 2 * margin_y # 2352 x 688
    radius = 22

    # Drop shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([margin_x - 2, margin_y + 4, margin_x + cw + 2, margin_y + ch + 8],
                         radius=radius + 4, fill=(0, 0, 0, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, shadow)

    # Card
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)

    # Gradient base
    for y in range(ch):
        ratio = y / ch
        r = int(10 + (16 - 10) * ratio)
        g = int(12 + (20 - 12) * ratio)
        b = int(20 + (32 - 20) * ratio)
        cd.line([(0, y), (cw, y)], fill=(r, g, b, 255))

    # Ambient Glow: Warm Royal Gold (top left) + Soft Laser Cyan (top right)
    glow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(-120, -100), (850, 420)], fill=(245, 158, 11, 16)) # Gold
    gd.ellipse([(1350, -80), (2400, 480)], fill=(56, 189, 248, 16)) # Cyan
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    card = Image.alpha_composite(card, glow)
    cd = ImageDraw.Draw(card)

    # Dual Bezel: Crisp Saffron/Gold outer line + Slate inner line
    card_mask = Image.new("L", (cw, ch), 0)
    cmd = ImageDraw.Draw(card_mask)
    cmd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=radius, fill=255)
    
    # Outer Bezel
    cd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=radius, outline=(245, 158, 11, 140), width=1)
    cd.rounded_rectangle([2, 2, cw - 3, ch - 3], radius=radius - 2, outline=(51, 65, 85, 160), width=1)

    font_brand = get_font("segoeuib.ttf", 66, "arialbd.ttf")
    font_sub_brand = get_font("segoeui.ttf", 25, "arial.ttf")
    font_desc = get_font("segoeui.ttf", 21, "arial.ttf")
    font_val = get_font("segoeuib.ttf", 38, "arialbd.ttf")
    font_lbl = get_font("segoeuib.ttf", 14, "arialbd.ttf")
    font_meta = get_font("segoeui.ttf", 14, "arial.ttf")
    font_mono = get_font("consola.ttf", 14, "courier.ttf")

    # Brand Lockup
    bx, by = 75, 65
    cd.text((bx, by), "INDICPIXEL", fill=(248, 250, 252, 255), font=font_brand)
    
    # Saffron Pillar Line
    cd.rectangle([bx + 400, by + 22, bx + 404, by + 62], fill=(245, 158, 11, 255))
    cd.text((bx + 420, by + 25), "Pan-Indic Document & Vision Corpus", fill=(245, 158, 11, 245), font=font_sub_brand)

    cd.text((bx, by + 86),
            "High-fidelity synthetic document corpus across 23 South Asian languages and 12 writing systems.\n"
            "Full 4-tier document structure with word & line bounding coordinates in standard WebDataset format.",
            fill=(226, 232, 240, 230), font=font_desc)

    # Right Side: The 12-Script Golden Showcase Matrix
    seal_x, seal_y = 1335, 55
    seal_w, seal_h = 940, 325
    seal_bg = Image.new("RGBA", (seal_w, seal_h), (0, 0, 0, 0))
    sbd = ImageDraw.Draw(seal_bg)
    sbd.rounded_rectangle([0, 0, seal_w - 1, seal_h - 1], radius=16,
                          fill=(16, 20, 30, 200), outline=(245, 158, 11, 100), width=1)
    sbd.text((22, 12), "REPRESENTED SOUTH ASIAN WRITING SYSTEMS (12 SCRIPTS)", fill=(245, 158, 11, 220), font=font_lbl)
    card.paste(seal_bg, (seal_x, seal_y), seal_bg)
    cd = ImageDraw.Draw(card)

    cols = 6
    tw, th = 142, 122
    for idx, s in enumerate(SCRIPTS):
        c = idx % cols
        r = idx // cols
        tx = seal_x + 22 + c * (tw + 10)
        ty = seal_y + 42 + r * (th + 10)

        t_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        td = ImageDraw.Draw(t_img)
        td.rounded_rectangle([0, 0, tw - 1, th - 1], radius=10,
                             fill=(22, 27, 40, 230), outline=(51, 65, 85, 150), width=1)
        if s["font"].exists():
            try:
                g_font = ImageFont.truetype(str(s["font"]), 36)
                gb = td.textbbox((0, 0), s["char"], font=g_font)
                gw = gb[2] - gb[0]
                td.text(((tw - gw) // 2, 8), s["char"], fill=(251, 191, 36, 255), font=g_font)
            except Exception:
                pass
        nb = td.textbbox((0, 0), s["name"], font=font_meta)
        td.text(((tw - (nb[2] - nb[0])) // 2, 64), s["name"], fill=(248, 250, 252, 240), font=font_meta)
        cb = td.textbbox((0, 0), s["lang"], font=font_lbl)
        td.text(((tw - (cb[2] - cb[0])) // 2, 92), s["lang"], fill=(148, 163, 184, 210), font=font_lbl)

        card.paste(t_img, (tx, ty), t_img)
        cd = ImageDraw.Draw(card)

    # Bottom 5 Executive Metric Cards
    cards = [
        ("12,000,000+", "VERIFIED OCR SAMPLES", "4-Tier Document Corpus", (245, 158, 11)), # Saffron
        ("2,400+", "WEBDATASET SHARDS", "Streaming POSIX (.tar)", (52, 211, 153)),       # Emerald
        ("23", "PAN-INDIC LANGUAGES", "Constitutional Scope", (56, 189, 248)),          # Cyan
        ("12", "WRITING SYSTEMS", "OpenType Complex Text", (167, 139, 250)),            # Iris
        ("4", "GRANULARITY TIERS", "Pages • Paras • Lines • Words", (244, 114, 182))    # Rose
    ]
    card_w = 422
    card_h = 175
    cy = 415
    for i, (val, lbl, sub, col) in enumerate(cards):
        cx = bx + i * (card_w + 30)
        c_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        cd_c = ImageDraw.Draw(c_img)
        cd_c.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=14,
                               fill=(16, 20, 30, 220), outline=col + (120,), width=1)
        cd_c.rounded_rectangle([16, 0, card_w - 16, 3], radius=2, fill=col + (230,))
        cd_c.text((22, 26), val, fill=(248, 250, 252, 255), font=font_val)
        cd_c.text((22, 88), lbl, fill=col + (240,), font=font_lbl)
        cd_c.text((22, 120), sub, fill=(148, 163, 184, 210), font=font_meta)
        card.paste(c_img, (cx, cy), c_img)
        cd = ImageDraw.Draw(card)

    cd.text((bx, 638), "Apache 2.0 Open Data  •  POSIX WebDataset (.tar)  •  Word & Line Level Bounding Boxes  •  Zero .notdef Glyphs",
            fill=(100, 116, 139, 220), font=font_meta)

    canvas.paste(card, (margin_x, margin_y), card)
    out_path = ASSETS_DIR / "banner_theme5_synthesis.png"
    canvas.save(out_path, format="PNG", optimize=True)
    return canvas

# =============================================================================
# BUILD COMPREHENSIVE 5-THEME COMPARISON PROOF PLATE
# =============================================================================
def build_comparison_plate(t1, t2, t3, t4, t5):
    plate_w = 2600
    plate_h = 4400
    plate = Image.new("RGB", (plate_w, plate_h), (18, 20, 26))
    p_draw = ImageDraw.Draw(plate)

    title_font = get_font("segoeuib.ttf", 46, "arialbd.ttf")
    sub_font = get_font("segoeui.ttf", 22, "arial.ttf")
    theme_title_font = get_font("segoeuib.ttf", 28, "arialbd.ttf")
    theme_sub_font = get_font("segoeui.ttf", 18, "arial.ttf")

    p_draw.text((80, 50), "FRONTIER RESEARCH LAB HERO BANNERS: 5 THEMATIC ARCHETYPES", fill=(255, 255, 255), font=title_font)
    p_draw.text((80, 115), "Engineered with Graphic Design Rigor  •  Zero Generic Templates  •  100% Meaningful Architectural Structure", fill=(156, 163, 175), font=sub_font)

    themes = [
        (t5, "THEME 5 (RECOMMENDED): THE FRONTIER SYNTHESIS (Heritage Gold + Precision AI + True RGBA)",
         "Warm royal saffron & obsidian, 12-script golden emblem, floating physical drop shadow, perfect dual-mode contrast."),
        (t4, "THEME 4: HERITAGE SAFFRON & OBSIDIAN (Contemporary Deep Tech India / Sarvam AI / Bhashini)",
         "Architectural jali micro-lattice, warm saffron-gold radiance, and 12-script constitutional seal."),
        (t1, "THEME 1: THE LINGUISTIC CONTINUUM (DeepMind / Swiss International Style)",
         "Mathematical Cartesian grid, datum shirorekha horizon, and vision bounding coordinate brackets."),
        (t2, "THEME 2: VELVET EDITORIAL (Parisian Minimalist / Haute Typographie Specimen)",
         "Monograph layout, subtle analog grain, giant sculptural Devanagari watermark, and literary specimen hierarchy."),
        (t3, "THEME 3: NEURAL DOCUMENT BLUEPRINT (Linear / NASA Technical Telemetry)",
         "Engineering blueprint grid, document spread ray-cast decomposition, and token bounding wireframes.")
    ]

    curr_y = 180
    for idx, (img_banner, t_name, t_desc) in enumerate(themes):
        accent_col = (245, 158, 11) if idx == 0 or idx == 1 else ((56, 189, 248) if idx == 2 else ((225, 29, 72) if idx == 3 else (163, 230, 53)))
        p_draw.text((80, curr_y), t_name, fill=accent_col, font=theme_title_font)
        p_draw.text((80, curr_y + 36), t_desc, fill=(156, 163, 175), font=theme_sub_font)

        b_rgb = img_banner.convert("RGB") if img_banner.mode == "RGBA" else img_banner
        plate.paste(b_rgb, (100, curr_y + 75))
        curr_y += 820

    proof_plate_path = BRAIN_MEDIA_DIR / "frontier_5themes_master_comparison_plate.png"
    plate.save(proof_plate_path, format="PNG", quality=90)
    print(f"\n>>> MASTER 5-THEME COMPARISON PLATE SAVED: {proof_plate_path} <<<")

if __name__ == "__main__":
    print("Synthesizing Theme 1: The Linguistic Continuum...")
    t1 = generate_theme1()
    print("Synthesizing Theme 2: Velvet Editorial (Fixed)...")
    t2 = generate_theme2()
    print("Synthesizing Theme 3: Neural Document Blueprint...")
    t3 = generate_theme3()
    print("Synthesizing Theme 4: Heritage Saffron & Obsidian...")
    t4 = generate_theme4()
    print("Synthesizing Theme 5: The Frontier Synthesis...")
    t5 = generate_theme5_synthesis()

    print("Building Master 5-Theme Comparison Plate...")
    build_comparison_plate(t1, t2, t3, t4, t5)
