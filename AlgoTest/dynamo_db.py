import time_helper
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb", region_name='ap-south-1')
ALGOTESTLOGIN = dynamodb.Table('AlgoTestLogin')


def get_pk():
    return time_helper.get_current_date()


def save(login_data, account):
    print("Saving to account : " + str(login_data))
    item = {
        'pk': get_pk(),
        'sk': account,
        'login_details': login_data,
        'broker_login': False,
        'strategies': []
    }
    save_item(item)


def save_item(item):
    ALGOTESTLOGIN.put_item(Item=item)


def get(account):
    data = ALGOTESTLOGIN.query(
        KeyConditionExpression=Key('pk').eq(get_pk()) & Key('sk').eq(account)
    )

    if data.get("Items"):
        return data.get("Items")[0]

    return {}
