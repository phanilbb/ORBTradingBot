from datetime import datetime, time
from datetime import timedelta


def get_current_date():
    return datetime.today().strftime('%Y-%m-%d')


def is_within_days(target_date_str, delta):
    current_date = datetime.now().date()
    target_date = datetime.strptime(target_date_str, '%Y-%m-%dT%H:%M:%S').date()
    days_from_now = current_date + timedelta(days=delta)
    return days_from_now <= current_date <= target_date


def is_before_current_time(target_date_str):
    current_date = datetime.now().date()
    target_date = datetime.strptime(target_date_str, '%Y-%m-%dT%H:%M:%S').date()
    return target_date < current_date


def is_algotest_strategy_activation_time():
    current_time = datetime.now().time()
    target_time = time(8, 45)
    return current_time >= target_time


def get_current_day():
    return datetime.now().strftime('%A').lower()
