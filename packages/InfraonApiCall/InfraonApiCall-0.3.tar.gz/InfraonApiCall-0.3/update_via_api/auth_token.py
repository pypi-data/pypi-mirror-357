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
    operations = ["bulk_department_upload", "workflow_edit", "report_download"]
    print("Available operations:")
    for op in operations:
        print(f"- {op}")
    return operations

def main():
    sub_domain = input("Enter your Infraon sub domain: ")
    username = input("Enter your email ID: ")
    password = input("Enter your password: ")

    # Get the token
    get_auth_token(sub_domain, username, password)

    # Ask if user wants to list operations
    if input("Enter yes to list operations: ").strip().lower() == "yes":
        list_operations()

if __name__ == "__main__":
    main()
