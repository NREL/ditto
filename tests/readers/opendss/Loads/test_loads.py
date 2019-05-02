# -*- coding: utf-8 -*-

"""
test_loads.py
----------------------------------

Tests for parsing all values of Loads from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_loads():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_loads.dss"))
    r.parse(m)
    m.set_names()

    # Reading OpenDSS default values
    d_v = Default_Values(
        os.path.join(
            current_directory,
            "../../../../ditto/default_values/opendss_default_values.json",
        )
    )
    parsed_values = d_v.parse()

    precision = 0.001
    assert m["load_zipv"].name == "load_zipv"
    assert m["load_zipv"].connection_type == parsed_values["Load"]["connection_type"]
    assert m["load_zipv"].vmin == 0.0
    assert m["load_zipv"].vmax == 1.2
    assert m["load_zipv"].connecting_element == "load"
    assert m["load_zipv"].nominal_voltage == 1 * 10 ** 3
    assert m["load_zipv"].feeder_name == "src_src"
    assert m["load_zipv"].peak_coincident_p == None
    assert m["load_zipv"].peak_coincident_q == None
    assert len(m["load_zipv"].phase_loads) == 1  # Load is a one phase load
    assert m["load_zipv"].phase_loads[0].phase == "A"
    assert m["load_zipv"].phase_loads[0].p == 1 * 10 ** 3
    assert m["load_zipv"].phase_loads[0].q == pytest.approx(
        1.0 * math.sqrt(1.0 / 0.88 ** 2 - 1) * 10 ** 3, precision
    )
    assert m["load_zipv"].phase_loads[0].model == 8
    assert m["load_zipv"].phase_loads[0].use_zip == 1
    assert m["load_zipv"].phase_loads[0].ppercentcurrent == -0.9855 * 100
    assert m["load_zipv"].phase_loads[0].qpercentcurrent == -2.963 * 100
    assert m["load_zipv"].phase_loads[0].ppercentpower == 1.1305 * 100
    assert m["load_zipv"].phase_loads[0].qpercentpower == 1.404 * 100
    assert m["load_zipv"].phase_loads[0].ppercentimpedance == 0.855 * 100
    assert m["load_zipv"].phase_loads[0].qpercentimpedance == 2.559 * 100
