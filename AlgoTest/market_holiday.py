import requests
import dynamo_db

import time_helper


def is_holiday(login_data):
    if not login_data:
        return False
    current_date = time_helper.get_current_date()
    url = "https://algotest.in/api/calendar/is-market-holiday/{}".format(current_date)
    access_token_cookie = login_data['access_token_cookie']
    csrf_access_token = login_data['csrf_access_token']
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'access_token_cookie=' + access_token_cookie + ';csrf_access_token=' + csrf_access_token,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN-ACCESS': csrf_access_token,
    }

    r = requests.get(url=url, headers=headers)
    data = r.json()
    return 'is_holiday' in data and data['is_holiday']


def run(account, result):
    try:
        db_data = dynamo_db.get(account['name'])
        login_data = db_data['login_details']
        result['notify'] = db_data['holiday'] is None
        if db_data['holiday'] is None:
            db_data['holiday'] = is_holiday(login_data)
            dynamo_db.save_item(db_data)
        result['holiday'] = db_data['holiday']

    except Exception as e:
        return False
