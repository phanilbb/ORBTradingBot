from AlgoTestSubscription import lambda_function

if __name__ == '__main__':
    event = {
        "phone_number": "+917013376537",
        "password": "jVChDH5zMg2@h3"
    }
    lambda_function.lambda_handler(event, None)
