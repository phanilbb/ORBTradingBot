import angel_one
import report


def lambda_handler(event, context):
    rep = report.Report()
    rep.generate_report(event)
