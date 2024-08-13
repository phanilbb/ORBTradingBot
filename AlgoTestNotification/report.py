from datetime import datetime

import gspread

r = '''
The NITian Algo
_______________
Day - {day_number} ({day})
Capital used: {capital}
Live Result : Rs. {profit} (after estimated brokerage deduction)
Day's ROI : {day_roi} %
Cumulative ROI: {cum_roi} %
_______________
'''


def convert_to_words(num):
    def format_number(n):
        return f"{n:.1f}".rstrip('0').rstrip('.')

    if num >= 10 ** 7:  # 1 Crore or more
        return f"{format_number(num / 10 ** 7)}Cr"
    elif num >= 10 ** 5:  # 1 Lakh or more
        return f"{format_number(num / 10 ** 5)}Lakhs"
    elif num >= 10 ** 3:  # 1 Thousand or more
        return f"{format_number(num / 10 ** 3)}K"
    else:  # Less than 1000
        return str(num)


class Report:
    start_row = 2
    report_template = None

    def __init__(self):
        global r
        self.report_template = r

    def get_text_report(self):
        # Initialize gspread and get the current sheet
        gc = gspread.service_account(filename='credentials.json')
        now = datetime.now()
        sheet = gc.open('Trades').worksheet(str(now.year))

        # Get day and calculate necessary values
        day_number = sheet.acell('N36').value
        day = now.strftime('%A')

        # Calculate the column for the current month
        current_month_num = now.month
        column = chr(ord('A') + current_month_num)

        # Calculate capital and profit cell references
        capital = float(sheet.acell(f"{column}2").value)
        row = now.day + 2
        profit = float(sheet.acell(f"{column}{row}").value)

        # Calculate day ROI and round to 2 decimal places
        day_roi = round(profit * 100 / capital, 2)

        # Retrieve cumulative ROI and each month's ROI in a loop
        cum_roi = sheet.acell('N35').value
        month_rois = {}
        for i, month in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            month_rois[month] = float(sheet.acell(f"{chr(ord('B') + i)}35").value)

        # Format the report template
        self.report_template = self.report_template.format(
            day_number=day_number,
            day=day,
            capital=convert_to_words(capital),
            day_roi=day_roi,
            cum_roi=cum_roi,
            profit=profit
        )

        current_month_abbr = now.strftime('%b').lower()

        for month, roi in month_rois.items():
            if roi != 0:
                if month == current_month_abbr:
                    self.report_template += f'\n{month.capitalize()} (ROI) : {roi} % (Running)'
                else:
                    self.report_template += f'\n{month.capitalize()} (ROI) : {roi} %'

        self.report_template += '\n_______________\n'

        return self.report_template
