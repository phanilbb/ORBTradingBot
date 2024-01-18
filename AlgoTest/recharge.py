import dynamo_db
import requests
import errors
import json
import time_helper

URL = "https://algotest.in/api/plans"


def get_plans(access_token_cookie, csrf_access_token):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'access_token_cookie=' + access_token_cookie + ';csrf_access_token=' + csrf_access_token,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN-ACCESS': csrf_access_token
    }

    r = requests.get(url=URL, headers=headers)
    if r.status_code != 200:
        raise errors.CustomError("Get Plans failed {}".format(r.text))
    print("Get Plan data : " + json.dumps(r.json()))
    return r.json()


def subscribe_plans(access_token_cookie, csrf_access_token):
    payload = {
        "plans": {
            "external_connect": False,
            "live_execution": {
                "max_strategies": 2
            }
        }
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'access_token_cookie=' + access_token_cookie + ';csrf_access_token=' + csrf_access_token,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN-ACCESS': csrf_access_token
    }

    r = requests.post(url=URL, headers=headers, data=json.dumps(payload))
    if r.status_code != 200:
        raise errors.CustomError("Subscribe Plans failed {}".format(r.text))
    print("Subscribe Plans data : " + json.dumps(r.json()))
    return r.status_code == 200


def run(account, result, combined_result):
    try:
        db_data = dynamo_db.get(account['name'])
        login_data = db_data['login_details']

        if 'plan_found' in db_data and db_data['plan_found']:
            print("Plan details found")
            return

        plan_data = get_plans(login_data['access_token_cookie'], login_data['csrf_access_token'])

        if not plan_data['expiration'] or time_helper.is_before_current_time(plan_data['expiration']):
            print("Plan Expired | Subscribing to plans")
            if subscribe_plans(login_data['access_token_cookie'], login_data['csrf_access_token']):
                db_data['plan_found'] = True
        else:
            print("Plan will expire on : {}".format(plan_data['expiration']))
            db_data['plan_found'] = True
        dynamo_db.save_item(db_data)

    except Exception as e:
        print("Recharge Exception : {}".format(str(e)))

    return True
