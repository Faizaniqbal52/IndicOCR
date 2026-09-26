import json, sys

with open('scripts/comprehensive_sample_audit.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('scripts/all_lines_report.txt', 'w', encoding='utf-8') as out:
    for lang, samples in data.items():
        out.write('=' * 80 + '\n')
        out.write(f'LANGUAGE: {lang.upper()} (Total Samples: {len(samples)})\n')
        out.write('=' * 80 + '\n')
        for s in samples:
            out.write(f"\n--- Sample: {s['sample_id']} | Tier: {s['tier']} | Font: {s['font']} ---\n")
            for line in s['lines']:
                words = [w['word'] for w in line['words']]
                out.write(f"  [L{line['line_num']}] ({len(words)} words): {' '.join(words)}\n")
                # List each word and its characters
                for w_obj in line['words']:
                    w = w_obj['word']
                    cps = [f"{c['char']}({c['codepoint']})" for c in w_obj['chars']]
                    out.write(f"     Word: {w:<20} | Chars: {' '.join(cps)}\n")

print("Generated scripts/all_lines_report.txt successfully.")
