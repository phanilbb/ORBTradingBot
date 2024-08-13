from datetime import datetime

import gspread

import angel_one
import communication


class Report:
    start_row = 2

    def __init__(self):
        return

    def update(self, event):
        angelOneObj = angel_one.AngelOne(event['angel_one_login_details'])
        pos = angelOneObj.get_positions()

        profit = 0
        for each in pos['data']:
            amount = float(each['buyqty']) * (float(each['totalsellavgprice']) - float(each['totalbuyavgprice']))
            profit += amount

        order_book = angelOneObj.get_order_book()
        charges = angelOneObj.get_estimated_charges(order_book, pos)
        pnl = profit - charges

        now = datetime.now()
        current_month_num = now.month
        column = chr(ord('A') + current_month_num)
        row = now.day + 2
        cell_reference = f"{column}{row}"

        print("Updating the column")
        gc = gspread.service_account(filename='credentials.json')
        sheet = gc.open('Trades').worksheet(str(now.year))
        sheet.update_acell(cell_reference, round(pnl, 2))

        comm = communication.Communication()
        if charges == 0:
            comm.send_telegram_msg("Estimated charges failed")
