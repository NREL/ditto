# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import (
    DiTToHasTraits,
    Float,
    Unicode,
    Any,
    Int,
    List,
    Bool,
    observe,
    Instance,
)

from .position import Position
from .winding import Winding


class PowerTransformer(DiTToHasTraits):

    name = Unicode(help="""Name of the transformer object""", default_value="")

    # Modification: Nicolas (August 2017)
    # Moved the rated_power from the transformer down to the windings
    # rated_power = Float(help='''The rated power of the entire transformer''', default_value=None)

    install_type = Unicode(
        help="""The mounting type of the transformer: one of {POLETOP, PADMOUNT, VAULT}""",
        default_value=None,
    )
    noload_loss = Float(
        help="""The no-load loss for a zero sequence short-circuit test on the entire transformer""",
        default_value=None,
    )
    phase_shift = Float(
        help="""The degree phase shift that the transformer causes.""",
        default_value=None,
    )
    from_element = Any(
        help="""Name of the node which connects to the 'from' end of the transformer""",
        default_value=None,
    )
    to_element = Any(
        help="""'Name of the node which connects to the 'to' end of the transformer""",
        default_value=None,
    )
    from_element_connection_index = Int(
        help="""Index of the position in the node that the 'from' end of the line connects to (e.g. for a long bus)""",
        default_value=None,
    )
    to_element_connection_index = Int(
        help="""Index of the position in the node that the 'to' end of the line connects to (e.g. for a long bus)""",
        default_value=None,
    )

    reactances = List(
        Float(),
        help="""Reactances are described between all the windings. There are n*(n-1)/2 reactances (where n is the number of windings). For two a winding transformer this gives one value, and for a 3 winding transformer it gives 3.""",
        default_value=None,
    )

    windings = List(
        Instance(Winding),
        help="""A list of the windings that the transformer contains. Most will have two windings but center tap transformers have three.""",
        default_value=None,
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the transformer - it should contain just one. The positions are objects containing elements of long, lat and elevation.""",
        default_value=None,
    )

    # Modification: Nicolas (August 2017)
    loadloss = Float(help="Percent Losses at rated load", default_value=None)
    normhkva = Float(help="Normal maximum kVA rating for H winding", default_value=None)

    # Modification: Nicolas (November 2017)
    is_center_tap = Bool(
        help="""Set to 1 if the transformer is a center tap transformer"""
    )

    # Modification: Nicolas (December 2017)
    is_substation = Bool(
        help="""Set to 1 if the transformer is a substation or is inside a substation""",
    )

    # Modification: Nicolas (December 2017)
    # Multiple feeder support. Each element keeps track of the name of the substation it is connected to, as well as the name of the feeder.
    # I think we need both since a substation might have multiple feeders attached to it.
    # These attributes are filled once the DiTTo model has been created using the Network module
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
    )
    feeder_name = Unicode(help="""The name of the feeder the object is on.""",)

    def build(self, model):
        """
        The high and low properties are used to creat windings which are added to the windings list
        Winding data (e.g. high_ground_reactance) should be referenced thorugh the windings list
        """
        self._model = model
