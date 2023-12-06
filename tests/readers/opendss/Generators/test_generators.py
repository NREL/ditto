# -*- coding: utf-8 -*-

"""
test_generators.py
----------------------------------

Tests for parsing all values of Generators from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_generators():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_generators.dss"))
    r.parse(m)

    # Reading OpenDSS default values
    d_v = Default_Values(
        os.path.join(
            current_directory,
            "../../../../ditto/default_values/opendss_default_values.json",
        )
    )


    assert m["gen"].name == "gen"
    assert m["gen"].connecting_element == "powerbus1"
    assert m["gen"].forced_on == "No"
    assert m["gen"].power_factor == 0.95
    assert m["gen"].rated_power == 1.2 * 10 ** 3
    assert m["gen"].v_min_pu == 0.0
    assert m["gen"].v_max_pu == 1.2
    assert m["gen"].nominal_voltage == 2 * 10 ** 3
    assert m["gen"].feeder_name == "src_src"
    assert m["gen"].model == 3

test_generators()
