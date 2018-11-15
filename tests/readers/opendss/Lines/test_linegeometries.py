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
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C", "N"])

    phased_wires = {}
    for wire in m["line1"].wires:
        phased_wires[wire.phase] = wire

    # Nameclass
    for p in ["A", "B", "C"]:
        assert phased_wires[p].nameclass == "ACSR336"
    assert phased_wires["N"].nameclass == "ACSR1/0"

    # Positions of the wires
    assert (phased_wires["A"].X, phased_wires["A"].Y) == (-1.2909, 13.716)
    assert (phased_wires["B"].X, phased_wires["B"].Y) == (
        -0.1530096 * 0.3048,
        4.1806368 * 0.3048,
    )
    assert (phased_wires["C"].X, phased_wires["C"].Y) == (0.5737, 13.716)
    assert (phased_wires["N"].X, phased_wires["N"].Y) == (0.0, 14.648)

    # GMR
    for p in ["A", "B", "C"]:
        assert phased_wires[p].gmr == 0.0255 * 0.3048
    assert phased_wires["N"].gmr == 0.00446 * 0.3048

    # Diameter
    for p in ["A", "B", "C"]:
        assert phased_wires[p].diameter == 0.741 * 0.0254
    assert phased_wires["N"].diameter == 0.398 * 0.0254

    # Resistance
    # TODO: Change this once the resistance of a Wire object will no longer be the total
    # resistance, but the per meter resistance...
    #
    for p in ["A", "B", "C"]:
        assert phased_wires[p].resistance == pytest.approx(
            0.306 * 0.000621371 * 300 * 0.3048, 0.00001
        )
    assert phased_wires["N"].resistance == pytest.approx(
        1.12 * 0.000621371 * 300 * 0.3048, 0.00001
    )

    assert len(m["line2"].wires) == 3  # Line1 should have 3 wires
    assert set([w.phase for w in m["line2"].wires]) == set(["A", "B", "C"])

    phased_wires = {}
    for wire in m["line2"].wires:
        phased_wires[wire.phase] = wire

    # Nameclass
    for p in ["A", "B", "C"]:
        assert phased_wires[p].nameclass == "250_1/3"

    #    for p in ["A", "B", "C"]:
    #        assert phased_wires[p].concentric_neutral_resistance ==  pytest.approx(
    #            0.076705 * 0.000621371 * 300 * 0.3048, 0.00001
    #        )

    for p in ["A", "B", "C"]:
        assert phased_wires[p].concentric_neutral_diameter == 0.064 * 0.0254

    for p in ["A", "B", "C"]:
        assert phased_wires[p].concentric_neutral_outside_diameter == 1.16 * 0.0254

    for p in ["A", "B", "C"]:
        assert phased_wires[p].concentric_neutral_nstrand == 13
