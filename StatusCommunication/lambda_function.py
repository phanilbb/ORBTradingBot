import json
import requests
import angel_one
import time_helper
import gspread


def telegram_bot_sendtext(bot_message):
    bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
    bot_chatID = '1170124746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


STATUS_TEMPLATE = '''

Trade : {t}
Quantity : {q}
Current P/L : {p}


'''

STATUS_COMMUNICATION_ENABLE = False


def lambda_handler(event, context):
    obj = angel_one.get_session()
    pos = angel_one.get_positions(obj)

    for each in pos:
        trade = each['tradingsymbol']
        qty = each['netqty']
        p = each['pnl']

        if int(qty) and STATUS_COMMUNICATION_ENABLE:
            message = STATUS_TEMPLATE.format(t=trade, q=qty, p=p)
            telegram_bot_sendtext(message)

    if time_helper.report_generation_time():
        generate_report(pos)


def generate_report(pos):
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key("1m1Gm_TmilUNlsA_EfmoTDb5LGHj15qQqdjAX2vZbFzo")
    wsheet = gsheet.worksheet("2023")

    for each in pos:
        data = []

        bp = float(each['totalbuyavgprice'])
        sp = float(each['totalsellavgprice'])
        qty = int(each['buyqty'])

        charges = get_charges(bp, sp, qty)

        data.append(time_helper.get_current_date())
        data.append(each['tradingsymbol'])
        data.append(each['strikeprice'])
        data.append(each['optiontype'])
        data.append('BUY')
        data.append(bp)
        data.append(sp)
        data.append(qty)
        amount = float(each['buyqty']) * (float(each['totalsellavgprice']) - float(each['totalbuyavgprice']))
        data.append(amount)
        data.append(charges)
        data.append(amount - charges)
        data.append('1' if amount - charges > 0 else '0')
        print(wsheet.append_row(data, 2))


def get_charges(bp, sp, qty):
    brokerage = 40

    turnover = float("%.2f" % float((bp + sp) * qty))

    stt_total = round(float("%.2f" % float(sp * qty * 0.0005)))

    etc = float("%.2f" % float(0.00053 * turnover))

    stax = float("%.2f" % float(0.18 * (brokerage + etc)))

    sebi_charges = float("%.2f" % float(turnover * 0.000001))
    sebi_charges = float("%.2f" % float(sebi_charges + (sebi_charges * 0.18)))

    stamp_charges = round(float("%.2f" % float(bp * qty * 0.00003)))

    total_tax = float("%.2f" % float(brokerage + stt_total + etc + stax + sebi_charges + stamp_charges))

    return total_tax
