from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position
from .phase_winding import PhaseWinding

from ..constant import V, OHM, VA


class Winding(DiTToHasTraits):
    connection_type = Unicode(
        help="""The connection type (D, Y, Z, A) for Delta, Wye, Zigzag or autotransformer.""",
        default_value=None,
        unit=None,
    )
    voltage_type = Int(
        help="""0 for a high voltage connection, 2 for a low voltage connection, and 1 for an intermediary connection.""",
        default_value=None,
        unit=None,
    )
    nominal_voltage = Float(
        help="""The nominal voltage of the transformer winding""",
        default_value=None,
        unit=V,
    )
    voltage_limit = Float(
        help="""The maximum voltage allowed on the PT secondary.""",
        default_value=None,
        unit=V,
    )
    resistance = Float(
        help="""The per unit resistance of the winding. For a representation with only one resistance for the entire transformer, this is split equally between the windings.""",
        default_value=None,
        unit=OHM,  # NOT SURE....
    )
    reverse_resistance = Float(
        help="""The per unit resistance of the winding with reverse powerflow. For a representation with only one resistance for the entire transformer, this is split equally between the windings.""",
        default_value=None,
        unit=OHM,  # NOT SURE...
    )
    phase_windings = List(
        Instance(PhaseWinding),
        help="""A list of phasewinding objects which contain the phase, tap position and compensator settings""",
        default_value=None,
        unit=None,
    )

    # Added by Nicolas (August 2017)
    # Better results are obtained if the rated power is specified at the windings rather
    # than for the whole transformer
    rated_power = Float(
        help="""The rated power of the winding""", default_value=None, unit=VA
    )
    emergency_power = Float(
        help="""The emergency power of the winding""", default_value=None, unit=VA
    )

    def build(self, model):
        self._model = model
