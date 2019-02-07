from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe

from .position import Position

from ..constant import S, A, OHM, W


class LoadLayer(DiTToHasTraits):

    name = Unicode(help="""Name of the load object""", unit=None)
    interval = Integer(
        help="""The time resolution (in seconds) for the measured data""", unit=S
    )
    current = Any(
        help="""The input data for the ZIP current measurements""", unit=A
    )  # TODO: Check that
    impedance = Any(
        help="""The input data for the ZIP imedance measurements""", unit=OHM
    )
    power = Any(help="""The input data for the ZIP power measurements""", unit=W)
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the load data. The positions are objects containing elements of long, lat and elevation (See Position object documentation).""",
        unit=None,
    )

    def build(self, model):
        self._model = model
