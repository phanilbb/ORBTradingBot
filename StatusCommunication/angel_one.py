import json
from boto3.dynamodb.conditions import Key, Attr
import boto3
from smartapi import SmartConnect
import time_helper

historical_apis = {
    'api_key': 'dxZUmplW',
    'secret_key': '678c3eef-6137-4206-a1f9-26ee5ad8f933'
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


def get_session():
    # get saved data in db
    session_data = get_session_data()

    if not session_data:
        return None

    obj = SmartConnect(api_key=historical_apis['api_key'], access_token=historical_apis['secret_key'])
    data = obj.generateSessionWithData(session_data)

    if not data.get('status'):
        return None

    print("session generated from DB : {}".format(json.dumps(data)))

    return obj


def order_book(obj):
    order_book = obj.orderBook()
    order_book = [] if not order_book['data'] else order_book['data']
    print("Order Book Response : {}".format(json.dumps(order_book)))
    return order_book


def get_positions(obj):
    r = obj.position()
    print("The Positions response is: {}".format(json.dumps(r)))
    p = [] if not r['data'] else r['data']
    return p
