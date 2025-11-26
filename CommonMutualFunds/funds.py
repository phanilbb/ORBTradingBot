import time

import requests
import communication

URL = "https://groww.in/v1/api/search/v3/query/filter_derived_data/st_filter?doc_type=scheme&page={}&plan_type=Direct&scheme_type=Growth&size=1000"

payload = {}


def get_funds(headers):
    data = []
    for i in range(0, 5):
        url = URL.format(i)
        r = requests.get(url=url, headers=headers)
        print("Requesting for url : " + url)
        if r.status_code != 200:
            com = communication.Communication()
            com.send_telegram_msg("Funds get request Failed with status " + str(r.status_code))
            break
        else:
            data.extend(filter_funds(r.json()['content']))

        if r.json()['total_results'] < (i + 1) * 1000:
            break

        time.sleep(0.5)

    return data


def filter_funds(data):
    filtered_funds = []

    for each_fund in data:
        if 'groww_rating' not in each_fund or each_fund['groww_rating'] < 4:
            continue

        if 'risk_rating' not in each_fund or each_fund['risk_rating'] < 3:
            continue

        if 'search_id' not in each_fund:
            continue

        filtered_funds.append(each_fund['search_id'])

    return filtered_funds
