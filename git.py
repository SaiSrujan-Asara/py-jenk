import subprocess

# Input variables (Jenkins environment variables)
branch_name = "release/v1.0.0"
current_build = 5  # Must be an integer so we can mathematically increase it

# 1. Clean the branch name to get just "26.1.1"
clean_version = branch_name.replace("release/", "")

while True:
    # 2. Generate the tag candidate (e.g., "26.1.15", "26.1.16", etc.)
    tag_candidate = f"{clean_version}{current_build}"
    print(f"Checking tag availability for: {tag_candidate}...")

    # 3. Check if this tag candidate already exists on GitHub
    check_remote = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", tag_candidate],
        capture_output=True,
        text=True
    )

    # 4. If the output is empty, the tag does NOT exist. It's safe to use!
    if not check_remote.stdout.strip():
        print(f"✨ Success! '{tag_candidate}' is available.")
        break
    
    # 5. If it exists, warn the user, increment the build number, and try again
    print(f"⚠️ Tag '{tag_candidate}' already exists on GitHub.")
    current_build += 1

# --- At this point, tag_candidate holds the next available version ---
print(f"🚀 Final tag selected for pipeline: {tag_candidate}")

# Optional: Run Git commands to create and push the safe tag
# subprocess.run(["git", "tag", tag_candidate])
# subprocess.run(["git", "push", "origin", tag_candidate])
