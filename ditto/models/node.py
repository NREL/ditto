# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

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


class Node(DiTToHasTraits):
    """Inheritance:
    Asset (self._asset)
        -> Location (self._loc)

    ConnectivityNode (self._cn)
    """

    name = Unicode(help="""Name of the node object""")
    nominal_voltage = Float(
        help="""This parameter defines the base voltage at the node.""",
        default_value=None,
    )
    phases = List(
        Instance(Unicode),
        help="""This parameter is a list of all the phases at the node.""",
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the node - it should only contain one.
        The positions are objects containing elements of long, lat and elevation.""",
    )

    # Modification: Nicolas (December 2017)
    # Multiple feeder support. Each element keeps track of the name of the substation it is connected to, as well as the name of the feeder.
    # I think we need both since a substation might have multiple feeders attached to it.
    # These attributes are filled once the DiTTo model has been created using the Network module
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
    ).tag(default=None)
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""",
    ).tag(default=None)

    # Modification: Tarek (April 2018)
    # Support for substation connection points. These identify if the node connects the substation to a feeder or high voltage source
    is_substation_connection = Bool(
        help="""1 if the node connects from inside a substation to outside, 0 otherwise.""",
    ).tag(default=None)

    # Modification: Nicolas (May 2018)
    is_substation = Bool(
        help="""Flag that indicates wheter the element is inside a substation or not.""",
        default_value=False,
    )

    setpoint = Float(
        help="""Value that the node must be set to. This is typically used for feeder head points""",
        default_value=None,
    )

    def build(self, model, Asset=None, ConnectivityNode=None, Location=None):

        self._model = model


#        if ConnectivityNode is None:
#            self._cn = self._model.env.ConnectivityNode()
#        else:
#            self._cn = ConnectivityNode
#
#        if Asset is None:
#            self._asset = self._model.env.Asset()
#        else:
#            self._asset = Asset
#        self._asset.PowerSystemResource = self._asset.PowerSystemResource + (self._cn, )
#
#        if Location is None:
#            self._loc = self._model.env.Location()
#        else:
#            self._loc = Location
#        self._asset.Location = self._loc
#        self._loc.Assets = self._loc.Assets + (self._asset, )
#
#        self._model.model_store[self.name] = self
#
#    @observe('name', type='change')
#    def _set_name(self, bunch):
#        self._cn.name = bunch['new']
#
#    @observe('name', type='fetch')
#    def _get_name(self, bunch):
#        return self._cn.name
#
#    @observe('positions', type='change')
#    def _set_positions(self, bunch):
#        position_list = bunch['new']
#        self._loc.PositionPoints=[]
#        for position in position_list:
#            p = self._model.env.PositionPoint()
#            p.xPosition = position.long
#            p.yPosition = position.lat
#            p.zPosition = position.elevation
#            p.Location = self._loc
#            self._loc.PositionPoints = self._loc.PositionPoints + (p, )
#
#    @observe('positions', type='fetch')
#    def _get_positions(self, bunch):
#        positions = []
#        for p in self._loc.PositionPoints:
#            position = Position()
#            position.lat = p.xPosition
#            position.long = p.yPosition
#            position.elevation = p.zPosition
#            positions.append(position)
#        return positions
