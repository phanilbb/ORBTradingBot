import json
import time

import requests
import communication
import funds

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'Cookie': '__cf_bm=1xFucR9F3rDomA8bfQY87UrqYEBkNrpa8aNrf6G3GVY-1747888209-1.0.1.1-WPJpmJBeupoRWyhH.UyWzPhu0woNQuMS9Tv0g_RA7EnsgaRXboX3N6_VtOdFogx0E3cgNp8bLnCj6Bz4lL.MqSTxDtsSIwg4vTo6HKCJT3U; _cfuvid=VIvc418ejgNaLwJYEcx4ydjUftbzJWB06wenu1IR9HE-1747888209840-0.0.1.1-604800000'
}

URL = "https://groww.in/v1/api/data/mf/web/v4/scheme/search/{}"

required_top = 25


def get_holdings(fund):
    url = URL.format(fund)
    r = requests.get(url=url, headers=HEADERS)
    print("Requesting for url : " + url)
    if r.status_code != 200:
        com = communication.Communication()
        print("Request Failed with status {} for url {}".format(str(r.status_code), url))
        if r.status_code != 308:
            com.send_telegram_msg("Request Failed with status " + str(r.status_code))

    return r.json()['holdings']


def lambda_handler(event, context):
    com = communication.Communication()
    try:
        holdings_map = {}
        mfs = funds.get_funds(HEADERS)
        print("No of funds to process : {}".format(len(mfs)))
        for each_fund in mfs:
            holdings = get_holdings(each_fund)
            if holdings:
                for each_holding in holdings:
                    stock_id = each_holding.get('stock_search_id')
                    if stock_id:  # ensures it's not None or empty
                        holdings_map[stock_id] = holdings_map.get(stock_id, 0) + 1
            time.sleep(0.5)
        # Filter stocks that appear in more than 1 fund
        print("Filtering Holdings")
        filtered_holdings = {k: v for k, v in holdings_map.items() if v > 1}

        # Sort the filtered holdings by count in descending order
        print("sorting Holdings")
        sorted_holdings = sorted(filtered_holdings.items(), key=lambda item: item[1], reverse=True)

        com.send_telegram_msg("Analyzed {} mutual funds".format(len(mfs)))
        # Pick top 10 stock IDs
        if len(sorted_holdings) > required_top:
            top_10_stock_ids = dict(sorted_holdings[:required_top])
            print("Top 10 Common Stock IDs:", top_10_stock_ids)
            com.send_telegram_msg("Common stocks : \n" + str(json.dumps(top_10_stock_ids, indent=2)))
            return

        top_stock_ids = dict(sorted_holdings)
        print("Top Common Stock IDs:", top_stock_ids)
        com.send_telegram_msg("Common stocks : \n" + str(json.dumps(top_stock_ids, indent=2)))
        return


    except Exception as e:
        print("Request Failed with exception " + str(e))
        com.send_telegram_msg("Request Failed with exception " + str(e))
