from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance


class Position(DiTToHasTraits):
    long = Float(help="""Decimal Longitude""")
    lat = Float(help="""Decimal Latitude""")
    elevation = Float(help="""Decimal elevation (meters)""")

    def build(self, model):
        self._model = model
