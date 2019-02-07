from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import (
    DiTToHasTraits,
    Float,
    Complex,
    Unicode,
    Any,
    Int,
    List,
    observe,
    Instance,
)

from .position import Position
from .wire import Wire

from ..constant import A, W, OHM


class PhaseReactor(DiTToHasTraits):
    """
    TODO
    """
    phase = Unicode(
        help="""The phase (A, B, C, N, s1, s2) of the phase reactor""",
        default_value=None,
        unit=None,
    )
    ampacity = Float(
        help="""The ampacity rating for the phase reactor under nomal conditions""",
        default_value=None,
        unit=A,
    )
    emergency_ampacity = Float(
        help="""The ampacity rating for the phase reactor under emergency conditions""",
        default_value=None,
        unit=A,
    )
    rated_power = Float(
        help="""The rated power of the phase reactor""", default_value=None, unit=W
    )
    resistance = Float(
        help="""The total resistance of the phase reactor.""",
        default_value=None,
        unit=OHM,
    )
    reactance = Float(
        help="""The total reactance of the phase reactor.""",
        default_value=None,
        unit=OHM,
    )

    def build(self, model):
        self._model = model
