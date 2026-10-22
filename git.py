
import os
import subprocess
import sys

# Get values from Jenkins
branch_name = os.getenv("BRANCH_NAME") or os.getenv("GIT_BRANCH", "")
current_build = os.getenv("BUILD_NUMBER", "")

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

# Check whether tag exists remotely
result = subprocess.run(
    [
        "git", "ls-remote", "--tags", "origin",
        f"refs/tags/{tag_candidate}"
    ],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("ERROR: Unable to check remote tags.")
    print(result.stderr)
    sys.exit(1)

if result.stdout.strip():
    print(f"ERROR: Tag '{tag_candidate}' is already in use!")
    sys.exit(1)

print(f"Tag '{tag_candidate}' is available. Creating tag...")

# Create and push tag
subprocess.run(["git", "tag", tag_candidate], check=True)
subprocess.run(["git", "push", "origin", tag_candidate], check=True)

print(f"SUCCESS: Tag '{tag_candidate}' created and pushed.")
