import subprocess
import re
import sys

command1 = ["trivy","fs","--scanners","vuln,misconfig,secret,license","--ignorefile","","."]
command2 = ["trivy","image","--input","/tmp/myapp.tar","--scanners", "vuln,misconfig,secret"]
command3 = ["trivy", "fs", "--scanners", "vuln,misconfig,secret,license","--ignorefile", ".trivyignore", "."]

result = subprocess.run(command1, capture_output=True, text=True)

print("--- SCANNING OSS VULNERABLES BEFORE EXCEPTION---")
print(result.stdout)

# print("--- STDERR ---")
# print(result.stderr)

# print("--- RETURN CODE ---")
# print(result.returncode)

print("==============================================")

print("--- SCANNING OSS VULNERABLES AFTER EXCEPTION ---")

print("=============================================")

result = subprocess.run(command3, capture_output=True, text=True)
print(result.stdout)

m1 = 0
m2 = 0

for line in result.stdout.splitlines():
    if "Total:" in line:
        m1 = re.search(r"Total:\s+(\d+)", line)
        print("Total number of Vulnerables:",m1.group(1))
        m1 = int(m1.group(1))

    elif "Failures:" in line:
        m2 = re.search(r"Failures:\s+(\d+)",line)
        print("Total number of Failures:",m2.group(1))
        m2 = int(m2.group(1))

count = m1 + m2

if count > 0:
   print("Pipeline is Failed because of Vulnerables found", count)
   sys.exit(1)
elif count == 0:
   print("Pipeline has Zero Vulnerables & OSS Scan Stage is passed")
else:
   print("THere is some issue please check the script")
   sys.exit(1)