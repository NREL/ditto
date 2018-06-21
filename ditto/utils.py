from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import bytes, str, open, super, range, zip, round, input, int, pow

from json import JSONEncoder
import logging
import numpy as np


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
    logging.getLogger().setLevel(log_level)
    logging.getLogger().addHandler(console_handler)


def start_file_log(
    filename,
    log_level=logging.WARN,
    log_format="%(asctime)s|%(levelname)s|%(name)s|\n    %(message)s",
):
    logfile = logging.FileHandler(filename=filename)
    logfile.setLevel(log_level)
    logformat = logging.Formatter(log_format)
    logfile.setFormatter(logformat)
    logging.getLogger().setLevel(log_level)
    logging.getLogger().addHandler(logfile)


def reject_outliers(data, m = 2.):
    """
    This function returns a Numpy array where the outliers were removed as well
    as the indices of the elements to keep and the indices of the elements to remove.
    The estimator used is the median and absolute distance to the median since
    the mean of a distribution tends to be biased by outliers.
    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m], np.argwhere(s<m).flatten(), np.argwhere(s>=m).flatten()
