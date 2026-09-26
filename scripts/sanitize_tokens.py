import os

target_str = os.environ.get("HF_TOKEN", "")
root_dir = r"c:\OCR - All"

sanitized_count = 0
for root, dirs, files in os.walk(root_dir):
    if ".git" in root or "data" in root:
        continue
    for fn in files:
        if fn.endswith((".py", ".md", ".json", ".txt", ".sh", ".yaml", ".yml")) and fn != ".env":
            fp = os.path.join(root, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if target_str in content:
                    new_content = content.replace(f'"{target_str}"', 'os.environ.get("HF_TOKEN", "")')
                    new_content = new_content.replace(f"'{target_str}'", 'os.environ.get("HF_TOKEN", "")')
                    new_content = new_content.replace(target_str, 'os.environ.get("HF_TOKEN", "")')
                    with open(fp, "w", encoding="utf-8") as out_f:
                        out_f.write(new_content)
                    print(f"Sanitized: {fp}")
                    sanitized_count += 1
            except Exception as e:
                print(f"Error {fp}: {e}")

print(f"Total sanitized files: {sanitized_count}")
