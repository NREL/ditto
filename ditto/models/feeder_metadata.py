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


class Feeder_metadata(DiTToHasTraits):
    """TODO

"""
    name = Unicode(help="""Name of the feeder object""")
    nominal_voltage = Float(
        help="""Nominal voltage at the feeder head.""", default_value=None
    )
    headnode = Unicode(help="""Name of the headnode/FEEDERHEAD.""", default_value=None)
    transformer = Unicode(
        help="""Name of the transformer representing the substation.""",
        default_value=None,
    )
    substation = Unicode(
        help="""Name of the object representing the substation in the feeder files (often a bus downstream of the transformer).""",
        default_value=None,
    )
    operating_voltage = Float(
        help="""Operating voltage at the feeder head.""", default_value=None
    )
    operating_angle1 = Float(help="""Angle 1.""", default_value=None)
    operating_angle2 = Float(help="""Angle 2.""", default_value=None)
    operating_angle3 = Float(help="""Angle 3.""", default_value=None)
    positive_sequence_resistance = Float(
        help="""Positive sequence resistance for the source equivalent.""",
        default_value=None,
    )
    positive_sequence_reactance = Float(
        help="""Positive sequence reactance for the source equivalent.""",
        default_value=None,
    )
    zero_sequence_resistance = Float(
        help="""Zero sequence resistance for the source equivalent.""",
        default_value=None,
    )
    zero_sequence_reactance = Float(
        help="""Zero sequence reactance for the source equivalent.""",
        default_value=None,
    )
    negative_sequence_resistance = Float(
        help="""Negative sequence resistance for the source equivalent.""",
        default_value=None,
    )
    negative_sequence_reactance = Float(
        help="""Negative sequence reactance for the source equivalent.""",
        default_value=None,
    )

    def build(self, model, Asset=None, ConnectivityNode=None, Location=None):

        self._model = model
