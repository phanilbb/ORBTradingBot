import algotest
import time_helper
import communication


def lambda_handler(event, context):
    algo = algotest.AlgoTest()
    algo.login_algo_test(event)
    comm = communication.Communication()

    plan_data = algo.get_renew_plans()
    expiration = plan_data.get('expiration') or algo.get_plans().get('expiration')

    if not expiration or time_helper.is_within_days(expiration, -2):
        print("Plan Expired | Subscribing to plans")
        subscribe_plans = algo.subscribe_plans()
        if subscribe_plans:
            comm.send_telegram_msg("Plan Recharge Successful")
        else:
            comm.send_telegram_msg("Plan Recharge Failed")
    else:
        comm.send_telegram_msg("Active plan found")
