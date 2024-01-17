import login
import angel_one_login
import activate_strategy
import communication
import json
import boto3
import event_bridge
import recharge

ssm = boto3.client('ssm')


def get_input_payload():
    response = ssm.get_parameter(Name='algo_test_input', WithDecryption=False)
    return json.loads(response['Parameter']['Value'])


def lambda_handler(event, context):
    input_data = get_input_payload()
    accounts = input_data.get('accounts', [])

    combined_result = {
        'disable_rules': True
    }

    for each_account in accounts:
        result = {
            'success': True,
            'error': None,
            'notify': True
        }
        for process in [login.run, recharge.run, angel_one_login.run, activate_strategy.run]:
            if result['success']:
                process(each_account, result, combined_result)

        if result['success'] and result['notify']:
            communication.telegram_bot_sendtext("{} - AlgoTest Successful".format(each_account['name']))
        elif not result['success']:
            communication.telegram_bot_sendtext(
                "{} - AlgoTest Failed : {}".format(each_account['name'], result['error']))

    event_bridge.start_second_eventbridge_rule()

    if combined_result['disable_rules']:
        event_bridge.stop_second_eventbridge_rule()


if __name__ == '__main__':
    lambda_handler(None, None)
