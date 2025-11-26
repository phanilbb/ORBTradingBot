import requests

import dynamo_db
import time_helper
from communication import Communication


def lambda_handler(event, context):
    comm = Communication()
    session_id = comm.get_today_session_id()
    if not session_id:
        print("Session ID not found for today")
        return

    current_date = time_helper.get_current_date()
    page_size = 20
    tasks = []
    for page in range(1, 4):
        url = "https://api-bliss.joinditto.in/crm/tasks?page={}&page_size={}&sort_by=due_date&reverse=false&extra_fields=lead_phone_num&due_after={}&due_before={}".format(
            page, page_size, current_date, current_date)

        payload = {}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,te;q=0.6',
            'Connection': 'keep-alive',
            'Origin': 'https://falcon.joinditto.in',
            'Referer': 'https://falcon.joinditto.in/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': 'sessionid={}'.format(session_id)
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            break
        response = response.json()
        tasks.extend(response['data']['tasks'])
        if page_size * page > response['data']['count']:
            break

    new_pending_tasks = []
    upcoming_tasks = []

    for each_task in tasks:
        if each_task['status'] != 'PENDING':
            continue

        if time_helper.compare_time(each_task['start_time']):
            upcoming_tasks.append(each_task)
            continue

        task_id = each_task['task_id']
        saved_tasks = dynamo_db.get(task_id)
        if not saved_tasks:
            new_pending_tasks.append(each_task)
            dynamo_db.save(task_id)

    if upcoming_tasks:
        comm.send_telegram_msg("You have a call to attend in 5 minutes")
    if new_pending_tasks:
        comm.send_telegram_msg("You have {} upcoming new pending tasks".format(len(new_pending_tasks)))

    comm.delete_old_messages()
