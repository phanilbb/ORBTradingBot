from datetime import datetime, time


def get_current_date():
    return datetime.today().strftime('%Y-%m-%d')
