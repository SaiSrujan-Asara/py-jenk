import os
import subprocess
import sys

# Get values from Jenkins
branch_name = os.getenv("BRANCH_NAME") or os.getenv("GIT_BRANCH", "")
current_build = os.getenv("BUILD_NUMBER", "")

# GIT_BRANCH may look like "origin/release/26.10.1"
if branch_name.startswith("origin/"):
    branch_name = branch_name.replace("origin/", "", 1)

# Validate branch
if not branch_name.startswith("release/"):
    print(f"ERROR: Not a release branch: {branch_name}")
    sys.exit(1)

# Validate build number
if not current_build.isdigit():
    print("ERROR: BUILD_NUMBER is missing or invalid.")
    sys.exit(1)

# Generate tag
clean_version = branch_name.replace("release/", "", 1)
tag_candidate = f"{clean_version}{current_build}"

print(f"Checking tag availability: {tag_candidate}")

# ---- Build authenticated remote URL from Jenkins credentials ----
user = os.getenv("GHCR_USER")
token = os.getenv("GHCR_PASS")

origin_url = subprocess.run(
    ["git", "remote", "get-url", "origin"],
    capture_output=True, text=True, check=True
).stdout.strip()

if not origin_url.startswith("https://"):
    print("ERROR: origin is not an https URL.")
    sys.exit(1)

auth_url = origin_url.replace("https://", f"https://{user}:{token}@", 1)

# Check whether tag exists remotely
result = subprocess.run(
    ["git", "ls-remote", "--tags", auth_url, f"refs/tags/{tag_candidate}"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("ERROR: Unable to check remote tags.")
    sys.exit(1)

if result.stdout.strip():
    print(f"ERROR: Tag '{tag_candidate}' is already in use!")
    sys.exit(1)

print(f"Tag '{tag_candidate}' is available. Creating tag...")

# Create and push tag (using authenticated URL)
subprocess.run(["git", "tag", tag_candidate], check=True)
subprocess.run(["git", "push", auth_url, tag_candidate], check=True)

print(f"SUCCESS: Tag '{tag_candidate}' created and pushed.")

# Save tag for Jenkins / Docker image
with open("tag.txt", "w") as f:
    f.write(tag_candidate)