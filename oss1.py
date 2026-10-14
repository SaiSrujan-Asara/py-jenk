import subprocess
import sys
import os

# Ensure Python uses UTF-8 where possible
os.environ["PYTHONIOENCODING"] = "utf-8"

SCANNERS = "vuln,misconfig,secret,license"


def run_trivy(command, title):
    print("\n" + "=" * 70, flush=True)
    print(title, flush=True)
    print("=" * 70, flush=True)

    try:
        # Send Trivy output directly to Jenkins console.
        # Do not capture, rewrite, or clean up its output.
        result = subprocess.run(
            command,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )

        if result.returncode != 0:
            print(
                f"\nTrivy scan failed with exit code: "
                f"{result.returncode}",
                flush=True
            )
            sys.exit(result.returncode)

    except FileNotFoundError:
        print(
            "ERROR: Trivy executable was not found. "
            "Ensure Trivy is installed and available in PATH.",
            file=sys.stderr,
            flush=True
        )
        sys.exit(2)


# --------------------------------------------------
# 1. SCAN BEFORE EXCEPTIONS
# --------------------------------------------------

command1 = [
    "trivy",
    "fs",
    "--scanners", SCANNERS,
    "."
]

run_trivy(
    command1,
    "SCANNING OSS VULNERABILITIES BEFORE EXCEPTION"
)


# --------------------------------------------------
# 2. SCAN AFTER EXCEPTIONS
# --------------------------------------------------

command3 = [
    "trivy",
    "fs",
    "--scanners", SCANNERS,
    "--ignorefile", ".trivyignore",
    "."
]

run_trivy(
    command3,
    "SCANNING OSS VULNERABILITIES AFTER EXCEPTION"
)


# --------------------------------------------------
# 3. PIPELINE RESULT
# --------------------------------------------------
# Trivy's default output is preserved above.
# Use --exit-code 1 to make the AFTER scan fail
# when it finds vulnerabilities.
#
# If you want the pipeline to fail for all finding
# types, including misconfigurations, secrets and
# licenses, use the explicit counting approach
# described below instead.

print("\n" + "=" * 70, flush=True)
print("TRIVY SCANS COMPLETED SUCCESSFULLY", flush=True)
print("=" * 70, flush=True)

sys.exit(0)