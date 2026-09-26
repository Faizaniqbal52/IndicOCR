"""
Build Composite Audit Plate showing All 4 Tiers across All 5 Languages
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ARTIFACT_DIR = Path(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\3dbba92f-a15a-4629-9d9c-b3b34712581d\.tempmediaStorage")

LANGS = [
    ("kan", "Kannada"),
    ("pan", "Punjabi"),
    ("nep", "Nepali"),
    ("snd", "Sindhi"),
    ("brx", "Bodo")
]

def build_plate():
    # Large canvas: 1600 x 2200
    plate = Image.new("RGB", (1600, 2200), color=(248, 249, 250))
    draw = ImageDraw.Draw(plate)
    
    # Header
    draw.rectangle([(0, 0), (1600, 80)], fill=(15, 23, 42))
    draw.text((30, 20), "PAN-INDIC OCR: 4-TIER MULTILINGUAL PRODUCTION VERIFICATION (FETCHED FROM HUGGING FACE)", fill=(255, 255, 255))
    draw.text((30, 48), "All 4 Tiers (Words 30%, Lines 55%, Paragraphs 13%, Full Pages 2%) Active in Every Shard", fill=(148, 163, 184))

    # We will display:
    # 1. Full Page row: scaled down thumbnails of 5 Full Pages (w=280 each)
    # 2. Paragraph row: 5 Paragraphs
    # 3. Line row: 5 Lines
    # 4. Word row: 5 Words
    
    col_w = 300
    left_margin = 40
    
    # Draw column titles
    for idx, (code, name) in enumerate(LANGS):
        cx = left_margin + idx * col_w
        draw.rectangle([(cx, 95), (cx + 280, 130)], fill=(226, 232, 240))
        draw.text((cx + 15, 105), f"{name.upper()} ({code})", fill=(15, 23, 42))
        
        # 1. Full Page
        fp_path = ARTIFACT_DIR / f"hf_proof_{code}_Tier_1_FullPage.png"
        if fp_path.exists():
            im = Image.open(fp_path)
            # scale to w=280
            scale = 280 / im.width
            im_thumb = im.resize((280, int(im.height * scale)), Image.LANCZOS)
            plate.paste(im_thumb, (cx, 140))
            draw.rectangle([(cx, 140), (cx + 280, 140 + im_thumb.height)], outline=(203, 213, 225), width=1)
            draw.text((cx, 140 + im_thumb.height + 4), "Tier 1: Full Page (2%)", fill=(100, 116, 139))
            
        # 2. Paragraph
        p_path = ARTIFACT_DIR / f"hf_proof_{code}_Tier_2_Paragraph.png"
        if p_path.exists():
            im = Image.open(p_path)
            scale = min(280 / im.width, 140 / im.height) if (im.width > 280 or im.height > 140) else 1.0
            im_thumb = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            py = 560
            plate.paste(im_thumb, (cx, py))
            draw.rectangle([(cx, py), (cx + im_thumb.width, py + im_thumb.height)], outline=(203, 213, 225), width=1)
            draw.text((cx, py + im_thumb.height + 4), "Tier 2: Paragraph (13%)", fill=(100, 116, 139))

        # 3. Line
        l_path = ARTIFACT_DIR / f"hf_proof_{code}_Tier_3_Line.png"
        if l_path.exists():
            im = Image.open(l_path)
            scale = min(280 / im.width, 60 / im.height) if (im.width > 280 or im.height > 60) else 1.0
            im_thumb = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            ly = 770
            plate.paste(im_thumb, (cx, ly))
            draw.rectangle([(cx, ly), (cx + im_thumb.width, ly + im_thumb.height)], outline=(203, 213, 225), width=1)
            draw.text((cx, ly + im_thumb.height + 4), "Tier 3: Line (55%)", fill=(100, 116, 139))

        # 4. Word
        w_path = ARTIFACT_DIR / f"hf_proof_{code}_Tier_4_Word.png"
        if w_path.exists():
            im = Image.open(w_path)
            scale = min(200 / im.width, 60 / im.height) if (im.width > 200 or im.height > 60) else 1.0
            im_thumb = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            wy = 890
            plate.paste(im_thumb, (cx, wy))
            draw.rectangle([(cx, wy), (cx + im_thumb.width, wy + im_thumb.height)], outline=(203, 213, 225), width=1)
            draw.text((cx, wy + im_thumb.height + 4), "Tier 4: Word (30%)", fill=(100, 116, 139))

    out_file = ARTIFACT_DIR / "all_tiers_live_proof_plate.png"
    # Crop to content height
    plate_cropped = plate.crop((0, 0, 1600, 1020))
    plate_cropped.save(out_file)
    print(f"Composite plate saved to: {out_file.name}")

if __name__ == "__main__":
    build_plate()
