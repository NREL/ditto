from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToHasTraits, Float, Complex, Unicode, Any, Int, List, observe, Instance

from .position import Position

class NetworkAttributes(DiTToHasTraits):
    '''Class describing the networks of a system (feeders, substations, subtransmission...).'''
    name = Unicode(help='''Network ID.''')
    network_type = Unicode(help='''Type of network (feeder, substation...).''')
    headnode = Unicode(help='''Name of the headnode/FEEDERHEAD of the network.''', default_value=None)
    nominal_voltage = Float(help='''Nominal voltage at the feeder head.''', default_value=None)
    sourceID = Unicode(help='''Name of the Power Source object. Either the connected source or source equivalent.''', default_value=None)
    substation_name = Unicode(help='''Name of the substation of this network.''', default_value=None)
    positions = List(Instance(Position), help="""List of Nodes Positions belonging to the subnetwork. """, default_value=None)
    average_position = List(Instance(Position), help="""Average position for the subnetwork.""", default_value=None)

    def build(self, model, Asset=None, ConnectivityNode=None, Location=None):

        self._model = model