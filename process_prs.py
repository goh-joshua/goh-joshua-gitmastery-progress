import subprocess
import json
import os

from github import Github

g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

processed_users = []
user_map = {}

os.makedirs("students", exist_ok=True)

for pr in repo.get_pulls(state="open", base="main"):
    username = pr.user.login
    user_id = pr.user.id
    pr_repo = pr.head.repo
    pr_ref = pr.head.ref

    try:
        contents = pr_repo.get_contents("progress.json", ref=pr_ref)
        progress_data = json.loads(contents.decoded_content.decode())

        with open(f"students/{user_id}.json", "w") as f:
            json.dump(progress_data, f, indent=2)

        user_map[user_id] = username

        subprocess.run(["git", "add", f"students/{user_id}.json"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Update {username} progress"], check=True
        )

        print(f"Processed PR from {username}")
        processed_users.append(username)

    except Exception as e:
        print(f"Could not process PR from {username}: {e}")

with open("user_map.json", "w") as f:
    json.dump(user_map, f, indent=2)

diff_result = subprocess.run(
    ["git", "diff", "--quiet", "user_map.json"], capture_output=True
)

if diff_result.returncode != 0:
    subprocess.run(["git", "add", "user_map.json"], check=True)
    subprocess.run(["git", "commit", "-m", "Update user_map.json"], check=True)
else:
    print("No changes to user_map.json")

subprocess.run(["git", "push", "origin", "tracker"], check=True)
