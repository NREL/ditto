# -*- coding: utf-8 -*-

"""
test_pvsystems.py
----------------------------------

Tests for parsing all values of PVsystem from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_pvsystem():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_pvsystem.dss"))
    r.parse(m)
    m.set_names()

    # Reading OpenDSS default values
    '''d_v = Default_Values(
        os.path.join(
            current_directory,
            "../../../../ditto/default_values/opendss_default_values.json",
        )
    )


    parsed_values = d_v.parse()'''


    assert m["pvsystem.pv680"].name == "pvsystem.pv680"
    assert m["pvsystem.pv680"].connecting_element == "trafo_pv_680"
    assert m["pvsystem.pv680"].nominal_voltage == 0.48 * 10 ** 3
    assert m["pvsystem.pv680"].rated_power == 500.0 * 10 ** 3
    assert m["pvsystem.pv680"].phases[0].default_value == 'C'
    assert m["pvsystem.pv680"].control_type == "wye"
    assert m["pvsystem.pv680"].resistance == 50.0
    assert m["pvsystem.pv680"].reactance == 0.0
    assert m["pvsystem.pv680"].temperature == 25.0
    assert m["pvsystem.pv680"].cutout_percent == 0.1
    assert m["pvsystem.pv680"].cutin_percent == 0.1
    assert m["pvsystem.pv680"].feeder_name == "sourcebus_src"
    assert m["pvsystem.pv680"].v_max_pu == 1.1
    assert m["pvsystem.pv680"].v_min_pu == 0.9
    assert m["pvsystem.pv680"].min_power_factor == -1.0
    assert m["pvsystem.pv680"].power_factor == -1.0
