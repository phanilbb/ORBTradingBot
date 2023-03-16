import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import requests

todaysTradesTemplate = '''

Todays trade : {s}

'''

orderEnteredTemplate = '''

{t} Limit entry order for {s} has been placed with 
Order id : {id}
Entry price : {p}

'''

entryOrderPlacedTemplate = '''

{t} entry order for {s} has been triggered with 
Order id : {id}
Entry price : {p}

'''

orderPlacedTemplate = '''

Target and SL for {s} has been placed.
Target : {t}
Stoploss : {sl}

'''

slHitTemplate = '''

SL for symbol {s} has been hit

'''

targetHitTemplate = '''

Target for symbol {s} has been hit

'''

exitTemplate = '''

Exited from trade {s} 

'''

cancelledTemplate = '''

Trade {s} has been cancelled

'''

createdTemplate = '''

Trade {s} ORB has been defined

'''

DB_ORDER_STATUS = {
    "INIT": "init",
    "CREATED": "created",
    "ENTRY_PLACED": "entry_placed",
    "TARGETS_PLACED": "targets_placed",
    "ENTERED": "entered",
    "SL_HIT": "stoploss_hit",
    "TARGET_HIT": "target_hit",
    "EXITED": "exited",
    "CANCELLED": "cancelled"
}


def telegram_bot_sendtext(bot_message):
    bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
    bot_chatID = '1170124746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def SendCommunication(event, context):
    print(event)

    message = getMessage(event)

    if message:

        telegram_bot_sendtext(message)

        print("Message triggered successfully")

    else:
        print("No messages found for communication")

    return message


def getMessage(event):
    messages = []

    for each_record in event['Records']:

        if each_record['eventName'] == "INSERT":
            message = eventDataForInsert(each_record)
            if message:
                messages.append(message)
        elif each_record['eventName'] == "MODIFY":
            message = eventDataForUpdate(each_record)
            if message:
                messages.append(message)

    return ",".join(messages)


def eventDataForInsert(record):
    new = unmarshall(record['dynamodb']['NewImage'])
    return todaysTradesTemplate.format(s=new['sk'])


def eventDataForUpdate(record):
    old = unmarshall(record['dynamodb']['OldImage'])
    new = unmarshall(record['dynamodb']['NewImage'])

    if new['status'] == DB_ORDER_STATUS['CREATED'] and old['status'] != DB_ORDER_STATUS['CREATED']:
        return getMessageForCreatedOrders(new)
    elif new['status'] == DB_ORDER_STATUS['ENTRY_PLACED'] and old['status'] != DB_ORDER_STATUS['ENTRY_PLACED']:
        return getMessageForEnteredOrders(new)
    elif new['status'] == DB_ORDER_STATUS['ENTERED'] and old['status'] != DB_ORDER_STATUS['ENTERED']:
        return getMessageForEnteredPlacedOrders(new)
    elif new['status'] == DB_ORDER_STATUS['TARGETS_PLACED'] and old['status'] != DB_ORDER_STATUS['TARGETS_PLACED']:
        return getMessageForPlacedOrders(new)
    elif new['status'] == DB_ORDER_STATUS['SL_HIT'] and old['status'] != DB_ORDER_STATUS['SL_HIT']:
        return getMessageForSLHitOrders(new)
    elif new['status'] == DB_ORDER_STATUS['TARGET_HIT'] and old['status'] != DB_ORDER_STATUS['TARGET_HIT']:
        return getMessageForTargetHitOrders(new)
    elif new['status'] == DB_ORDER_STATUS['EXITED'] and old['status'] != DB_ORDER_STATUS['EXITED']:
        return getMessageForExistedOrders(new)
    elif new['status'] == DB_ORDER_STATUS['CANCELLED'] and old['status'] != DB_ORDER_STATUS['CANCELLED']:
        return getMessageForCancelledOrders(new)

    return None


def getMessageForEnteredPlacedOrders(record):
    return entryOrderPlacedTemplate.format(s=record['sk'], p=record['entry_price'], t=record['type'],
                                           id=record['entry_id'])


def getMessageForCreatedOrders(record):
    return createdTemplate.format(s=record['sk'])


def getMessageForExistedOrders(record):
    return exitTemplate.format(s=record['sk'])


def getMessageForCancelledOrders(record):
    return cancelledTemplate.format(s=record['sk'])


def getMessageForEnteredOrders(record):
    return orderEnteredTemplate.format(s=record['sk'], p=record['entry_price'], t=record['type'], id=record['entry_id'])


def getMessageForPlacedOrders(record):
    return orderPlacedTemplate.format(s=record['sk'], t=record['target'], sl=record['stop_loss'])


def getMessageForSLHitOrders(record):
    return slHitTemplate.format(s=record['sk'])


def getMessageForTargetHitOrders(record):
    return targetHitTemplate.format(s=record['sk'])


def unmarshall(dynamo_obj: dict) -> dict:
    """Convert a DynamoDB dict into a standard dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}


def marshall(python_obj: dict) -> dict:
    """Convert a standard dict into a DynamoDB ."""
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_obj.items()}
