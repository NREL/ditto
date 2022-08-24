# -*- coding: utf-8 -*-

"""
test_pvsystems.py
----------------------------------

Tests for parsing all values of PVsystem from OpenDSS into DiTTo.
"""

import os
import math
from ditto.models.base import Unicode
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))

def test_reactor():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_reactors.dss"))
    r.parse(m)
    m.set_names()

    assert m["generator.pv633_1"].name == "generator.pv633_1"
    assert m["generator.pv633_1"].nominal_voltage == 0.48 * 10 ** 3
    assert m["generator.pv633_1"].from_element == "pv_633"
    assert m["generator.pv633_1"].connection_type == 'Y'
    assert m["generator.pv633_1"].feeder_name == "sourcebus_src"
    assert m["generator.pv633_1"].phase_reactors[0].phase == "A"
    assert m["generator.pv633_1"].phase_reactors[1].phase == "B"
    assert m["generator.pv633_1"].phase_reactors[2].phase == "C"
