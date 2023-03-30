import time_helper
import boto3
import angel_one
from boto3.dynamodb.conditions import Key, Attr
import time
import exception_handling
import math
import dynamo

dynamodb = boto3.resource("dynamodb", region_name='ap-south-1')
trading_table = dynamodb.Table('Trading')

obj = None
order_book = []

DB_ORDER_STATUS = {
    "INIT": "init",
    "CREATED": "created",
    "ENTRY_PLACED": "entry_placed",
    "ENTERED": "entered",
    "TARGETS_PLACED": "targets_placed",
    "SL_HIT": "stoploss_hit",
    "TARGET_HIT": "target_hit",
    "EXITED": "exited",
    "CANCELLED": "cancelled"
}


def run():
    if not time_helper.is_within_trading_time():
        print("Skipping entry : not within trading time")
        return

    global order_book
    global obj

    obj = angel_one.get_session()
    order_book = angel_one.order_book(obj)

    orbTargets()
    placeEntryOrders()
    checkEntryOrders()
    placeExitOrder()
    checkExitOrder()


def get_orb_targets(type, high, low):
    if type == 'BUY':
        target = high + 303
        sl = low
    else:
        target = low - 300
        sl = high

    return {
        'target': target,
        'sl': sl
    }


def orbTargets():
    try:

        if not time_helper.orb_targets_time():
            print("Skipping orb_targets_time : not within orb_targets_time time")
            return

        instruments = get_instruments_filter_by_status(DB_ORDER_STATUS['INIT'])
        instruments = sorted(instruments, key=lambda x: x['type'])
        if not instruments:
            print("No data to checkEntry")
            return

        for each_instrument in instruments:

            current_date = time_helper.get_current_date()
            current_time = time_helper.get_current_time_with_delta(-1)
            fromdate = current_date + " 09:15"
            todate = current_date + " " + current_time

            historic_data = angel_one.historic_data(obj, each_instrument['token'], fromdate, todate, "15m")

            if not historic_data:
                print("No historic data found for symbol :" + each_instrument['sk'])
                continue

            orb_candle = historic_data[0]
            orb_high = orb_candle[2]
            orb_low = orb_candle[3]
            targets = get_orb_targets(each_instrument['type'], orb_high, orb_low)

            each_instrument['entry_price'] = str(orb_high) if each_instrument['type'] == 'BUY' else str(orb_low)
            each_instrument['target'] = str(int(math.ceil(targets['target'])))
            each_instrument['stop_loss'] = str(int(targets['sl']))
            each_instrument['status'] = DB_ORDER_STATUS['CREATED']

            trading_table.put_item(Item=each_instrument)
            print("Entry data created for symbol {}".format(each_instrument['sk']))

    except Exception as e:
        print("Exception in orbTargets {}".format(e))
        exception_handling.send_message("Exception in orbTargets {}".format(e))


def placeEntryOrders():
    try:

        if not time_helper.is_within_entry_time():
            print("Skipping placeEntryOrders : not within placeEntryOrders time")
            return

        instruments = get_instruments_filter_by_status(DB_ORDER_STATUS['CREATED'])
        instruments = sorted(instruments, key=lambda x: x['type'])
        if not instruments:
            print("No data to placeEntryOrders")
            return

        for each_instrument in instruments:

            instrument_data = {
                'symbol': each_instrument['sk'],
                'token': each_instrument['token'],
                'quantity': each_instrument['qty']
            }

            price = each_instrument['entry_price']

            orderId = angel_one.place_sl_limit_order(obj, each_instrument['type'], instrument_data, price)
            update_orderbook(obj)
            if orderId and (is_order_placed(orderId, 'trigger pending') or is_order_placed(orderId,
                                                                                           'complete') or is_order_placed(
                orderId, 'open')):
                each_instrument['status'] = DB_ORDER_STATUS['ENTRY_PLACED']
                entry_price = get_price_by_orderid(str(orderId))
                each_instrument['entry_price'] = str(entry_price) if float(entry_price) > 0 else str(price)
                each_instrument['entry_id'] = str(orderId)
                trading_table.put_item(Item=each_instrument)

                print("Entry orders placed for symbol {}".format(each_instrument['sk']))


    except Exception as e:
        print("Exception in placeEntryOrders {}".format(e))
        exception_handling.send_message("Exception in placeEntryOrders {}".format(e))


def checkEntryOrders():
    try:
        instruments = get_instruments_filter_by_status(DB_ORDER_STATUS['ENTRY_PLACED'])
        instruments = sorted(instruments, key=lambda x: x['type'])
        if not instruments:
            print("No data to checkEntryOrders")
            return

        for each_instrument in instruments:

            entry_id = each_instrument['entry_id']
            if is_order_placed(entry_id, "complete"):
                each_instrument['status'] = DB_ORDER_STATUS['ENTERED']
                trading_table.put_item(Item=each_instrument)
                print("Entry order triggered for symbol {}".format(each_instrument['sk']))

    except Exception as e:
        print("Exception in checkEntryOrders {}".format(e))
        exception_handling.send_message("Exception in checkEntryOrders {}".format(e))


def placeExitOrder():
    try:
        instruments = get_instruments_filter_by_symbols(active_position_symbols())
        instruments = sorted(instruments, key=lambda x: x['type'])
        if not instruments:
            print("No data to placeExitOrder")
            return

        for each_instrument in instruments:

            # blocking this for hedge orders
            if each_instrument['type'] == 'BUY':
                continue

            target = float(each_instrument['target'])
            stoploss = float(each_instrument['stop_loss'])

            if not each_instrument['target_id'] and not each_instrument['stoploss_id']:
                instrument_data = {
                    'symbol': each_instrument['sk'],
                    'token': each_instrument['token'],
                    'quantity': each_instrument['qty']
                }

                orderId = angel_one.place_sl_limit_order(obj, 'SELL', instrument_data, stoploss)

                update_orderbook(obj)
                if orderId and (is_order_placed(orderId, 'trigger pending') or is_order_placed(orderId, 'complete')):
                    each_instrument['status'] = DB_ORDER_STATUS['TARGETS_PLACED']
                    each_instrument['stoploss_id'] = orderId
                    trading_table.put_item(Item=each_instrument)
                    print("StopLoss order placed for symbol {}".format(each_instrument['sk']))

            else:

                ohlc = get_OHLC_data(each_instrument['token'], "3m")
                close = ohlc['close']
                print("LTP close for symbol {} is {}".format(each_instrument['sk'], str(close)))

                orderId = each_instrument['target_id'] if each_instrument['target_id'] else each_instrument[
                    'stoploss_id']

                order_details = filter_order_by_id(order_book, orderId)

                if not order_details:
                    continue

                is_stoploss_order = order_details[0]['variety'] == 'STOPLOSS'

                if abs(close - stoploss) > abs(close - target) and is_stoploss_order:
                    if angel_one.modify_sl_limit_order_to_limit_order(obj, order_details[0], target):
                        each_instrument['stoploss_id'] = ''
                        each_instrument['target_id'] = orderId
                        trading_table.put_item(Item=each_instrument)
                        print("StopLoss order modified to target order for symbol {}".format(each_instrument['sk']))

                if abs(close - stoploss) < abs(close - target) and not is_stoploss_order:
                    if angel_one.modify_limit_order_to_sl_limit_order(obj, order_details[0], stoploss):
                        each_instrument['stoploss_id'] = orderId
                        each_instrument['target_id'] = ''
                        trading_table.put_item(Item=each_instrument)
                        print("Target order modified to Stoploss order for symbol {}".format(each_instrument['sk']))

    except Exception as e:
        print("Exception in placeExitOrder {}".format(e))
        exception_handling.send_message("Exception in placeExitOrder {}".format(e))


def checkExitOrder():
    try:
        instruments = get_instruments_filter_by_status(DB_ORDER_STATUS['TARGETS_PLACED'])
        instruments = sorted(instruments, key=lambda x: x['type'])
        if not instruments:
            print("No data to checkTargetOrders")
            return

        for each_instrument in instruments:

            # blocking this for hedge orders
            if each_instrument['type'] == 'BUY':
                continue

            target_id = each_instrument['target_id']
            if target_id and is_order_placed(target_id, "complete"):
                each_instrument['status'] = DB_ORDER_STATUS['TARGET_HIT']
                trading_table.put_item(Item=each_instrument)
                print("Target order triggered for symbol {}".format(each_instrument['sk']))

            stoploss_id = each_instrument['stoploss_id']
            if stoploss_id and is_order_placed(stoploss_id, "complete"):
                each_instrument['status'] = DB_ORDER_STATUS['SL_HIT']
                trading_table.put_item(Item=each_instrument)
                print("Stoploss order triggered for symbol {}".format(each_instrument['sk']))

    except Exception as e:
        print("Exception in checkExitOrder {}".format(e))
        exception_handling.send_message("Exception in checkExitOrder {}".format(e))


def checkExit():
    try:

        instruments = get_instruments_filter_by_symbols(active_position_symbols())
        instruments = sorted(instruments, key=lambda x: x['type'])
        if not instruments:
            print("No data to checkExit")
            return

        for each_instrument in instruments:
            target = each_instrument['target']
            stoploss = each_instrument['stop_loss']
            ltp_data = angel_one.get_ltp_data(obj, each_instrument)
            current_high = ltp_data['data']['high']
            current_low = ltp_data['data']['low']

            if float(current_high) >= float(target) or float(current_low) <= float(stoploss):

                instrument_data = {
                    'symbol': each_instrument['sk'],
                    'token': each_instrument['token'],
                    'quantity': each_instrument['qty']
                }
                orderId = angel_one.place_market_order(obj, 'SELL', instrument_data)

                update_orderbook(obj)
                if orderId and (is_order_placed(orderId, 'complete')):

                    if each_instrument['target_id']:
                        order_details = filter_order_by_id(each_instrument['target_id'])

                        if order_details:
                            angel_one.cancel_order(obj, order_details[0]['orderid'], order_details[0]['variety'])

                    if each_instrument['stoploss_id']:
                        order_details = filter_order_by_id(each_instrument['stoploss_id'])

                        if order_details:
                            angel_one.cancel_order(obj, order_details[0]['orderid'], order_details[0]['variety'])

                    if float(current_high) >= float(target):
                        each_instrument['status'] = DB_ORDER_STATUS['TARGET_HIT']
                        each_instrument['target_id'] = orderId
                        print("Target Hit for symbol {}".format(each_instrument['sk']))
                    else:
                        each_instrument['status'] = DB_ORDER_STATUS['SL_HIT']
                        each_instrument['stoploss_id'] = orderId
                        print("SL Hit for symbol {}".format(each_instrument['sk']))

                    trading_table.put_item(Item=each_instrument)

    except Exception as e:
        print("Exception in checkExit {}".format(e))
        exception_handling.send_message("Exception in checkExit {}".format(e))


def get_instruments_filter_by_status(status):
    trade_items = trading_table.query(
        KeyConditionExpression=Key("pk").eq(dynamo.get_dynamo_pk())
    )
    return [e for e in trade_items.get("Items") if e['status'] == status]


def get_instruments_filter_by_symbols(symbols):
    trade_items = trading_table.query(
        KeyConditionExpression=Key("pk").eq(dynamo.get_dynamo_pk())
    )
    return [e for e in trade_items.get("Items") if e['sk'] in symbols]


def get_price_by_orderid(order_id):
    global order_book

    order = [e for e in order_book if e['orderid'] == order_id]

    if not order:
        return None

    return str(order[0]['averageprice'])


def get_order_by_symbol(symbol):
    global order_book
    return [e for e in order_book if e['tradingsymbol'] == symbol and e['orderstatus'] == 'complete']


def is_order_placed(orderid, checkStatus):
    global order_book
    order = [e for e in order_book if e['orderid'] == orderid]

    if not order:
        print('Order not found')
        return False

    if order[0]['orderstatus'] != checkStatus:
        print('Status not matched : ' + order[0]['orderstatus'])
        return False

    return True


def filter_order_by_status(order_book, status):
    return [e for e in order_book if e['orderstatus'] == status]


def filter_order_by_id(order_book, orderid):
    return [e for e in order_book if e['orderid'] == orderid]


def filter_order_by_status_and_id(order_book, status, orderid):
    return [e for e in order_book if e['orderid'] == orderid and e['orderstatus'] == status]


def is_position_active(symbol):
    pos = angel_one.get_positions(obj)

    pos_sym = [e for e in pos if e['tradingsymbol'] == symbol]

    return len(pos_sym) and int(pos_sym[0]['netqty']) != 0


def active_position_symbols():
    pos = angel_one.get_positions(obj)
    return [e['tradingsymbol'] for e in pos if int(e['netqty']) > 0]


def get_OHLC_data(token, time_interval):
    current_date = time_helper.get_current_date()
    to_time = time_helper.get_current_time_with_delta(-1)

    from_time = time_helper.get_current_time_with_delta(-10)
    fromdate = current_date + " " + from_time
    todate = current_date + " " + to_time

    historic_data = angel_one.historic_data(obj, token, fromdate, todate, time_interval)

    if not historic_data:
        return {}

    return {
        'open': historic_data[len(historic_data) - 1][1],
        'high': historic_data[len(historic_data) - 1][2],
        'low': historic_data[len(historic_data) - 1][3],
        'close': historic_data[len(historic_data) - 1][4]
    }


def update_orderbook(obj):
    time.sleep(1)
    global order_book
    order_book = angel_one.order_book(obj)
