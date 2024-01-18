import requests


def get_all(login_data):
    url = 'https://algotest.in/api/execution/executions'
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
    return data


def get(strategy_id, login_data):
    data = get_all(login_data)
    for each in data:
        if each['strategy_id'] == strategy_id:
            return each
    return {}
