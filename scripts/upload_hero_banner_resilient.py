"""
Upload hero_banner.png with automatic 429 rate limit backoff
"""

import time
import sys
from huggingface_hub import HfApi

TOKEN = os.environ.get("HF_TOKEN", "")
REPO_ID = "Faizaniqbal/IndicOCR"

api = HfApi(token=TOKEN)

max_retries = 10
base_delay = 30.0

print("Uploading assets/hero_banner.png with rate-limit resilience...")
for attempt in range(1, max_retries + 1):
    try:
        api.upload_file(
            path_or_fileobj="assets/hero_banner.png",
            path_in_repo="assets/hero_banner.png",
            repo_id=REPO_ID,
            repo_type="dataset",
            commit_message="Update Hero Banner: 12M samples, 23 languages, 12 writing systems [IndicPixel]"
        )
        print(">>> SUCCESS: hero_banner.png uploaded to Hugging Face Hub! <<<")
        sys.exit(0)
    except Exception as e:
        err_str = str(e)
        print(f"[Attempt {attempt}/{max_retries}] Upload failed: {err_str[:120]}...")
        if "429" in err_str:
            wait_time = 75 + (attempt * 15)
            print(f"Detected 429 Rate Limit. Waiting {wait_time}s for commit window to clear...")
            time.sleep(wait_time)
        else:
            time.sleep(15)

print("Failed to upload after max retries.")
sys.exit(1)
