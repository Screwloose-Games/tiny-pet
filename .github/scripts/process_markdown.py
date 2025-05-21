import os
import re
import shutil

MARKDOWN_FILE = "README.md"
ASSETS_BRANCH_PATH = "assets-branch"
ASSETS_FOLDER = os.path.join(ASSETS_BRANCH_PATH, "uploaded-assets")

os.makedirs(ASSETS_FOLDER, exist_ok=True)

with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

image_pattern = r'!\[.*?\]\((.*?)\)'
matches = re.findall(image_pattern, content)

repo = os.getenv("GITHUB_REPOSITORY")
new_lines = content

for image_path in matches:
    if not os.path.isfile(image_path):
        continue
    filename = os.path.basename(image_path)
    target_path = os.path.join(ASSETS_FOLDER, filename)
    shutil.copy2(image_path, target_path)

    raw_url = f"https://raw.githubusercontent.com/{repo}/assets/uploaded-assets/{filename}"
    new_lines = new_lines.replace(f"]({image_path})", f"]({raw_url})")

with open(MARKDOWN_FILE, "w", encoding="utf-8") as f:
    f.write(new_lines)
