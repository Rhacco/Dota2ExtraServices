import datetime
import logging

logs = 'logs_' + str(datetime.date.today())
logging.basicConfig(format='%(message)s', filename=logs, level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

def log(message):
    now = datetime.datetime.now().strftime('%d/%b/%Y %H:%M:%S')
    logging.info('[%s] %s' % (now, message))
