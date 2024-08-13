import json
import pyotp
import uuid
import re
import requests


class AngelOne:
    login_url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
    pos_url = 'https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/getPosition'
    order_book_url = 'https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/getOrderBook'
    charges_url = 'https://apiconnect.angelbroking.com/rest/secure/angelbroking/brokerage/v1/estimateCharges'
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
        r = requests.get(self.pos_url, headers=self.get_request_headers())
        print("Get Positions response : {}".format(r.text))
        if r.status_code != 200:
            print("Get Positions API failed")
            return None
        return r.json()

    def get_order_book(self):
        r = requests.get(self.order_book_url, headers=self.get_request_headers())
        print("Get Order Book response : {}".format(r.text))
        if r.status_code != 200:
            print("Get Positions API failed")
            return None
        return r.json()

    def get_request_headers(self):
        return {
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

    def get_estimated_charges(self, order_book, pos):

        token_symbol_map = {}

        for each_pos in pos.get('data', []):
            token_symbol_map[each_pos['symboltoken']] = each_pos['symbolname']

        orders = []
        for each_order in order_book.get('data', []):
            orders.append({
                "product_type": each_order['producttype'],
                "transaction_type": each_order['transactiontype'],
                "quantity": each_order['quantity'],
                "price": each_order['price'],
                "exchange": each_order['exchange'],
                "symbol_name": token_symbol_map.get(each_order['symboltoken'], each_order['tradingsymbol']),
                "token": each_order['symboltoken']
            })

        payload = {
            'orders': orders
        }

        r = requests.post(self.charges_url, data=json.dumps(payload), headers=self.get_request_headers())
        print("Estimate charges response : {}".format(r.text))
        if r.status_code != 200 or not r.json() or not r.json().get('data'):
            print("Estimate charges failed")
            return len(order_book.get('data', [])) * 20 + 100
        return r.json().get('data', {}).get('summary', {}).get('total_charges', 0)
