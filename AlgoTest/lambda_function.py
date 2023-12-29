import login
import angel_one_login
import activate_strategy
import communication
import json


def lambda_handler(event, context):
    with open('input.json', 'r') as file:
        input_data = json.load(file)
        accounts = input_data.get('accounts', [])

        for each_account in accounts:
            result = {
                'success': True,
                'error': None,
                'notify': True
            }
            for process in [login.run, angel_one_login.run, activate_strategy.run]:
                if result['success']:
                    process(each_account, result)

            if result['success'] and result['notify']:
                communication.telegram_bot_sendtext("{} - AlgoTest Successful".format(each_account['name']))
            elif not result['success']:
                communication.telegram_bot_sendtext(
                    "{} - AlgoTest Failed : {}".format(each_account['name'], result['error']))
