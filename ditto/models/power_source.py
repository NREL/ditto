from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import (
    DiTToHasTraits,
    Float,
    Unicode,
    Any,
    Int,
    List,
    observe,
    Instance,
    Complex,
)

from .position import Position

from ..constant import V, M, VA, OHM, DEG


class PowerSource(DiTToHasTraits):

    name = Unicode(help="""Name of the power source object""", unit=None)
    nominal_voltage = Float(
        help="""This parameter defines the base voltage at the power source.""",
        default_value=None,
        unit=V,
    )
    per_unit = Float(
        help="""This parameter defines the per unit voltage at the source.""",
        default_value=1.0,
        unit=None,
    )
    phases = List(
        Instance(Unicode),
        help="""This parameter is a list of all the phases at the power source.""",
        unit=None,
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the power source - it should only contain one. The positions are objects containing elements of long, lat and elevation.""",
        unit=None,
    )
    is_sourcebus = Int(
        help="""A Boolean flag which is 1 if the PowerSource object is an external power source at the distribution system head""",
        unit=None,
    )
    rated_power = Float(
        help="""The rated power of the source node""", default_value=None, unit=VA
    )
    emergency_power = Float(
        help="""The emergency power of the source node""", default_value=None, unit=VA
    )

    connection_type = Unicode(
        help="""The connection type (D, Y, Z, A) for Delta, Wye, Zigzag or autotransformer.""",
        default_value=None,
        unit=None,
    )

    cutout_percent = Float(
        help="""The cutout percentage. If  the per-unit power drops below this value the power source turns off""",
        default_value=None,
        unit=None,
    )
    cutin_percent = Float(
        help="""The cutin percentage. If  the per-unit power rises above this value the power source turns on""",
        default_value=None,
        unit=None,
    )

    resistance = Float(
        help="""The per-unit internal resistance of the power source""",
        default_value=None,
        unit=OHM,  # Not sure, to confirm...
    )
    reactance = Float(
        help="""The per-unit internal reactance of the power source""",
        default_value=None,
        unit=OHM,  # Not sure, to confirm...
    )
    v_max_pu = Float(
        help="""The per-unit maximum voltage. Beyond this constant impedance model is applied""",
        default_value=None,
        unit=None,
    )
    v_min_pu = Float(
        help="""The per-unit minimum voltage. Below this, constant impedance model is applied""",
        default_value=None,
        unit=None,
    )
    power_factor = Float(
        help="""The power factor for the power source object""",
        default_value=None,
        unit=None,
    )

    connecting_element = Unicode(
        help="""Name of the bus to which the power source is connected. This can be interpreted as "from" at a feeder head and "to" for a PV inverter""",
        default_value=None,
        unit=None,
    )

    # Addition Nicolas November 2017:
    phase_angle = Float(
        help="""Base angle, degree of the first phase.""", default_value=0, unit=DEG
    )
    positive_sequence_impedance = Complex(
        help="""Positive-sequence impedance of the source.""",
        default_value=None,
        unit=OHM + "/" + M,
    )
    zero_sequence_impedance = Complex(
        help="""Zero-sequence impedance of the source.""",
        default_value=None,
        unit=OHM + "/" + M,
    )

    def build(self, model):
        self._model = model
