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
    current_time = time_helper.get_current_time_with_delta(-5)
    fromdate = time_helper.get_date_with_delta(-15) + " 09:15"
    todate = time_helper.get_date_with_delta(0) + " " + current_time

    print("Drom date : {date}".format(date=fromdate))
    print("To date : {date}".format(date=todate))

    obj = angel_one.get_session()
    f = open("trades.json")
    data = json.load(f)

    for each_data in data:

        # if each_data['symbol'] != 'ZEEL-EQ':
        #     continue

        try:
            print("________________________________________")
            print("check for trade : " + each_data['symbol'])

            historic_data = angel_one.historic_data(obj, each_data['token'], fromdate, todate, "30m")
            closes = [e[4] for e in historic_data]
            ema_50 = calculate_ema(closes, 50)
            ema_200 = calculate_ema(closes, 200)
            rsi, k1, d1 = stoch_rsi_tradingview(pd.Series(closes))
            k_value = pd.Series.tolist(k1)[len(pd.Series.tolist(k1)) - 1]
            k_value_prev = pd.Series.tolist(k1)[len(pd.Series.tolist(k1)) - 2]

            ema_1 = ema_50[len(ema_50) - 1]
            ema_2 = ema_200[len(ema_200) - 1]
            print("EMA 50 for trade {trade} is {value}".format(trade=each_data['symbol'], value=ema_1))
            print("EMA 200 for trade {trade} is {value}".format(trade=each_data['symbol'], value=ema_2))
            print("Stochastic K value for trade {trade} is {value}".format(trade=each_data['symbol'], value=k_value))
            print("Stochastic K prev value for trade {trade} is {value}".format(trade=each_data['symbol'],
                                                                                value=k_value_prev))
            print("Last data : " + str(historic_data[len(historic_data) - 1]))

            if k_value_prev <= 20 and k_value > 20 and ema_1 > closes[len(closes) - 1] > ema_2:
                print("Strong Buy entry found for trade : {trade}".format(trade=each_data['symbol']))
                send_message("Strong Buy entry found for trade : {trade}".format(trade=each_data['symbol']))
            elif k_value_prev >= 80 and k_value < 80 and ema_1 < closes[len(closes) - 1] < ema_2:
                print("Strong sell entry found for trade : {trade}".format(trade=each_data['symbol']))
                send_message("Strong sell entry found for trade : {trade}".format(trade=each_data['symbol']))
            elif k_value_prev <= 20 and k_value > 20 and ema_1 > ema_2:
                print("Buy entry found for trade : {trade}".format(trade=each_data['symbol']))
                send_message("Buy entry found for trade : {trade}".format(trade=each_data['symbol']))
            elif k_value_prev >= 80 and k_value < 80 and ema_1 < ema_2:
                print("Sell entry found for trade : {trade}".format(trade=each_data['symbol']))
                send_message("Sell entry found for trade : {trade}".format(trade=each_data['symbol']))
            else:
                print("NO entry found for trade : {trade}".format(trade=each_data['symbol']))
        except Exception as e:
            print("Exception for trade {trade} : {e}".format(trade=each_data['symbol'], e=e))

        time.sleep(0.35)


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
