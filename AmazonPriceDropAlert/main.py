from AmazonPriceDropAlert import lambda_function

if __name__ == '__main__':
    event = None
    lambda_function.lambda_handler(event, None)
