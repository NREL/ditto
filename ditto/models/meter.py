from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position


class Meter(DiTToHasTraits):

    name = Unicode(help="""Name of the meter object""")
    nominal_voltage = Float(help="""The nominal voltage of the meter""")
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the line. The positions are objects containing elements of long, lat and elevation (See Position object documentation). The points can be used to map the position of the line.  """,
    )

    # NOT YET CIM COMPATIBLE
    phases = List(
        Instance(Unicode),
        help="""This parameter is a list of all the phases at the node. The Phases are Strings of  'A', 'B', 'C', 'N', 's1' or 's2' (for secondaries).""",
    )

    def build(self, model):
        self._model = model
