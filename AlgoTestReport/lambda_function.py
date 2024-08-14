import report
from communication import Communication


def lambda_handler(event, context):
    rep = report.Report()
    rep.update(event)
    message = rep.get_text_report()
    comm = Communication()
    comm.send_telegram_msg(message)
