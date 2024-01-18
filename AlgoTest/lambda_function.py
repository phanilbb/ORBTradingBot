import login
import angel_one_login
import activate_strategy
import communication
import json
import boto3
import event_bridge
import time_helper
import recharge
import execution_checker

ssm = boto3.client('ssm')


def get_input_payload():
    response = ssm.get_parameter(Name='algo_test_input', WithDecryption=False)
    return json.loads(response['Parameter']['Value'])


def lambda_handler(event, context):
    if not time_helper.is_algotest_strategy_activation_time():
        print("Not in strategy activation time")
        return

    if not event:
        input_data = get_input_payload()
    else:
        input_data = event

    accounts = input_data.get('accounts', [])

    for each_account in accounts:
        result = {
            'success': True,
            'error': None,
            'notify': True
        }
        for process in [login.run, recharge.run, angel_one_login.run, activate_strategy.run, execution_checker.run]:
            if result['success']:
                process(each_account, result)

        if result['success'] and result['notify']:
            communication.telegram_bot_sendtext("{} - AlgoTest Successful".format(each_account['name']))
        elif not result['success']:
            communication.telegram_bot_sendtext(
                "{} - AlgoTest Failed : {}".format(each_account['name'], result['error']))


if __name__ == '__main__':
    lambda_handler(None, None)
