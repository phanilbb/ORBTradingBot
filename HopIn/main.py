from HopIn import lambda_function

if __name__ == '__main__':
    event = {
        'report': 'daily'
    }
    lambda_function.lambda_handler(event, None)
