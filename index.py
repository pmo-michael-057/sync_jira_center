#!/usr/bin/env python3

import requests
import json
# import os

JIRA_URL_CENTER = "https://nevel-tech.atlassian.net"

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
# ISSUELIST_INCOME = "ZCENTER-412, ZCENTER-413"
ISSUELIST_INCOME = ["ZCENTER-537"]
# PROJECT_OUTPUT = ["Z01SV02", "Z03LD02", "Z04MAY02", "Z06DB", "Z07KN02", "Z08BC02", "Z17VB", "Z21VUA"]
# PROJECT_OUTPUT = ["Z01SV02"]
PROJECT_OUTPUT = ["S2TEST011", "S2TEST02"]
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

def get_stories_from_center():
    url = f"{JIRA_URL_CENTER}/rest/api/3/search"

    # Get data from Ticket ID
    issueKeysStr = ",".join(ISSUELIST_INCOME)
    jqlQuery = f"project = ZCENTER AND issueKey IN ({issueKeysStr})"
    query = {
        "jql": jqlQuery,
        "maxResults": 100
    }

    response = requests.get(url, params=query, headers=HEADERS, auth=AUTH)
    if response.status_code == 200:
        # Prepare the US data
        issuesData = response.json().get("issues", [])
        for issue in issuesData:
            prepareUSPayload = []
            userStoryNewList = []
            for project in PROJECT_OUTPUT:
                prepareUSPayload.append({
                    "fields": {
                        "project": {"key": project},
                        "summary": f"{issue["fields"]["summary"]}",
                        "description": issue["fields"]["description"],
                        "issuetype": {"name": "Story"}
                    }
                })

            payload = {"issueUpdates": prepareUSPayload} 

            userStoryResponse = create_by_bulk(payload)
            if userStoryResponse.status_code == 201:
                print(f"Successfully created")
                outputData = userStoryResponse.json().get("issues", [])

                # Save the new UserStory Key 
                for us in outputData:
                    userStoryNewList.append({
                        "id": us['key']
                    })
            else:
                print(f"{userStoryResponse.text}")

            # Prepare the SubTask List by the new UserStory Key
            subtask_list = [
                {"summary": "[DES] Design UI/UX"},
                {"summary": "[DEV] Implement task and fix bug"},
                {"summary": "[QC] Execute test cases"},
                {"summary": "[QC] Verify bugs"}
            ]
            prepareSubTaskPayload = []
            for project in PROJECT_OUTPUT:
                
                for userStoryNew in userStoryNewList:
                    for subtask in subtask_list:
                        prepareSubTaskPayload.append({
                            "fields": {
                                "project": {"key": project},
                                "summary": subtask['summary'],
                                "issuetype": {"name": "Sub-task"},
                                "parent": {"key": f"{userStoryNew["id"]}"}
                            }
                        })
            subTaskResponse = create_by_bulk({"issueUpdates": prepareSubTaskPayload})
            if userStoryResponse.status_code == 201:
                print(f"Successfully - SubTask created")
            else:
                print(f"{subTaskResponse.text}")

            # Link new US with Center US
            for centerUSKey in ISSUELIST_INCOME:
                for userStory in userStoryNewList:
                    link_issues(centerUSKey, userStory["id"])
    else:
        print(f"Error fetching stories")

    print(f"DONE")


if __name__ == "__main__":
    print(f"START")
    get_stories_from_center()



