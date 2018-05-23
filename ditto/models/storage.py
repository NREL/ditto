from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position
from .phase_storage import PhaseStorage


class Storage(DiTToHasTraits):

    name                   = Unicode(                     help='''Name of the storage object.''', default_value='')
    connecting_element     = Unicode(                     help='''Name of the bus the storage is connected to.''' , default_value=None)
    nominal_voltage        = Float(                       help='''Nominal voltage for the storage element.''', default_value=None)
    rated_power            = Float(                       help='''Rated power of the device. In watts.''', default_value=None)
    rated_kWh              = Float(                       help='''Rated storage capacity. In kilo-watt-hours.''', default_value=None)
    stored_kWh             = Float(                       help='''Present amount of energy stored. In kilo-watt-hours.''', default_value=None)
    reserve                = Float(                       help='''Percent of rated_kWh storage capacity to be held in reserve for normal operation.''', default_value=None)
    state                  = Unicode(                     help='''Present state of the device: {IDLING,CHARGING,DISCHARGING}.''', default_value=None)
    discharge_rate         = Float(                       help='''Discharge rate in percent of rated power.''', default=0)
    charge_rate            = Float(                       help='''Charging rate in percent of rated power.''', default=0)
    charging_efficiency    = Float(                       help='''Percent efficiency for charging the storage element.''', default=None)
    discharging_efficiency = Float(                       help='''Percent efficiency for discharging the storage element.''', default=None)
    resistance             = Float(                       help='''Equivalent percent internal resistance. In ohms.''', default=None)
    reactance              = Float(                       help='''Equivalent percent internal reactance. In ohms.''', default=None)
    model_                 = Int(                         help='''Model to use for power output with voltage. 1=constant P at specified pf. 2=constant admittance. 3=User-written model.''', default=None)
    yearly                 = Unicode(                     help='''Dispatch shape to use for yearly simulations.''', default=None)
    daily                  = Unicode(                     help='''Dispatch shape to use for daily simulations.''', default=None)
    duty                   = Unicode(                     help='''Load shape to use for duty cycle dispatch simulations.''', default=None)
    discharge_trigger      = Float(                       help='''Dispatch trigger value for discharging the storage.''', default=None)
    charge_trigger         = Float(                       help='''Dispatch trigger value for charging the storage.''', default=None)
    phase_storages         = List(Instance(PhaseStorage), help='''A list of the phase storage that the storage contains.''', default=None)
    substation_name        = Unicode(                     help='''The name of the substation to which the object is connected.''', default=None)
    feeder_name            = Unicode(                     help='''The name of the feeder the object is on.''', default=None)

    #Modification: Nicolas (May 2018)
    is_substation = Int(help='''Flag that indicates wheter the element is inside a substation or not.''', default_value=0)

    def build(self, model):
        """
        TODO...
        """
        self._model = model
