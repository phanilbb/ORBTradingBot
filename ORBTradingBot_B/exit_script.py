import json
import angel_one

checkStatus = ["complete", "cancelled", "rejected"]


def run():
    global order_book
    global obj
    obj = angel_one.get_session()
    order_book = angel_one.order_book(obj)
    order_book = sorted(order_book, key=lambda x: x['netqty'], reverse=True)

    for e in order_book:
        if e['orderstatus'] in checkStatus:
            continue
        angel_one.cancel_order(obj, e['orderid'], e['variety'])

    pos = angel_one.get_positions(obj)

    for e in pos:

        qty = 0
        t = ''
        if isBuyPosition(e):
            t = "SELL"
            qty = int(e['netqty'])
        elif isSellPosition(e):
            t = "BUY"
            qty = -int(e['netqty'])

        if qty:
            data = {
                'symbol': e['tradingsymbol'],
                'token': e['symboltoken'],
                'quantity': qty
            }
            angel_one.place_market_order(obj, t, data)


def isBuyPosition(openPos):
    return int(openPos['netqty']) > 0


def isSellPosition(openPos):
    return int(openPos['netqty']) < 0
