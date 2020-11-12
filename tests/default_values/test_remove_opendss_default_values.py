# -*- coding: utf-8 -*-

"""
test_remove_opendss_default_values.py
----------------------------------

Tests for checking the remove_opendss_default_values option.
"""

import os
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_remove_opendss_default_values():
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_default_values.dss"),
        remove_opendss_default_values_flag=True,
    )
    r.parse(m)

    assert m["line1"].faultrate == None
    assert m["line1"].impedance_matrix == None
    assert m["line1"].capacitance_matrix == None

    assert m["cap1"].connection_type == None
    assert m["cap1"].low == None
    assert m["cap1"].high == None
    assert m["cap1"].delay == None
    assert m["cap1"].pt_ratio == None
    assert m["cap1"].ct_ratio == None
    assert m["cap1"].pt_phase == None

    assert m["reg1"].reactances == None

    assert m["regulator_reg1"].ct_prim == None
    assert m["regulator_reg1"].delay == None
    assert m["regulator_reg1"].highstep == None
    assert m["regulator_reg1"].pt_ratio == None
    assert m["regulator_reg1"].bandwidth == None
    assert m["regulator_reg1"].bandcenter == None

    assert m["load_load1"].connection_type == None
    assert m["load_load1"].vmin == None
    assert m["load_load1"].vmax == None
