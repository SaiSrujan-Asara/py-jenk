import subprocess
import sys
import os

# Configure UTF-8 for Python and child processes
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "C.UTF-8"
os.environ["LC_ALL"] = "C.UTF-8"

SCANNERS = "vuln,misconfig,secret,license"


def run_trivy(command, title):
    print("\n" + title, flush=True)
    print("=" * 70, flush=True)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=os.environ.copy()
        )

        # Print output without modifying Trivy's formatting.
        print(result.stdout, end="", flush=True)

        if result.returncode != 0:
            print(
                f"\nTrivy command failed with exit code "
                f"{result.returncode}",
                flush=True
            )
            return False

        return True

    except FileNotFoundError:
        print(
            "ERROR: Trivy executable not found in PATH.",
            file=sys.stderr,
            flush=True
        )
        sys.exit(2)


# 1. Scan before exceptions
command1 = [
    "trivy", "fs",
    "--scanners", SCANNERS,
    "."
]

if not run_trivy(
    command1,
    "SCANNING OSS VULNERABILITIES BEFORE EXCEPTION"
):
    sys.exit(2)


# 2. Scan after exceptions
command3 = [
    "trivy", "fs",
    "--scanners", SCANNERS,
    "--ignorefile", ".trivyignore",
    "--exit-code", "1",
    "."
]

if not run_trivy(
    command3,
    "SCANNING OSS VULNERABILITIES AFTER EXCEPTION"
):
    sys.exit(1)


print("\nOSS scan stage passed.", flush=True)
sys.exit(0)