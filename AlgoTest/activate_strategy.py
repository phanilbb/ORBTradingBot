import json
import requests
import dynamo_db
import trade_executions

URL = "https://algotest.in/api/execution/start"


def run(account, result):
    db_data = dynamo_db.get(account['name'])
    activated_strategies = db_data.get('strategies', [])

    if len(account['strategies']) == len(activated_strategies):
        result['notify'] = False
        return result

    print("Strategy Activation for account {}".format(account['name']))
    for each_strategy in account['strategies']:
        try:
            if each_strategy['strategy'] not in activated_strategies:
                login_data = db_data['login_details']
                activate = get_activate_status(each_strategy, login_data)
                if not activate:
                    print("strategy activation skipped")
                    continue
                data = activate_strategy(each_strategy, login_data)
                if data["msg"] == "Strategy successfully submitted for execution":
                    activated_strategies.append(each_strategy['strategy'])
                    continue
                else:
                    result['success'] = False
                    result['error'] = "{}' Activation Failed : {}".format(each_strategy['name'], data["msg"])

        except Exception as e:
            result['success'] = False
            result['error'] = "{}' Activation Failed : {}".format(each_strategy['name'], str(e))
        finally:
            db_data['strategies'] = activated_strategies
            dynamo_db.save_item(db_data)


def calculate_profit_loss(trades):
    buy_trades = [trade for trade in trades if trade["Position"] == 1]
    sell_trades = [trade for trade in trades if trade["Position"] == -1]
    profit_loss = 0
    for buy_trade in buy_trades:
        for sell_trade in sell_trades:
            if buy_trade["Symbol"] == sell_trade["Symbol"] and buy_trade["LegID"] == sell_trade["LegID"]:
                quantity = min(buy_trade["Quantity"], sell_trade["Quantity"])
                profit_loss += (sell_trade["TradedPrice"] - buy_trade["TradedPrice"]) * quantity

    return profit_loss


def get_activate_status(strategy, login_data):
    if 'execute_after' not in strategy or not strategy['execute_after']:
        return True
    execution = trade_executions.get(strategy['execute_after'], login_data)
    if not execution or execution['status'] != 'square_off':
        return False
    profit_loss = calculate_profit_loss(execution['trades'])
    return profit_loss < 0


def activate_strategy(strategy, login_data):
    access_token_cookie = login_data['access_token_cookie']
    csrf_access_token = login_data['csrf_access_token']
    payload = json.dumps(strategy)
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'access_token_cookie=' + access_token_cookie + ';csrf_access_token=' + csrf_access_token,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN-ACCESS': csrf_access_token,
    }
    r = requests.post(url=URL, headers=headers, data=payload)
    data = r.json()
    print("Activate Strategy : " + json.dumps(data))
    return data


def telegram_bot_sendtext(bot_message):
    bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
    bot_chatID = '1170124746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()
