from HopIn import swiggy_report
from HopIn import hop_in_report


def lambda_handler(event, context):
    hop_in_report.run(event)
    # swiggy_report.run()
