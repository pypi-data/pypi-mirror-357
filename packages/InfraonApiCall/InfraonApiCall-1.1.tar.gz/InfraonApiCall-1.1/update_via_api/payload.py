import requests

url = "https://cenindenv01.api.infraon.app/ux/common/workflow/config/"

params = {
    "items_per_page": "100",
    "page": "1"
}

headers = {
    "Authorization": "infraonDNS A5XkghbUJ93zMhqb3FksRjGUMmAzh/dg7hbDXBijiLCq8qiwE8rqFy0/%2B4aTHTD/PIrVnHIHWlGGI9HY7z4vSJeaD3vibd9gnAysWApveS0iMigWL3oAaBKuyYM7BiNTaUAZcuLJLenKtL9xnWDgehcPnGJSQikXCkmzge2WNuAoUU79rIvhW40d5StDsk4vaSdvdEy7WhFvo1ZESi04k52tY7O3W3iua6Gge31Vux1hw6wtBHiGv59ufuy8XwLMT77AZG5JlmKlSFC9U6jcqrmXP37TS513YBj4QJTCV/gXZq9O5satQYZsm1ZAI/Y5PmZwhy5Nb0gJ4JNJB/UTyIkwHTsnEfdgPd9dvQqUTzJADX3wLlHVIKIYFDKgSJxVcuACzMyqYZxypoxouL0n/qD9PHVTUtCuaF4FivJPBpEdonAieJ7s9aTerRzhnZf0weZcC4kXqYJUKAAuphLbbss0lPj2q5XrG0WiL8bVtu5qaMGrAiChk33v3W0tQsX6NQrlKsxxZEGCLvkxN7eT6ZpkbcuOVQitY/5LLs8ijWjKkhgOzB56ZgfMvvw/aQ2%2B1O4esLu30SQLPZDj%2BVzqI8Kn2YPTkMJGQtEpV1GvMX/%2B2miIo0OHSpRpOjxSLDam0UI1J3TVCeZ5Ca6GZPP3B%2Bb1KcKWruRNwMVhJ/ob/9Yjd2zbBOsnAymbyKT4PJC1"  # Replace with actual token
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    workflows = data.get("results", [])   # Adjust this based on actual response structure

    titles = [wf.get("title") for wf in workflows if "title" in wf]

    print("Workflow Titles:")
    for title in titles:
        print(title)
else:
    print(f"Failed to fetch workflows. Status code: {response.status_code}")
    print(response.text)
