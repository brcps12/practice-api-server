from os import access
import requests

BASE_URL = 'http://localhost/elevator'
USER_KEY = 'testuser'
PROBLEM_ID = 0
NUMBER_OF_ELEVATORS = 1

access_token = ''

def start():
    global access_token

    url = '/start/{}/{}/{}'.format(USER_KEY, PROBLEM_ID, NUMBER_OF_ELEVATORS)
    headers = {}

    result = requests.post(BASE_URL + url, headers=headers)

    data = result.json()
    access_token = data.get('token')

def oncalls():
    url = '/oncalls'
    headers = {
        'X-Auth-Token': access_token
    }

    result = requests.get(BASE_URL + url, headers=headers)

    print(result.json())

if __name__ == '__main__':
    start()
    oncalls()
