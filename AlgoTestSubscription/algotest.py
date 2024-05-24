import requests
import json


class AlgoTest:
    login_url = "https://algotest.in/api/login"
    plan_url = "https://algotest.in/api/plans"
    renew_plan_url = "https://algotest.in/api/plans_renew"
    access_token_cookie = None
    csrf_access_token = None

    def __init__(self):
        return

    def get_headers(self):
        return {
            'Accept': 'application/json, text/plain, */*',
            'Cookie': 'access_token_cookie=' + self.access_token_cookie + ';csrf_access_token=' + self.csrf_access_token,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'X-CSRF-TOKEN-ACCESS': self.csrf_access_token
        }

    def login_algo_test(self, data):
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
        r = requests.post(url=self.login_url, headers=headers, data=payload)
        if r.status_code != 200:
            print("Login failed {}".format(r.text))
        print("AlgoTest Login data : " + json.dumps(r.json()))
        cookies = r.cookies.get_dict()
        self.access_token_cookie = cookies.get('access_token_cookie', None)
        self.csrf_access_token = cookies.get('csrf_access_token', None)
        return r.cookies.get_dict()

    def get_plans(self):
        r = requests.get(url=self.renew_plan_url, headers=self.get_headers())
        if r.status_code != 200:
            print("Get Plans failed {}".format(r.text))
        print("Get Plan data : " + json.dumps(r.json()))
        return r.json()

    def subscribe_plans(self):
        payload = {
            "plans": {
                "live_execution": {
                    "max_strategies": 1
                }
            }
        }
        r = requests.post(url=self.renew_plan_url, headers=self.get_headers(), data=json.dumps(payload))
        if r.status_code != 200:
            print("Subscribe Plans failed {}".format(r.text))
        print("Subscribe Plans data : " + json.dumps(r.json()))
        return r.json()
