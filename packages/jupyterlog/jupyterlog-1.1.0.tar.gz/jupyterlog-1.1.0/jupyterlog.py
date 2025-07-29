import logging
from logging import Formatter, Handler, StreamHandler
import sys
import time


def is_running_in_jupyter():
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass

    if any('ipykernel' in arg for arg in sys.argv):
        return True
    return False


LEVEL_COLORS = {
    'DEBUG': 'gray',
    'INFO': 'blue',
    'WARNING': 'orange',
    'ERROR': 'red',
    'CRITICAL': 'darkred'
}

LEVEL_COLOR_CODES = {
    'NOSET': "\033[00m",
    'DEBUG': "\033[97m",
    'INFO': "\033[96m",
    'WARNING': "\033[93m",
    'ERROR': "\033[91m",
    'CRITICAL': "\033[95m",
}


class TimeoffsetFormatter(Formatter):
    """TimeoffsetFormatter

    See also:
        https://docs.python.org/3/library/logging.html#logging.Formatter
    """
    def __init__(self, *args, datetime=None, **kwargs):
        super().__init__(*args, **kwargs)
        if datetime:
            self.timeoffset = datetime.timestamp() - time.time()
        else:
            self.timeoffset = 0

    def formatTime(self, record, datefmt=None):
        """formatTime

        See also:
            https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime
        """
        timestamp = record.created + self.timeoffset
        ct = self.converter(timestamp)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s

    def format(self, record):
        """format

        See also:
            https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """
        formatted_time = self.formatTime(record, self.datefmt)
        message = record.getMessage()
        default_color_code = LEVEL_COLOR_CODES["NOSET"]
        color_code = LEVEL_COLOR_CODES.get(record.levelname, default_color_code)
        s = f"""{color_code}{formatted_time} [{record.levelname}] {default_color_code}{message}"""
        return s


class TimeoffsetHTMLFormatter(TimeoffsetFormatter):
    def format(self, record):
        """format

        See also:
            https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """
        formatted_time = self.formatTime(record, self.datefmt)
        level_color = LEVEL_COLORS.get(record.levelname, 'black')
        message = record.getMessage()
        html = f"""
            <div style="font-family: monospace; line-height: 1; background-color: white;">
                <span style="color: {level_color};">{formatted_time} [{record.levelname}]</span>
                <span>{message}</span>
            </div>"""
        return html


class HTMLHandler(Handler):
    """HTMLHandler

    See also:
        https://docs.python.org/3/library/logging.html#logging.Handler
    """
    def emit(self, record):
        """emit

        See also:
            https://docs.python.org/3/library/logging.html#logging.Handler.emit
        """
        from IPython.display import display, HTML

        html_output = self.format(record)
        display(HTML(html_output))


def config(level=None, **kwargs):
    """Concise configuration.

    Parameters:
        level (int, Optional):
        datetime (datetime.datetime, Optional): Overwrite current datetime of logging.
        **kwargs (dict, Optional): keyword arguments for Formatter, including fmt, datefmt, style, validate, defaults.

    Examples:
        >>> import datetime
        >>> import logging
        >>> jupyterlog.config(level=logging.DEBUG, datefmt="%H:%M:%S", datetime=datetime.datetime(2000, 1, 1))
    """
    logger = logging.getLogger()
    if level:
        logger.setLevel(level)

    logger.handlers.clear()
    if is_running_in_jupyter():
        formatter = TimeoffsetHTMLFormatter(**kwargs)
        handler = HTMLHandler()
        handler.setFormatter(formatter)
    else:
        formatter = TimeoffsetFormatter(**kwargs)
        handler = StreamHandler()
        handler.setFormatter(formatter)
    logger.addHandler(handler)
