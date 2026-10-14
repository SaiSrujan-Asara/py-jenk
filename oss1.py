import subprocess
import re
import sys

# FIX: Removed '--ignorefile ""' from command1 to avoid CLI parser crashes
command1 = [
    "trivy", "fs", 
    "--scanners", "vuln,misconfig,secret,license",
    "--output", "report_before.txt",
    "."
]

command2 = ["trivy", "image", "--input", "/tmp/myapp.tar", "--scanners", "vuln,misconfig,secret"]

# FIX: Added '--output' to write directly to a text file
command3 = [
    "trivy", "fs", 
    "--scanners", "vuln,misconfig,secret,license",
    "--ignorefile", ".trivyignore", 
    "--output", "report_after.txt",
    "."
]

# --- 1. RUN FIRST SCAN ---
print("--- SCANNING OSS VULNERABILITIES BEFORE EXCEPTION ---")
subprocess.run(command1, capture_output=True, text=True)

try:
    with open("report_before.txt", "r") as f:
        content = f.read()
        # Clean up the box-drawing characters for the Jenkins visual console log
        clean_content = content.replace("", "").replace("│", "|").replace("─", "-").replace("┌", "+").replace("┐", "+").replace("└", "+").replace("┘", "+")
        print(clean_content)
except FileNotFoundError:
    print("Error: report_before.txt was not created.", file=sys.stderr)

print("==============================================")
print("--- SCANNING OSS VULNERABILITIES AFTER EXCEPTION ---")
print("=============================================")

# --- 2. RUN SECOND SCAN ---
subprocess.run(command3, capture_output=True, text=True)

report_after_content = ""
try:
    with open("report_after.txt", "r") as f:
        report_after_content = f.read()
        # Clean up the box-drawing characters for the Jenkins visual console log
        clean_content = report_after_content.replace("", "").replace("│", "|").replace("─", "-").replace("┌", "+").replace("┐", "+").replace("└", "+").replace("┘", "+")
        print(clean_content)
except FileNotFoundError:
    print("Error: report_after.txt was not created.", file=sys.stderr)
    sys.exit(1)

# --- 3. PARSE TOTALS SAFELY FROM THE FILE CONTENT ---
m1 = 0
m2 = 0

for line in report_after_content.splitlines():
    if "Total:" in line:
        match = re.search(r"Total:\s+(\d+)", line)
        if match:
            val = int(match.group(1))
            print("Found Vulnerabilities group:", val)
            m1 += val  # Accumulate instead of overwriting

    elif "Failures:" in line:
        match = re.search(r"Failures:\s+(\d+)", line)
        if match:
            val = int(match.group(1))
            print("Found Failures group:", val)
            m2 += val

count = m1 + m2
print("=============================================")
print(f"Final Aggregated Count: {count}")

# --- 4. PIPELINE PASS/FAIL DECISION ---
if count > 0:
   print("Pipeline is Failed because of Vulnerables found:", count)
   sys.exit(1)
elif count == 0:
   print("Pipeline has Zero Vulnerables & OSS Scan Stage is passed")
   sys.exit(0)
else:
   print("There is some issue please check the script")
   sys.exit(1)
