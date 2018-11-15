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

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_loads():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_loads.dss"))
    r.parse(m)
    m.set_names()

    precision = 0.001
    #    assert m["load_load_zipv"].connection_type == None # Y
    assert m["load_zipv"].vmin == 0.0
    assert m["load_zipv"].vmax == 1.2
    assert m["load_zipv"].connecting_element == "load"
    assert m["load_zipv"].nominal_voltage == 1 * 10 ** 3
    #    assert m["load_zipv"].num_users == None # 1.0
    assert m["load_zipv"].feeder_name == "src_src"

    #    assert m["load_zipv"].positions == None # []
    #    assert m["load_zipv"].timeseries == None # []
    assert m["load_zipv"].rooftop_area == None
    assert m["load_zipv"].peak_p == None
    assert m["load_zipv"].peak_q == None
    assert m["load_zipv"].peak_coincident_p == None
    assert m["load_zipv"].peak_coincident_q == None
    assert m["load_zipv"].yearly_energy == None
    assert m["load_zipv"].num_levels == None
    assert m["load_zipv"].substation_name == None
    assert m["load_zipv"].upstream_transformer_name == None
    assert m["load_zipv"].transformer_connected_kva == None
    assert m["load_zipv"].is_substation == 0
    assert m["load_zipv"].is_center_tap == None
    assert m["load_zipv"].center_tap_perct_1_N == None
    assert m["load_zipv"].center_tap_perct_N_2 == None
    assert m["load_zipv"].center_tap_perct_1_2 == None

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
    assert m["load_zipv"].phase_loads[0].drop == 0


"""
    # P and Q values should be equally divided accross phase loads
    # Here we sum P and Q and check that the obtained values match the values in the DSS file
    #
    precision = 0.001
    assert len(m["load_load1"].phase_loads) == 3  # Load1 is a three phase load
    assert sum(
        [phase_load.p for phase_load in m["load_load1"].phase_loads]
    ) == pytest.approx(5400 * 10 ** 3, precision)
    assert sum(
        [phase_load.q for phase_load in m["load_load1"].phase_loads]
    ) == pytest.approx(4285 * 10 ** 3, precision)

    assert len(m["load_load2"].phase_loads) == 3  # Load2 is a three phase load
    assert sum(
        [phase_load.p for phase_load in m["load_load2"].phase_loads]
    ) == pytest.approx(3466 * 10 ** 3, precision)
    assert sum(
        [phase_load.q for phase_load in m["load_load2"].phase_loads]
    ) == pytest.approx(3466.0 * math.sqrt(1.0 / 0.9 ** 2 - 1) * 10 ** 3, precision)

    assert len(m["load_load3"].phase_loads) == 2  # Load3 is a two phase load
    assert sum(
        [phase_load.p for phase_load in m["load_load3"].phase_loads]
    ) == pytest.approx(1600 * 10 ** 3, precision)
    assert sum(
        [phase_load.q for phase_load in m["load_load3"].phase_loads]
    ) == pytest.approx(980 * 10 ** 3, precision)

    assert len(m["load_load4"].phase_loads) == 2  # Load4 is a two phase load
    assert sum(
        [phase_load.p for phase_load in m["load_load4"].phase_loads]
    ) == pytest.approx(1555 * 10 ** 3, precision)
    assert sum(
        [phase_load.q for phase_load in m["load_load4"].phase_loads]
    ) == pytest.approx(1555.0 * math.sqrt(1.0 / 0.95 ** 2 - 1) * 10 ** 3, precision)

    assert len(m["load_load5"].phase_loads) == 1  # Load5 is a one phase load
    assert sum(
        [phase_load.p for phase_load in m["load_load5"].phase_loads]
    ) == pytest.approx(650 * 10 ** 3, precision)
    assert sum(
        [phase_load.q for phase_load in m["load_load5"].phase_loads]
    ) == pytest.approx(500.5 * 10 ** 3, precision)

    assert len(m["load_load6"].phase_loads) == 1  # Load6 is a one phase load
    assert sum(
        [phase_load.p for phase_load in m["load_load6"].phase_loads]
    ) == pytest.approx(623.21 * 10 ** 3, precision)
    assert sum(
        [phase_load.q for phase_load in m["load_load6"].phase_loads]
    ) == pytest.approx(623.21 * math.sqrt(1.0 / 0.85 ** 2 - 1) * 10 ** 3, precision)

"""
