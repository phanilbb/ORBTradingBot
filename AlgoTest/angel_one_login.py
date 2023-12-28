import requests
import dynamo_db
import communication
import json
from smartapi import SmartConnect
import pyotp

URL = "https://algotest.in/api/broker_login/angelone_confirm/{}?auth_token={}&refresh_token={}&feed_token"


def create_session(angel_one_details):
    obj = SmartConnect(api_key=angel_one_details['api_key'], access_token=angel_one_details['secret_key'])
    totp = pyotp.TOTP(angel_one_details['topt'])
    data = obj.generateSession(angel_one_details['id'], angel_one_details['pin'], str(totp.now()))
    print("new session generated : {}".format(json.dumps(data)))
    return data


def run(account):
    try:
        print("Broker Logging in for account {}".format(account['name']))
        login_data = dynamo_db.get(account['name'])
        angel_one_details = account['broker_login']
        broker_id = angel_one_details.get('broker_id')
        data = create_session(angel_one_details)
        refresh_token = data['data']['refreshToken']
        auth_token = data['data']['accessToken']
        feed_token = data['data']['feedToken']
        login_angelone_algotest(broker_id, refresh_token, auth_token, feed_token, login_data['access_token_cookie'],
                                login_data['csrf_access_token'])
    except Exception as e:
        communication.telegram_bot_sendtext("{} Broker login Failed with err : {}".format(account['name'], str(e)))
        return False


def login_angelone_algotest(broker_id, refresh_token, auth_token, feed_token, access_token_cookie, csrf_access_token):
    url = URL.format(broker_id, auth_token, refresh_token, feed_token)
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'access_token_cookie=' + access_token_cookie + ';csrf_access_token=' + csrf_access_token,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN-ACCESS': csrf_access_token
    }
    r = requests.get(url=url, headers=headers)
    data = r.json()
    print("Algotest Angelone Login data : " + json.dumps(data))
    return True
