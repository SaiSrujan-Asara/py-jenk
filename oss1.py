import os
import sys
import subprocess

SCANNERS = "vuln,misconfig,secret,license"


def run_trivy(title, command):
    print("\n" + "=" * 70, flush=True)
    print(title, flush=True)
    print("=" * 70, flush=True)

    try:
        # Inherit the Jenkins process's output streams directly.
        # No capture_output, decoding, or character replacement.
        result = subprocess.run(
            command,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=os.environ.copy()
        )

        if result.returncode != 0:
            print(
                f"Trivy failed with exit code {result.returncode}",
                flush=True
            )
            return False

        return True

    except FileNotFoundError:
        print("ERROR: Trivy executable not found in PATH.", flush=True)
        return False


def main():
    # 1. Scan before exceptions
    before_command = [
        "trivy", "fs",
        "--scanners", SCANNERS,
        "."
    ]

    if not run_trivy(
        "SCANNING OSS VULNERABILITIES BEFORE EXCEPTION",
        before_command
    ):
        return 2

    # 2. Scan after exceptions
    after_command = [
        "trivy", "fs",
        "--scanners", SCANNERS,
        "--ignorefile", ".trivyignore",
        "."
    ]

    if not run_trivy(
        "SCANNING OSS VULNERABILITIES AFTER EXCEPTION",
        after_command
    ):
        return 2

    print("\nBoth Trivy scans completed.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())