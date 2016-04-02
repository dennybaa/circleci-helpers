# -*- coding: utf-8 -*-

import logging


class Log(object):  # pylint: disable=too-few-public-methods
    """
    Setup basic console logging.
    """
    logger = None

    class OutputFormatter(logging.Formatter):
        def format(self, record):
            '''Log message formatering method. Messages of all levels except
               INFO are preceeded with header "{levelname}: ".
            '''
            fmt = '{levelname}: ' if record.levelno != logging.INFO else ''
            fmt = fmt + '{msg}'
            msg = fmt.format(**vars(record))
            return msg % record.args

    @staticmethod
    def console_logger(level=logging.ERROR, name=__name__):
        if Log.logger is not None:
            return Log.logger

        _logger = logging.getLogger(name)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = Log.OutputFormatter('%(levelname)s: %(message)s')
        console.setFormatter(formatter)
        _logger.addHandler(console)
        # set logger level
        _logger.setLevel(level)
        Log.logger = _logger
        return Log.logger
