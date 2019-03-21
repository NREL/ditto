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

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_powersource():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_powersource.dss"))
    r.parse(m)
    m.set_names()

    assert m["Vsource.source"].name == "Vsource.source"
    assert m["Vsource.source"].nominal_voltage == 230.0 * 10 ** 3
    assert m["Vsource.source"].per_unit == 0.99
    assert m["Vsource.source"].is_sourcebus == 1
    #    assert m["Vsource.source"].rated_power == None # 100000000.0
    #    assert m["Vsource.source"].emergency_power == None # 14331000000.0
    assert m["Vsource.source"].zero_sequence_impedance == 1.1208 + 3.5169j
    assert m["Vsource.source"].positive_sequence_impedance == 1.1208 + 3.5169j
    #    assert m["Vsource.source"].phase_angle == None # 0.0 # To be deprecated
    assert m["Vsource.source"].connecting_element == "st_mat"

    # assert (m["Vsource.source"].phases) == set(["A", "B", "C"])
    # assert (m["Vsource.source"].phases[1].default_value) == "B"
    # assert (m["Vsource.source"].phases[2].default_value) == "C"
    # assert (m["Vsource.source"].positions[0].long) == float(200)
    # assert (m["Vsource.source"].positions[0].lat) == float(400)
    # assert (m["Vsource.source"].positions[0].elevation) == 0
    # assert m["Vsource.source"].connection_type == None # To be deprecated
    # assert m["Vsource.source"].cutout_percent == None # To be deprecated
    # assert m["Vsource.source"].cutin_percent == None  # To be deprecated
    # assert m["Vsource.source"].resistance == None # To be deprecated
    # assert m["Vsource.source"].reactance == None # To be deprecated
    # assert m["Vsource.source"].v_max_pu == None # To be deprecated
    # assert m["Vsource.source"].v_min_pu == None # To be deprecated
    # assert m["Vsource.source"].power_factor == None # To be deprecated
