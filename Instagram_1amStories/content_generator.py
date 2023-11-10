import os
import requests
import gspread
import communication


def get_quote():
    url = "https://api.quotable.io/quotes/random"
    response = requests.get(url=url)
    if response.status_code == 200:
        response_json = response.json()
        content = response_json[0]['content']
        author = response_json[0]['author']
        return content, author
    return None, None


def get_text_from_sheet():
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    wsheet = gsheet.worksheet("upload")
    val = wsheet.acell('A2')
    topic = wsheet.acell('B2')
    if val:
        return val.value, topic.value
    else:
        communication.telegram_bot_sendtext("No data available in google sheets")

    return get_quote()


def delete_row():
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key(os.environ['google_sheets_key'])
    uploadSheet = gsheet.worksheet("upload")
    val = uploadSheet.acell('A2')
    topic = uploadSheet.acell('B2')
    if val:
        data = []
        data.append(val.value)
        data.append(topic.value)
        uploadSheet.delete_row(2)
        uploadSheet.append_row(data, 2)


if __name__ == "__main__":
    val, topic = get_text_from_sheet()
