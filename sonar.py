import requests
import os
import sys

project_url = os.environ.get('SONARQUBE_URL')
tk = os.environ.get('TOKEN')
key = os.environ.get('PROJECT_KEY')

# response = requests.get(project_url)
# print(response.status_code)

response1 = requests.get(f"{project_url}/api/system/status", auth=(tk, ""), params={"component": key})
response2 = requests.get(f"{project_url}/api/components/show", auth=(tk, ""), params={"component": key, "metricKeys": "bugs,vulnerabilities,code_smells"})
response3 = requests.get(f"{project_url}/api/measures/component", auth=(tk, ""), params={"component": key, "metricKeys": "bugs,vulnerabilities,code_smells,security_rating,reliability_rating,sqale_rating,coverage,duplicated_lines_density"})
response4 = requests.get(f"{project_url}/api/qualitygates/project_status", auth=(tk, ""), params={"projectKey": key})


# print(response1.status_code)
# print(response3.json())
# print(response4.json())

if response1.status_code == 200:
    data = response3.json()
    metrics = data.get("component", {}).get("measures", [])

    print("--------------------DISPLAY ALL SONAR METRICS ------------------------------")

    for i in metrics:
        metric = i.get("metric")
        value = i.get("value", "N/A")
        print(f"{metric}:- {value}")

    print("-----------------CHECKING FINAL SONARQUBE QUALITY GATE STATUS------------------")

    data = response4.json()
    metrics = data.get("projectStatus", {})
    project_status = metrics.get("status")
    print(f"SonarQube_Quality_Gate_status:- {project_status}")

    if project_status == "OK":
        print("SOnarQube Stage is Passed Successfully")
    else:
        print("SonarQube Stage is Failed Because of Not Acheving Quality Gate Standard")
        sys.exit(1)
else:
    print("Not able to Access SonarQube API")
    sys.exit(1)