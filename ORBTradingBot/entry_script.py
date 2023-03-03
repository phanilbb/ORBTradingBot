import boto3
import time_helper
import requests
import ijson
import urllib.request
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb", region_name='ap-south-1')
trading_table = dynamodb.Table('Trading')

optionList = ["NIFTY"]

CE_ALLOWED_DAYS = [0, 1, 2, 3]
PE_ALLOWED_DAYS = [0, 1, 2, 3]

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


def run():
    return populateOptionsData(optionList)


def populateOptionsData(optionList):
    for e in optionList:
        ts = getTradeSymbol(e)

        if not ts:
            continue
        for ece in ts:

            instruments = get_instruments_filter_by_status(time_helper.get_current_date(), ece['symbol'],
                                                           DB_ORDER_STATUS['INIT'])

            if not instruments:

                item = {
                    'pk': time_helper.get_current_date(),
                    'sk': ece['symbol'],
                    'token': ece['token'],
                    'qty': str(100),
                    'status': DB_ORDER_STATUS['INIT'],
                    'entry_price': '',
                    'stop_loss': '',
                    'target': '',
                    'type': 'BUY',
                    'entry_id': '',
                    'stoploss_id': '',
                    'target_id': '',
                    'sl_trailing_points': str(20),
                    'sl_trail_by': str(1),
                    'reverse': str(0)
                }

                response = trading_table.put_item(Item=item)
                print(response)
            else:
                print("Instrument {} exists".format(ece['symbol']))

    return "Done"


def getStrikePrice(instrument):
    nextExpiryDate = time_helper.nextExpiryDate()
    data = getSymbolData(instrument, nextExpiryDate.strftime('%Y-%m-%d'))

    # strikeCE = getITMStrikePrice(data, "CE", 1)
    # strikePE = getITMStrikePrice(data, "PE", 1)
    diffCE = 1000
    diffPE = 1000
    strikePE = ''
    strikeCE = ''
    for e in data:
        if 200 <= float(e['ceQt']['ltp']) <= 250:
            diff = float(e['ceQt']['ltp']) - 200.0
            if diff < diffCE:
                diffCE = diff
                strikeCE = str(int(float(e['stkPrc'])))

        if 200 <= float(e['peQt']['ltp']) <= 250:
            diff = float(e['peQt']['ltp']) - 200.0
            if diff < diffPE:
                diffPE = diff
                strikePE = str(int(float(e['stkPrc'])))

    response = {
        'CE': strikeCE,
        'PE': strikePE
    }
    print(response)
    return response


def getITMStrikePrice(data, t, c):
    atmIndex = -1
    for i in range(0, len(data)):
        if data[i]['ATM']:
            atmIndex = i
            break

    if atmIndex != -1:
        if t == "CE":
            index = atmIndex - c
            return str(int(float(data[index]['stkPrc'])))

        if t == "PE":
            index = atmIndex + c
            return str(int(float(data[index]['stkPrc'])))

    return None


def getTradeSymbol(instrument):
    symbol = getStrikePrice(instrument)

    nextExpiryDate = time_helper.nextExpiryDate()

    # BANKNIFTY29DEC2241200CE

    s = "{instrument}{day}{month}{year}{strike}{option}"

    ol = []

    if symbol['CE'] and time_helper.get_current_weekday() in CE_ALLOWED_DAYS:
        sym = s.format(instrument=instrument, day='{:02d}'.format(nextExpiryDate.day),
                       month=nextExpiryDate.strftime("%b").upper(),
                       year=nextExpiryDate.strftime("%y"), strike=symbol['CE'], option="CE")
        print(sym)
        t = getSymbolTokenInfo(sym)
        if t:
            ol.append({
                'symbol': sym,
                'token': t
            })

    if symbol['PE'] and time_helper.get_current_weekday() in PE_ALLOWED_DAYS:
        sym = s.format(instrument=instrument, day='{:02d}'.format(nextExpiryDate.day),
                       month=nextExpiryDate.strftime("%b").upper(),
                       year=nextExpiryDate.strftime("%y"), strike=symbol['PE'], option="PE")
        print(sym)
        t = getSymbolTokenInfo(sym)

        if t:
            ol.append({
                'symbol': sym,
                'token': t
            })

    return ol


def getSymbolData(name, expiry):
    URL = "https://ewin.edelweiss.in/edelmw-content/content/options/optionchaindetails/OPTIDX/{}/{}".format(name,
                                                                                                            expiry)
    headers = {
        'authority': 'ewin.edelweiss.in',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'appidkey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOjEsImZmIjoiVyIsImJkIjoid2ViLXBjIiwibmJmIjoxNTc5MjQxODMyLCJzcmMiOiJlbXRtdyIsImF2IjoiMS4wLjAuNCIsImFwcGlkIjoiNGZlNjhiNzUzNjc4NGUzNDA3YzNlY2YxOWJlN2M0YWQiLCJpc3MiOiJlbXQiLCJleHAiOjE2MTA3NzgxMzIsImlhdCI6MTU3OTI0MjEzMn0.IR-PKf1Jjr69bsERFmMeuZrZ2RafBDiTGgKA6Ygofdo',
        'cache-control': 'no-cache',
        'origin': 'https://www.nuvamawealth.com',
        'pragma': 'no-cache',
        'referer': 'https://www.nuvamawealth.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'source': 'EDEL',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    r = requests.get(url=URL, headers=headers)
    data = r.json()
    return data['data']['opChn']


def getSymbolTokenInfo(symbol):
    with urllib.request.urlopen(
            "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json") as f:
        for record in ijson.items(f, "item"):
            if record['symbol'] == symbol:
                return record['token']
    return None


def get_instruments_filter_by_status(date, symbol, status):
    trade_items = trading_table.query(
        KeyConditionExpression=Key("pk").eq(date)
    )
    return [e for e in trade_items.get("Items") if e['status'] == status and e['sk'] == symbol]
