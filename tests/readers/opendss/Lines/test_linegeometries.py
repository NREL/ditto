# -*- coding: utf-8 -*-

"""
test_linegeometries.py
----------------------------------

Tests for reading LineGeometries from OpenDSS into DiTTo.
"""

import os
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_linegeometries():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_linegeometries.dss"))
    r.parse(m)
    m.set_names()

    # Number of wires
    assert len(m["line1"].wires) == 4  # Line1 should have 4 wires

    # Phases of the different wires
    assert [w.phase for w in m["line1"].wires] == ["A", "B", "C", "N"]

    # Nameclass
    assert [w.nameclass for w in m["line1"].wires] == ["ACSR336"] * 3 + ["ACSR1/0"]

    # Positions of the wires
    assert [w.X for w in m["line1"].wires] == [
        -1.2909,
        -0.1530096 * 0.3048,
        0.5737,
        0.0,
    ]
    assert [w.Y for w in m["line1"].wires] == [
        13.716,
        4.1806368 * 0.3048,
        13.716,
        14.648,
    ]

    # GMR
    assert [w.gmr for w in m["line1"].wires] == [0.0255 * 0.3048] * 3 + [
        0.00446 * 0.3048
    ]

    # Diameter
    assert [w.diameter for w in m["line1"].wires] == [0.741 * 0.0254] * 3 + [
        0.398 * 0.0254
    ]

    # Resistance
    # TODO: Change this once the resistance of a Wire object will no longer be the total
    # resistance, but the per meter resistance...
    #
    assert np.allclose(
        [w.resistance for w in m["line1"].wires],
        [0.306 * 0.000621371 * 300 * 0.3048] * 3 + [1.12 * 0.000621371 * 300 * 0.3048],
    )
