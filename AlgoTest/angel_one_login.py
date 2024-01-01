import requests
import dynamo_db
import json
import pyotp
import errors
from SmartApi import SmartConnect

URL = "https://algotest.in/api/broker_login/angelone_confirm/{}?auth_token={}&refresh_token={}"


def create_session(angel_one_details):
    smartApi = SmartConnect(angel_one_details['api_key'])
    totp = pyotp.TOTP(angel_one_details['totp'])
    data = smartApi.generateSession(angel_one_details['id'], angel_one_details['pin'], totp.now())
    print("Angle one login response : {}".format(str(data)))
    userData = smartApi.getProfile(data['data']['refreshToken'])
    print("Angle one User data response : {}".format(str(userData)))
    return data


def run(account, result):
    try:
        db_data = dynamo_db.get(account['name'])
        login_data = db_data['login_details']
        angel_one_details = account['broker_login']

        if not db_data.get('broker_login'):
            print("Broker Logging in for account {}".format(account['name']))
            data = create_session(angel_one_details)
            if login_angelone_algotest(angel_one_details['broker_id'], data['data']['refreshToken'],
                                       data['data']['jwtToken'], login_data['access_token_cookie'],
                                       login_data['csrf_access_token']):
                db_data['broker_login'] = True
                dynamo_db.save_item(db_data)

    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        return False


def login_angelone_algotest(broker_id, refresh_token, auth_token, access_token_cookie, csrf_access_token):
    url = URL.format(broker_id, auth_token, refresh_token)
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'access_token_cookie=' + access_token_cookie + ';csrf_access_token=' + csrf_access_token,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN-ACCESS': csrf_access_token
    }
    r = requests.get(url=url, headers=headers)
    if r.status_code != 200:
        raise errors.CustomError("AlgoTest AngelOne login failed : {}".format(r.text))

    data = r.json()
    print("AlgoTest AngelOne Login data : " + json.dumps(data))
    return r.status_code == 200
