import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os, json, re, unicodedata
from datasets import load_dataset
from collections import Counter

# Let's inspect what happened in Punjabi at index 9, 30, 143...
# What tier was index 9?
# In task_tiers:
# words: 30% (1500)
# lines: 55% (2750)
# paras: 13% (650)
# pages: 2% (100)
# How was task_tiers constructed in indicpixel_kaggle_cloud_pipeline.py?
with open("kaggle_cloud_pipeline/indicpixel_kaggle_cloud_pipeline.py", "r", encoding="utf-8") as f:
    text = f.read()

# find task_tiers construction
for line in text.splitlines():
    if "task_tiers" in line:
        print(line)
