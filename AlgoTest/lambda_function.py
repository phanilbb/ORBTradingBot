import login
import angel_one_login
import activate_strategy
import communication


def lambda_handler(event, context):
    accounts = event.get('accounts', [])

    for each_account in accounts:
        executions = each_account['executions']
        success = True
        if 'algo_test_login' in executions and success:
            success = login.run(each_account)
        if 'broker_login' in executions and success:
            success = angel_one_login.run(each_account)
        if 'strategies' in executions and success:
            success = activate_strategy.run(each_account)

        if success:
            communication.telegram_bot_sendtext("{} - AlgoTest Successful".format(each_account['name']))
