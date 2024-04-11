import requests
import dynamo_db
import json
import pyotp
import errors
import re
import uuid
import market_holiday

URL = "https://algotest.in/api/broker_login/angelone_confirm/{}?auth_token={}&refresh_token={}"
ANGEL_ONE_LOGIN_URL = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"


def create_session(angel_one_details):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-UserType': 'USER',
        'X-SourceID': 'WEB',
        'X-PrivateKey': angel_one_details['api_key'],
        'X-ClientLocalIP': "127.0.0.1",
        'X-ClientPublicIP': "106.193.147.98",
        'X-MACAddress': ':'.join(re.findall('..', '%012x' % uuid.getnode())),
    }
    totp = pyotp.TOTP(angel_one_details['totp'])
    payload = {
        'clientcode': angel_one_details['id'],
        'password': angel_one_details['pin'],
        'totp': str(totp.now())
    }
    r = requests.post(ANGEL_ONE_LOGIN_URL, data=json.dumps(payload), headers=headers)
    print("Angle one login response : {}".format(r.text))
    if r.status_code != 200:
        raise errors.CustomError("Angle one login Failed {}".format(r.text))
    return r.json()


def run(account, result):
    try:
        db_data = dynamo_db.get(account['name'])
        login_data = db_data['login_details']
        angel_one_details = account['broker_login']

        if 'holiday' in db_data and db_data['holiday']:
            return

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
        result['holiday'] = market_holiday.is_holiday(login_data)
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
