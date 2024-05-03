import json
import pyotp
import uuid
import re
import requests


class AngelOne:
    login_url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
    pos_url = 'https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/getPosition'
    login_data = None
    api_key = None

    def __init__(self, angel_one_details):
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
        r = requests.post(self.login_url, data=json.dumps(payload), headers=headers)
        print("Angle one login response : {}".format(r.text))
        if r.status_code != 200:
            print("AngelOne login failed")
        self.login_data = r.json()
        self.api_key = angel_one_details['api_key']

    def get_positions(self):

        headers = {
            'Authorization': 'Bearer {}'.format(self.login_data['data']['jwtToken']),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-PrivateKey': self.api_key,
            'X-ClientLocalIP': "127.0.0.1",
            'X-ClientPublicIP': "106.193.147.98",
            'X-MACAddress': ':'.join(re.findall('..', '%012x' % uuid.getnode())),
        }

        r = requests.get(self.pos_url, headers=headers)
        print("Get Positions response : {}".format(r.text))
        if r.status_code != 200:
            print("Get Positions API failed")
            return None
        return r.json()
