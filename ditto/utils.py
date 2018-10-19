from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import bytes, str, open, super, range, zip, round, input, int, pow

from json import JSONEncoder
import logging


class DittoEncoder(JSONEncoder):

    def default(self, obj):
        return {k: getattr(obj, k) for k in obj._attrs}


def combine(*dicts):
    """Given multiple dicts, merge them into a new dict as a shallow copy."""
    super_dict = {key: val for d in dicts for key, val in d.items()}
    return super_dict


def start_console_log(
    log_level=logging.WARN,
    log_format="%(asctime)s|%(levelname)s|%(name)s|\n    %(message)s",
):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    logformat = logging.Formatter(log_format)
    console_handler.setFormatter(logformat)
    logging.getLogger("ditto").setLevel(log_level)
    logging.getLogger("ditto").addHandler(console_handler)


def start_file_log(
    filename,
    log_level=logging.WARN,
    log_format="%(asctime)s|%(levelname)s|%(name)s|\n    %(message)s",
):
    file_handler = logging.FileHandler(filename=filename)
    file_handler.setLevel(log_level)
    logformat = logging.Formatter(log_format)
    file_handler.setFormatter(logformat)
    logging.getLogger("ditto").setLevel(log_level)
    logging.getLogger("ditto").addHandler(file_handler)
