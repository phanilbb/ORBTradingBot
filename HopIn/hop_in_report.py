import json
from datetime import datetime, timedelta
import gspread
import requests

DAILY_REPORT_TEMPLATE = '''Daily Report - {}
<pre>
{}
</pre>
'''

TODAY_REPORT_TEMPLATE = '''Today's Report - {}
<pre>
{}
</pre>
'''

IN_STOCK_REPORT_TEMPLATE = '''In Stock Report - {}
<pre>
{}
</pre>
'''

COOKIES = {
    'AWSALB': 'N1NDF/cTUayEAfZWnrUI8iMr93f+gcUPLvERMwLNRac/qxZkADO57u6w+zVO69wDIbWqqTup99zcrbReO3glFgexrmHlDAlAhxkclyIXLasYNRwF7cOggsEPvr5C',
    'AWSALBCORS': 'N1NDF/cTUayEAfZWnrUI8iMr93f+gcUPLvERMwLNRac/qxZkADO57u6w+zVO69wDIbWqqTup99zcrbReO3glFgexrmHlDAlAhxkclyIXLasYNRwF7cOggsEPvr5C',
    'JSESSIONID': 'node01bo3xzphuxak289ciz4n300mh113010.node0', 'ownercub-lls': 'feac9b06-3aad-4b42-abce-c6c05f95565b'
}


def transform_to_characters(text, count):
    original_length = len(text)
    if original_length >= count:
        return text
    else:
        padding_length = (count - original_length) // 2
        padding = ' ' * padding_length
        padded_text = padding + text + padding
        if len(padded_text) < count:
            padded_text += ' '
        return padded_text


def create_table(headers, data, space_formats):
    a = ''
    a += "|{}|{}|\n".format(transform_to_characters(headers[0], space_formats[0]),
                            transform_to_characters(headers[1], space_formats[1]))
    a += "|{}|{}|\n".format(transform_to_characters('-' * space_formats[0], space_formats[0]),
                            transform_to_characters('-' * space_formats[1], space_formats[1]))

    for each_data in data:
        a += "|{}|{}|\n".format(transform_to_characters(each_data[0], space_formats[0]),
                                transform_to_characters(each_data[1], space_formats[1]))
    return a


def recaptcha():
    key = "6LdCH9IUAAAAAFP6czcCwYhAgc7yGegk8vT9C8bt"
    api_key = "22544668f9ccfb67d0506296b4e0e63a"
    from twocaptcha import TwoCaptcha
    solver = TwoCaptcha(api_key)
    try:
        result = solver.solve_captcha(
            site_key=key,
            page_url='https://loyverse.com/en/login')

        print(result)
        return result

    except Exception as e:
        print(e)


def login():
    code = recaptcha()
    url = "https://r.loyverse.com/data/cabinetlogin"
    payload = {
        "email": "Phanilbb@gmail.com",
        "password": "Phanindra173@pandu",
        "recaptchaResponse": code,
        "rememberMe": True, "devId": None,
        "cabinetLang": "eng", "type": "pos"
    }

    headers = {
        'authority': 'r.loyverse.com',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://loyverse.com',
        'referer': 'https://loyverse.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    r = requests.post(url=url, headers=headers, data=json.dumps(payload))
    print(r.status_code)
    print(r.cookies.get_dict())
    return r.cookies.get_dict()


def get_receipt_report(cookies, current_date=datetime.now().strftime('%Y-%m-%d')):
    url = "https://r.loyverse.com/data/ownercab/getreceiptsarchive"
    payload = {
        "limit": "100",
        "offset": 0,
        "receiptType": None,
        "payType": None,
        "startDate": "{} 00:00:00".format(current_date),
        "endDate": "{} 23:59:59".format(current_date),
        "search": None,
        "tzOffset": 19800000,
        "tzName": "Asia/Calcutta",
        "startWeek": 1,
        "receiptId": None,
        "predefinedPeriod": {
            "name": None,
            "period": None
        },
        "customPeriod": True
    }
    headers = {
        'authority': 'r.loyverse.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://r.loyverse.com',
        'Cookie': 'JSESSIONID={}; ownercub-lls={}; AWSALB={}; AWSALBCORS={}'.format(cookies['JSESSIONID'],
                                                                                    cookies['ownercub-lls'],
                                                                                    cookies['AWSALB'],
                                                                                    cookies['AWSALBCORS'])
    }

    r = requests.post(url=url, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        return r.json()

    print("Get Receipts failed : {}".format(r.text))
    return {}


def get_sheet():
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key("1m1Gm_TmilUNlsA_EfmoTDb5LGHj15qQqdjAX2vZbFzo")
    return gsheet


def push_to_excel(receipt_data, items_res):
    receipts_list = []
    items_list = []
    payments_list = []

    items_to_cat_map = {}
    for each_item in items_res['wares']:
        items_to_cat_map[each_item['name']] = each_item['category']

    for each_receipt in receipt_data['receipts']:
        original_date_time = datetime.fromisoformat(each_receipt['date'])
        updated_date_time = original_date_time + timedelta(hours=5, minutes=30)
        date = str(updated_date_time.date())
        time = str(updated_date_time.time())
        if each_receipt['cancelled']:
            continue
        receipt_info = {
            "date": date,
            "time": time,
            "receiptId": each_receipt['receiptId'],
            "type": each_receipt['type'],
            "totalAmount": each_receipt['totalAmount'] / 100 if each_receipt['type'] == 'SALE' else -each_receipt[
                'totalAmount'] / 100,
            "discountAmount": each_receipt['discountAmount'] / 100 if each_receipt['type'] == 'SALE' else -each_receipt[
                'discountAmount'] / 100,
        }
        receipts_list.append(list(receipt_info.values()))
        for each_item in each_receipt['itemRows']:
            q = each_item['quantity'] / 1000
            amt = each_item['amount'] / 100
            discountAmount = 0
            for each_discount in each_item['discounts']:
                discountAmount = discountAmount + (each_discount['amount'] / 100)
            item_data = {
                "date": date,
                "time": time,
                "receiptId": each_receipt['receiptId'],
                "type": each_receipt['type'],
                "item": each_item['name'],
                "quantity": q,
                "Category": items_to_cat_map.get(each_item['name'], ''),
                "amount": q * amt if each_receipt['type'] == 'SALE' else -q * amt,
                "discountAmount": discountAmount if each_receipt['type'] == 'SALE' else -discountAmount,
                "net": q * amt - discountAmount if each_receipt['type'] == 'SALE' else - (q * amt - discountAmount)
            }
            items_list.append(list(item_data.values()))

        for each_payment in each_receipt['payments']:
            payment_data = {
                "date": date,
                "time": time,
                "receiptId": each_receipt['receiptId'],
                "type": each_receipt['type'],
                "paymentTotal": each_payment['paymentTotal'] / 100 if each_receipt['type'] == 'SALE' else -each_payment[
                    'paymentTotal'] / 100,
                "paymentTypeName": "Cash" if not each_payment['paymentTypeName'] else each_payment[
                    'paymentTypeName']
            }
            payments_list.append(list(payment_data.values()))

    gsheet = get_sheet()
    gsheet.worksheet("Receipts").append_rows(receipts_list)
    gsheet.worksheet("Items").append_rows(items_list)
    gsheet.worksheet("Payments").append_rows(payments_list)


def get_payment_types(cookies, fromDate, toDate):
    url = "https://r.loyverse.com/data/ownercab/paymentstypesreport"
    payload = {
        "fromDate": "{} 00:00:00".format(fromDate),
        "toDate": "{} 23:59:59".format(toDate),
        "tzOffset": 19800000,
        "tzName": "Asia/Calcutta",
        "customPeriod": True
    }
    headers = {
        'authority': 'r.loyverse.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://r.loyverse.com',
        'Cookie': 'JSESSIONID={}; ownercub-lls={}; AWSALB={}; AWSALBCORS={}'.format(cookies['JSESSIONID'],
                                                                                    cookies['ownercub-lls'],
                                                                                    cookies['AWSALB'],
                                                                                    cookies['AWSALBCORS'])
    }

    r = requests.post(url=url, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        return r.json()

    return {}


def get_items(cookies):
    url = "https://r.loyverse.com/data/ownercab/getwares"
    payload = {
        "offset": 0,
        "limit": "100",
        "search": None,
        "outletId": None,
        "filters": {
            "inventory": "all",
            "category": "all"
        }
    }
    headers = {
        'authority': 'r.loyverse.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://r.loyverse.com',
        'Cookie': 'JSESSIONID={}; ownercub-lls={}; AWSALB={}; AWSALBCORS={}'.format(cookies['JSESSIONID'],
                                                                                    cookies['ownercub-lls'],
                                                                                    cookies['AWSALB'],
                                                                                    cookies['AWSALBCORS'])
    }

    r = requests.post(url=url, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        return r.json()

    print("Get Items failed : {}".format(r.text))
    return {}


def push_to_excel_payment_types(payment_types_response):
    upi_personal, upi_business, cash = 0, 0, 0
    for each_type in payment_types_response['items']:
        if each_type['paymentTypeName'].lower() == "cash":
            cash = cash + each_type['totalCollected'] / 100
        elif each_type['paymentTypeName'].lower() == "upi personal":
            upi_personal = upi_personal + each_type['totalCollected'] / 100
        elif each_type['paymentTypeName'].lower() == "upi business":
            upi_business = upi_business + each_type['totalCollected'] / 100
    data = [payment_types_response['startDateString'], cash, upi_personal, upi_business]
    sheet = get_sheet().worksheet('payment_types')
    sheet.append_row(data)


def telegram_bot_sendtext(bot_message):
    bot_token = '7194587495:AAGOhw2lKEupuU4mZa9BjmzciA5kCPNVakk'
    bot_chatID = '-4102625159'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=HTML&text=' + bot_message

    response = requests.get(send_text)

    if response.status_code != 200:
        print(response.text)

    return response.json()


def get_daily_report_dates():
    return datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')


def get_weekly_report_dates():
    current_date = datetime.now()
    days_until_monday = (current_date.weekday() - 0) % 7
    from_date = current_date - timedelta(days=days_until_monday)
    to_date = from_date + timedelta(days=6)
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    return from_date_str, to_date_str


def get_monthly_report_dates():
    current_date = datetime.now()
    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1, day=1) - timedelta(days=1))
    from_date_str = first_day_of_month.strftime("%Y-%m-%d")
    to_date_str = last_day_of_month.strftime("%Y-%m-%d")
    return from_date_str, to_date_str


def send_instock_message(items_response):
    headers = ["Item", "Stock"]
    spaces = [26, 6]
    data = []
    for each_item in items_response['wares']:
        if each_item['category'] != 'Raw materials':
            continue
        name = each_item['name'].lstrip('X - ').rsplit(' ', 1)[0]
        data.append([name, str(each_item['count'] / 1000)])

    table = create_table(headers, data, spaces)
    telegram_bot_sendtext(IN_STOCK_REPORT_TEMPLATE.format(datetime.now().strftime('%d-%m-%y'), table))


def send_daily_report_message(payment_types_response_daily, payment_types_response_weekly,
                              payment_types_response_monthly):
    headers = ["Category", "Amount"]
    spaces = [16, 10]
    data = []

    for each_type in payment_types_response_daily['items']:
        data.append([each_type['paymentTypeName'], str(each_type['totalCollected'] / 100)])

    dailyCollected = payment_types_response_daily['total']['totalCollected'] / 100
    weeklyCollected = payment_types_response_weekly['total']['totalCollected'] / 100
    monthlyCollected = payment_types_response_monthly['total']['totalCollected'] / 100

    data.append(["-" * spaces[0], '-' * spaces[1]])
    data.append(["Total", str(dailyCollected)])
    data.append(["-" * spaces[0], '-' * spaces[1]])
    data.append(["Weekly Total", str(weeklyCollected)])
    data.append(["Monthly Total", str(monthlyCollected)])

    table = create_table(headers, data, spaces)
    telegram_bot_sendtext(DAILY_REPORT_TEMPLATE.format(datetime.now().strftime('%d-%m-%y'), table))


def send_todays_report_message(payment_types_response_daily):
    headers = ["Category", "Amount"]
    spaces = [16, 10]
    data = []

    for each_type in payment_types_response_daily['items']:
        data.append([each_type['paymentTypeName'], str(each_type['totalCollected'] / 100)])

    dailyCollected = payment_types_response_daily['total']['totalCollected'] / 100 if payment_types_response_daily[
        'total'] else 0

    data.append(["-" * spaces[0], '-' * spaces[1]])
    data.append(["Total", str(dailyCollected)])
    data.append(["-" * spaces[0], '-' * spaces[1]])

    table = create_table(headers, data, spaces)
    telegram_bot_sendtext(TODAY_REPORT_TEMPLATE.format(str(dailyCollected), table))


def run(event):
    # cookies = login()
    # print(cookies)

    if event and event.get('report') == 'daily':
        fromDate, toDate = get_daily_report_dates()
        payment_types_response_daily = get_payment_types(COOKIES, fromDate, toDate)
        send_todays_report_message(payment_types_response_daily)
        return

    items_response = get_items(COOKIES)
    receipt_response = get_receipt_report(COOKIES)
    push_to_excel(receipt_response, items_response)

    fromDate, toDate = get_daily_report_dates()
    payment_types_response_daily = get_payment_types(COOKIES, fromDate, toDate)
    push_to_excel_payment_types(payment_types_response_daily)

    fromDate, toDate = get_weekly_report_dates()
    payment_types_response_weekly = get_payment_types(COOKIES, fromDate, toDate)

    fromDate, toDate = get_monthly_report_dates()
    payment_types_response_monthly = get_payment_types(COOKIES, fromDate, toDate)

    send_daily_report_message(payment_types_response_daily, payment_types_response_weekly,
                              payment_types_response_monthly)
    send_instock_message(items_response)
