from datetime import datetime
import logging
import time


class HTMLFormatter(logging.Formatter):
    """HTMLFormatter

    See also:
        https://docs.python.org/3/library/logging.html#logging.Formatter
    """
    LEVEL_COLORS = {
        'DEBUG': 'gray',
        'INFO': 'blue',
        'WARNING': 'orange',
        'ERROR': 'red',
        'CRITICAL': 'darkred'
    }

    def __init__(self, *args, datetime=None, datefmt=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.datefmt = datefmt or "%H:%M:%S"
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
        formattedTime = datetime.fromtimestamp(timestamp).strftime(datefmt or self.datefmt)
        return formattedTime

    def format(self, record):
        """format

        See also:
            https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """
        time_str = self.formatTime(record)
        level_color = self.LEVEL_COLORS.get(record.levelname, 'black')
        html = f"""
        <div style="font-family: monospace; line-height: 1">
            <span style="color: gray;">{time_str}</span>
            <span style="color: {level_color}; font-weight: bold;">[{record.levelname}]</span>
            <span>{record.getMessage()}</span>
        </div>"""
        return html


class LogHandler(logging.Handler):
    """LogHandler

    See also:
        https://docs.python.org/3/library/logging.html#logging.Handler
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.setFormatter(HTMLFormatter(**kwargs))

    def emit(self, record):
        """emit

        See also:
            https://docs.python.org/3/library/logging.html#logging.Handler.emit
        """
        from IPython.display import display, HTML

        html_output = self.format(record)
        display(HTML(html_output))


def setup(level=None, datetime=None, datefmt=None, **kwargs):
    """setup

    Parameters:
        level (int, Optional):
        datetime (datetime.datetime, Optional): Overwrite current datetime of logging.
        datefmt (str, Optional):
        **kwargs (dict, Optional):
    """
    logger = logging.getLogger()
    if level:
        logger.setLevel(level)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    handler = LogHandler(datetime=datetime, datefmt=datefmt, **kwargs)
    logger.addHandler(handler)
