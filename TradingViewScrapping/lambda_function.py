import json
import time

import requests
import time_helper
import angel_one
import numpy as np
import pandas as pd


def send_message(bot_message):
    bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
    bot_chatID = '1170124746'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def lambda_handler(event, context):
    obj = angel_one.create_session()
    current_time = time_helper.get_current_time_with_delta(-5)
    fromdate = time_helper.get_date_with_delta(-15) + " 09:15"
    todate = time_helper.get_date_with_delta(0) + " " + current_time

    f = open("trades.json")
    data = json.load(f)

    for each_data in data:

        # if each_data['symbol'] != 'IRCTC-EQ':
        #     continue

        try:
            print("check for trade : " + each_data['symbol'])

            historic_data = angel_one.historic_data(obj, each_data['token'], fromdate, todate, "30m")
            closes = [e[4] for e in historic_data]
            ema_50 = calculate_ema(closes, 50)
            ema_200 = calculate_ema(closes, 200)
            rsi, k1, d1 = StochRSI(pd.Series(closes))
            k_value = pd.Series.tolist(k1)[len(pd.Series.tolist(k1)) - 1] * 100
            k_value_prev = pd.Series.tolist(k1)[len(pd.Series.tolist(k1)) - 2] * 100

            ema_1 = ema_50[len(ema_50) - 1]
            ema_2 = ema_200[len(ema_200) - 1]
            print(
                "EMA 50 for trade {trade} is {value}".format(trade=each_data['symbol'], value=ema_1))
            print("EMA 200 for trade {trade} is {value}".format(trade=each_data['symbol'], value=ema_2))
            print("Stochastic K value for trade {trade} is {value}".format(trade=each_data['symbol'], value=k_value))
            print("Stochastic K prev value for trade {trade} is {value}".format(trade=each_data['symbol'],
                                                                                value=k_value_prev))
            print("Last data : " + str(historic_data[len(historic_data) - 1]))

            if k_value_prev <= 20 and k_value > 20 and ema_1 < closes[len(closes) - 1] < ema_2:
                print("Buy entry found for trade : {trade}".format(trade=each_data['symbol']))
                send_message("Buy entry found for trade : {trade}".format(trade=each_data['symbol']))
            elif k_value_prev >= 80 and k_value < 80 and ema_1 > closes[len(closes) - 1] > ema_2:
                print("sell entry found for trade : {trade}".format(trade=each_data['symbol']))
                send_message("sell entry found for trade : {trade}".format(trade=each_data['symbol']))
            else:
                print("NO entry found for trade : {trade}".format(trade=each_data['symbol']))
        except Exception as e:
            print("Exception for trade {trade} : {e}".format(trade=each_data['symbol'], e=e))

        time.sleep(0.5)


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


def RSI(series, period=14):
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period - 1]] = np.mean(ups[:period])  # first value is sum of avg gains
    ups = ups.drop(ups.index[:(period - 1)])
    downs[downs.index[period - 1]] = np.mean(downs[:period])  # first value is sum of avg losses
    downs = downs.drop(downs.index[:(period - 1)])
    rs = ups.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         downs.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    return 100 - 100 / (1 + rs)


# calculating Stoch RSI (gives the same values as TradingView)
# https://www.tradingview.com/wiki/Stochastic_RSI_(STOCH_RSI)
def StochRSI(series, period=14, smoothK=3, smoothD=3):
    # Calculate RSI
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period - 1]] = np.mean(ups[:period])  # first value is sum of avg gains
    ups = ups.drop(ups.index[:(period - 1)])
    downs[downs.index[period - 1]] = np.mean(downs[:period])  # first value is sum of avg losses
    downs = downs.drop(downs.index[:(period - 1)])
    rs = ups.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         downs.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI
    stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.rolling(smoothK).mean()
    stochrsi_D = stochrsi_K.rolling(smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D


# calculating Stoch RSI
#  -- Same as the above function but uses EMA, not SMA
def StochRSI_EMA(series, period=14, smoothK=3, smoothD=3):
    # Calculate RSI
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period - 1]] = np.mean(ups[:period])  # first value is sum of avg gains
    ups = ups.drop(ups.index[:(period - 1)])
    downs[downs.index[period - 1]] = np.mean(downs[:period])  # first value is sum of avg losses
    downs = downs.drop(downs.index[:(period - 1)])
    rs = ups.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         downs.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI
    stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.ewm(span=smoothK).mean()
    stochrsi_D = stochrsi_K.ewm(span=smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D
