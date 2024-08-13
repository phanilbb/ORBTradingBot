import report


def lambda_handler(event, context):
    rep = report.Report()
    rep.update(event)
