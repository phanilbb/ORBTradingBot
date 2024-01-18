import trade_executions
import dynamo_db
import errors


def run(account, result):
    try:
        db_data = dynamo_db.get(account['name'])
        login_data = db_data['login_details']

        executions = trade_executions.get_all(login_data)

        for execution in executions:
            if 'error' in execution['status'].lower():
                raise errors.CustomError("Error in Execution : {}".format(execution['name']))

        print("All strategies working fine")
        return True
    except Exception as e:
        result['notify'] = True
        result['success'] = False
        result['error'] = str(e)
        return False
