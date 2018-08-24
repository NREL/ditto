from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position
from .phase_storage import PhaseStorage

from ..constant import V, W, KWH, OHM


class Storage(DiTToHasTraits):

    name = Unicode(help="""Name of the storage object.""", default_value="", unit=None)
    connecting_element = Unicode(
        help="""Name of the bus the storage is connected to.""",
        default_value=None,
        unit=None,
    )
    nominal_voltage = Float(
        help="""Nominal voltage for the storage element.""", default_value=None, unit=V
    )
    rated_power = Float(
        help="""Rated power of the device. In watts.""", default_value=None, unit=W
    )
    reactive_rating = Float(
        help="""Rated reactive power of the device. In watts.""", default_value=None
    )
    min_powerfactor = Float(
        help="""Minimum power factor of the device""", default_value=None
    )
    rated_kWh = Float(
        help="""Rated storage capacity. In kilo-watt-hours.""",
        default_value=None,
        unit=KWH,
    )
    stored_kWh = Float(
        help="""Present amount of energy stored. In kilo-watt-hours.""",
        default_value=None,
        unit=KWH,
    )
    reserve = Float(
        help="""Percent of rated_kWh storage capacity to be held in reserve for normal operation.""",
        default_value=None,
        unit=None,
    )
    state = Unicode(
        help="""Present state of the device: {IDLING,CHARGING,DISCHARGING}.""",
        default_value=None,
        unit=None,
    )
    discharge_rate = Float(
        help="""Discharge rate in percent of rated power.""", default=0, unit=None
    )
    charge_rate = Float(
        help="""Charging rate in percent of rated power.""", default=0, unit=None
    )
    charging_efficiency = Float(
        help="""Percent efficiency for charging the storage element.""",
        default=None,
        unit=None,
    )
    discharging_efficiency = Float(
        help="""Percent efficiency for discharging the storage element.""",
        default=None,
        unit=None,
    )
    resistance = Float(
        help="""Equivalent percent internal resistance. In ohms.""",
        default=None,
        unit=OHM,
    )
    reactance = Float(
        help="""Equivalent percent internal reactance. In ohms.""",
        default=None,
        unit=OHM,
    )
    model_ = Int(
        help="""Model to use for power output with voltage. 1=constant P at specified pf. 2=constant admittance. 3=User-written model.""",
        default=None,
        unit=None,
    )
    yearly = Unicode(
        help="""Dispatch shape to use for yearly simulations.""",
        default=None,
        unit=None,
    )
    daily = Unicode(
        help="""Dispatch shape to use for daily simulations.""", default=None, unit=None
    )
    duty = Unicode(
        help="""Load shape to use for duty cycle dispatch simulations.""",
        default=None,
        unit=None,
    )
    discharge_trigger = Float(
        help="""Dispatch trigger value for discharging the storage.""",
        default=None,
        unit=None,
    )
    charge_trigger = Float(
        help="""Dispatch trigger value for charging the storage.""",
        default=None,
        unit=None,
    )
    phase_storages = List(
        Instance(PhaseStorage),
        help="""A list of the phase storage that the storage contains.""",
        default=None,
        unit=None,
    )
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
        """
        TODO...
        """
        self._model = model
