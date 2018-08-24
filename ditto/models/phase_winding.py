from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position

from ..constant import OHM


class PhaseWinding(DiTToHasTraits):
    tap_position = Float(
        help="""The initial tap position of the phase on the winding. It should be in the range [lowstep,highstep] provided by the transformer or regulator""",
        default_value=None,
        unit=None,
    )
    phase = Unicode(
        help="""The phase for this componant of the winding (A,B,C, N,s1,s2)""",
        default_value=None,
        unit=None,
    )
    compensator_r = Float(
        help="""The compensator resistance value for the phase""",
        default_value=None,
        unit=OHM,
    )
    compensator_x = Float(
        help="""The compensator reactance value for the phase""",
        default_value=None,
        unit=OHM,
    )

    def build(self, model):
        self._model = model
