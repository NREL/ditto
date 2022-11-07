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
from numpy import testing as npt

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
    m.set_names()

    assert m["Vsource.source"].name == "Vsource.source"
    assert m["Vsource.source"].nominal_voltage == 230.0 * 10 ** 3
    assert m["Vsource.source"].per_unit == 0.99
    assert m["Vsource.source"].is_sourcebus == 1
    assert m["Vsource.source"].rated_power == 150000000.0
    #  MVASc3 = baseKVA^2 / Z1 ; Z1 = sqrt( r1^2 + x1^2)
    emerg_power = int((230.0) ** 2 / math.sqrt(1.1208 ** 2 + 3.5169 ** 2)) * 10 ** 6 
    npt.assert_almost_equal(m["Vsource.source"].emergency_power/10e9, emerg_power/10e9, decimal=4)

    assert m["Vsource.source"].zero_sequence_impedance == 1.1208 + 3.5169j
    assert m["Vsource.source"].positive_sequence_impedance == 1.1208 + 3.5169j
    assert m["Vsource.source"].connecting_element == "sourcebus"
    assert m["Vsource.source"].phases[0].default_value == "A"
    assert m["Vsource.source"].phases[1].default_value == "B"
    assert m["Vsource.source"].phases[2].default_value == "C"
    assert (m["Vsource.source"].positions[0].long) == float(200)
    assert (m["Vsource.source"].positions[0].lat) == float(400)
