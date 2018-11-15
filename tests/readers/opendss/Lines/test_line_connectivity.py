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
    r = Reader(
        master_file=os.path.join(current_directory, "test_line_connectivity.dss")
    )
    r.parse(m)
    m.set_names()
    #    assert len(m["line1"].wires) == 4 # Number of wires # Neutral wire is not counted. TBD
    #    Phases of the different wires
    #    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C", "N"]) # Neutral wire is not counted. TBD
    assert m["line1"].nominal_voltage == float(4.16) * 10 ** 3
    #    assert m["line1"].line_type == "underground" # Default is overhead, ditto changed it to underground since it checks for OH in linecode
    assert m["line1"].length == 100
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].is_banked is None
    #    assert m["line1"].faultrate is None # 0.1
    #    assert m["line1"].positions is None  # []
    #    assert m["line1"].impedance_matrix is None # Value
    #    assert m["line1"].capacitance_matrix is None # Value
    assert m["line1"].substation_name is None
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None
    assert m["line1"].is_sectionalizer is None
    #    assert m["line1"].nameclass is None ## ''
    assert m["line1"].is_substation == 0  ## Value is 0, assumed None
    assert m["line1"].is_network_protector is None

    for w in m["line1"].wires:
        #        assert w.nameclass is None # Value is ''
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        #        assert w.ampacity is None # 400.0
        #        assert w.emergency_ampacity is None # 600.0
        assert w.resistance is None
        #        assert w.insulation_thickness is None # 0.0
        #        assert w.is_fuse is None # 0
        #        assert w.is_switch is None # 0
        assert w.is_open is None
        assert w.interrupting_rating is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
        assert w.drop == 0
        #        assert w.is_recloser is None # 0
        #        assert w.is_breaker is None # 0
        assert w.is_network_protector is None
        assert w.is_sectionalizer is None

    """
    assert m["line1"].from_element == "sourcebus"
    assert m["line1"].to_element == "bus1"

#    assert len(m["line2"].wires) == 4
    assert m["line2"].from_element == "bus1"
    assert m["line2"].to_element == "bus2"

    #assert len(m["line3"].wires) == 3
    assert m["line3"].from_element == "bus2"
    assert m["line3"].to_element == "bus3"

    #assert len(m["line4"].wires) == 3
    assert m["line4"].from_element == "bus3"
    assert m["line4"].to_element == "bus4"

    #assert len(m["line1"].wires) == 3
    assert m["line5"].from_element == "bus1"
    assert m["line5"].to_element == "bus5"
    assert (m["line5"].length) == float(1500 * 0.3048) #units = ft

    #assert len(m["line1"].wires) == 3
    assert m["line6"].from_element == "bus4"
    assert m["line6"].to_element == "bus6"

    #assert len(m["line1"].wires) == 3
    assert m["line7"].from_element == "bus1"
    assert m["line7"].to_element == "bus2"

"""
