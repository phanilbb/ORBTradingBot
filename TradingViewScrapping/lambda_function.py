import json
import time

import requests
import time_helper
import angel_one
import numpy as np
import pandas as pd
from _datetime import datetime


def send_message(bot_message):
    bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
    bot_chatID = '1170124746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def lambda_handler(event, context):
    current_time = time_helper.get_current_time_with_delta(-5)
    fromdate = time_helper.get_date_with_delta(-60) + " 09:15"
    todate = time_helper.get_date_with_delta(0) + " " + current_time

    print("From date : {date}".format(date=fromdate))
    print("To date : {date}".format(date=todate))

    obj = angel_one.get_session()
    f = open("trades.json")
    data = json.load(f)

    t1 = datetime.now()
    call_count = 0

    for each_data in data:

        closes = {}
        ema_50 = {}
        ema_200 = {}
        k_values = {}

        try:
            print("________________________________________")
            print("check for trade : " + each_data['symbol'])

            # historic_data_1hr = angel_one.historic_data(obj, each_data['token'], fromdate, todate, "1h")
            # historic_data_30m = angel_one.historic_data(obj, each_data['token'], fromdate, todate, "30m")
            historic_data_2hr = angel_one.historic_data_2hr(
                angel_one.historic_data(obj, each_data['token'], fromdate, todate, "1h"))
            call_count += 1

            # closes['1hr'] = [e[4] for e in historic_data_1hr]
            # closes['30m'] = [e[4] for e in historic_data_30m]
            closes['2hr'] = [e[4] for e in historic_data_2hr]

            # ema_50['1hr'] = calculate_ema(closes['1hr'], 50)
            # ema_50['30m'] = calculate_ema(closes['30m'], 50)
            ema_50['2hr'] = calculate_ema(closes['2hr'], 50)

            # ema_200['1hr'] = calculate_ema(closes['1hr'], 200)
            # ema_200['30m'] = calculate_ema(closes['30m'], 200)
            ema_200['2hr'] = calculate_ema(closes['2hr'], 200)

            # rsi_1hr, k1_1hr, d1_1hr = stoch_rsi_tradingview(pd.Series(closes['1hr']))
            # rsi_30m, k1_30m, d1_30m = stoch_rsi_tradingview(pd.Series(closes['30m']))
            rsi_2hr, k1_2hr, d1_2hr = stoch_rsi_tradingview(pd.Series(closes['2hr']))

            # k_values['1hr'] = k1_1hr
            # k_values['30m'] = k1_30m
            k_values['2hr'] = k1_2hr

            check_condition(closes, ema_50, ema_200, k_values, each_data['symbol'], '2hr')
            # check_condition(closes, ema_50, ema_200, k_values, each_data['symbol'], '1hr')
            # check_condition(closes, ema_50, ema_200, k_values, each_data['symbol'], '30m')

            if call_count % 3 == 0:
                t2 = datetime.now()
                if (t2 - t1).microseconds * 0.001 * 0.001 < 1:
                    time.sleep(1 - (t2 - t1).microseconds * 0.001 * 0.001 + 0.1)

        except Exception as e:
            print("Exception for trade {trade} : {e}".format(trade=each_data['symbol'], e=e))


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
            send_message("[1hr] Buy entry found for trade : {trade}".format(trade=symbol))
            return True, 'BUY'
        elif k_value_prev >= 80 and k_value < 80 and ema_1 < ema_2:
            print("{condition_type}  Sell entry found for trade : {trade}".format(condition_type=condition_type,
                                                                                  trade=symbol))
            send_message("[1hr] Sell entry found for trade : {trade}".format(trade=symbol))
            return True, 'SELL'
        else:
            print("NO entry found for trade : {trade}".format(trade=symbol))
            return False, None
    except Exception as e:
        print("Exception for trade {trade} : {e}".format(trade=symbol, e=e))

    return False, None


def check_1hr_condition(closes, ema_50, ema_200, k_values, symbol):
    try:
        k_value_prev_1hr = pd.Series.tolist(k_values['1hr'])[len(pd.Series.tolist(k_values['1hr'])) - 2]
        k_value_1hr = pd.Series.tolist(k_values['1hr'])[len(pd.Series.tolist(k_values['1hr'])) - 1]

        ema_1_1hr = ema_50['1hr'][len(ema_50['1hr']) - 1]
        ema_2_1hr = ema_200['1hr'][len(ema_200['1hr']) - 1]

        closes_1hr = closes['1hr']

        print(("1hr - current close for symbol : {symbol} is {value}".format(symbol=symbol,
                                                                             value=closes_1hr[len(closes_1hr) - 1])))
        print("1hr - ema 50 for symbol : {symbol} is {value}".format(symbol=symbol, value=ema_1_1hr))
        print("1hr - ema 200 for symbol : {symbol} is {value}".format(symbol=symbol, value=ema_2_1hr))
        print("1hr - k value for symbol : {symbol} is {value}".format(symbol=symbol, value=k_value_1hr))
        print("1hr - k previous value for symbol : {symbol} is {value}".format(symbol=symbol, value=k_value_prev_1hr))

        if k_value_prev_1hr <= 20 and k_value_1hr > 20 and ema_1_1hr > closes_1hr[len(closes_1hr) - 1] > ema_2_1hr:
            print("[1hr] Strong Buy entry found for trade : {trade}".format(trade=symbol))
            send_message("[1hr] Strong Buy entry found for trade : {trade}".format(trade=symbol))
            return True, 'BUY'
        elif k_value_prev_1hr >= 80 and k_value_1hr < 80 and ema_1_1hr < closes_1hr[
            len(closes_1hr) - 1] < ema_2_1hr:
            print("[1hr] Strong sell entry found for trade : {trade}".format(trade=symbol))
            send_message("[1hr] Strong sell entry found for trade : {trade}".format(trade=symbol))
            return True, 'SELL'
        elif k_value_prev_1hr <= 20 and k_value_1hr > 20 and ema_1_1hr > ema_2_1hr:
            print("[1hr] Buy entry found for trade : {trade}".format(trade=symbol))
            # send_message("[1hr] Buy entry found for trade : {trade}".format(trade=symbol))
            return True, 'BUY'
        elif k_value_prev_1hr >= 80 and k_value_1hr < 80 and ema_1_1hr < ema_2_1hr:
            print("[1hr] Sell entry found for trade : {trade}".format(trade=symbol))
            # send_message("[1hr] Sell entry found for trade : {trade}".format(trade=symbol))
            return True, 'SELL'
        else:
            print("NO entry found for trade : {trade}".format(trade=symbol))
            return False, None
    except Exception as e:
        print("Exception for trade {trade} : {e}".format(trade=symbol, e=e))

    return False, None


def check_30m_condition(closes, ema_50, ema_200, k_values, symbol):
    try:
        k_value_30m = pd.Series.tolist(k_values['30m'])[len(pd.Series.tolist(k_values['30m'])) - 1]

        ema_1_30m = ema_50['30m'][len(ema_50['30m']) - 1]
        ema_2_30m = ema_200['30m'][len(ema_200['30m']) - 1]

        print("30m - ema 50 for symbol : {symbol} is {value}".format(symbol=symbol, value=ema_1_30m))
        print("30m - ema 200 for symbol : {symbol} is {value}".format(symbol=symbol, value=ema_2_30m))
        print("30m - k value for symbol : {symbol} is {value}".format(symbol=symbol, value=k_value_30m))

        if k_value_30m < 30 and ema_1_30m > ema_2_30m:
            return True, 'BUY'
        elif k_value_30m > 80 and ema_1_30m < ema_2_30m:
            return True, 'SELL'
        else:
            return False, None
    except Exception as e:
        print("Exception for trade {trade} : {e}".format(trade=symbol, e=e))

    return False, None


def check_15m_condition(closes, ema_50, ema_200, k_values, symbol):
    try:
        k_value_15m = pd.Series.tolist(k_values['15m'])[len(pd.Series.tolist(k_values['15m'])) - 1]

        ema_1_15m = ema_50['15m'][len(ema_50['15m']) - 1]
        ema_2_15m = ema_200['15m'][len(ema_200['15m']) - 1]

        print("15m - ema 50 for symbol : {symbol} is {value}".format(symbol=symbol, value=ema_1_15m))
        print("15m - ema 200 for symbol : {symbol} is {value}".format(symbol=symbol, value=ema_2_15m))
        print("15m - k value for symbol : {symbol} is {value}".format(symbol=symbol, value=k_value_15m))

        if k_value_15m < 30 and ema_1_15m > ema_2_15m:
            return True, 'BUY'
        elif k_value_15m > 80 and ema_1_15m < ema_2_15m:
            return True, 'SELL'
        else:
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
