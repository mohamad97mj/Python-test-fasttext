import logging


class Logger:
    logging.basicConfig(level=logging.INFO)

    @staticmethod
    def info(message):
        logging.info(message)

    @staticmethod
    def warn(message):
        logging.warning(message)
