import tarfile, json, os, unicodedata

out_path = 'scripts/v12_plate_samples_audit.txt'
langs = ['brx', 'mni']
shards_dir = 'kaggle_cloud_pipeline/smoke_test_v12_output/shards'

with open(out_path, 'w', encoding='utf-8') as out:
    out.write("=" * 80 + "\n")
    out.write("VERSION 12 AUDIT PLATE LINGUISTIC INSPECTION (BODO & MANIPURI)\n")
    out.write("=" * 80 + "\n\n")

    for lang in langs:
        tar_path = os.path.join(shards_dir, lang, f'{lang}_train_00000.tar')
        out.write(f">>> LANGUAGE: {lang.upper()} ({tar_path})\n")
        with tarfile.open(tar_path, 'r') as tar:
            for idx in range(8):
                key = f'{lang}_{idx:07d}'
                j_name = f'{key}.json'
                try:
                    f = tar.extractfile(j_name)
                    data = json.load(f)
                    tier = data.get('tier')
                    font = data.get('font_name')
                    text = data.get('text', '').replace('\n', ' \\n ')
                    tokens = [t.get('text') for t in data.get('tokens', [])]
                    script_chars = sum(1 for c in text if c.isalpha())
                    
                    out.write(f"\n--- [{key}] Tier: {tier} | Font: {font} | ScriptChars: {script_chars} ---\n")
                    out.write(f"Raw Text:\n  {text}\n")
                    out.write(f"Tokens ({len(tokens)}):\n  {tokens}\n")
                except Exception as e:
                    out.write(f"[{key}] Error reading: {e}\n")
        out.write("\n" + "-" * 80 + "\n\n")

print(f"Audit written to {out_path}")
