import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import tarfile, json, os

SCRIPT_RANGES = {
    'kan': range(0x0C80, 0x0CFF + 1),
    'pan': range(0x0A00, 0x0A7F + 1),
    'nep': range(0x0900, 0x097F + 1),
    'snd': range(0x0600, 0x06FF + 1),
    'brx': range(0x0900, 0x097F + 1),
    'sat': range(0x1C50, 0x1C7F + 1),
    'mni': range(0xABC0, 0xABFF + 1),
}

# Cross-language stopword contamination filters
CROSS_LANG_CONTAMINATION = {
    'brx': {'के', 'लिए', 'को', 'है', 'था', 'थी', 'थीं', 'पर', 'तू', 'सब', 'कर', 'नहीं', 'मंजिल', 'होता', 'होती', 'करना', 'अपनी', 'अपने', 'बहुत', 'साथ', 'लेकिन', 'क्योंकि', 'इसलिए'},
    'nep': {'होता', 'होती', 'होते', 'करना', 'करने', 'लेकिन', 'क्योंकि', 'इसलिए', 'उन्होंने', 'उसने'},
    'mni': set(), # Mtei is completely disjoint from Deva/Bengali
    'snd': {'ٹ', 'ڈ', 'ڑ', 'ے'}, # Pure Urdu letters absent in Sindhi
}

# Strictly verified font whitelist per language
AUTHORIZED_FONTS = {
    'kan': {'NotoSansKannada-Regular.ttf', 'NotoSerifKannada-Regular.ttf', 'BalooTamma2-Regular.ttf', 'AnekKannada-Regular.ttf'},
    'pan': {'NotoSansGurmukhi-Regular.ttf', 'NotoSerifGurmukhi-Regular.ttf', 'BalooPaaji2-Regular.ttf', 'AnekGurmukhi-Regular.ttf'},
    'nep': {'NotoSansDevanagari-Regular.ttf', 'NotoSerifDevanagari-Regular.ttf', 'YatraOne-Regular.ttf', 'RozhaOne-Regular.ttf'},
    'snd': {'NotoSansArabic-Regular.ttf', 'NotoNaskhArabic-Regular.ttf', 'Lateef-Regular.ttf', 'Amiri-Regular.ttf'},
    'brx': {'NotoSansDevanagari-Regular.ttf', 'NotoSerifDevanagari-Regular.ttf', 'YatraOne-Regular.ttf'},
    'sat': {'NotoSansOlChiki-Regular.ttf'},
    'mni': {'NotoSansMeeteiMayek-Regular.ttf'}, # NotoSansBengali is strictly prohibited!
}

def audit_shard(tar_path, lang_name):
    print("=" * 80)
    print(f"ENHANCED ZERO-DEFECT AUTOPSY: {lang_name.upper()} ({os.path.basename(tar_path)})")
    print("=" * 80)
    
    if not os.path.exists(tar_path):
        print(f"File not found: {tar_path}")
        return
        
    size_mb = os.path.getsize(tar_path) / (1024 * 1024)
    if size_mb < 5.0:
        print(f"File still downloading... ({size_mb:.2f} MB)")
        return

    script_range = SCRIPT_RANGES.get(lang_name, range(0, 0))
    contam_words = CROSS_LANG_CONTAMINATION.get(lang_name, set())
    authorized_fonts = AUTHORIZED_FONTS.get(lang_name, set())

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

    print(f"Total Samples Audited               : {len(json_members):,} pairs (JSON + lossless WebP)")
    print(f"Total Tokens Audited                : {total_tokens:,} tokens")
    print(f"Tier Breakdown                      : {tiers_count}")
    print(f"Font Distribution                   : {fonts_count}")
    print(f"Augmentation Ratio                  : {clean_count} Clean, {degraded_count} Degraded")
    print(f"Glyph ID 0 (.notdef) Count          : {zero_glyph_count}")
    print(f"Empty Text Count                    : {empty_text_count}")
    print(f"Clipped / OOB Tokens Count          : {len(clipped_tokens)}")
    print(f"Bare Punctuation / Missing Script   : {len(bare_punctuation_samples)}")
    print(f"Cross-Language Contaminated Samples : {len(cross_lang_samples)}")
    print(f"Unauthorized Font Samples           : {len(unauthorized_font_samples)}")
    
    # Forensic Defect Details if any
    if bare_punctuation_samples:
        print(f"  [DEFECT 1] Bare Punctuation Samples: {bare_punctuation_samples[:3]}")
    if cross_lang_samples:
        print(f"  [DEFECT 2] Cross-Language Samples: {cross_lang_samples[:3]}")
    if unauthorized_font_samples:
        print(f"  [DEFECT 3] Unauthorized Font Samples: {unauthorized_font_samples[:3]}")
    
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
        print(">>> RESULT: 100% INVARIANT VERIFIED — ZERO DEFECTS! CERTIFIED FLIP-READY! <<<")
    else:
        print(">>> RESULT: REJECTED / QUARANTINED — PIPELINE AMENDMENT REQUIRED! <<<")
    print()

if __name__ == '__main__':
    shards_dir = "kaggle_cloud_pipeline/smoke_fleet_v11_output/shards"
    for lang in ["kan", "nep", "brx", "mni", "pan", "sat", "snd"]:
        tar_path = os.path.join(shards_dir, lang, f"{lang}_train_00000.tar")
        if os.path.exists(tar_path):
            audit_shard(tar_path, lang)
