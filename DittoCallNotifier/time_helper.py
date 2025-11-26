from datetime import datetime, timedelta


def get_current_date():
    return datetime.today().strftime('%Y-%m-%d')


def compare_time(t, mins=5):
    event_time = datetime.fromisoformat(t)
    now = datetime.now(event_time.tzinfo)
    if event_time - now < timedelta(minutes=mins) and event_time - now > timedelta(minutes=0):
        return True

    return False
