import json

policynos = [
    "ALFTP20240000720"
]

url = "https://sureos-policy-service.internal.ackolife.com/policy-service/v1/policies?policyNumber={policy_number}"

repsonse = []

headers = {
    'directory-location': "/acko/life",
    'content-type': "application/json"
}

import requests

for each_policy_no in policynos:
    formedUrl = url.format(policy_number=each_policy_no)
    res = requests.get(formedUrl, headers=headers)
    if res.status_code == 200:
        for each_r in res.json():
            repsonse.append(each_r)

data = []
for each_res in repsonse:

    ppid = []
    for each_plan in each_res['plans']:
        ppid.append(each_plan['proposal_plan_id'])

    data.append({
        'proposal_id': each_res['proposal_id'],
        'policy_id': each_res['header']['policy_id'],
        'policy_number': each_res['header']['policy_number'],
        'proposal_plan_ids': ppid
    })

result = {}
for each_data in data:
    if result.get(each_data['proposal_id']):
        policies = result[each_data['proposal_id']]['policies']
        policies.append({
            'proposal_plan_ids': each_data['proposal_plan_ids'],
            'policy_number': each_data['policy_number'],
            'policy_id': each_data['policy_id']
        })

    else:
        result[each_data['proposal_id']] = {}
        result[each_data['proposal_id']]['policies'] = []
        result[each_data['proposal_id']]['proposal_id'] = each_data['proposal_id']
        result[each_data['proposal_id']]['policies'].append({
            'proposal_plan_ids': each_data['proposal_plan_ids'],
            'policy_number': each_data['policy_number'],
            'policy_id': each_data['policy_id']
        })

final_result = []

for value in result.values():
    final_result.append(value)

print(json.dumps(final_result))
