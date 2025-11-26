import time_helper
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb", region_name='ap-south-1')
DITTO_CALLS = dynamodb.Table('DittoCalls')


def get_pk():
    return time_helper.get_current_date()


def save(task_id, ttl_seconds=3 * 24 * 60 * 60):
    print("Saving task : " + str(task_id))
    item = {
        'pk': get_pk(),
        'sk': task_id,
        'notified': True,
        'ttl': int(time.time()) + ttl_seconds
    }
    save_item(item)


def save_item(item):
    DITTO_CALLS.put_item(Item=item)


def get(task_id):
    data = DITTO_CALLS.query(
        KeyConditionExpression=Key('pk').eq(get_pk()) & Key('sk').eq(task_id)
    )

    if data.get("Items"):
        return data.get("Items")[0]

    return {}
