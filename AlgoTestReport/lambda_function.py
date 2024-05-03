import angel_one
import report


def lambda_handler(event, context):
    angelOneObj = angel_one.AngelOne(event['angel_one_login_details'])
    pos = angelOneObj.get_positions()
    rep = report.Report()
    rep.generate_report(pos)
