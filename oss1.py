import subprocess
import json
import sys

SCANNERS = "vuln,misconfig,secret,license"


def run_trivy(report_file, use_ignore=False):
    command = [
        "trivy", "fs",
        "--scanners", SCANNERS,
        "--format", "json",
        "--output", report_file,
    ]

    if use_ignore:
        command.extend(["--ignorefile", ".trivyignore"])

    command.append(".")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        print(f"Trivy scan failed: {report_file}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(2)

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Unable to read {report_file}: {exc}", file=sys.stderr)
        sys.exit(2)


def summarize(report, title):
    categories = {
        "Vulnerabilities": "Vulnerabilities",
        "Misconfigurations": "Misconfigurations",
        "Secrets": "Secrets",
        "Licenses": "Licenses",
    }

    totals = {name: 0 for name in categories}

    print(f"\n{'=' * 65}")
    print(title)
    print("=" * 65)

    results = report.get("Results") or []

    if not results:
        print("No scan results returned.")

    for item in results:
        target = item.get("Target", "Unknown target")
        target_totals = {}

        for field, label in categories.items():
            findings = item.get(field) or []
            count = len(findings)
            totals[label] += count
            target_totals[label] = count

        print(
            f"{target}: "
            f"Vulnerabilities={target_totals['Vulnerabilities']}, "
            f"Misconfigurations={target_totals['Misconfigurations']}, "
            f"Secrets={target_totals['Secrets']}, "
            f"Licenses={target_totals['Licenses']}"
        )

    print("-" * 65)
    for name, count in totals.items():
        print(f"{name}: {count}")

    total = sum(totals.values())
    print(f"Total findings: {total}")

    return total


# 1. Scan before exceptions
before_report = run_trivy("report_before.json")
before_count = summarize(
    before_report,
    "TRIVY SCAN - BEFORE EXCEPTIONS"
)

# 2. Scan after exceptions
after_report = run_trivy(
    "report_after.json",
    use_ignore=True
)
after_count = summarize(
    after_report,
    "TRIVY SCAN - AFTER EXCEPTIONS"
)

# 3. Pipeline decision based on remaining findings
print("\n" + "=" * 65)
print(f"Findings before exceptions: {before_count}")
print(f"Findings after exceptions:  {after_count}")
print("=" * 65)

if after_count > 0:
    print("PIPELINE FAILED: Security findings remain.")
    sys.exit(1)
else:
    print("PIPELINE PASSED: No findings remain.")
    sys.exit(0)