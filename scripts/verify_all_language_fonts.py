import urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont

FONTS_TO_CHECK = [
    # Devanagari
    ("NotoSansDevanagari-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf", range(0x0900, 0x097F + 1)),
    ("NotoSerifDevanagari-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifdevanagari/NotoSerifDevanagari%5Bwdth%2Cwght%5D.ttf", range(0x0900, 0x097F + 1)),
    ("YatraOne-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/yatraone/YatraOne-Regular.ttf", range(0x0900, 0x097F + 1)),
    ("RozhaOne-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/rozhaone/RozhaOne-Regular.ttf", range(0x0900, 0x097F + 1)),
    # Arabic / Perso-Arabic (Sindhi, Kashmiri, Urdu)
    ("NotoSansArabic-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf", range(0x0600, 0x06FF + 1)),
    ("NotoNaskhArabic-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notonaskharabic/NotoNaskhArabic%5Bwght%5D.ttf", range(0x0600, 0x06FF + 1)),
    ("Lateef-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/lateef/Lateef-Regular.ttf", range(0x0600, 0x06FF + 1)),
    # Gurmukhi (Punjabi)
    ("NotoSansGurmukhi-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansgurmukhi/NotoSansGurmukhi%5Bwdth%2Cwght%5D.ttf", range(0x0A00, 0x0A7F + 1)),
    ("NotoSerifGurmukhi-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifgurmukhi/NotoSerifGurmukhi%5Bwght%5D.ttf", range(0x0A00, 0x0A7F + 1)),
    ("BalooPaaji2-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/baloopaaji2/BalooPaaji2%5Bwght%5D.ttf", range(0x0A00, 0x0A7F + 1)),
    # Kannada (Kannada, Tulu)
    ("NotoSansKannada-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskannada/NotoSansKannada%5Bwdth%2Cwght%5D.ttf", range(0x0C80, 0x0CFF + 1)),
    ("NotoSerifKannada-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifkannada/NotoSerifKannada%5Bwght%5D.ttf", range(0x0C80, 0x0CFF + 1)),
    ("BalooTamma2-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/balootamma2/BalooTamma2%5Bwght%5D.ttf", range(0x0C80, 0x0CFF + 1)),
]

test_dir = Path("c:/OCR - All/scratch/font_test")
test_dir.mkdir(parents=True, exist_ok=True)
headers = {"User-Agent": "Mozilla/5.0"}

print(f"Testing {len(FONTS_TO_CHECK)} font URLs and cmap coverage...", flush=True)
for fname, url, srange in FONTS_TO_CHECK:
    fpath = test_dir / fname
    try:
        if not fpath.exists():
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(fpath, "wb") as f:
                f.write(data)
        tt = TTFont(str(fpath))
        cmap = tt.getBestCmap()
        cps = sum(1 for cp in cmap.keys() if cp in srange)
        print(f"  [OK] {fname:32s}: {fpath.stat().st_size / 1024:.1f} KB | {cps} script codepoints in cmap", flush=True)
    except Exception as e:
        print(f"  [FAIL] {fname}: {e}", flush=True)

print("Font verification complete!", flush=True)
