import requests
import json

def get_auth_token(sub_domain, username, password):
    url = f"https://{sub_domain}.api.infraon.app/ux/api-token-auth/"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.text)

    try:
        response_data = response.json()
        auth_token = response_data.get("token")
        if auth_token:
            print(f"Auth Token: {auth_token}")
            return auth_token
        else:
            print("Auth token not found in the response.")
            return None
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
        return None

def list_operations():
    operations = {
        "1": "bulk_department_upload",
        "2": "workflow_edit",
        "3": "report_download"
    }
    print("Available operations:")
    for key, op in operations.items():
        print(f"{key}: {op}")
    return operations

def workflow_edit(sub_domain, auth_token):
    url = f"https://{sub_domain}.api.infraon.app/ux/common/workflow/config/"
    params = {
        "items_per_page": "100",
        "page": "1"
    }
    headers = {
        "Authorization": auth_token  # Use Bearer token
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        workflows = data.get("results", [])
        titles = [wf.get("title") for wf in workflows if "title" in wf]
        print("Workflow Titles:")
        for title in titles:
            print(f"- {title}")
    else:
        print(f"Failed to fetch workflows. Status code: {response.status_code}")
        print(response.text)

def main():
    sub_domain = input("Enter your Infraon sub domain: ")
    username = input("Enter your email ID: ")
    password = input("Enter your password: ")

    # Get the token
    auth_token = get_auth_token(sub_domain, username, password)
    if not auth_token:
        return

    # Ask if user wants to list operations
    if input("Enter 'yes' to see the list of operations: ").strip().lower() == "yes":
        list_operations()

    option = input("Enter the option number to execute the operation: ").strip()
    if option == "2":
        workflow_edit(sub_domain, auth_token)
    else:
        print("Selected option not implemented yet.")

if __name__ == "__main__":
    main()
