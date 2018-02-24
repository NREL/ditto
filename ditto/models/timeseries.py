from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import pandas as pd
from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position


class Timeseries(DiTToHasTraits):

    data = Instance(pd.DataFrame, help='''This is the data that is stored in the timeseries object.''', default_value=None)
    data_label = Unicode(
        help='The label assigned to the dataset. This describes what the name should be when it is outputted to through the writers'
        '',
        default_value=None
    )
    interval = Float(
        help=
        '''This is the interval in the default units that the timeseries data is recorded at. E.g. minute data would have an interval of 60 for a unit of seconds''',
        default=None
    )
    data_location = Unicode(help='''The absolute location on disk of the data''', default_value=None)

    data_type = Unicode(help='''This is the python datatype of the timeseries e.g. float, complex etc.''', default_value=None)
    loaded = Int(
        help=
        '''A boolean describing whether the data is in memory or on disk. If this is 1, the data is loaded into the data field. Otherwise it is not in memory and is on disk at data_location''',
        default=None
    )

    scale_factor = Float(help='''A number to multiply the entire timeseries by for scaling purposes''', default_value=1)

    def build(self, model):
        self._model = model
