import random
import gspread
import os


def get_background_index(topic, max):
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    wsheet = gsheet.worksheet("bg selector")
    print("BG selector for topic : " + topic)
    for i in range(2, wsheet.row_count):
        val = wsheet.acell('A' + str(i))
        print("Picked topic : " + str(val.value))
        if val.value.lower() == topic.lower() or val.value.lower() == "default":
            index = int(wsheet.acell('B' + str(i)).value)
            if os.environ.get("env", "aws") != "local":
                if index + 1 > max:
                    wsheet.update_acell('B' + str(i), 0)
                else:
                    wsheet.update_acell('B' + str(i), index + 1)
                print("BG index for topic : " + topic + " is : " + str(index))
            return index

    return int(random.randrange(0, max + 1))
