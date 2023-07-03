import json
from boto3.dynamodb.conditions import Key, Attr
import boto3
from smartapi import SmartConnect
import pyotp
import time_helper
import exception_handling

trading_apis = {
    'api_key': 'pSbQYzxm',
    'secret_key': 'fda93c38-d97f-4078-96fb-271e2d52ea1f'
}

historical_apis = {
    'api_key': 'dxZUmplW',
    'secret_key': '678c3eef-6137-4206-a1f9-26ee5ad8f933'
}

EXCHANGE_TYPE = "NSE"
INTERVAL = {
    '3m': "THREE_MINUTE",
    '30m': 'THIRTY_MINUTE',
    '15m': 'FIFTEEN_MINUTE',
    '1h': 'ONE_HOUR'
}

dynamodb = boto3.resource("dynamodb", region_name='ap-south-1')
session_table = dynamodb.Table('Session')


def get_session_data():
    items = session_table.query(
        KeyConditionExpression=Key("pk").eq(time_helper.get_current_date())
    )
    items_list = items.get("Items")
    if not items_list:
        return None

    return items_list[0]


def set_session_data(data):
    data['pk'] = time_helper.get_current_date()
    data['sk'] = time_helper.get_current_date()
    session_table.put_item(Item=data)


def create_session():
    obj = SmartConnect(api_key=historical_apis['api_key'], access_token=historical_apis['secret_key'])
    totp = pyotp.TOTP('M3SAGK57IJCJIB5GH5NFG7DITI')
    data = obj.generateSession('L128041', '1703', str(totp.now()))
    set_session_data(data['data'])
    print("new session generated : {}".format(json.dumps(data)))
    return obj


def get_session():
    # get saved data in db
    session_data = get_session_data()

    if not session_data:
        return create_session()

    obj = SmartConnect(api_key=historical_apis['api_key'], access_token=historical_apis['secret_key'])
    data = obj.generateSessionWithData(session_data)

    if not data.get('status'):
        return create_session()

    print("session generated from DB : {}".format(json.dumps(data)))

    return obj


def historic_data(obj, token, fromdate, todate, interval):
    historicParam = {
        "exchange": EXCHANGE_TYPE,
        "symboltoken": str(token),
        "interval": INTERVAL[interval],
        "fromdate": fromdate,
        "todate": todate
    }

    try:
        response = obj.getCandleData(historicParam)
        if not response['status']:
            print("Historic data api failed with status false")
            return []

        if not response['data']:
            print("Historic data api failed with data null")
            return []

        print("Historic Response for token : {} is {}".format(str(token), json.dumps(response)))

        return response['data']

    except Exception as e:
        print("Historic Api failed: {}".format(e))
        exception_handling.send_message("Historic Api failed: {}".format(e))
        return []


def order_book(obj):
    order_book = obj.orderBook()
    order_book = [] if not order_book['data'] else order_book['data']
    print("Order Book Response : {}".format(json.dumps(order_book)))
    return order_book


def place_market_order(obj, transaction_type, instrument_data):
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": instrument_data['symbol'],
        "symboltoken": instrument_data['token'],
        "transactiontype": transaction_type,
        "exchange": EXCHANGE_TYPE,
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "quantity": instrument_data['quantity']
    }
    print(orderparams)
    print("Market order params for symbol {} is {}".format(instrument_data['symbol'], json.dumps(orderparams)))
    orderId = obj.placeOrder(orderparams)
    print("The market order id for {} is: {}".format(instrument_data['symbol'], orderId))
    return orderId


def place_limit_order(obj, transaction_type, instrument_data, price):
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": instrument_data['symbol'],
        "symboltoken": instrument_data['token'],
        "transactiontype": transaction_type,
        "exchange": EXCHANGE_TYPE,
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "price": str(price),
        "duration": "DAY",
        "quantity": instrument_data['quantity']
    }
    print("Limit order params for symbol {} is {}".format(instrument_data['symbol'], json.dumps(orderparams)))
    orderId = obj.placeOrder(orderparams)
    print("The Limit order id for {} is: {}".format(instrument_data['symbol'], orderId))
    return orderId


def place_sl_order(obj, transaction_type, instrument_data, price):
    orderparams = {
        "variety": "STOPLOSS",
        "tradingsymbol": instrument_data['symbol'],
        "symboltoken": instrument_data['token'],
        "transactiontype": transaction_type,
        "exchange": EXCHANGE_TYPE,
        "ordertype": "STOPLOSS_MARKET",
        "producttype": "INTRADAY",
        "triggerprice": str(price),
        "duration": "DAY",
        "quantity": instrument_data['quantity']
    }
    print("SL order params for symbol {} is {}".format(instrument_data['symbol'], json.dumps(orderparams)))
    orderId = obj.placeOrder(orderparams)
    print("The SL order id for {} is: {}".format(instrument_data['symbol'], orderId))
    return orderId


def place_sl_limit_order(obj, transaction_type, instrument_data, price):
    triggerprice = float(price) + 2
    if transaction_type == 'BUY':
        triggerprice = float(price)
        price = float(price) + 2

    orderparams = {
        "variety": "STOPLOSS",
        "tradingsymbol": instrument_data['symbol'],
        "symboltoken": instrument_data['token'],
        "transactiontype": transaction_type,
        "exchange": EXCHANGE_TYPE,
        "ordertype": "STOPLOSS_LIMIT",
        "producttype": "INTRADAY",
        "triggerprice": str(triggerprice),
        "price": str(price),
        "duration": "DAY",
        "quantity": instrument_data['quantity']
    }
    print("SL Limit order params for symbol {} is {}".format(instrument_data['symbol'], json.dumps(orderparams)))
    orderId = obj.placeOrder(orderparams)
    print("The SL Limit order id for {} is: {}".format(instrument_data['symbol'], orderId))
    return orderId


def cancel_order(obj, order_id, variety):
    orderId = obj.cancelOrder(order_id, variety)
    print("The Cancel order id is: {}".format(orderId))
    return orderId


def get_positions(obj):
    r = obj.position()
    print("The Positions response is: {}".format(json.dumps(r)))
    p = [] if not r['data'] else r['data']
    return p


def modify_sl_limit_order_to_limit_order(obj, order, price):
    order['ordertype'] = 'LIMIT'
    order['variety'] = "NORMAL"
    order['price'] = str(price)

    response = obj.modifyOrder(order)

    return response.get('status') == True


def modify_limit_order_to_sl_limit_order(obj, order, price):
    triggerprice = float(price) + 2
    if order['transactiontype'] == 'BUY':
        triggerprice = float(price)
        price = float(price) + 2

    order['ordertype'] = 'STOPLOSS_LIMIT'
    order['variety'] = "STOPLOSS"
    order['price'] = str(price)
    order['triggerprice'] = str(triggerprice)

    response = obj.modifyOrder(order)
    return response.get('status') == True


def get_ltp_data(obj, instrument_data):
    return obj.ltpData(EXCHANGE_TYPE, instrument_data['sk'], instrument_data['token'])
