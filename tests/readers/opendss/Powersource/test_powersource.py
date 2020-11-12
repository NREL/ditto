# -*- coding: utf-8 -*-

"""
test_powersource.py
----------------------------------

Tests for parsing all values of power source from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.models.power_source import PowerSource
from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_powersource():
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_powersource.dss"),
        buscoordinates_file=os.path.join(current_directory, "buscoord.dss"),
    )
    r.parse(m)

    element = m.get_element(PowerSource, "Vsource.source")
    assert element.name == "Vsource.source"
    assert element.nominal_voltage == 230.0 * 10 ** 3
    assert element.per_unit == 0.99
    assert element.is_sourcebus == 1
    assert element.rated_power == 150000000.0
    #  MVASc3 = baseKVA^2 / Z1 ; Z1 = sqrt( r1^2 + x1^2)
    emerg_power = int((230.0) ** 2 / math.sqrt(1.1208 ** 2 + 3.5169 ** 2)) * 10 ** 6
    assert element.emergency_power == emerg_power
    assert element.zero_sequence_impedance == 1.1208 + 3.5169j
    assert element.positive_sequence_impedance == 1.1208 + 3.5169j
    assert element.connecting_element == "sourcebus"
    assert element.phases[0].default_value == "A"
    assert element.phases[1].default_value == "B"
    assert element.phases[2].default_value == "C"
    assert element.positions[0].long == 200.0
    assert element.positions[0].lat == 400.0
