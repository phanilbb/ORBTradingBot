import time_helper
import dynamo_db
from communication import Communication
import requests


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

    tasks_to_notify = []
    for each_task in tasks:
        if each_task['status'] != 'PENDING':
            continue
        task_id = each_task['task_id']
        saved_tasks = dynamo_db.get(task_id)
        if not saved_tasks:
            tasks_to_notify.append(each_task)
            dynamo_db.save(task_id)

    if tasks_to_notify:
        comm.send_telegram_msg("{} upcoming pending tasks".format(len(tasks_to_notify)))

    comm.delete_old_messages()
