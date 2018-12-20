# -*- coding: utf-8 -*-

"""
test_load_p_and_q.py
----------------------------------

Tests for parsing P and Q values of Loads from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_load_p_and_q():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_load_p_and_q.dss"))
    r.parse(m)
    m.set_names()

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
