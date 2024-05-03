import gspread
from datetime import datetime
from datetime import date
import communication


class Report:
    reference_date = None
    date_format = None

    def __init__(self):
        self.reference_date = '01/05/2024'
        self.date_format = '%d/%m/%Y'

    def generate_report(self, pos):
        gc = gspread.service_account(filename='credentials.json')
        today_date = datetime.strptime(date.today().strftime(self.date_format), self.date_format)
        reference_date = datetime.strptime(self.reference_date, self.date_format)
        difference = today_date - reference_date
        row_number = difference.days + 1

        pnl = 0
        for each in pos['data']:
            bp = float(each['totalbuyavgprice'])
            sp = float(each['totalsellavgprice'])
            qty = int(each['buyqty'])

            amount = float(each['buyqty']) * (float(each['totalsellavgprice']) - float(each['totalbuyavgprice']))
            charges = self.get_charges(bp, sp, qty)
            pnl += (amount - charges)

        print("Updating the column")
        gc.open('Trades').worksheet('2024').update_cell(row_number, 3, round(pnl, 2))

        comm = communication.Communication()
        comm.send_telegram_msg("Updated the Sheet for today")

    def get_charges(self, bp, sp, qty):
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
