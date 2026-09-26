"""
Generate State-of-the-Art Hero Banner for IndicPixel (Faizaniqbal/IndicOCR)
Optimized for both Light Mode and Dark Mode on Hugging Face Hub.
Uses genuine per-script Noto fonts for zero tofu / zero .notdef rendering.
Resolution: 2400 x 640 px (High-DPI Retina Display).
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

# 12 Verified Script Fonts for Native Watermark Glyphs
FONT_MAPPING = {
    "अ": Path(r"c:\OCR - All\fonts\devanagari\NotoSansDevanagari.ttf"),
    "অ": Path(r"c:\OCR - All\fonts\bengali\NotoSansBengali-Regular.ttf"),
    "அ": Path(r"c:\OCR - All\fonts\tamil\NotoSansTamil-Regular.ttf"),
    "అ": Path(r"c:\OCR - All\fonts\telugu\NotoSansTelugu-Regular.ttf"),
    "ಅ": Path(r"c:\OCR - All\kaggle_cloud_pipeline\latest_cloud_output\fonts\kannada\NotoSansKannada-Regular.ttf"),
    "ਅ": Path(r"c:\OCR - All\kaggle_cloud_pipeline\latest_cloud_output\fonts\punjabi\NotoSansGurmukhi-Regular.ttf"),
    "અ": Path(r"c:\OCR - All\fonts\gujarati\NotoSansGujarati-Regular.ttf"),
    "അ": Path(r"c:\OCR - All\fonts\malayalam\NotoSansMalayalam-Regular.ttf"),
    "ଅ": Path(r"c:\OCR - All\fonts\odia\NotoSansOriya-Regular.ttf"),
    "أ": Path(r"C:\Windows\Fonts\segoeui.ttf"),
    "ᱥ": Path(r"c:\OCR - All\kaggle_cloud_pipeline\smoke_fleet_v11_output\fonts\sat\NotoSansOlChiki-Regular.ttf"),
    "ꯃ": Path(r"c:\OCR - All\kaggle_cloud_pipeline\smoke_fleet_v11_output\fonts\mni\NotoSansMeeteiMayek-Regular.ttf"),
}

def find_font(font_name, size, fallback="arial.ttf"):
    windows_font_dir = Path("C:/Windows/Fonts")
    candidates = [
        windows_font_dir / font_name,
        windows_font_dir / fallback,
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf")
    ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_hero_banner():
    W, H = 2400, 640
    
    # Base deep slate canvas with gradient from #080c14 to #0c1424
    img = Image.new("RGBA", (W, H), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        ratio = y / H
        r = int(8 + (12 - 8) * ratio)
        g = int(12 + (20 - 12) * ratio)
        b = int(20 + (36 - 20) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 1. Atmospheric Ambient Glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([(-120, -120), (750, 420)], fill=(56, 189, 248, 26))  # Cyan glow
    g_draw.ellipse([(1650, 180), (2520, 720)], fill=(168, 85, 247, 24)) # Purple glow
    g_draw.ellipse([(850, -60), (1550, 320)], fill=(16, 185, 129, 18))   # Emerald glow
    glow = glow.filter(ImageFilter.GaussianBlur(85))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 2. Sleek Outer Border for Light & Dark Mode Adaptability
    draw.rounded_rectangle([4, 4, W - 5, H - 5], radius=22, outline=(51, 65, 85, 230), width=2)
    # Inner subtle glow edge
    draw.rounded_rectangle([6, 6, W - 7, H - 7], radius=20, outline=(30, 41, 59, 140), width=1)

    # 3. Native Script Glyphs Watermark (Along the top edge, safely above text)
    gx_start = 120
    spacing_g = 180
    gy = 20
    for idx, (glyph, font_path) in enumerate(FONT_MAPPING.items()):
        if font_path.exists():
            try:
                g_font = ImageFont.truetype(str(font_path), 38)
                gx = gx_start + idx * spacing_g
                # Elegant translucent slate watermark
                draw.text((gx, gy), glyph, fill=(148, 163, 184, 26), font=g_font)
            except Exception:
                pass

    # 4. Standard UI Typography
    font_pill = find_font("segoeuib.ttf", 15, "arialbd.ttf")
    font_brand = find_font("segoeuib.ttf", 66, "arialbd.ttf")
    font_sub_brand = find_font("segoeuib.ttf", 25, "arialbd.ttf")
    font_desc = find_font("segoeui.ttf", 21, "arial.ttf")
    font_val = find_font("segoeuib.ttf", 34, "arialbd.ttf")
    font_lbl = find_font("segoeuib.ttf", 14, "arialbd.ttf")
    font_footer = find_font("segoeui.ttf", 17, "arial.ttf")

    # 5. Top Pill Badge: Positioned cleanly
    pill_x, pill_y = 90, 72
    pill_text = "FOUNDATIONAL PAN-INDIC DOCUMENT AI & OCR BENCHMARK"
    bbox_p = draw.textbbox((0, 0), pill_text, font=font_pill)
    pw = (bbox_p[2] - bbox_p[0]) + 36
    ph = 32
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + ph], radius=16,
                           fill=(15, 23, 42, 230), outline=(56, 189, 248, 140), width=1)
    # Glowing green status pip
    draw.ellipse([pill_x + 12, pill_y + 11, pill_x + 22, pill_y + 21], fill=(52, 211, 153, 255))
    draw.text((pill_x + 28, pill_y + 6), pill_text, fill=(226, 232, 240, 240), font=font_pill)

    # 6. Brand Lockup
    brand_x = 90
    brand_y = 118
    # Cyan drop shadow / glow
    draw.text((brand_x + 2, brand_y + 2), "INDICPIXEL", fill=(14, 165, 233, 140), font=font_brand)
    draw.text((brand_x, brand_y), "INDICPIXEL", fill=(56, 189, 248, 255), font=font_brand)

    # Separator & Subtitle
    sep_x = brand_x + 405
    draw.text((sep_x, brand_y + 16), "|", fill=(100, 116, 139, 180), font=font_sub_brand)
    draw.text((sep_x + 26, brand_y + 24), "23 SOUTH ASIAN LANGUAGES  •  12 WRITING SYSTEMS", fill=(248, 250, 252, 250), font=font_sub_brand)

    # Description
    draw.text((brand_x, brand_y + 88), "Dense 4-Tier Document Structure with Word-Level Bounding Box Ground Truth Across Pan-Indic Scripts",
              fill=(148, 163, 184, 230), font=font_desc)

    # 7. Executive Metric Badges (5 Cards)
    cards = [
        ("12,000,000+", "VERIFIED SAMPLES", (56, 189, 248)),     # Vibrant Cyan
        ("2,400+ SHARDS", "POSIX WEBDATASET", (52, 211, 153)),    # Emerald
        ("23 LANGUAGES", "SCHEDULED & LITERARY", (192, 132, 252)), # Purple
        ("12 SCRIPTS", "WRITING SYSTEMS", (251, 191, 36)),       # Amber Gold
        ("4-TIER HIERARCHY", "PAGES • PARAS • LINES • WORDS", (244, 114, 182)) # Rose
    ]

    card_y = 282
    card_w = 412
    card_h = 192
    spacing = 38
    cx_start = 90

    for idx, (val, label, stroke_color) in enumerate(cards):
        cx = cx_start + idx * (card_w + spacing)
        
        # Card Background
        card_bg = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(card_bg)
        # Deep slate with translucent fill
        c_draw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=16,
                                fill=(15, 23, 42, 220), outline=stroke_color + (130,), width=2)
        # Top glowing accent line
        c_draw.rounded_rectangle([20, 0, card_w - 20, 4], radius=2, fill=stroke_color + (240,))
        
        img.paste(card_bg, (cx, card_y), card_bg)
        draw = ImageDraw.Draw(img)

        # Center numerical value
        bbox_val = draw.textbbox((0, 0), val, font=font_val)
        val_w = bbox_val[2] - bbox_val[0]
        val_x = cx + (card_w - val_w) // 2
        val_y = card_y + 54
        draw.text((val_x, val_y), val, fill=stroke_color + (255,), font=font_val)

        # Center label
        bbox_lbl = draw.textbbox((0, 0), label, font=font_lbl)
        lbl_w = bbox_lbl[2] - bbox_lbl[0]
        lbl_x = cx + (card_w - lbl_w) // 2
        lbl_y = card_y + 118
        draw.text((lbl_x, lbl_y), label, fill=(148, 163, 184, 240), font=font_lbl)

    # 8. Footer Section
    footer_y = 542
    footer_text = "High-Fidelity Complex Text Layout (CTL)  •  Dynamic Zone Metric Protection  •  Word-Level Bounding Box Ground Truth  •  Apache 2.0"
    bbox_ft = draw.textbbox((0, 0), footer_text, font=font_footer)
    ft_w = bbox_ft[2] - bbox_ft[0]
    ft_x = (W - ft_w) // 2
    draw.text((ft_x, footer_y), footer_text, fill=(100, 116, 139, 230), font=font_footer)

    # 9. Save and Export
    out_asset = ASSETS_DIR / "hero_banner.png"
    img.convert("RGB").save(out_asset, format="PNG", quality=95)
    
    out_artifact = BRAIN_MEDIA_DIR / "hero_banner.png"
    img.convert("RGB").save(out_artifact, format="PNG", quality=95)
    
    print(f"Successfully generated hero banner: {out_asset}")
    print(f"Saved artifact copy to: {out_artifact}")

if __name__ == "__main__":
    create_hero_banner()
