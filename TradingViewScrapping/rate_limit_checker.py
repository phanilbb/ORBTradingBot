from datetime import datetime
import time

historic_api_rate_limit = 3
historic_api_rate_limit_times = []


def historic_rate_limit_checker():
    if len(historic_api_rate_limit_times) < historic_api_rate_limit:
        historic_api_rate_limit_times.append(datetime.now())
        return

    wait_time(max(historic_api_rate_limit_times), min(historic_api_rate_limit_times))
    if historic_api_rate_limit_times:
        historic_api_rate_limit_times.remove(min(historic_api_rate_limit_times))
    historic_api_rate_limit_times.append(datetime.now())


def wait_time(t2, t1):
    if (t2 - t1).microseconds * 0.001 * 0.001 < 1:
        time.sleep(1 - (t2 - t1).microseconds * 0.001 * 0.001 + 0.1)
        global historic_api_rate_limit_times
        historic_api_rate_limit_times = []

    return


def print_times():
    print("times : " + str(historic_rate_limit_checker()))
