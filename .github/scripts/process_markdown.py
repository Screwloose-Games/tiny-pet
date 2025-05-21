import os
import re
import shutil
import sys
import requests

# Expect the markdown file path as the first argument
if len(sys.argv) < 2:
    print("Usage: python process_markdown.py <markdown_file_path>")
    sys.exit(1)
MARKDOWN_FILE = sys.argv[1]

ASSETS_BRANCH_PATH = "assets-branch"
ASSETS_FOLDER = os.path.join(ASSETS_BRANCH_PATH, "uploaded-assets")

os.makedirs(ASSETS_FOLDER, exist_ok=True)

# Process markdown as before
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

# Instead of writing to file, post or update GitHub comment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_ISSUE_NUMBER = os.getenv("GITHUB_ISSUE_NUMBER")

if not (GITHUB_TOKEN and GITHUB_REPOSITORY and GITHUB_ISSUE_NUMBER):
    print("Missing required GitHub environment variables.")
    sys.exit(1)

owner, repo_name = GITHUB_REPOSITORY.split("/")

api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{GITHUB_ISSUE_NUMBER}/comments"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

comment_headline = "## GLTF Validation Results\n\n"
comment_body = comment_headline + new_lines

# Find existing comments
response = requests.get(api_url, headers=headers)
if response.status_code != 200:
    print(f"Failed to fetch comments: {response.status_code}")
    sys.exit(1)
comments = response.json()

existing_comment = next((c for c in comments if c.get("body", "").startswith(comment_headline)), None)

if existing_comment:
    # Update existing comment
    update_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/comments/{existing_comment['id']}"
    update_resp = requests.patch(update_url, headers=headers, json={"body": comment_body})
    if update_resp.status_code != 200:
        print(f"Failed to update comment: {update_resp.status_code}")
        sys.exit(1)
    print("Updated existing GitHub comment.")
else:
    # Create new comment
    create_resp = requests.post(api_url, headers=headers, json={"body": comment_body})
    if create_resp.status_code != 201:
        print(f"Failed to create comment: {create_resp.status_code}")
        sys.exit(1)
    print("Created new GitHub comment.")
