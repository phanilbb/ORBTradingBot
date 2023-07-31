import json
import time

import requests
import time_helper
import angel_one
import numpy as np
import pandas as pd
from _datetime import datetime


def send_message(bot_message):
    print("Sending msg : " + bot_message)
    bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
    bot_chatID = '1170124746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


trades_taken = [{
    'symbol': 'POWERGRID-EQ',
    'entry_type': 'BUY'
}]


def lambda_handler(event, context):
    current_time = time_helper.get_current_time_with_delta(-5)
    fromdate = time_helper.get_date_with_delta(-60) + " 09:15"
    todate = time_helper.get_date_with_delta(0) + " " + current_time

    print("From date : {date}".format(date=fromdate))
    print("To date : {date}".format(date=todate))

    obj = angel_one.get_session()
    f = open("trades.json")
    data = json.load(f)

    for each_data in data:

        if each_data['symbol'] != 'BRITANNIA-EQ':
            continue

        closes = {}
        ema_50 = {}
        ema_200 = {}
        k_values = {}

        try:
            print("________________________________________")
            print("check for trade : " + each_data['symbol'])

            historic_data_1hr = angel_one.historic_data(obj, each_data['token'], fromdate, todate, "1h")
            historic_data_2hr = angel_one.historic_data_2hr(historic_data_1hr)

            closes['2hr'] = [e[4] for e in historic_data_2hr]
            ema_50['2hr'] = calculate_ema(closes['2hr'], 50)
            ema_200['2hr'] = calculate_ema(closes['2hr'], 200)
            # rsi_2hr, k1_2hr, d1_2hr = stoch_rsi_tradingview(pd.Series(closes['2hr']))
            # k_values['2hr'] = k1_2hr
            # check_condition(closes, ema_50, ema_200, k_values, each_data['symbol'], '2hr')
            check_ema_crossover(ema_50, ema_200, '2hr', each_data['symbol'])

        except Exception as e:
            print("Exception for trade {trade} : {e}".format(trade=each_data['symbol'], e=e))

    send_message("Ran Successfully")


def check_ema_crossover(ema_50, ema_200, condition_type, symbol):
    ema_50_current = ema_50[condition_type][len(ema_50[condition_type]) - 1]
    ema_50_previous = ema_50[condition_type][len(ema_50[condition_type]) - 2]

    ema_200_current = ema_200[condition_type][len(ema_200[condition_type]) - 1]
    ema_200_previous = ema_200[condition_type][len(ema_200[condition_type]) - 2]

    print("50 EMA Current : " + str(ema_50_current))
    print("200 EMA Current : " + str(ema_200_current))
    print("50 EMA Previous : " + str(ema_50_previous))
    print("200 EMA Previous : " + str(ema_200_previous))

    if ema_50_current < ema_200_current and ema_50_previous > ema_200_previous:
        send_message(
            "Strong SELL entry found for trade : {trade}".format(condition_type=condition_type,
                                                                 trade=symbol))

    if ema_50_current > ema_200_current and ema_50_previous < ema_200_previous:
        send_message(
            "Strong BUY entry found for trade : {trade}".format(condition_type=condition_type,
                                                                trade=symbol))

    if trades_taken:
        for each_trade in trades_taken:
            if each_trade['symbol'] == symbol:
                if each_trade['entry_type'] == "BUY" and ema_50_current < ema_200_current:
                    send_message(
                        "EXIT entry found for trade : {trade}".format(condition_type=condition_type,
                                                                      trade=symbol))
                if each_trade['entry_type'] == "SELL" and ema_50_current > ema_200_current:
                    send_message(
                        "EXIT entry found for trade : {trade}".format(condition_type=condition_type,
                                                                      trade=symbol))


def check_condition(closes, ema_50, ema_200, k_values, symbol, condition_type):
    try:
        k_value_prev = pd.Series.tolist(k_values[condition_type])[
            len(pd.Series.tolist(k_values[condition_type])) - 2]
        k_value = pd.Series.tolist(k_values[condition_type])[len(pd.Series.tolist(k_values[condition_type])) - 1]

        ema_1 = ema_50[condition_type][len(ema_50[condition_type]) - 1]
        ema_2 = ema_200[condition_type][len(ema_200[condition_type]) - 1]

        closes_ = closes[condition_type]

        print(("{condition_type} - current close for symbol : {symbol} is {value}".format(condition_type=condition_type,
                                                                                          symbol=symbol, value=closes_[
                len(closes_) - 1])))
        print("{condition_type} - ema 50 for symbol : {symbol} is {value}".format(condition_type=condition_type,
                                                                                  symbol=symbol, value=ema_1))
        print("{condition_type} - ema 200 for symbol : {symbol} is {value}".format(condition_type=condition_type,
                                                                                   symbol=symbol, value=ema_2))
        print("{condition_type} - k value for symbol : {symbol} is {value}".format(condition_type=condition_type,
                                                                                   symbol=symbol, value=k_value))
        print(
            "{condition_type} - k previous value for symbol : {symbol} is {value}".format(condition_type=condition_type,
                                                                                          symbol=symbol,
                                                                                          value=k_value_prev))

        if k_value_prev <= 20 and k_value > 20 and ema_1 > closes_[len(closes_) - 1] > ema_2:
            print("{condition_type}  Strong Buy entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                        trade=symbol))
            send_message(
                "{condition_type}  Strong Buy entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                      trade=symbol))
            return True, 'BUY'
        elif k_value_prev >= 80 and k_value < 80 and ema_1 < closes_[
            len(closes_) - 1] < ema_2:
            print("{condition_type}  Strong sell entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                         trade=symbol))
            send_message(
                "{condition_type}  Strong sell entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                       trade=symbol))
            return True, 'SELL'
        elif k_value_prev <= 20 and k_value > 20 and ema_1 > ema_2:
            print("{condition_type}  Buy entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                 trade=symbol))
            send_message("{condition_type}  Buy entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                        trade=symbol))
            return True, 'BUY'
        elif k_value_prev >= 80 and k_value < 80 and ema_1 < ema_2:
            print("{condition_type}  Sell entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                  trade=symbol))
            send_message("{condition_type}  Sell entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                         trade=symbol))
            return True, 'SELL'
        else:
            print("NO entry found for trade : {trade}".format(trade=symbol))
            return False, None
    except Exception as e:
        print("Exception for trade {trade} : {e}".format(trade=symbol, e=e))

    return False, None


def calculate_ema(data, period):
    # Calculate the smoothing factor
    smoothing_factor = 2 / (period + 1)

    # Calculate the initial SMA as the average of the first period values
    sma = np.mean(data[:period])

    ema_values = [sma]  # Store the EMA values

    # Calculate EMA for the remaining data points
    for i in range(period, len(data)):
        ema = (data[i] - ema_values[-1]) * smoothing_factor + ema_values[-1]
        ema_values.append(ema)

    return ema_values


def stoch_rsi_tradingview(series, period=14, smoothK=3, smoothD=3):
    # Calculate RSI
    rsi = rsi_tradingview(series, period=period, round_rsi=False)

    # Calculate StochRSI
    rsi = pd.Series(rsi)
    stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.rolling(smoothK).mean()
    stochrsi_D = stochrsi_K.rolling(smoothD).mean()

    return round(rsi, 2), round(stochrsi_K * 100, 2), round(stochrsi_D * 100, 2)


def rsi_tradingview(series, period: int = 14, round_rsi: bool = True):
    delta = series.diff()

    up = delta.copy()
    up[up < 0] = 0
    up = pd.Series.ewm(up, alpha=1 / period).mean()

    down = delta.copy()
    down[down > 0] = 0
    down *= -1
    down = pd.Series.ewm(down, alpha=1 / period).mean()

    rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))

    return np.round(rsi, 2) if round_rsi else rsi
