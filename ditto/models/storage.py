# -*- coding: utf-8 -*-
from .base import (
    DiTToHasTraits,
    Float,
    Unicode,
    Any,
    Bool,
    Int,
    List,
    observe,
    Instance,
)

from .position import Position
from .phase_storage import PhaseStorage


class Storage(DiTToHasTraits):

    name = Unicode(help="""Name of the storage object.""", default_value="")
    connecting_element = Unicode(
        help="""Name of the bus the storage is connected to.""", default_value=None
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the power source - it should only contain one. The positions are objects containing elements of long, lat and elevation.""",
    )
    nominal_voltage = Float(
        help="""Nominal voltage for the storage element.""", default_value=None
    )
    rated_power = Float(
        help="""Rated power of the device. In watts.""", default_value=None
    )
    reactive_rating = Float(
        help="""Rated reactive power of the inverter. In watts.""", default_value=None
    )
    active_rating = Float(
        help="""Rated reactive power of the inverter. In watts.""", default_value=None
    )
    power_factor = Float(help="""Default power factor. In watts.""", default_value=None)

    min_powerfactor = Float(
        help="""Minimum power factor of the device""", default_value=None
    )
    rated_kWh = Float(
        help="""Rated storage capacity. In kilo-watt-hours.""", default_value=None
    )
    stored_kWh = Float(
        help="""Present amount of energy stored. In kilo-watt-hours.""",
        default_value=None,
    )
    reserve = Float(
        help="""Percent of rated_kWh storage capacity to be held in reserve for normal operation.""",
        default_value=None,
    )
    state = Unicode(
        help="""Present state of the device: {IDLING,CHARGING,DISCHARGING}.""",
        default_value=None,
    )
    discharge_rate = Float(
        help="""Discharge rate in percent of rated power.""", default_value=None
    )
    charge_rate = Float(
        help="""Charging rate in percent of rated power.""", default_value=None
    )
    charging_efficiency = Float(
        help="""Percent efficiency for charging the storage element.""",
        default_value=None,
    )
    discharging_efficiency = Float(
        help="""Percent efficiency for discharging the storage element.""",
        default_value=None,
    )
    resistance = Float(
        help="""Equivalent percent internal resistance. In ohms.""", default_value=None
    )
    reactance = Float(
        help="""Equivalent percent internal reactance. In ohms.""", default_value=None
    )
    model_ = Int(
        help="""Model to use for power output with voltage. 1=constant P at specified pf. 2=constant admittance. 3=User-written model.""",
        default_value=None,
    )
    yearly = Unicode(
        help="""Dispatch shape to use for yearly simulations.""", default_value=None
    )
    daily = Unicode(
        help="""Dispatch shape to use for daily simulations.""", default_value=None
    )
    duty = Unicode(
        help="""Load shape to use for duty cycle dispatch simulations.""",
        default_value=None,
    )
    discharge_trigger = Float(
        help="""Dispatch trigger value for discharging the storage.""",
        default_value=None,
    )
    charge_trigger = Float(
        help="""Dispatch trigger value for charging the storage.""", default_value=None
    )
    phase_storages = List(
        Instance(PhaseStorage),
        help="""A list of the phase storage that the storage contains.""",
        default_value=None,
    )
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
        default_value=None,
    )
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""", default_value=None
    )

    # Modification: Nicolas (May 2018)
    is_substation = Bool(
        help="""Flag that indicates wheter the element is inside a substation or not.""",
        default_value=False,
    )

    def build(self, model):
        """
        TODO...
        """
        self._model = model
