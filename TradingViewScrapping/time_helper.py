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


def get_date_with_delta(delta):
    current_date = get_current_date()
    delta_time = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=delta)

    return delta_time.strftime('%Y-%m-%d')


def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def is_weekend():
    weekday = datetime.today().weekday()
    return weekday == 5 or weekday == 6


def is_within_market_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("09:15:00", "%H:%M:%S")
    end_time = time.strptime("15:30:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()


def is_within_trading_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("09:30:00", "%H:%M:%S")
    end_time = time.strptime("15:14:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()


def is_within_entry_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("09:30:00", "%H:%M:%S")
    end_time = time.strptime("09:34:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()


def is_within_exit_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("15:15:00", "%H:%M:%S")
    end_time = time.strptime("15:17:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()


def entry_script_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("09:27:00", "%H:%M:%S")
    end_time = time.strptime("09:29:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()


def orb_targets_time():
    current_time = time.strptime(get_current_time(), "%H:%M:%S")
    start_time = time.strptime("09:30:00", "%H:%M:%S")
    end_time = time.strptime("09:34:00", "%H:%M:%S")

    return start_time < current_time < end_time and not is_weekend()


def get_current_weekday():
    date = datetime.today()
    return date.weekday()


def nextExpiryDate():
    """
    Returns the date of the next given weekday after
    the given date. For example, the date of next Monday.

    NB: if it IS the day we're looking for, this returns 0.
    consider then doing onDay(foo, day + 1).
    """
    date = datetime.today()
    day = 3  # thrusday
    days = (day - date.weekday() + 7) % 7
    # if not days:
    #     days = 7
    return date + timedelta(days=days)
