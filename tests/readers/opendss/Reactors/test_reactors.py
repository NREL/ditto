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

    assert m["reactor.714"].name == "reactor.714"
    assert m["reactor.714"].nominal_voltage == 12.47 * 10 **3
    assert m["reactor.714"].to_element == "714"
    assert m["reactor.714"].from_element == "700t1"
    assert m["reactor.714"].connection_type == "Y"
    assert m["reactor.714"].faultrate == 0.0005
    assert m["reactor.714"].phase_reactors[0].phase == "A"
    assert m["reactor.714"].phase_reactors[1].phase == "B"
    assert m["reactor.714"].phase_reactors[2].phase == "C"
