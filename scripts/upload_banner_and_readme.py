"""
Upload Hero Banner v4 and updated README.md to Hugging Face Hub in a single atomic commit.
Includes automated 429 rate-limit backoff handling.
"""

import time
import sys
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd

TOKEN = os.environ.get("HF_TOKEN", "")
REPO_ID = "Faizaniqbal/IndicOCR"

api = HfApi(token=TOKEN)

banner_path = Path("assets/hero_banner.png")
readme_path = Path("README.md")

if not banner_path.exists() or not readme_path.exists():
    print(f"Error: Missing {banner_path} or {readme_path}")
    sys.exit(1)

print(f"Preparing atomic commit for {banner_path} and {readme_path}...")
operations = [
    CommitOperationAdd(path_in_repo="assets/hero_banner.png", path_or_fileobj=str(banner_path)),
    CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=str(readme_path))
]

max_retries = 12
for attempt in range(1, max_retries + 1):
    try:
        print(f"[Attempt {attempt}/{max_retries}] Pushing atomic commit to {REPO_ID}...")
        res = api.create_commit(
            repo_id=REPO_ID,
            repo_type="dataset",
            operations=operations,
            commit_message="Update Hero Banner & Data Card: Adaptive dual-mode layout & factual metrics"
        )
        print(">>> SUCCESS: Hero Banner & README.md atomically uploaded to Hugging Face Hub! <<<")
        print(f"Commit URL: {res.commit_url if hasattr(res, 'commit_url') else 'Success'}")
        sys.exit(0)
    except Exception as e:
        err_str = str(e)
        print(f"[Attempt {attempt}/{max_retries}] Upload failed: {err_str[:160]}...")
        if "429" in err_str:
            wait_time = 60 + (attempt * 15)
            print(f"Rate limit detected. Waiting {wait_time}s before retrying...")
            time.sleep(wait_time)
        else:
            time.sleep(15)

print("Failed to push after max retries.")
sys.exit(1)
