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
    observe,
    Instance,
    Complex,
    Bool,
)

from .position import Position


class Generator(DiTToHasTraits):

    name = Unicode(help="""Name of the power source object""")
    nominal_voltage = Float(
        help="""This parameter defines the base voltage at the power source.""",
        default_value=None,
    )
    connecting_element = Unicode(
        help="""Name of the bus the generator is connected to.""", default_value=None
    )
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
        default_value=None,
    )
    forced_on = Unicode(
        help="""Check if generator active.""",
        default_value=None
    )
    model = Int(
        help="""Type of generator.""",
        default_value=None
    )
    power_factor = Float(
        help="""Default power factor. In watts.""",
        default_value=None,       
    )
    rated_power = Float(
        help="""Rated power of the device. In watts.""", default_value=None
    )
    phases = List(
        Instance(Unicode),
        help="""This parameter is a list of all the phases at the power source.""",
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the power source - it should only contain one. The positions are objects containing elements of long, lat and elevation.""",
    )
    v_max_pu = Float(
        help="""The per-unit maximum voltage. Beyond this constant impedance model is applied""",
        default_value=None,
    )
    v_min_pu = Float(
        help="""The per-unit minimum voltage. Below this, constant impedance model is applied""",
        default_value=None,
    )
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""", default_value=None
    )

    def build(self, model):
        self._model = model
