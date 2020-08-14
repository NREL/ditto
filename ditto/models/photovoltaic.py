
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


class Photovoltaic(DiTToHasTraits):

    name = Unicode(help="""Name of the PV object""")
    nominal_voltage = Float(
        help="""This parameter defines the base voltage at the power source.""",
        default_value=None,
    )
    phases = List(
        Instance(Unicode),
        help="""This parameter is a list of all the phases at the power source.""",
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the power source - it should only contain one. The positions are objects containing elements of long, lat and elevation.""",
    )
    rated_power = Float(
        help="""The rated power of the source node""", default_value=None
    )
    control_type = Unicode(
        help="""The control scheme (voltvar_vars_over_watts, voltvar_watts_over_vars, voltvar_fixed_vars, voltvar_novars, voltwatt, watt_powerfactor, powerfactor, none) being used""",
        default_value=None,
    )
    active_rating = Float(
        help="""The active rating of the inverter""", default_value=None
    )
    reactive_rating = Float(
        help="""The reactive rating of the inverter""", default_value=None
    )
    connecting_element = Unicode(
        help="""Name of the bus to which the power source is connected. This can be interpreted as "from" at a feeder head and "to" for a PV inverter""",
        default_value=None,
    )
    min_power_factor = Float(
        help="""The minimum power factor for the inverter""", default_value=None
    )

    cutout_percent = Float(
        help="""The cutout percentage. If  the per-unit power drops below this value the power source turns off""",
        default_value=None,
    )
    cutin_percent = Float(
        help="""The cutin percentage. If  the per-unit power rises above this value the power source turns on""",
        default_value=None,
    )
    resistance = Float(
        help="""The per-unit internal resistance of the power source""",
        default_value=None,
    )
    reactance = Float(
        help="""The per-unit internal reactance of the power source""",
        default_value=None,
    )
    v_max_pu = Float(
        help="""The per-unit maximum voltage. Beyond this constant impedance model is applied""",
        default_value=None,
    )
    v_min_pu = Float(
        help="""The per-unit minimum voltage. Below this, constant impedance model is applied""",
        default_value=None,
    )

    rise_limit = Float(help="""The % rise per minute""", default_value=None)
    fall_limit = Float(help="""The % fall per minute""", default_value=None)

    power_factor = Float(
        help="""The powerfactor used when using powerfactor control setting""",
        default_value=1,
    )
    voltvar_curve = Unicode(
        help="""The voltvar curve being used. Use CYME's default volt-var curve""",
        default_value="DEFAULT VOLT-VAR",
    )
    wattpowerfactor_curve = Unicode(
        help="""The watt-powerfactor curve being used. Use CYME's default volt-var curve""",
        default_value="DEFAULT WATT-PF",
    )
    voltwatt_curve = Unicode(
        help="""The volt-watt curve being used. Use CYME's default volt-var curve""",
        default_value="DEFAULT VOLT-WATT",
    )
    var_injection = Float(
        help="""The percentage of available reacive power injected to the system""",
        default_value=100,
    )

    temperature = Float(
        help="""The ambinent temperature in degrees celcius""", default_value=None
    )

    timeseries = List(
        Instance(Timeseries),
        help="""A list of all the timeseries elements used to represent the Solar Irradiance""",
        default_value=None,
    )
    # Modification: Tarek (August 2018)
    # Multiple feeder support. Each element keeps track of the name of the substation it is connected to, as well as the name of the feeder.
    # I think we need both since a substation might have multiple feeders attached to it.
    # These attributes are filled once the DiTTo model has been created using the Network module
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
    ).tag(default=None)
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""",
    ).tag(default=None)

    def build(self, model):
        self._model = model
