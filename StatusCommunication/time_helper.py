from datetime import datetime
import time
from datetime import timedelta


def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def get_current_time2():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return current_time


def get_current_time_with_delta(delta):
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    delta_time = datetime.strptime(current_time, "%H:%M") + timedelta(minutes=delta)

    return delta_time.strftime("%H:%M")


def get_current_date():
    return datetime.today().strftime('%Y-%m-%d')


def is_weekend():
    weekday = datetime.today().weekday()
    return weekday == 5 or weekday == 6


def report_generation_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("15:30:00", "%H:%M:%S")
    end_time = time.strptime("15:38:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()

