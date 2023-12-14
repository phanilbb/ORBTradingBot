import upload_reel
import upload_post
import upload_corousal
from datetime import datetime, time, timedelta

reels_time = [12]

carousel_time = [13]


def lambda_handler(event, context):
    if time_checker(reels_time):
        upload_reel.new_reel()
    elif time_checker(carousel_time):
        upload_corousal.new_carousel()
    else:
        upload_post.new_post()


def time_checker(time_checker):
    current_time = datetime.now().time()

    for reel_time in time_checker:
        actual_time = time(reel_time, 0, 0)
        time_range = timedelta(minutes=60)
        start_time = (datetime.combine(datetime.today(), actual_time) - time_range).time()
        end_time = (datetime.combine(datetime.today(), actual_time) + time_range).time()
        if start_time <= current_time <= end_time:
            return True

    return False
