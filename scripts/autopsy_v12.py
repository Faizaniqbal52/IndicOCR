import sys, os, tarfile, json

SCRIPT_RANGES = {
    'brx': range(0x0900, 0x097F + 1),
    'mni': range(0xABC0, 0xABFF + 1),
}

CROSS_LANG_CONTAMINATION = {
    'brx': {'के', 'लिए', 'को', 'है', 'था', 'थी', 'थीं', 'पर', 'तू', 'सब', 'कर', 'नहीं', 'मंजिल', 'होता', 'होती', 'करना', 'अपनी', 'अपने', 'बहुत', 'साथ', 'लेकिन', 'क्योंकि', 'इसलिए'},
    'mni': set(),
}

AUTHORIZED_FONTS = {
    'brx': {'NotoSansDevanagari-Regular.ttf', 'NotoSerifDevanagari-Regular.ttf', 'YatraOne-Regular.ttf'},
    'mni': {'NotoSansMeeteiMayek-Regular.ttf'},
}

def audit_v12_shard(tar_path, lang_name, out):
    out.write("=" * 80 + "\n")
    out.write(f"VERSION 12 FORENSIC AUTOPSY: {lang_name.upper()} ({os.path.basename(tar_path)})\n")
    out.write("=" * 80 + "\n")
    
    script_range = SCRIPT_RANGES[lang_name]
    contam_words = CROSS_LANG_CONTAMINATION.get(lang_name, set())
    authorized_fonts = AUTHORIZED_FONTS[lang_name]

    with tarfile.open(tar_path, "r") as tar:
        members = tar.getmembers()
        json_members = [m for m in members if m.name.endswith(".json")]
        webp_members = [m for m in members if m.name.endswith(".webp")]
        
        fonts_count = {}
        tiers_count = {}
        clean_count = 0
        degraded_count = 0
        total_tokens = 0
        clipped_tokens = []
        zero_glyph_count = 0
        empty_text_count = 0
        bare_punctuation_samples = []
        cross_lang_samples = []
        unauthorized_font_samples = []
        
        for m in json_members:
            f = tar.extractfile(m)
            data = json.load(f)
            
            tier = data.get("tier", "Unknown")
            tiers_count[tier] = tiers_count.get(tier, 0) + 1
            
            font = data.get("font_name", "Unknown")
            fonts_count[font] = fonts_count.get(font, 0) + 1
            
            if font not in authorized_fonts:
                unauthorized_font_samples.append((m.name, font))
            
            if data.get("is_clean", False):
                clean_count += 1
            else:
                degraded_count += 1
                
            text = data.get("text", "")
            if not text.strip():
                empty_text_count += 1
                
            # Gate 1: Check for bare punctuation / stripped script characters
            script_chars = sum(1 for c in text if ord(c) in script_range)
            if script_chars < 2:
                bare_punctuation_samples.append((m.name, font, text))
                
            # Gate 2: Check for cross-language contamination
            if contam_words:
                words = set(text.split())
                hits = words.intersection(contam_words)
                if len(hits) >= 2:
                    cross_lang_samples.append((m.name, hits, text[:60]))
                
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

    out.write(f"Total Samples Audited               : {len(json_members):,} pairs (JSON + lossless WebP)\n")
    out.write(f"Total Tokens Audited                : {total_tokens:,} tokens\n")
    out.write(f"Tier Breakdown                      : {tiers_count}\n")
    out.write(f"Font Distribution                   : {fonts_count}\n")
    out.write(f"Augmentation Ratio                  : {clean_count} Clean, {degraded_count} Degraded\n")
    out.write(f"Glyph ID 0 (.notdef) Count          : {zero_glyph_count}\n")
    out.write(f"Empty Text Count                    : {empty_text_count}\n")
    out.write(f"Clipped / OOB Tokens Count          : {len(clipped_tokens)}\n")
    out.write(f"Bare Punctuation / Missing Script   : {len(bare_punctuation_samples)}\n")
    out.write(f"Cross-Language Contaminated Samples : {len(cross_lang_samples)}\n")
    out.write(f"Unauthorized Font Samples           : {len(unauthorized_font_samples)}\n")
    
    passed = (
        len(json_members) == 5000 and
        len(webp_members) == 5000 and
        len(clipped_tokens) == 0 and
        zero_glyph_count == 0 and
        len(bare_punctuation_samples) == 0 and
        len(cross_lang_samples) == 0 and
        len(unauthorized_font_samples) == 0
    )
    
    if passed:
        out.write(">>> RESULT: 100% INVARIANT VERIFIED — ZERO DEFECTS! CERTIFIED FLIP-READY! <<<\n")
    else:
        out.write(">>> RESULT: REJECTED / QUARANTINED! <<<\n")
    out.write("\n")

out_file = 'scripts/autopsy_v12_report.txt'
with open(out_file, 'w', encoding='utf-8') as out:
    shards_dir = 'kaggle_cloud_pipeline/smoke_test_v12_output/shards'
    for lang in ['brx', 'mni']:
        tar_path = os.path.join(shards_dir, lang, f'{lang}_train_00000.tar')
        audit_v12_shard(tar_path, lang, out)

print(f"Report written to {out_file}")
