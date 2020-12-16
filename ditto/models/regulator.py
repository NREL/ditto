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
from .winding import Winding


class Regulator(DiTToHasTraits):

    name = Unicode(help="""Name of the regulator object""", default_value="")
    delay = Float(
        help="""The delay for first tap change operation""", default_value=None
    )
    highstep = Int(
        help="""The hightest possible tap step position from neutral""",
        default_value=None,
    )
    lowstep = Int(
        help="""The lowest possible tap step position from neutral""",
        default_value=None,
    )
    pt_ratio = Float(
        help="""The turns ratio used for the power transducer with a line-drop compensator.""",
        default_value=None,
    )
    ct_ratio = Float(
        help="""The turns ratio used for the current transducer with a line-drop compensator.""",
        default_value=None,
    )
    phase_shift = Float(
        help="""The degree phase shift that the regulator causes.""", default_value=None
    )
    ltc = Int(
        help="""1 if this regulator is a load tap changer, 0 otherwise.""",
        default_value=None,
    )
    bandwidth = Float(
        help="""The band before a change occurs in the regulator""", default_value=None
    )
    bandcenter = Float(
        help="""This is the target value for the regulator. Should often be the nominal voltage""",
        default_value=None,
    )
    voltage_limit = Float(
        help="""The maximum voltage allowed on the PT secondary""", default_value=None
    )
    from_element = Any(
        help="""The node which connects to the 'from' end of the regulator""",
        default_value=None,
    )
    to_element = Any(
        help="""'The node which connects to the 'to' end of the regulator""",
        default_value=None,
    )
    connected_transformer = Unicode(
        help="""The name of the transformer that the voltage regulator is attached to""",
        default_value=None,
    )
    pt_phase = Unicode(
        help="""The phase being used to monitor the voltage""", default_value=None
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the regulator (typically just one). The positions are objects containing elements of long, lat and elevation (See Position object documentation).""",
        default_value=None,
    )
    reactances = List(
        Float(),
        help="""Reactances are described between all the windings. There are n*(n-1)/2 reactances (where n is the number of windings). For two a winding transformer this gives one value, and for a 3 winding transformer it gives 3.  The list elements have (from_winding, to_winding, reactance) where from_winding and to_winding are the 1-based indices of the windings list.""",
        default_value=None,
    )

    windings = List(
        Instance(Winding),
        help=""" This is a list containing one element for each winding in the voltage regulator. It describes attributes of the winding. This paramter is required to describe many compontants of the regulator. The simplest versions have two windings representing a high and low voltage.""",
        default_value=None,
    )

    # Added by Nicolas (August 2017)
    winding = Int(
        help="""Number of the winding of the transformer element that the RegControl is monitoring.""",
        default_value=None,
    )

    ct_prim = Float(
        help="""Rating, in Amperes, of the primary CT rating for converting the line amps to control amps""",
        default_value=None,
    )

    # Added by Tarek (September 26)

    noload_loss = Float(
        help="""The no-load loss for a zero sequence short-circuit test on the regulator""",
        default_value=None,
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
    setpoint = Float(
        help="""The percentage p.u. voltage setpoint of the regulator""",
        default_value=None,
    )

    # Modification: Nicolas (May 2018)
    is_substation = Bool(
        help="""Flag that indicates wheter the element is inside a substation or not.""",
        default_value=False,
    )

    def build(self, model):
        self._model = model
