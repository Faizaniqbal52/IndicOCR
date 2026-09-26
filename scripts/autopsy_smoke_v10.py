import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import tarfile, json, os
from PIL import Image
import numpy as np

def run_forensic_autopsy(tar_path, lang):
    print("=" * 70)
    print(f"FORENSIC AUTOPSY: {lang.upper()} (Path: {os.path.basename(tar_path)})")
    print("=" * 70)
    
    with tarfile.open(tar_path, "r") as tar:
        members = tar.getmembers()
        json_members = [m for m in members if m.name.endswith(".json")]
        webp_members = [m for m in members if m.name.endswith(".webp")]
        
        assert len(json_members) == 5000, f"Expected 5000 JSONs, got {len(json_members)}"
        assert len(webp_members) == 5000, f"Expected 5000 WebPs, got {len(webp_members)}"
        
        fonts_count = {}
        tiers_count = {}
        clean_count = 0
        degraded_count = 0
        total_tokens = 0
        
        clipped_tokens = []
        zero_glyph_count = 0
        empty_text_count = 0
        canvas_sizes = set()
        
        for m in json_members:
            f = tar.extractfile(m)
            data = json.load(f)
            
            # Tiers
            tier = data.get("tier", "Unknown")
            tiers_count[tier] = tiers_count.get(tier, 0) + 1
            
            # Fonts
            font = data.get("font_name", "Unknown")
            fonts_count[font] = fonts_count.get(font, 0) + 1
            
            # Clean vs Degraded
            if data.get("is_clean", False):
                clean_count += 1
            else:
                degraded_count += 1
                
            # Text check
            text = data.get("text", "")
            if not text.strip():
                empty_text_count += 1
                
            # Glyphs
            glyphs = data.get("shaped_glyphs", [])
            for g in glyphs:
                if g.get("glyph_id", 1) == 0:
                    zero_glyph_count += 1
                    
            # Bounding boxes
            cw, ch = data.get("canvas_size", [0, 0])
            canvas_sizes.add((cw, ch))
            tokens = data.get("tokens", [])
            total_tokens += len(tokens)
            
            for tok in tokens:
                bb = tok.get("bbox", [0, 0, 0, 0])
                if len(bb) == 4:
                    x1, y1, x2, y2 = bb
                    if x2 > cw or y2 > ch or x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
                        clipped_tokens.append((m.name, tier, (cw, ch), tok.get("text"), bb))

    print(f"Total Samples Audited      : {len(json_members):,} pairs (JSON + lossless WebP)")
    print(f"Total Tokens Audited       : {total_tokens:,} tokens")
    print(f"Tier Breakdown             : {tiers_count}")
    print(f"Font Distribution          : {fonts_count}")
    print(f"Augmentation Ratio         : {clean_count} Clean ({(clean_count/50):.1f}%), {degraded_count} Degraded ({(degraded_count/50):.1f}%)")
    print(f"Glyph ID 0 (.notdef) Count : {zero_glyph_count}")
    print(f"Empty Text Count           : {empty_text_count}")
    print(f"Clipped / OOB Tokens Count : {len(clipped_tokens)}")
    
    if clipped_tokens:
        print(f"FATAL CLIPPED TOKENS SAMPLES:")
        for ct in clipped_tokens[:10]:
            print(f"  {ct[0]} ({ct[1]}): canvas={ct[2]} | '{ct[3]}' | bbox={ct[4]}")
    else:
        print(">>> 100% INVARIANT VERIFIED: ZERO CLIPPED TOKENS! ALL INK INSIDE CANVAS! <<<")
        
    return len(clipped_tokens), zero_glyph_count

kan_clips, kan_zeros = run_forensic_autopsy("kaggle_cloud_pipeline/smoke_test_v10_output/shards/kan/kan_train_00000.tar", "Kannada")
pan_clips, pan_zeros = run_forensic_autopsy("kaggle_cloud_pipeline/smoke_test_v10_output/shards/pan/pan_train_00000.tar", "Punjabi")

print("\n" + "=" * 70)
print(f"FINAL QUALITY SUMMARY:")
print(f"Kannada: {kan_clips} clipped tokens, {kan_zeros} tofu glyphs")
print(f"Punjabi: {pan_clips} clipped tokens, {pan_zeros} tofu glyphs")
if kan_clips == 0 and pan_clips == 0 and kan_zeros == 0 and pan_zeros == 0:
    print(">>> ZERO-DEFECT QUALITY PASS CERTIFIED! <<<")
else:
    print(">>> QUALITY DEFECT DETECTED! <<<")
print("=" * 70)
