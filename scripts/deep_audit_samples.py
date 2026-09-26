import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import tarfile, json, os
from PIL import Image
import numpy as np

def deep_inspect_samples(tar_path, lang, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with tarfile.open(tar_path, 'r') as tar:
        members = tar.getmembers()
        json_members = [m for m in members if m.name.endswith('.json')]
        
        tier_samples = {}
        for m in json_members:
            f = tar.extractfile(m)
            data = json.load(f)
            t = data.get('tier')
            if t not in tier_samples:
                tier_samples[t] = []
            if len(tier_samples[t]) < 3:
                base_name = m.name[:-5]
                im_member = tar.getmember(f"{base_name}.webp")
                im_bytes = tar.extractfile(im_member).read()
                im = Image.open(io.BytesIO(im_bytes))
                tier_samples[t].append((data, im, base_name))
        
        print(f"=== {lang.upper()} DEEP SAMPLE INSPECTION ===")
        for tier, sample_list in tier_samples.items():
            print(f"\n--- Tier: {tier} ---")
            for data, im, name in sample_list:
                tokens = data.get('tokens', [])
                font = data.get('font_name')
                is_clean = data.get('is_clean')
                text_preview = data.get('text', '')[:50].replace('\n', ' ')
                
                # Check mean brightness and contrast
                im_gray = im.convert('L')
                arr = np.array(im_gray)
                mean_bright = np.mean(arr)
                std_bright = np.std(arr)
                
                print(f"Sample {name} ({font}) | Clean: {is_clean} | Canvas: {im.size} | Mean: {mean_bright:.1f}, Std: {std_bright:.1f} | Tokens: {len(tokens)}")
                print(f"  Text: {text_preview}")

deep_inspect_samples('c:/OCR - All/kaggle_cloud_pipeline/latest_cloud_output/shards/kan/kan_train_00000.tar', 'Kannada', 'kaggle_cloud_pipeline/deep_audit/kan')
deep_inspect_samples('c:/OCR - All/kaggle_cloud_pipeline/latest_cloud_output/shards/pan/pan_train_00000.tar', 'Punjabi', 'kaggle_cloud_pipeline/deep_audit/pan')
