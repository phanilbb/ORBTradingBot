import login
import angel_one_login
import activate_strategy
import communication


def lambda_handler(event, context):
    accounts = event.get('accounts', [])

    for each_account in accounts:
        executions = each_account['executions']
        result = {
            'success': True,
            'error': None
        }
        if 'algo_test_login' in executions and result['success']:
            login.run(each_account, result)
        if 'broker_login' in executions and result['success']:
            angel_one_login.run(each_account, result)
        if 'strategies' in executions and result['success']:
            activate_strategy.run(each_account, result)

        if result['success']:
            communication.telegram_bot_sendtext("{} - AlgoTest Successful".format(each_account['name']))
        else:
            communication.telegram_bot_sendtext(
                "{} - AlgoTest Failed : {}".format(each_account['name'], result['error']))
