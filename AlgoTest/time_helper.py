from datetime import datetime


def get_current_date():
    return datetime.today().strftime('%Y-%m-%d')


def is_before_current_time(target_date_str):
    current_date = datetime.now().date()
    target_date = datetime.strptime(target_date_str, '%Y-%m-%dT%H:%M:%S').date()
    return target_date < current_date
