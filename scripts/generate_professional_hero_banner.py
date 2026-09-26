"""
IndicPixel / IndicOCR Hero Banner Generator (v4 - Master Edition)
Engineered by Professional Design Principles for Flawless Light & Dark Mode Adaptability.
Zero buzzwords, zero unproven claims, 100% factual dataset representation.

Design Engineering Features:
- RGBA Transparent Canvas with Physical Drop Shadow:
  Renders genuine rounded corners on any background (White Light Mode or Dark Mode).
- 2-Zone Balanced Layout:
  Left: Brand Identity & Factual Scope
  Right: 12-Writing System Showcase Matrix (6x2 grid, eliminates all dead void space)
- Bottom: 5 Proportionally Unified Metric Cards with Pure Numerals
- Footer: Factual Format & Compatibility Spec
- 100% Genuine Noto Fonts for All 12 Writing Systems (Fixed Naskh Arabic for Perso-Arabic)
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(r"c:\OCR - All")
ASSETS_DIR = REPO_ROOT / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_MEDIA_DIR = Path(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\3dbba92f-a15a-4629-9d9c-b3b34712581d\.tempmediaStorage")
BRAIN_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# 12 Verified Script Fonts, Representative Native Glyphs, and ISO/Scope labels
SCRIPT_DATA = [
    {
        "name": "Devanagari",
        "char": "अ",
        "font": Path(r"c:\OCR - All\fonts\devanagari\NotoSansDevanagari.ttf"),
        "lang": "hin / mar / san"
    },
    {
        "name": "Bengali",
        "char": "অ",
        "font": Path(r"c:\OCR - All\fonts\bengali\NotoSansBengali-Regular.ttf"),
        "lang": "ben / asm"
    },
    {
        "name": "Tamil",
        "char": "அ",
        "font": Path(r"c:\OCR - All\fonts\tamil\NotoSansTamil-Regular.ttf"),
        "lang": "tam"
    },
    {
        "name": "Telugu",
        "char": "అ",
        "font": Path(r"c:\OCR - All\fonts\telugu\NotoSansTelugu-Regular.ttf"),
        "lang": "tel"
    },
    {
        "name": "Kannada",
        "char": "ಅ",
        "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\latest_cloud_output\fonts\kannada\NotoSansKannada-Regular.ttf"),
        "lang": "kan"
    },
    {
        "name": "Gurmukhi",
        "char": "ਅ",
        "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\latest_cloud_output\fonts\punjabi\NotoSansGurmukhi-Regular.ttf"),
        "lang": "pan"
    },
    {
        "name": "Gujarati",
        "char": "અ",
        "font": Path(r"c:\OCR - All\fonts\gujarati\NotoSansGujarati-Regular.ttf"),
        "lang": "guj"
    },
    {
        "name": "Malayalam",
        "char": "അ",
        "font": Path(r"c:\OCR - All\fonts\malayalam\NotoSansMalayalam-Regular.ttf"),
        "lang": "mal"
    },
    {
        "name": "Odia",
        "char": "ଅ",
        "font": Path(r"c:\OCR - All\fonts\odia\NotoSansOriya-Regular.ttf"),
        "lang": "ori"
    },
    {
        "name": "Perso-Arabic",
        "char": "آ",
        "font": Path(r"c:\OCR - All\fonts\urdu\NotoNaskhArabic-Regular.ttf"),
        "lang": "urd / snd / kas"
    },
    {
        "name": "Ol Chiki",
        "char": "ᱚ",
        "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\smoke_fleet_v11_output\fonts\sat\NotoSansOlChiki-Regular.ttf"),
        "lang": "sat"
    },
    {
        "name": "Meetei Mayek",
        "char": "ꯃ",
        "font": Path(r"c:\OCR - All\kaggle_cloud_pipeline\smoke_fleet_v11_output\fonts\mni\NotoSansMeeteiMayek-Regular.ttf"),
        "lang": "mni"
    },
]

def get_sys_font(name: str, size: int, fallback: str = "arial.ttf") -> ImageFont.FreeTypeFont:
    win_dir = Path("C:/Windows/Fonts")
    for f in [name, fallback, "segoeui.ttf", "arial.ttf"]:
        p = win_dir / f
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_hero_banner():
    # Master Canvas Dimensions
    CANVAS_W, CANVAS_H = 2400, 720
    
    # Card Margins (Room for floating drop shadow)
    MARGIN_X = 24
    MARGIN_Y = 18
    CARD_W = CANVAS_W - 2 * MARGIN_X # 2352 px
    CARD_H = CANVAS_H - 2 * MARGIN_Y # 684 px
    RADIUS = 22

    # 1. Master RGBA Canvas (Initially completely transparent)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

    # 2. Ambient Drop Shadow (Renders physical depth on Light Mode, dissolves on Dark Mode)
    shadow = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([MARGIN_X - 2, MARGIN_Y + 4, MARGIN_X + CARD_W + 2, MARGIN_Y + CARD_H + 8],
                             radius=RADIUS + 4, fill=(0, 0, 0, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, shadow)

    # 3. Card Surface (Deep Obsidian / Slate-950 Gradient)
    card = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card)

    gradient = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(CARD_H):
        ratio = y / CARD_H
        r = int(11 + (17 - 11) * ratio)
        g = int(16 + (24 - 16) * ratio)
        b = int(28 + (39 - 28) * ratio)
        g_draw.line([(0, y), (CARD_W, y)], fill=(r, g, b, 255))

    # Ambient Atmospheric Radiance
    glow = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    gl_draw = ImageDraw.Draw(glow)
    gl_draw.ellipse([(-120, -120), (780, 420)], fill=(56, 189, 248, 20))
    gl_draw.ellipse([(1300, -100), (2380, 480)], fill=(99, 102, 241, 18))
    gl_draw.ellipse([(850, 360), (1650, 720)], fill=(16, 185, 129, 14))
    glow = glow.filter(ImageFilter.GaussianBlur(85))
    gradient = Image.alpha_composite(gradient, glow)

    # Mask gradient into rounded rectangle
    card_mask = Image.new("L", (CARD_W, CARD_H), 0)
    cm_draw = ImageDraw.Draw(card_mask)
    cm_draw.rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], radius=RADIUS, fill=255)
    card.paste(gradient, (0, 0), card_mask)
    c_draw = ImageDraw.Draw(card)

    # Architectural Double-Bezel Border
    c_draw.rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], radius=RADIUS,
                             outline=(71, 85, 105, 210), width=2)
    c_draw.rounded_rectangle([2, 2, CARD_W - 3, CARD_H - 3], radius=RADIUS - 2,
                             outline=(255, 255, 255, 18), width=1)

    # Typography Configuration
    font_badge = get_sys_font("segoeuib.ttf", 15, "arialbd.ttf")
    font_brand = get_sys_font("segoeuib.ttf", 64, "arialbd.ttf")
    font_sub_brand = get_sys_font("segoeuib.ttf", 26, "arialbd.ttf")
    font_desc_line1 = get_sys_font("segoeui.ttf", 22, "arial.ttf")
    font_desc_line2 = get_sys_font("segoeui.ttf", 19, "arial.ttf")
    
    font_card_val = get_sys_font("segoeuib.ttf", 38, "arialbd.ttf")
    font_card_lbl = get_sys_font("segoeuib.ttf", 15, "arialbd.ttf")
    font_card_sub = get_sys_font("segoeui.ttf", 14, "arial.ttf")
    
    font_script_name = get_sys_font("segoeuib.ttf", 14, "arialbd.ttf")
    font_script_lang = get_sys_font("segoeui.ttf", 12, "arial.ttf")
    font_footer = get_sys_font("segoeui.ttf", 16, "arial.ttf")

    # =========================================================================
    # ZONE 1: TOP-LEFT BRAND & IDENTITY (X: 65 -> 1260)
    # =========================================================================
    pill_x, pill_y = 65, 48
    pill_text = "MULTILINGUAL INDIC OCR DATASET"
    bbox_p = c_draw.textbbox((0, 0), pill_text, font=font_badge)
    pw = (bbox_p[2] - bbox_p[0]) + 38
    ph = 32
    c_draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + ph], radius=16,
                            fill=(15, 23, 42, 210), outline=(56, 189, 248, 120), width=1)
    c_draw.ellipse([pill_x + 14, pill_y + 11, pill_x + 24, pill_y + 21], fill=(52, 211, 153, 255))
    c_draw.text((pill_x + 32, pill_y + 6), pill_text, fill=(226, 232, 240, 240), font=font_badge)

    brand_x, brand_y = 65, 98
    c_draw.text((brand_x, brand_y), "INDICOCR", fill=(248, 250, 252, 255), font=font_brand)
    
    slash_x = brand_x + 342
    c_draw.text((slash_x, brand_y + 12), "/", fill=(100, 116, 139, 160), font=font_sub_brand)
    c_draw.text((slash_x + 20, brand_y + 16), "IndicPixel Synthetic Corpus", fill=(56, 189, 248, 240), font=font_sub_brand)

    desc_y = brand_y + 86
    c_draw.text((brand_x, desc_y),
               "Comprehensive 12-Million Sample Dataset across 23 South Asian Languages & 12 Writing Systems",
               fill=(226, 232, 240, 230), font=font_desc_line1)
    
    c_draw.text((brand_x, desc_y + 36),
               "Standard POSIX WebDataset (.tar) Shards  •  Full Pages, Paragraphs, Reading Lines & Isolated Words",
               fill=(148, 163, 184, 210), font=font_desc_line2)

    # =========================================================================
    # ZONE 2: TOP-RIGHT SCRIPT COVERAGE MATRIX (X: 1315 -> 2285, Y: 42 -> 378)
    # =========================================================================
    matrix_x = 1315
    matrix_y = 42
    matrix_w = 970
    matrix_h = 336
    
    m_panel = Image.new("RGBA", (matrix_w, matrix_h), (0, 0, 0, 0))
    mp_draw = ImageDraw.Draw(m_panel)
    mp_draw.rounded_rectangle([0, 0, matrix_w - 1, matrix_h - 1], radius=16,
                             fill=(15, 23, 42, 160), outline=(51, 65, 85, 140), width=1)
    
    mp_draw.text((20, 12), "REPRESENTED WRITING SYSTEMS (12 SCRIPTS)", fill=(148, 163, 184, 220), font=font_script_name)
    card.paste(m_panel, (matrix_x, matrix_y), m_panel)
    c_draw = ImageDraw.Draw(card)

    cols = 6
    tile_w = 148
    tile_h = 132
    tile_gap_x = 12
    tile_gap_y = 12
    grid_start_x = matrix_x + 18
    grid_start_y = matrix_y + 44

    for idx, s in enumerate(SCRIPT_DATA):
        c = idx % cols
        r = idx // cols
        tx = grid_start_x + c * (tile_w + tile_gap_x)
        ty = grid_start_y + r * (tile_h + tile_gap_y)

        t_img = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, 0))
        t_draw = ImageDraw.Draw(t_img)
        t_draw.rounded_rectangle([0, 0, tile_w - 1, tile_h - 1], radius=12,
                                fill=(19, 29, 49, 220), outline=(51, 65, 85, 160), width=1)
        
        # Native Glyph Rendering
        if s["font"].exists():
            try:
                glyph_size = 40 if s["name"] != "Perso-Arabic" else 38
                g_font = ImageFont.truetype(str(s["font"]), glyph_size)
                gb = t_draw.textbbox((0, 0), s["char"], font=g_font)
                gw = gb[2] - gb[0]
                gx = (tile_w - gw) // 2
                # Slightly adjust y offset for Naskh Arabic to center optically
                gy = 10 if s["name"] != "Perso-Arabic" else 8
                t_draw.text((gx, gy), s["char"], fill=(56, 189, 248, 255), font=g_font)
            except Exception:
                pass
        
        # Script Name
        nb = t_draw.textbbox((0, 0), s["name"], font=font_script_name)
        nw = nb[2] - nb[0]
        nx = (tile_w - nw) // 2
        t_draw.text((nx, 70), s["name"], fill=(241, 245, 249, 240), font=font_script_name)
        
        # Scope Language Code
        lb = t_draw.textbbox((0, 0), s["lang"], font=font_script_lang)
        lw = lb[2] - lb[0]
        lx = (tile_w - lw) // 2
        t_draw.text((lx, 96), s["lang"], fill=(100, 116, 139, 220), font=font_script_lang)

        card.paste(t_img, (tx, ty), t_img)
        c_draw = ImageDraw.Draw(card)

    # =========================================================================
    # ZONE 3: BOTTOM ROW METRIC CARDS (5 Unified Executive Pillars)
    # Pure Numerals + Descriptive Labels + Architectural Accents
    # =========================================================================
    cards = [
        {
            "val": "12,000,000+",
            "label": "VERIFIED OCR SAMPLES",
            "sub": "Multi-Tier Document Hierarchy",
            "color": (56, 189, 248) # Sky
        },
        {
            "val": "2,400+",
            "label": "WEBDATASET SHARDS",
            "sub": "High-Throughput Streaming (.tar)",
            "color": (52, 211, 153) # Emerald
        },
        {
            "val": "23",
            "label": "PAN-INDIC LANGUAGES",
            "sub": "Constitutional & Literary Scope",
            "color": (167, 139, 250) # Iris Purple
        },
        {
            "val": "12",
            "label": "WRITING SYSTEMS",
            "sub": "Complex Text Layouts (CTL)",
            "color": (251, 191, 36) # Amber
        },
        {
            "val": "4",
            "label": "GRANULARITY TIERS",
            "sub": "Pages • Paras • Lines • Words",
            "color": (244, 114, 182) # Rose
        }
    ]

    card_y = 414
    card_w = 422
    card_h = 184
    spacing = 28
    cx_start = 65

    for idx, c_data in enumerate(cards):
        cx = cx_start + idx * (card_w + spacing)
        color = c_data["color"]

        c_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        c_draw_card = ImageDraw.Draw(c_img)
        
        c_draw_card.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=16,
                                     fill=(15, 23, 42, 220), outline=color + (140,), width=1)
        # Top color accent line (3px)
        c_draw_card.rounded_rectangle([18, 0, card_w - 18, 3], radius=2, fill=color + (240,))

        # Value
        bbox_v = c_draw_card.textbbox((0, 0), c_data["val"], font=font_card_val)
        vw = bbox_v[2] - bbox_v[0]
        vx = (card_w - vw) // 2
        c_draw_card.text((vx, 34), c_data["val"], fill=color + (255,), font=font_card_val)

        # Label
        bbox_l = c_draw_card.textbbox((0, 0), c_data["label"], font=font_card_lbl)
        lw = bbox_l[2] - bbox_l[0]
        lx = (card_w - lw) // 2
        c_draw_card.text((lx, 96), c_data["label"], fill=(241, 245, 249, 240), font=font_card_lbl)

        # Subtitle
        bbox_s = c_draw_card.textbbox((0, 0), c_data["sub"], font=font_card_sub)
        sw = bbox_s[2] - bbox_s[0]
        sx = (card_w - sw) // 2
        c_draw_card.text((sx, 130), c_data["sub"], fill=(148, 163, 184, 210), font=font_card_sub)

        card.paste(c_img, (cx, card_y), c_img)
        c_draw = ImageDraw.Draw(card)

    # =========================================================================
    # ZONE 4: FOOTER METADATA STRIP (Y: 636 -> 666)
    # =========================================================================
    footer_text = "Apache 2.0 Open Data  •  POSIX WebDataset (.tar)  •  Word & Line Level Bounding Boxes  •  Compatible with TrOCR, Donut, LayoutLMv3"
    bbox_f = c_draw.textbbox((0, 0), footer_text, font=font_footer)
    fw = bbox_f[2] - bbox_f[0]
    fx = (CARD_W - fw) // 2
    c_draw.text((fx, 638), footer_text, fill=(100, 116, 139, 220), font=font_footer)

    # Composite card onto master canvas with shadow
    canvas.paste(card, (MARGIN_X, MARGIN_Y), card)

    # Save master high-resolution RGBA PNG
    out_asset = ASSETS_DIR / "hero_banner.png"
    canvas.save(out_asset, format="PNG", optimize=True)
    
    out_artifact = BRAIN_MEDIA_DIR / "hero_banner.png"
    canvas.save(out_artifact, format="PNG", optimize=True)
    
    print(f"Generated hero banner v4 successfully: {out_asset} ({CANVAS_W}x{CANVAS_H})")
    print(f"Artifact mirror: {out_artifact}")
    return out_asset

if __name__ == "__main__":
    create_hero_banner()
