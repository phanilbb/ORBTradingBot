import gspread
from datetime import datetime
from datetime import date
import communication
import angel_one


class Report:
    reference_date = None
    date_format = None

    def __init__(self):
        self.reference_date = '01/05/2024'
        self.date_format = '%d/%m/%Y'

    def generate_report(self, event):
        angelOneObj = angel_one.AngelOne(event['angel_one_login_details'])
        pos = angelOneObj.get_positions()

        gc = gspread.service_account(filename='credentials.json')
        today_date = datetime.strptime(date.today().strftime(self.date_format), self.date_format)
        reference_date = datetime.strptime(self.reference_date, self.date_format)
        difference = today_date - reference_date
        row_number = difference.days + 1

        profit = 0
        for each in pos['data']:
            amount = float(each['buyqty']) * (float(each['totalsellavgprice']) - float(each['totalbuyavgprice']))
            profit += amount

        order_book = angelOneObj.get_order_book()
        charges = angelOneObj.get_estimated_charges(order_book, pos)
        pnl = profit - charges

        print("Updating the column")
        sheet = gc.open('Trades').worksheet('2024')
        sheet.update_cell(row_number, 3, round(profit, 2))
        sheet.update_cell(row_number, 4, round(charges, 2))
        sheet.update_cell(row_number, 5, round(pnl, 2))

        comm = communication.Communication()
        if charges == 0:
            comm.send_telegram_msg("Estimated charges failed")
        comm.send_telegram_msg("Updated the Sheet for today")
