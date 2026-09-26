import sys
from datasets import load_dataset

token = os.environ.get("HF_TOKEN", "")

candidates = [
    ('Bhojpuri', 'bho', '20231101.bh'),
    ('Maithili', 'mai', '20231101.mai'),
    ('Konkani', 'gom', '20231101.gom'),
    ('Kashmiri', 'kas', '20231101.ks'),
    ('Newari', 'new', '20231101.new'),
    ('Awadhi', 'awa', '20231101.awa'),
    ('Dogri', 'doi', '20231101.doi'),
]

print("Testing Wikipedia...", flush=True)
for name, code, cfg in candidates:
    try:
        ds = load_dataset('wikimedia/wikipedia', cfg, split='train', streaming=True, token=token)
        s = next(iter(ds))
        txt = s.get('text', '')[:40].replace('\n', ' ')
        print(f"[WIKI OK] {name} ({code}, {cfg}): {txt}", flush=True)
    except Exception as e:
        print(f"[WIKI FAIL] {name} ({code}, {cfg}): {e}", flush=True)

# Also test Sangraha for Dogri, Konkani, Kashmiri, Maithili, Bodo
print("\nTesting Sangraha...", flush=True)
for lang_dir in ['doi', 'kok', 'kas', 'mai', 'brx']:
    try:
        ds = load_dataset('ai4bharat/sangraha', data_dir=f'data/{lang_dir}', split='train', streaming=True, token=token)
        s = next(iter(ds))
        txt = s.get('text', '')[:40].replace('\n', ' ')
        print(f"[SANGRAHA OK] {lang_dir}: {txt}", flush=True)
    except Exception as e:
        print(f"[SANGRAHA FAIL] {lang_dir}: {e}", flush=True)
