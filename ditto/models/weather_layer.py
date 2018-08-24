from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe

from .position import Position

from ..constant import K, S, M


class WeatherLayer(DiTToHasTraits):

    name = Unicode(help="""Name of the weather object""", unit=None)
    interval = Integer(
        help="""The time resolution (in seconds) for the measured data""", unit=S
    )
    ghi = Any(help="""The input data for global horizontal irradiance""", unit=None)
    temperature = Any(help="""The input data for temperature""", unit=K)
    relative_humitidy = Any(help="""The input data for relative humidity""", unit=None)
    surface_windspeed = Any(
        help="""The input data for surface windspeed""", unit=M + "/" + S
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the weather data. The positions are objects containing elements of long, lat and elevation (See Position object documentation).""",
        unit=None,
    )

    def build(self, model):
        self._model = model
