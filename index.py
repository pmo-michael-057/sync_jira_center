#!/usr/bin/env python3

import requests
import json

JIRA_URL_CENTER = "https://nevel-tech.atlassian.net"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ================
# Start dynamic data
# Config the jira account
EMAIL = ""
API_TOKEN = ""

AUTH = (EMAIL, API_TOKEN)

# Edit: Tickets and Projects data output
# ISSUELIST_INCOME = "ZCENTER-412, ZCENTER-413"
ISSUELIST_INCOME = "ZCENTER-507, ZCENTER-522"
PROJECT_OUTPUT = ["S2TEST011", "Z01SV"]
# End dynamic data
# ================

def create_by_bulk(payload):
    bulkAPIEndpoint = f"{JIRA_URL_CENTER}/rest/api/3/issue/bulk"
    userStoryResponse = requests.post(bulkAPIEndpoint, headers=HEADERS, auth=AUTH, json=payload)

    return userStoryResponse

def get_stories_from_center():
    url = f"{JIRA_URL_CENTER}/rest/api/3/search"

    # Get data from Ticket ID
    jqlQuery = f"project = ZCENTER AND issueKey IN ({ISSUELIST_INCOME})"
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

    else:
        print(f"Error fetching stories")

    print(f"DONE")


if __name__ == "__main__":
    print(f"START")
    get_stories_from_center()



