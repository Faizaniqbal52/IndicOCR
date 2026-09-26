"""
Audit of the 119 samples in brx_train_00001.tar with potential Hindi markers
"""

import tarfile
import json
from pathlib import Path
from collections import Counter

cache_dir = Path(r"c:\OCR - All\scratch\hf_audit_live\cache")
bodo_tar = list(cache_dir.glob("**/brx_train_00001.tar"))[0]

hindi_markers = {
    'के', 'लिए', 'को', 'है', 'था', 'थी', 'थीं', 'पर', 'तू', 'सब', 'कर', 'नहीं', 'मंजिल',
    'होता', 'होती', 'होते', 'करना', 'करने', 'अपनी', 'अपने', 'अपना', 'बहुत', 'साथ',
    'लेकिन', 'किंतु', 'परंतु', 'क्योंकि', 'इसलिए', 'उन्होंने', 'उसने', 'जिसने', 'कि', 'हैं',
    'में', 'आप', 'से', 'ने', 'का', 'की', 'और', 'यह', 'वह', 'हुआ', 'हुए', 'हुई', 'गया', 'गए', 'गई', 'विफल'
}

with tarfile.open(bodo_tar, 'r') as tar:
    jsons = [m for m in tar.getmembers() if m.name.endswith('.json')]
    samples_with_hindi = []
    
    for m in jsons:
        meta = json.loads(tar.extractfile(m).read().decode('utf-8'))
        text = meta.get('text', '')
        words = set(text.split())
        has_hindi = [w for w in hindi_markers if w in words]
        if has_hindi:
            samples_with_hindi.append((meta.get('sample_key'), meta.get('tier'), text, has_hindi))

out_path = Path(r"c:\OCR - All\scratch\bodo_119_audit.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"Total samples with Hindi markers: {len(samples_with_hindi)} / 5,000 (2.38%)\n\n")
    marker_counts = Counter()
    for _, _, _, hw in samples_with_hindi:
        for w in hw:
            marker_counts[w] += 1
    f.write(f"Marker frequency breakdown:\n")
    for w, c in marker_counts.most_common():
        f.write(f"  '{w}': {c}\n")
    f.write("\nDetailed Samples:\n")
    for k, tier, txt, hw in samples_with_hindi[:30]:
        f.write(f"[{k}] ({tier}) Markers: {hw}\n")
        f.write(f"  Text: {txt}\n\n")

print(f"Audit written to {out_path.name}")
