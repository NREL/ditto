# -*- coding: utf-8 -*-

"""
test_capacitor_connectivity.py
----------------------------------

Tests for parsing all the attributes of Capacitors when reading from OpenDSS to Ditto
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_capacitor_connectivity():
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_capacitor_connectivity.dss")
    )
    r.parse(m)
    m.set_names()

    assert len(m["cap1"].phase_capacitors) == 3  # Cap1 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["cap1"].phase_capacitors]
    ) == pytest.approx(600 * 10 ** 3, 0.0001)
    assert m["cap1"].nominal_voltage == float(4.16) * 10 ** 3
    #    assert m["cap1"].connection_type is None # Default is set as Y
    assert m["cap1"].delay is None
    assert m["cap1"].mode is None
    assert m["cap1"].low is None
    assert m["cap1"].high is None
    #    assert m["cap1"].resistance is None # 0.0
    assert m["cap1"].resistance0 is None
    #    assert m["cap1"].reactance is None # 0.0
    assert m["cap1"].reactance0 is None
    assert m["cap1"].susceptance is None
    assert m["cap1"].susceptance0 is None
    assert m["cap1"].conductance is None
    assert m["cap1"].conductance0 is None
    assert m["cap1"].pt_ratio is None
    assert m["cap1"].ct_ratio is None
    assert m["cap1"].pt_phase is None
    assert m["cap1"].connecting_element == "bus1"
    #    assert m["cap1"].positions is None # []
    assert m["cap1"].measuring_element is None
    #    assert m["cap1"].substation_name is None # ''
    assert m["cap1"].feeder_name == "sourcebus_src"
    assert m["cap1"].is_substation == 0

    assert set([pc.phase for pc in m["cap1"].phase_capacitors]) == set(["A", "B", "C"])
    assert [
        phase_capacitor.switch for phase_capacitor in m["cap1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.sections for phase_capacitor in m["cap1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.normalsections for phase_capacitor in m["cap1"].phase_capacitors
    ] == [None, None, None]

    assert len(m["cap2"].phase_capacitors) == 1  # Cap2 is a one phase capacitor
    assert m["cap2"].phase_capacitors[0].var == 100 * 10 ** 3

    assert len(m["cap3"].phase_capacitors) == 1  # Cap3 is a one phase capacitor
    assert m["cap3"].phase_capacitors[0].var == 200.37 * 10 ** 3

    assert len(m["cap4"].phase_capacitors) == 2  # Cap4 is a two phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["cap4"].phase_capacitors]
    ) == pytest.approx(400 * 10 ** 3, 0.0001)
