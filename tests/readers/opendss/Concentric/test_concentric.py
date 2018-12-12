# -*- coding: utf-8 -*-

"""
test_line_connectivity.py
----------------------------------

Tests for checking the line connectivity and all the attributes of line and wire
"""
import logging
import os

import six

import tempfile
import pytest as pt

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_line_connectivity():
    """Tests if line length units are in meters."""
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader

    # test on the test_line_connectivity.dss
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_concentric.dss"))
    r.parse(m)
    m.set_names()

    assert m["line1"].name == "line1"
    assert (
        len(m["line1"].wires) == 4
    )  # Number of wires # Neutral wire is not counted. TBD
    #    Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(
        ["A", "B", "C", "N"]
    )  # Neutral wire is not counted. TBD
    assert m["line1"].from_element == "bus1"
    assert m["line1"].to_element == "bus2"
    assert m["line1"].nominal_voltage == float(13.200000000000001) * 10 ** 3
    assert m["line1"].line_type == "underground"
    assert m["line1"].length == pt.approx(0.14602968000000002 * 1000)
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].is_banked is None
    assert m["line1"].faultrate == 0.1
    # assert m["line1"].positions is None  # []
    # assert m["line1"].impedance_matrix is None #  [[(3.889112e-05+6.05343e-05j), (-6.045299e-10-1.058095e-09j), (-3.3978949999999997e-10-5.525341e-10j)], [(-6.045299e-1....656239e-09j)], [(-3.3978949999999997e-10-5.525341e-10j), (-8.839466e-10-1.656239e-09j), (3.889101e-05+6.053392e-05j)]]
    # assert m["line1"].capacitance_matrix is None #  [[(0.4063406+0j), 0j, 0j], [0j, (0.4063406+0j), 0j], [0j, 0j, (0.4063406+0j)]]
    assert m["line1"].substation_name is None
    assert m["line1"].feeder_name == "cnbus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None
    assert m["line1"].is_sectionalizer is None
    assert m["line1"].nameclass == ""
    assert m["line1"].is_substation == 0
    assert m["line1"].is_network_protector is None

    for w in m["line1"].wires:
        assert w.nameclass == "cndata1"
        assert w.X == 0.0
        assert w.Y == pt.approx(-0.9144000000000001)
        # assert w.diameter == 0.0285496
        # assert w.gmr == 0.0111252
        # assert w.ampacity is None # -1.0
        # assert w.emergency_ampacity is None # -1.0
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_fuse == 0
        assert w.is_switch is None
        assert w.is_open is None
        assert w.interrupting_rating is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
        assert w.drop == 0
        assert w.is_recloser == 0
        assert w.is_breaker == 0
        assert w.is_network_protector is None
        assert w.is_sectionalizer is None
