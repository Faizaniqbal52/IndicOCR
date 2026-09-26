import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import tarfile, json, os

tar_path = "kaggle_cloud_pipeline/smoke_test_v10_output/shards/pan/pan_train_00000.tar"
with tarfile.open(tar_path, "r") as tar:
    members = tar.getmembers()
    json_members = [m for m in members if m.name.endswith(".json")]
    print(f"Total Punjabi JSON members: {len(json_members)}")
    
    zero_glyph_count = 0
    empty_text_count = 0
    clipped_tokens = []
    tiers_count = {}
    fonts_count = {}
    clean_count = 0
    degraded_count = 0
    total_tokens = 0
    
    for m in json_members:
        f = tar.extractfile(m)
        data = json.load(f)
        
        tier = data.get("tier", "Unknown")
        tiers_count[tier] = tiers_count.get(tier, 0) + 1
        
        font = data.get("font_name", "Unknown")
        fonts_count[font] = fonts_count.get(font, 0) + 1
        
        if data.get("is_clean", False):
            clean_count += 1
        else:
            degraded_count += 1
            
        text = data.get("text", "")
        if not text.strip():
            empty_text_count += 1
            
        glyphs = data.get("shaped_glyphs", [])
        for g in glyphs:
            if g.get("glyph_id", 1) == 0:
                zero_glyph_count += 1
                
        cw, ch = data.get("canvas_size", [0, 0])
        tokens = data.get("tokens", [])
        total_tokens += len(tokens)
        
        for tok in tokens:
            bb = tok.get("bbox", [0, 0, 0, 0])
            if len(bb) == 4:
                x1, y1, x2, y2 = bb
                if x2 > cw or y2 > ch or x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
                    clipped_tokens.append((m.name, tier, (cw, ch), tok.get("text"), bb))

print(f"Total Tokens Audited       : {total_tokens:,}")
print(f"Tier Breakdown             : {tiers_count}")
print(f"Font Distribution          : {fonts_count}")
print(f"Clean/Degraded             : {clean_count} Clean, {degraded_count} Degraded")
print(f"Zero Glyph Count           : {zero_glyph_count}")
print(f"Empty Text Count           : {empty_text_count}")
print(f"Clipped Tokens Count       : {len(clipped_tokens)}")
