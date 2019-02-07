from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position

from ..constant import VA


class PhaseCapacitor(DiTToHasTraits):

    phase = Unicode(
        help="""The phase (A, B, C, N, s1, s2) of the capacitor section""",
        default_value=None,
        unit=None,
    )
    var = Float(
        help="""The var rating of the capacitor phase""", default_value=None, unit=VA
    )
    switch = Int(
        help="""A boolean value to denote whether or not the capacitor is switched in. 1 means it's switched in, 0 means that it's not""",
        default_value=None,
        unit=None,
    )
    sections = Int(
        help="""The maximum number of sections connected to this phase""",
        default_value=None,
        unit=None,
    )
    normalsections = Int(
        help="""The normal number of sections connected to this phase""",
        default_value=None,
        unit=None,
    )

    def build(self, model):
        self._model = model
