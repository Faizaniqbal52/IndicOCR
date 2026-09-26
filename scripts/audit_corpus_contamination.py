import re, sys, unicodedata
from collections import Counter
from datasets import load_dataset

# Comprehensive Cross-Language Contamination Stopwords
HINDI_STOPWORDS_IN_DEVA = {
    'के', 'लिए', 'को', 'है', 'था', 'थी', 'थीं', 'पर', 'तू', 'सब', 'कर', 'नहीं', 'मंजिल',
    'होता', 'होती', 'होते', 'करना', 'करने', 'अपनी', 'अपने', 'अपना', 'बहुत', 'साथ',
    'लेकिन', 'किंतु', 'परंतु', 'क्योंकि', 'इसलिए', 'उन्होंने', 'उसने', 'जिसने', 'कि', 'हैं'
}

BENGALI_STOPWORDS = {
    'এবং', 'ও', 'কিন্তু', 'বা', 'না', 'হয়', 'হয়ে', 'ছিল', 'করে', 'করা', 'থেকে', 'জন্য'
}

URDU_ARABIC_COMMON = {
    'اور', 'کی', 'کے', 'کا', 'میں', 'سے', 'کو', 'پر', 'ہے', 'ہیں', 'تھا', 'تھی', 'نے'
}

# Unique Sindhi characters that MUST be present in authentic Sindhi
SINDHI_DISTINCTIVE_CHARS = set('ٻڄڏڳڱڌٿٺڦڻڙڪي')

def test_bodo_corpus():
    print("=" * 70)
    print("AUDITING BODO CORPUS (alayaran/bodo-monolingual-dataset)")
    print("=" * 70)
    try:
        ds = load_dataset("alayaran/bodo-monolingual-dataset", split="train", streaming=True)
        total_inspected = 0
        hindi_contaminated = []
        clean_bodo = []
        
        for item in ds:
            total_inspected += 1
            if total_inspected > 2000:
                break
            text = item.get("text", "").strip()
            if not text:
                continue
            words = set(text.split())
            hit_stopwords = words.intersection(HINDI_STOPWORDS_IN_DEVA)
            if len(hit_stopwords) >= 2:
                hindi_contaminated.append((text[:100], hit_stopwords))
            else:
                clean_bodo.append(text[:100])
                
        print(f"Total lines inspected: {total_inspected}")
        print(f"Hindi contaminated lines found: {len(hindi_contaminated)} ({len(hindi_contaminated)/max(total_inspected,1)*100:.1f}%)")
        if hindi_contaminated:
            print("Sample contaminated lines caught:")
            for s, hits in hindi_contaminated[:5]:
                print(f"  [HITS: {hits}] -> {s}...")
    except Exception as e:
        print(f"Error testing Bodo corpus: {e}")

def test_manipuri_corpus():
    print("\n" + "=" * 70)
    print("AUDITING MANIPURI CORPUS (wikimedia/wikipedia 20231101.mni)")
    print("=" * 70)
    try:
        ds = load_dataset("wikimedia/wikipedia", "20231101.mni", split="train", streaming=True)
        total = 0
        bengali_script_lines = []
        meetei_script_lines = []
        
        for item in ds:
            total += 1
            if total > 500:
                break
            text = item.get("text", "")
            for line in text.split("\n"):
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                mtei_count = sum(1 for c in line if 0xABC0 <= ord(c) <= 0xABFF)
                beng_count = sum(1 for c in line if 0x0980 <= ord(c) <= 0x09FF)
                if beng_count > mtei_count and beng_count >= 5:
                    bengali_script_lines.append(line[:80])
                elif mtei_count >= 5:
                    meetei_script_lines.append(line[:80])
                    
        print(f"Meetei Mayek script lines: {len(meetei_script_lines)}")
        print(f"Bengali script lines in Manipuri wiki: {len(bengali_script_lines)}")
        if bengali_script_lines:
            print("Notice: Manipuri wiki contains some historical Bengali script articles:")
            for l in bengali_script_lines[:3]:
                print(f"  Bengali script line: {l}")
    except Exception as e:
        print(f"Error testing Manipuri corpus: {e}")

if __name__ == '__main__':
    test_bodo_corpus()
    test_manipuri_corpus()
