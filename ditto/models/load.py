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
from .phase_load import PhaseLoad
from .timeseries import Timeseries


class Load(DiTToHasTraits):

    name = Unicode(help="""Name of the load object""", default_value="")
    nominal_voltage = Float(
        help="""This is the nominal voltage of the load.""", default_value=None
    )
    connection_type = Unicode(
        help="""The connection type (D, Y, Z, A) for Delta, Wye, Zigzag or autotransformer.""",
        default_value=None,
    )
    vmin = Float(
        help="""The minimum per-unit voltage value. Going below this implies constant impedance.""",
        default_value=None,
    )
    vmax = Float(
        help="""The maximum per-unit voltage value. Going below this implies constant impedance.""",
        default_value=None,
    )
    phase_loads = List(
        Instance(PhaseLoad),
        help="""A list of the different phase loads connected to the load. This contains information about the phase as well as the p&q or zip load data.""",
        default_value=None,
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the load- it should only contain one. The positions are objects containing elements of long, lat and elevation.""",
        default_value=None,
    )

    timeseries = List(
        Instance(Timeseries),
        help="""A list of all the timeseries elements used to represent the loads""",
        default_value=None,
    )

    # Modification: Nicolas (August 2017)
    # OpenDSS needs the name of the bus to which the load is connected, because it does not
    # represent the load as a bus with a connection line to another bus in the feeder.
    connecting_element = Unicode(
        help="""Name of the bus to which the load is connected""", default_value=None
    )

    # Modification: Claudio (August 2017)
    rooftop_area = Float(
        help="""This parameter is the rooftop area for all phases of the load""",
        default_value=None,
    )
    peak_p = Float(
        help="""This parameter is the annual peak p value of all combined phases of the load""",
        default_value=None,
    )
    peak_q = Float(
        help="""This parameter is the annual peak q value of all combined phases of the load""",
        default_value=None,
    )
    peak_coincident_p = Float(
        help="""This parameter is the annual coincident peak p value of all combined phases of the load""",
        default_value=None,
    )
    peak_coincident_q = Float(
        help="""This parameter is the annual coincident peak q value of all combined phases of the load""",
        default_value=None,
    )
    yearly_energy = Float(
        help="""This is the total energy used by the load across all phases over a typical year""",
        default_value=None,
    )
    num_levels = Float(
        help="""The number of floors (levels) that the building load has""",
        default_value=None,
    )
    num_users = Float(
        help="""The number of users at the loadpoint""", default_value=None
    )

    # Modification: Nicolas (December 2017)
    # Multiple feeder support. Each element keeps track of the name of the substation it is connected to, as well as the name of the feeder.
    # I think we need both since a substation might have multiple feeders attached to it.
    # These attributes are filled once the DiTTo model has been created using the Network module
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
        default_value=None,
    )
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""", default_value=None
    )

    # Modification: Nicolas (December 2017)
    upstream_transformer_name = Unicode(
        help="""The name of the distribution transformer which serves this load""",
        default_value=None,
    )

    # Modification: Nicolas (May 2018)
    transformer_connected_kva = Float(
        help="""KVA of the distribution transformer which serves this load.""",
        default_value=None,
    )

    # Modification: Nicolas (May 2018)
    is_substation = Bool(
        help="""Flag that indicates wheter the element is inside a substation or not.""",
        default_value=False,
    )

    # Modification: Nicolas (July 2018)
    is_center_tap = Bool(
        help="""Flag that indicates whether the element is a center tap load or not.""",
    )
    center_tap_perct_1_N = Float(
        help="""Percentage of the load between active 1 and neutral. Should be a float between 0 and 1.""",
        default_value=None,
    )
    center_tap_perct_N_2 = Float(
        help="""Percentage of the load between neutal and active 2. Should be a float between 0 and 1.""",
        default_value=None,
    )
    center_tap_perct_1_2 = Float(
        help="""Percentage of the load between active 1 and active 2. Should be a float between 0 and 1.""",
        default_value=None,
    )

    def build(self, model):
        self._model = model
