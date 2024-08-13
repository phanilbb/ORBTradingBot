import report
from communication import Communication
from s3 import S3
from screenshot import Screenshot
import os
from datetime import datetime


def lambda_handler(event, context):
    rep = report.Report()
    sc = Screenshot(event['algo_test_login'])
    sc.init_login()
    sc.login()
    sc.init_live()
    sc.init_mtm_graph()

    tmp_dir = '/tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    path = '{}.png'.format(str(datetime.now()))
    sc.take_screenshot(path)

    s3_obj = S3()
    s3_obj.upload_file(path)

    caption = rep.get_text_report()
    photo_url = s3_obj.get_public_url(path)
    comm = Communication()
    comm.send_telegram_photo(photo_url, caption)
    s3_obj.delete_file(path)
    os.remove(path)
