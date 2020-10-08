import logging


def set_log_conf():
    logging.basicConfig(filename='scanner.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


def log_debug(message):
    logging.debug(message)


# Method to reset the log file
def log_reset():
    with open('scanner.log', 'w')as file:
        file.write('')
set_log_conf()
