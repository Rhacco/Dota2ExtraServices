import datetime
import logging
import re

logs = 'logs_' + str(datetime.date.today())
logging.basicConfig(format='%(message)s', filename=logs, level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def log(message):
    now = datetime.datetime.now().strftime('%d/%b/%Y %H:%M:%S')
    logging.info('[%s] %s' % (now, message))


def list_to_string(string_list, separator):
    string = ''
    for entry in string_list:
        if entry and entry != 'Hidden':  # entries are null/hidden sometimes
            string += entry + separator
    return string[:len(string) - len(separator)]


def make_camel_case(string):
    return re.sub(r'\w+', lambda m: m.group(0).capitalize(), string)
