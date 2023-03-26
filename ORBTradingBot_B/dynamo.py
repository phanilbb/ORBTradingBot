import time_helper

DYNAMO_SUFFIX = "#B"


def get_dynamo_pk():
    return str(time_helper.get_current_date()) + DYNAMO_SUFFIX


def get_dynamo_sk():
    return str(time_helper.get_current_date()) + DYNAMO_SUFFIX
