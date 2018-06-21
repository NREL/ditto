from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe

from .position import Position


class LoadLayer(DiTToHasTraits):

    name = Unicode(help="""Name of the load object""")
    interval = Integer(
        help="""The time resolution (in seconds) for the measured data"""
    )
    current = Any(help="""The input data for the ZIP current measurements""")
    impedance = Any(help="""The input data for the ZIP imedance measurements""")
    power = Any(help="""The input data for the ZIP power measurements""")
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the load data. The positions are objects containing elements of long, lat and elevation (See Position object documentation).""",
    )

    def build(self, model):
        self._model = model
