# update_via_api/main.py

import requests

def print_ip():
    response = requests.get('https://httpbin.org/ip')
    print('Your IP is {0}'.format(response.json()['origin']))

# Only run if this file is executed directly
if __name__ == "__main__":
    print_ip()




