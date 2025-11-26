import time_helper
import dynamo_db
from communication import Communication
import requests


def lambda_handler(event, context):
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
            'Cookie': '_gcl_gs=2.1.k1^$i1762848639^$u240607896; _ga=GA1.1.1386895223.1762848643; _fbp=fb.1.1762848642810.97527204674530980; _scid=EjCKb4_9HKopL_63qzz5ZtJFRuENIvYA; _gcl_aw=GCL.1762848643.CjwKCAiA2svIBhB-EiwARWDPjlmMhWvhCM7_3eFHpLBEy3tYLQWncW-shQVJQc5uSvPr1dkfP0tEHxoCf58QAvD_BwE; _gcl_au=1.1.1086388903.1762848643; _hjSessionUser_3608805=eyJpZCI6IjAyMTYzMWFmLTM4M2ItNWE1MC1hNWI4LTkxNDdhYzhjZjBiMyIsImNyZWF0ZWQiOjE3NjI4NDg2NDI2NTMsImV4aXN0aW5nIjp0cnVlfQ==; _ScCbts=%5B%5D; _sctr=1%7C1763663400000; csrftoken=095sfsjTX8z1z44oAfVYI5qwT69iDKH3S6a7HyDqYptHBf3Ps5fzCmdP5GoRjUvF; csrftoken=QJyL7UlfCWNwmLuaPQ6gziiTQ0Pn2TTi; sessionid=m04qsc50firn5lipkohrzfgqzl9o16hk; _clck=b4cwju%5E2%5Eg1c%5E0%5E2141; _uetsid=5b0219c0c9fc11f09df1575d397d8283; _uetvid=e9f6aa60bed511f0a9b169dae9e1ccaa; _scid_r=JbCKb4_9HKopL_63qzz5ZtJFRuENIvYAZiQGrw; _clsk=1sdjgxk%5E1764138578951%5E2%5E1%5Ez.clarity.ms%2Fcollect; _ga_38WMG8VNT4=GS2.1.s1764138574^$o9^$g1^$t1764138589^$j45^$l0^$h0'
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
        comm = Communication()
        comm.send_telegram_msg("{} upcoming pending tasks".format(len(tasks_to_notify)))
