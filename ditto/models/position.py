from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from ..constant import M


class Position(DiTToHasTraits):
    # NOTE: We are not really using lat/long I believe, but mostly coordinates in various format
    # TODO: Build the conversion to parse to lat/long from given inputs...
    long = Float(help="""Decimal Longitude""", unit=M)
    lat = Float(help="""Decimal Latitude""", unit=M)
    elevation = Float(help="""Decimal elevation (meters)""", unit=M)

    def build(self, model):
        self._model = model
