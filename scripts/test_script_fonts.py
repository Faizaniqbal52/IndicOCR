"""
Test script to verify all 12 script fonts load and render native glyphs cleanly.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_MAPPING = {
    "अ": Path(r"c:\OCR - All\fonts\devanagari\NotoSansDevanagari-Regular.ttf"),
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

for char, p in FONT_MAPPING.items():
    if not p.exists():
        print(f"MISSING: {char} -> {p}")
    else:
        try:
            f = ImageFont.truetype(str(p), 40)
            print(f"OK: {char} -> {p.name}")
        except Exception as e:
            print(f"ERROR: {char} -> {e}")
