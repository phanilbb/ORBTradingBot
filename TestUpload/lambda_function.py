import time_helper
import entry_script
import trading_script
import exit_script


def lambda_handler(event, context):
    if not time_helper.is_within_market_time():
        print("------------------ Not in market time ------------------")
        return

    if time_helper.entry_script_time():
        print("------------------ Entry Script Time ------------------")
        entry_script.run()
        print("------------------ Entry Script END ------------------")

    if time_helper.is_within_trading_time():
        print("------------------ Trading Script Time ------------------")
        trading_script.run()

        print("------------------ Trading Script END ------------------")

    if time_helper.is_within_exit_time():
        print("------------------ Exit Script Time ------------------")
        exit_script.run()
        print("------------------ Exit Script END ------------------")
