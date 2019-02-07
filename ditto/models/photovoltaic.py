
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
from .timeseries import Timeseries

from ..constant import V, VA, OHM, K


class Photovoltaic(DiTToHasTraits):

    name = Unicode(help="""Name of the PV object""", unit=None)
    nominal_voltage = Float(
        help="""This parameter defines the base voltage at the power source.""",
        default_value=None,
        unit=V,
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
    rated_power = Float(
        help="""The rated power of the source node""", default_value=None, unit=VA
    )
    control_type = Unicode(
        help="""The control scheme (voltvar_vars_over_watts, voltvar_watts_over_vars, voltvar_fixed_vars, voltvar_novars, voltwatt, watt_powerfactor, powerfactor, none) being used""",
        default_value=None,
        unit=None,
    )
    active_rating = Float(
        help="""The active rating of the inverter""",
        default_value=None,
        unit=OHM,  # TODO: CHECK THAT
    )
    reactive_rating = Float(
        help="""The reactive rating of the inverter""",
        default_value=None,
        unit=OHM,  # TODO: CHECK THAT
    )
    connecting_element = Unicode(
        help="""Name of the bus to which the power source is connected. This can be interpreted as "from" at a feeder head and "to" for a PV inverter""",
        default_value=None,
        unit=None,
    )
    min_power_factor = Float(
        help="""The minimum power factor for the inverter""",
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
        unit=OHM,  # TODO: Check that....
    )
    reactance = Float(
        help="""The per-unit internal reactance of the power source""",
        default_value=None,
        unit=OHM,  # TODO: Check that
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

    rise_limit = Float(help="""The % rise per minute""", default_value=None, unit=None)
    fall_limit = Float(help="""The % fall per minute""", default_value=None, unit=None)

    power_factor = Float(
        help="""The powerfactor used when using powerfactor control setting""",
        default_value=1,
        unit=None,
    )
    voltvar_curve = Unicode(
        help="""The voltvar curve being used. Use CYME's default volt-var curve""",
        default_value="DEFAULT VOLT-VAR",
        unit=None,
    )
    wattpowerfactor_curve = Unicode(
        help="""The watt-powerfactor curve being used. Use CYME's default volt-var curve""",
        default_value="DEFAULT WATT-PF",
        unit=None,
    )
    voltwatt_curve = Unicode(
        help="""The volt-watt curve being used. Use CYME's default volt-var curve""",
        default_value="DEFAULT VOLT-WATT",
        unit=None,
    )
    var_injection = Float(
        help="""The percentage of available reacive power injected to the system""",
        default_value=100,
        unit=None,
    )

    temperature = Float(
        help="""The ambinent temperature in degrees kelvin""",
        default_value=None,
        unit=K,
    )

    timeseries = List(
        Instance(Timeseries),
        help="""A list of all the timeseries elements used to represent the Solar Irradiance""",
        default_value=None,
        unit=None,
    )
    # Modification: Tarek (August 2018)
    # Multiple feeder support. Each element keeps track of the name of the substation it is connected to, as well as the name of the feeder.
    # I think we need both since a substation might have multiple feeders attached to it.
    # These attributes are filled once the DiTTo model has been created using the Network module
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
        default=None,
    )
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""", default=None
    )

    def build(self, model):
        self._model = model
