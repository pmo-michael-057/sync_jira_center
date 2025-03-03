#!/usr/bin/env python3

import requests
import json
# import os

JIRA_URL_CENTER = "https://nevel-tech.atlassian.net"
ZCENTER_KEY = "ZCENTER"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ================
# Start dynamic data
# Config the jira account
# EMAIL = os.environ['EMAIL']
# API_TOKEN = os.environ['API_TOKEN']
EMAIL = "michael@nevel.tech"
API_TOKEN = "ATATT3xFfGF0LLojUIgPld4d-_sa-soqiRca3rWTt1_JODTbF2z7jFK6ysSMT2a-CS9f8pBXODohI9IMxgIIY3x8kuA7MZIYvatv_ggCUr8UQU2EJWQffUkfAbSy0iW5y2VS744hR8Jqs0yrRrKnNQHVFgaXd3Za_xRSA1iCYcIdfDz2m7hdtOY=098ABDFA"


AUTH = (EMAIL, API_TOKEN)

# Edit: Tickets and Projects data output
ISSUELIST_INCOME = [
    "ZCENTER-542",
]
# Max 11 projects
# PROJECT_OUTPUT = [
#     "Z01SV02",
#     "Z03LD02",
#     "Z04MAY02",
#     "Z06DB",
#     "Z07KN02",
#     "Z08BC02",
#     "Z17VB",
# ]

PROJECT_OUTPUT = [
    "Z21VUA",
    "Z24BIG",
    "Z27XI",
    "Z22GREEN",
    "Z28BIG",
    "Z29JOB",
    "Z31QI",
    "Z33BU",
    "Z34ZUN",
    "Z35DOM",
    "Z37GUN",
]

# End dynamic data 
# ================

def create_by_bulk(payload):
    bulkAPIEndpoint = f"{JIRA_URL_CENTER}/rest/api/3/issue/bulk"
    userStoryResponse = requests.post(bulkAPIEndpoint, headers=HEADERS, auth=AUTH, json=payload)

    return userStoryResponse

def link_issues(centerUSKey, targetUSKey):
    url = f"{JIRA_URL_CENTER}/rest/api/3/issueLink"
    
    payload = {
        "type": {"name": "Relates"},
        "inwardIssue": {"key": centerUSKey},
        "outwardIssue": {"key": targetUSKey}
    }

    response = requests.post(url, headers=HEADERS, auth=AUTH, json=payload)

    if response.status_code == 201:
        print(f"✅ Linked {centerUSKey} → {targetUSKey}")
    else:
        print(f"❌ Failed to link {centerUSKey} → {targetUSKey}: {response.text}")

def get_epic_by_summary(summary="On-shore Requirements", project_key=""):
    if project_key == "":
        return None

    jql_query = f'project = "{project_key}" AND issuetype = "Epic" AND summary ~ "{summary}"'
    url = f"{JIRA_URL_CENTER}/rest/api/3/search?jql={jql_query}&maxResults=1"

    response = requests.get(url, headers=HEADERS, auth=AUTH)

    if response.status_code == 200:
        issues = response.json().get("issues", [])
        if issues:
            return issues[0]["key"]  # Epic Key
        else:
            return None
    else:
        return None

def sync_jira_center():
    url = f"{JIRA_URL_CENTER}/rest/api/3/search"

    # Get data from Ticket ID
    issueKeysStr = ",".join(ISSUELIST_INCOME)
    jqlQuery = f"project = {ZCENTER_KEY} AND issueKey IN ({issueKeysStr})"
    query = {
        "jql": jqlQuery,
        "maxResults": 100
    }

    response = requests.get(url, params=query, headers=HEADERS, auth=AUTH)
    if response.status_code == 200:
        # Prepare the US data
        issuesData = response.json().get("issues", [])
        for issue in issuesData:
            newUSPayload = []
            userStoryNewList = []
            for project in PROJECT_OUTPUT:
                prepareUSPayload = {
                    "fields": {
                        "project": {"key": project},
                        "summary": f"[SYNC] {issue["fields"]["summary"]}",
                        "description": issue["fields"]["description"],
                        "issuetype": {"name": "Story"}
                    }
                }

                # Add Epic Key to UserStory or the default value is blank.
                requirementEpicKey = get_epic_by_summary("On-shore Requirements", project)
                if requirementEpicKey:
                    prepareUSPayload["fields"]["parent"] = {"key": requirementEpicKey}
                
                newUSPayload.append(prepareUSPayload)

            payload = {"issueUpdates": newUSPayload} 

            userStoryResponse = create_by_bulk(payload)
            if userStoryResponse.status_code == 201:
                print(f"✅ Successfully created")
                outputData = userStoryResponse.json().get("issues", [])

                # Save the new UserStory Key 
                print(f"✅  New US link")
                for us in outputData:
                    print(f"https://nevel-tech.atlassian.net/browse/{us['key']}")
                    userStoryNewList.append({
                        "key": us['key']
                    })
            else:
                print(f"{userStoryResponse.text}")

            # Prepare the SubTask List by the new UserStory Key
            subtask_list = [
                {"summary": "[DES] Design UXUI"},
                {"summary": "[DEV] Implement task and fix bug"},
                {"summary": "[QC] Execute test cases"},
                {"summary": "[QC] Verify bugs"}
            ]
            # prepareSubTaskPayload = []
            for project in PROJECT_OUTPUT:
                prepareSubTaskPayload = []
                for userStoryNew in userStoryNewList:
                    for subtask in subtask_list:
                        prepareSubTaskPayload.append({
                            "fields": {
                                "project": {"key": project},
                                "summary": subtask['summary'],
                                "issuetype": {"name": "Sub-task"},
                                "parent": {"key": f"{userStoryNew["key"]}"}
                            }
                        })
                subTaskResponse = create_by_bulk({"issueUpdates": prepareSubTaskPayload})
                if userStoryResponse.status_code == 201:
                    print(f"✅ Successfully - SubTask created")
                else:
                    print(f"❌ Error: {subTaskResponse.text}")

            # Link new US with Center US
            for centerUSKey in ISSUELIST_INCOME:
                for userStory in userStoryNewList:
                    link_issues(centerUSKey, userStory["key"])
    else:
        print(f"❌ Error fetching stories")

    print(f"✅ DONE")


if __name__ == "__main__":
    print(f"START")
    sync_jira_center()



