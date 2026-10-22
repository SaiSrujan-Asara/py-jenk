
import os
import subprocess
import sys
from urllib.parse import quote


def main():
    # 1. Read Jenkins environment variables
    branch_name = os.getenv("BRANCH_NAME") or os.getenv("GIT_BRANCH", "")
    current_build = os.getenv("BUILD_NUMBER", "")
    user = os.getenv("GHCR_USER", "")
    token = os.getenv("GHCR_PASS", "")

    # 2. Normalize branch name
    if branch_name.startswith("origin/"):
        branch_name = branch_name[len("origin/"):]

    # 3. Validate release branch
    if not branch_name.startswith("release/"):
        print(f"ERROR: Not a release branch: {branch_name}")
        sys.exit(1)

    # 4. Validate build number
    if not current_build.isdigit():
        print("ERROR: BUILD_NUMBER is missing or invalid.")
        sys.exit(1)

    # 5. Validate credentials
    if not user or not token:
        print("ERROR: GitHub credentials are missing.")
        sys.exit(1)

    # 6. Generate tag
    clean_version = branch_name[len("release/"):]
    tag_candidate = f"{clean_version}{current_build}"

    # Validate Git tag format
    check_tag = subprocess.run(
        ["git", "check-ref-format", f"refs/tags/{tag_candidate}"],
        capture_output=True,
        text=True
    )

    if check_tag.returncode != 0:
        print(f"ERROR: Invalid Git tag: {tag_candidate}")
        sys.exit(1)

    print(f"Checking tag availability: {tag_candidate}")

    # 7. Get origin URL
    origin_url = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    if not origin_url.startswith("https://"):
        print("ERROR: Origin must be an HTTPS URL.")
        sys.exit(1)

    # 8. Build authenticated URL
    # URL-encode credentials to handle special characters.
    safe_user = quote(user, safe="")
    safe_token = quote(token, safe="")

    auth_url = origin_url.replace(
        "https://",
        f"https://{safe_user}:{safe_token}@",
        1
    )

    # 9. Check remote tag availability
    result = subprocess.run(
        [
            "git", "ls-remote", "--tags",
            auth_url,
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
        print(f"ERROR: Tag '{tag_candidate}' already exists!")
        sys.exit(1)

    print(f"Tag '{tag_candidate}' is available. Creating tag...")

    try:
        # 10. Create local tag
        subprocess.run(
            ["git", "tag", tag_candidate],
            check=True
        )

        # 11. Push using authenticated URL (NOT origin)
        subprocess.run(
            [
                "git", "push",
                auth_url,
                f"refs/tags/{tag_candidate}"
            ],
            check=True
        )

        print(f"SUCCESS: Tag '{tag_candidate}' created and pushed.")

        # 12. Save tag for Jenkins / Docker image
        with open("tag.txt", "w", encoding="utf-8") as tag_file:
            tag_file.write(tag_candidate)

    except subprocess.CalledProcessError as error:
        print(f"ERROR: Git command failed with exit code {error.returncode}.")
        if error.stderr:
            print(error.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
