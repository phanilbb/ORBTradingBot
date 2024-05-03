from AlgoTestReport import lambda_function

if __name__ == '__main__':
    event = {
        "angel_one_login_details": {
            "api_key": "2T5UkAjm",
            "secret_key": "4c5f0347-f752-48ab-85b6-c43a6648d110",
            "totp": "JICUAHK6OJMNYDPCR32BDV6SBQ",
            "id": "K636871",
            "pin": "1706"
        }
    }
    lambda_function.lambda_handler(event, None)
