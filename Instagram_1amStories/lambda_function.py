import upload
from datetime import datetime, time, timedelta

reels_time = [1, 13]


def lambda_handler(event, context):
    if time_checker():
        upload.new_reel()
    else:
        upload.new_post()


def time_checker():
    current_time = datetime.now().time()

    for reel_time in reels_time:
        actual_time = time(reel_time, 0, 0)
        time_range = timedelta(minutes=60)
        start_time = (datetime.combine(datetime.today(), actual_time) - time_range).time()
        end_time = (datetime.combine(datetime.today(), actual_time) + time_range).time()
        if start_time <= current_time <= end_time:
            return True

    return False
