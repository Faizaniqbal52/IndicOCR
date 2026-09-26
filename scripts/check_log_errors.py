import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os, json, re, unicodedata, math, random
from PIL import Image
import numpy as np
import uharfbuzz as hb
import freetype
from fontTools.ttLib import TTFont

# Let's inspect the Punjabi fonts and corpora
fonts_dir = "kaggle_cloud_pipeline/smoke_test_v10_output/fonts/punjabi"
fonts = [
    "NotoSansGurmukhi-Regular.ttf",
    "NotoSerifGurmukhi-Regular.ttf",
    "BalooPaaji2-Regular.ttf",
    "AnekGurmukhi-Regular.ttf"
]

print("Available fonts:", fonts)
# Load Wikipedia Punjabi lines from cache or sample
# Let's see what is in indicpixel-cloud-smoke-test.log
with open("kaggle_cloud_pipeline/smoke_test_v10_output/indicpixel-cloud-smoke-test.log", "r", encoding="utf-8") as f:
    text = f.read()

# Did the log contain any stderr or traceback?
for line in text.splitlines():
    if "error" in line.lower() or "exception" in line.lower() or "traceback" in line.lower() or "failed" in line.lower():
        print(line[:120])
