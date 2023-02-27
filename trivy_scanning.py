from jira import JIRA
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint
import os
import json

load_dotenv(dotenv_path=Path("../.env"))

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_SERVER = os.getenv("JIRA_SERVER")

connection = JIRA(basic_auth=(JIRA_EMAIL, JIRA_TOKEN), server=JIRA_SERVER)


def __parse_findings():
    findings = []
    with open("./output/trivy_scan_results.json", "r") as f:
        results = json.loads(f.read())

    resource_type = "container-image"
    resource_id = results["ArtifactName"]
    resource_os_name = results["Metadata"]["OS"]["Family"]
    resource_os_version = results["Metadata"]["OS"]["Name"]

    for c in results["Results"]:
        if "Vulnerabilities" in c:
            for f in c["Vulnerabilities"]:
                finding = dict()

                if f["Severity"] in ["UNKNOWN"]:
                    continue

                finding["title"] = f.get("Title")
                if not finding["title"]:
                    finding[
                        "title"
                    ] = f"Package '{f['PkgName']}' with vulnerability {f['VulnerabilityID']} found in {resource_id}"
                finding["description"] = f.get("Description")
                if not finding["description"]:
                    finding[
                        "description"
                    ] = f"Package '{f['PkgName']}' with version {f['PkgID']} is found vulnerable to {f['VulnerabilityID']}"
                if f.get("References"):
                    finding["description"] += (
                        "\n\n" + "References:-\n\n" + "\n".join(f["References"])
                    )
                finding["severity"] = f["Severity"]
                finding["unique_ids"] = [
                    f["VulnerabilityID"],
                    resource_id,
                ]
                if f.get("PkgID"):
                    finding["unique_ids"].append(f["PkgID"])
                finding["labels"] = [
                    f"resource:type|{resource_type}",
                    f"resource:id|{f['PkgID'] if f.get('PkgID') else 'Unknown'}",
                    f"resource:name|{resource_id.split(':')[0]}",
                    f"resource:meta:package_name|{f['PkgName']}",
                    f"resource:meta:os_name|{resource_os_name}",
                    f"resource:meta:os_version|{resource_os_version}",
                    f"resource:meta:image_tag|{resource_id.replace(resource_id.split(':')[0]+':', '')}",
                    f"scanner|trivy",
                    f"rule|container_vulnerabilities",
                    f"vulnerability_id|{f['VulnerabilityID']}",
                ]
                findings.append(finding)
    return findings


def __raise_issues(findings):
    issues = []
    for finding in findings:
        if finding["severity"] in ["HIGH", "CRITICAL"]:
            issues.append(
                {
                    "issuetype": {"name": "Task"},
                    "summary": finding["title"],
                    "description": finding["description"],
                    "labels": finding["labels"],
                    "project": {"key": "CCP"},
                }
            )
    if len(issues) == 0:
        print("No issues found")
    else:
        connection.create_issues(field_list=issues)

def main():
    findings = __parse_findings()
    __raise_issues(findings)

main()
