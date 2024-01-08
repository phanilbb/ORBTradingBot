import boto3

SECOND_RULE = 'run_every_3_min_market_time'


def start_second_eventbridge_rule():
    client = boto3.client('events')
    response = client.describe_rule(Name=SECOND_RULE)
    if response['State'] == 'DISABLED':
        print("Enabling rule {}".format(SECOND_RULE))
        client.enable_rule(Name=SECOND_RULE)


def stop_second_eventbridge_rule():
    client = boto3.client('events')
    print("Disabling rule {}".format(SECOND_RULE))
    client.disable_rule(Name=SECOND_RULE)
