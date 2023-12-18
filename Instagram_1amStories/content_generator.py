import os
import gspread
import random
from helpers import string_helper, constants


def get_text_from_sheet(sheet):
    gc = gspread.service_account(filename='resources/credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    contentSheet = gsheet.worksheet(sheet)
    max_rows = contentSheet.row_count
    # random_row = random.randint(2, max_rows)
    random_row = 2
    values = contentSheet.row_values(random_row)
    result = dict(zip(contentSheet.row_values(1), values))
    format_results(result)
    result['row'] = random_row
    return result


def format_results(result):
    result['Category'] = 'love'
    result['Title'] = ''
    result['Content'] = result['Quote']

    result['Category'] = string_helper.remove_prefix_and_suffix(result['Category'], '"')
    result['Title'] = string_helper.add_prefix_and_suffix(result['Title'], '"')
    result['Content'] = string_helper.remove_prefix_and_suffix(result['Content'], '"')
    result['Caption'] = string_helper.remove_prefix_and_suffix(result['Caption'], '"')


def update_row_selector(sheet):
    gc = gspread.service_account(filename='resources/credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    row_selector = gsheet.worksheet(constants.ROW_SELECTOR_SHEET)
    for i in range(1, 10):
        val = row_selector.acell('A' + str(i))
        if val.value == sheet:
            row = int(row_selector.acell('B' + str(i)).value)
            row_selector.update_acell('B' + str(i), row + 1)
            return True

    return False


def backup_and_delete(upload_sheet_name, backup_sheet_name, row):
    gc = gspread.service_account(filename='resources/credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    upload_sheet = gsheet.worksheet(upload_sheet_name)
    values = upload_sheet.row_values(row)
    backup_sheet = gsheet.worksheet(backup_sheet_name)
    backup_sheet.append_row(values)
    upload_sheet.delete_row(row)
