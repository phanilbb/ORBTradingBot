from datetime import datetime
import time
from collections import deque

historic_api_rate_limit = 3
historic_api_rate_limit_times = []

request_times = deque(maxlen=3)


def historic_rate_limit_checker():
    current_time = time.time()
    if len(request_times) == 3 and current_time - request_times[0] < 1:
        # Calculate the time to sleep to meet the rate limit (3 requests per second)
        time_to_sleep = 1 - (current_time - request_times[0])
        time.sleep(time_to_sleep)

    request_times.append(current_time)


def wait_time(t2, t1):
    if (t2 - t1).microseconds * 0.001 * 0.001 < 1:
        time.sleep(1 - (t2 - t1).microseconds * 0.001 * 0.001)
        global historic_api_rate_limit_times
        historic_api_rate_limit_times = []

    return
