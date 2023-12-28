import json
import requests
import dynamo_db

URL = "https://algotest.in/api/login"


def run(account, result):
    try:
        print("Logging in for account {}".format(account['name']))
        login_data = login_algo_test(account['algo_test_login'])
        dynamo_db.save(login_data, account['name'])
    except Exception as e:
        result['success'] = False
        result['error'] = "{} AlgoTest login Failed : {}".format(account['name'], str(e))


def login_algo_test(data):
    payload = json.dumps({
        'phoneNumber': data['phone_number'],
        'password': data['password']
    })
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Cookie': 'access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY5NTAyOTIyMCwianRpIjoiZmVjMmIzMDMtMjRjOS00MTFmLWI1Y2UtODZlNWUxZDQ2ZmRkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjYzYWYwYThkMjY4YjFhOTlkZDAxMDVhNCIsIm5iZiI6MTY5NTAyOTIyMCwiY3NyZiI6IjA2NDk5MjBhLWY0ZWUtNDU4ZS1iYTMxLWExYWUzODIxMDBhMSIsImV4cCI6MTY5NTI4ODQyMH0.v4tRy5mvcyZInN03gtrvh3dtNV0NrYHwNs126df14rI; csrf_access_token=0649920a-f4ee-458e-ba31-a1ae382100a1'
    }
    r = requests.post(url=URL, headers=headers, data=payload)
    print("Broker Login data : " + json.dumps(r.json()))
    return r.cookies.get_dict()
