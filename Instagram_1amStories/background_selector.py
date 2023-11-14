import random
import gspread
import os


def get_background_index(topic, max):
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    wsheet = gsheet.worksheet("bg selector")
    for i in range(2, wsheet.row_count):
        val = wsheet.acell('A' + str(i))
        if val.value.lower() == topic.lower():
            index = int(wsheet.acell('B' + str(i)).value)
            if (index + 1 > max):
                wsheet.update_acell('B' + str(i), 0)
            else:
                wsheet.update_acell('B' + str(i), index + 1)

            return index

    return int(random.randrange(0, max))
