from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position
from .phase_capacitor import PhaseCapacitor

from ..constant import V, S, OHM, SIEMENS


class Capacitor(DiTToHasTraits):

    name = Unicode(help="""Name of the capacitor object""", default_value="", unit=None)
    nominal_voltage = Float(
        help="""The nominal voltage of the capacitor""", default_value=None, unit=V
    )
    connection_type = Unicode(
        help="""This is the type of connection that the capacitor connects to on the high side. The strings may be one of the following Delta (D), Wye (Y), Zigzap (Z) or autotransformer (A).""",
        default_value=None,
        unit=None,
    )
    delay = Float(
        help="""The time that the capacitor need to connect or disconnect by automatic voltage regulation""",
        default_value=None,
        unit=S,
    )
    mode = Unicode(
        help="""What control mode is used. A string from one of the options: {voltage, activePower, reactivePower, currentFlow, admittance, timeScheduled, none}""",
        default_value=None,
        unit=None,
    )
    low = Float(
        help="""This is the low value of the range that is being controlled by the capacitor (e.g. voltage).""",
        default_value=None,
        unit=None,  # PROBLEM HERE....
    )
    high = Float(
        help="""This is the high value of the range that is being controlled by the capacitor (e.g. voltage).""",
        default_value=None,
        unit=None,  # PROBLEM HERE...
    )
    resistance = Float(
        help="""The total series resistance of the capacitor""",
        default_value=None,
        unit=OHM,
    )
    resistance0 = Float(
        help="""The total series zero-sequence resistance of the capacitor""",
        default_value=None,
        unit=OHM,
    )
    reactance = Float(
        help="""The total series reactance of the capacitor""",
        default_value=None,
        unit=OHM,
    )
    reactance0 = Float(
        help="""The total series zero-sereactance of the capacitor""",
        default_value=None,
        unit=OHM,
    )
    susceptance = Float(
        help="""The total shunt susceptance of the capacitor section. Note that if the var value of the capacitor is provided this should follow the formula susceptance = -1*p.var/(nominal_voltage)**2""",
        default_value=None,
        unit=SIEMENS,
    )
    susceptance0 = Float(
        help="""The total zero sequence shunt susceptance of the capacitor""",
        default_value=None,
        unit=SIEMENS,
    )
    conductance = Float(
        help="""This is the shunt conductance of the capacitor """,
        default_value=None,
        unit=SIEMENS,
    )
    conductance0 = Float(
        help="""This is the zero sequence shunt conductance of the capacitor per section""",
        default_value=None,
        unit=SIEMENS,
    )
    pt_ratio = Float(
        help="""The voltage (potential) transformer ratio used to step down the voltage for controller.""",
        default_value=None,
        unit=None,
    )
    ct_ratio = Float(
        help="""The current transformer ratio used to define the current ratio for a controller.""",
        default_value=None,
        unit=None,
    )
    pt_phase = Unicode(
        help="""The phase that the controller is connected to.""",
        default_value=None,
        unit=None,
    )
    connecting_element = Unicode(
        help="""The bus which the capacitor is connected to""",
        default_value=None,
        unit=None,
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the capacitor (typically just one). The positions are objects containing elements of long, lat and elevation (See Position object documentation).""",
        default_value=None,
        unit=None,
    )
    phase_capacitors = List(
        Instance(PhaseCapacitor),
        help="""A list of phase capacitors which contain phase, var and switch values. The total var of the capacitor is defined through the phasecapacitors.""",
        default_value=None,
        unit=None,
    )

    # Modification: Nicolas (August 2017)
    # OpenDSS needs the name of the element to which the CapControl is measuring
    # This is not optional, it must be provided (Otherwise OpenDSSdirect will segfault...)
    measuring_element = Unicode(
        help="""Name of the circuit element, typically a line or transformer, to which the capacitor control's PT and/or CT are connected""",
        default_value=None,
        unit=None,
    )

    # Modification: Nicolas (December 2017)
    # Multiple feeder support. Each element keeps track of the name of the substation it is connected to, as well as the name of the feeder.
    # I think we need both since a substation might have multiple feeders attached to it.
    # These attributes are filled once the DiTTo model has been created using the Network module
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
        default=None,
        unit=None,
    )
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""", default=None, unit=None
    )

    # Modification: Nicolas (May 2018)
    is_substation = Int(
        help="""Flag that indicates wheter the element is inside a substation or not.""",
        default_value=0,
        unit=None,
    )

    def build(self, model):
        self._model = model
