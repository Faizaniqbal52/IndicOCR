import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os, math, random, re
from PIL import Image, ImageDraw
import numpy as np

# Test the robust word-wrapping algorithm for Kannada multi-column layout
def test_kannada_word_wrap():
    page_w, page_h = 1000, 1400
    col_w = (page_w - 120) // 2  # 440px
    col1_x = 40
    col2_x = 40 + col_w + 40   # 520px
    
    # Simulate long Kannada sentences
    sample_sentence = "ಕನ್ನಡ ತೆಲುಗು ಲಿಪಿ ಒಂದೇ ಸ್ವರೂಪದ್ದಾಗಿದೆಯೆಂದು ಹೇಳಬಹುದಾದ ಅನೇಕ ಪುರಾವೆಗಳು ಸಾಹಿತ್ಯದಲ್ಲಿ ದೊರೆಯುತ್ತವೆ ಮತ್ತು ಇತಿಹಾಸಕಾರರು ಇದನ್ನು ಒಪ್ಪುತ್ತಾರೆ."
    words = sample_sentence.split()
    
    # We will simulate wrapping with approximate widths (approx 12-16px per character at font_size=18)
    def estimate_word_width(word):
        # Kannada chars have ~12-18px width depending on glyphs
        return int(len(word) * 14.5)
    
    lines = []
    curr_line = []
    curr_w = 0
    max_line_w = col_w - 20 # 420px max
    
    for w in words:
        w_len = estimate_word_width(w)
        space_len = 8
        if curr_line and (curr_w + space_len + w_len > max_line_w):
            lines.append(" ".join(curr_line))
            curr_line = [w]
            curr_w = w_len
        else:
            curr_line.append(w)
            curr_w += (space_len + w_len) if len(curr_line) > 1 else w_len
            
    if curr_line:
        lines.append(" ".join(curr_line))
        
    print(f"Total lines wrapped for col_w={col_w}: {len(lines)}")
    for i, l in enumerate(lines):
        est_w = sum(estimate_word_width(w) for w in l.split()) + (len(l.split())-1)*8
        x_end_col2 = col2_x + est_w
        print(f"  Line {i+1}: '{l}' (est width: {est_w}px | Col 2 x_end: {x_end_col2}px <= {page_w}px -> {'SAFE' if x_end_col2 <= page_w else 'OVERFLOW'})")

test_kannada_word_wrap()
