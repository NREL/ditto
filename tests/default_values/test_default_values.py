# -*- coding: utf-8 -*-

"""
test_default_values.py
----------------------------------

Tests for assigning default values for Line
"""

import os
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_default_values():
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_default_values.dss"),
        default_values_file=os.path.join(current_directory, "test_default_values.json"),
    )
    r.parse(m)
    m.set_names()

    assert m["line1"].faultrate == 0.2

    assert m["line1"].impedance_matrix == [
        [(0.00113148 + 0.000884886j), (0.000142066 + 0.000366115j)],
        [(0.000142066 + 0.000366115j), (0.00113362 + 0.000882239j)],
    ]

    assert m["line1"].capacitance_matrix == [
        [(0.00733718 + 0j), (-0.00239809 + 0j)],
        [(-0.00239809 + 0j), (0.00733718 + 0j)],
    ]

    phased_wires = {}
    for wire in m["line1"].wires:
        phased_wires[wire.phase] = wire

    # Ampacity
    for p in ["A", "B", "C"]:
        assert phased_wires[p].ampacity == 200
        assert phased_wires[p].emergency_ampacity == 400

    assert m["cap1"].connection_type == "Y"
    assert m["cap1"].low == 114
    assert m["cap1"].high == 125
    assert m["cap1"].delay == 10
    assert m["cap1"].pt_ratio == 50
    assert m["cap1"].ct_ratio == 50
    assert m["cap1"].pt_phase == "A"

    assert m["reg1"].reactances == [6]

    assert m["regulator_reg1"].ct_prim == 300
    assert m["regulator_reg1"].delay == 16
    assert m["regulator_reg1"].highstep == 15
    assert m["regulator_reg1"].pt_ratio == 60
    assert m["regulator_reg1"].bandwidth == 3
    assert m["regulator_reg1"].bandcenter == 130

    assert m["load_load1"].connection_type == "Y"
    assert m["load_load1"].vmin == 0.95
    assert m["load_load1"].vmax == 1.05
