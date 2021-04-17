# -*- coding: utf-8 -*-

"""
test_capacitor_kvar.py
----------------------------------

Tests for parsing kvar values of Capacitors from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_capacitor_kvar():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_capacitor_kvar.dss"))
    r.parse(m)

    assert len(m["cap1"].phase_capacitors) == 3  # Cap1 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["cap1"].phase_capacitors]
    ) == pytest.approx(600 * 10 ** 3, 0.0001)

    assert len(m["cap2"].phase_capacitors) == 1  # Cap2 is a one phase capacitor
    assert m["cap2"].phase_capacitors[0].var == 100 * 10 ** 3

    assert len(m["cap3"].phase_capacitors) == 1  # Cap3 is a one phase capacitor
    assert m["cap3"].phase_capacitors[0].var == 200.37 * 10 ** 3
