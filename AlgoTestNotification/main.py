from AlgoTestNotification import lambda_function

if __name__ == '__main__':
    event = {
        "algo_test_login": {
            "phone_number": "7013376537",
            "password": "jVChDH5zMg2@h3"
        }
    }
    lambda_function.lambda_handler(event, None)
