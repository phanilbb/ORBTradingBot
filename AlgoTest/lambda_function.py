import login
import angel_one_login
import activate_strategy


def lambda_handler(event, context):
    accounts = event.get('accounts', [])

    for each_account in accounts:
        executions = each_account['executions']
        if 'algo_test_login' in executions:
            login.run(each_account)
        if 'broker_login' in executions:
            angel_one_login.run(each_account)
        if 'strategies' in executions:
            activate_strategy.run(each_account)
