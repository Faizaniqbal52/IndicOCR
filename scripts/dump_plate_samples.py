import sys, io
import tarfile, json, os, unicodedata

shards_dir = 'kaggle_cloud_pipeline/smoke_fleet_v11_output/shards'
langs = ['nep', 'snd', 'sat', 'mni', 'brx', 'pan', 'kan']

output_file = 'scripts/forensic_plate_samples_audit.txt'

with open(output_file, 'w', encoding='utf-8') as out:
    for lang in langs:
        tar_path = os.path.join(shards_dir, lang, f'{lang}_train_00000.tar')
        if not os.path.exists(tar_path):
            continue
        out.write("=" * 80 + "\n")
        out.write(f"DEEP LINGUISTIC INSPECTION: {lang.upper()} ({tar_path})\n")
        out.write("=" * 80 + "\n")
        
        with tarfile.open(tar_path, 'r') as tar:
            for idx in range(8):
                key = f'{lang}_{idx:07d}'
                j_name = f'{key}.json'
                try:
                    f = tar.extractfile(j_name)
                    data = json.load(f)
                    tier = data.get('tier')
                    text = data.get('text')
                    font = data.get('font_name')
                    tokens = [t.get('text') for t in data.get('tokens', [])]
                    
                    out.write(f"\n--- [{key}] Tier: {tier} | Font: {font} ---\n")
                    out.write(f"Raw Text:\n{text}\n")
                    out.write(f"Tokens ({len(tokens)}): {tokens}\n")
                    
                    # Character analysis
                    char_types = []
                    for c in text:
                        cp = ord(c)
                        cname = unicodedata.name(c, 'UNKNOWN')
                        char_types.append(f"{c} (U+{cp:04X}: {cname})")
                    out.write(f"Char Count: {len(text)} | Sample Codepoints:\n")
                    for ct in char_types[:15]:
                        out.write(f"  {ct}\n")
                    if len(char_types) > 15:
                        out.write(f"  ... (+{len(char_types)-15} more chars)\n")
                        
                except Exception as e:
                    out.write(f"[{key}] Error reading: {e}\n")

print("Audit written to:", output_file)
