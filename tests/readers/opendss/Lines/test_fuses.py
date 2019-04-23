# -*- coding: utf-8 -*-

"""
test_fuses.py
----------------------------------

Tests for fuse attribute of Line
"""
import logging
import os

import six

import tempfile
import pytest as pt
import json

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_fuses():
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader
    from ditto.default_values.default_values_json import Default_Values

    # test on the test_fuses.dss
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_fuses.dss"))
    r.parse(m)
    m.set_names()

    # Reading OpenDSS default values
    d_v = Default_Values(
        os.path.join(
            current_directory,
            "../../../../ditto/default_values/opendss_default_values.json",
        )
    )
    parsed_values = d_v.parse()

    assert len(m["origin"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["origin"].wires]) == set(["A", "B", "C"])
    assert m["origin"].name == "origin"
    assert m["origin"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["origin"].line_type == None
    assert m["origin"].length == 0.001 * 1000  # units = km
    assert m["origin"].from_element == "sourcebus"
    assert m["origin"].to_element == "node1"
    assert m["origin"].is_fuse is None
    assert m["origin"].is_switch is None
    assert m["origin"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["origin"].impedance_matrix == [
        [
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.470000000000001e-05j),
            (4.013333e-05 + 9.470000000000001e-05j),
        ],
        [
            (4.013333e-05 + 9.470000000000001e-05j),
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.470000000000001e-05j),
        ],
        [
            (4.013333e-05 + 9.470000000000001e-05j),
            (4.013333e-05 + 9.470000000000001e-05j),
            (9.813333e-05 + 0.0002153j),
        ],
    ]  # units = km
    assert m["origin"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (-0.0006 + 0j), (0.0028 + 0j)],
    ]  # units = km
    assert m["origin"].feeder_name == "sourcebus_src"
    assert m["origin"].is_recloser is None
    assert m["origin"].is_breaker is None
    assert m["origin"].nameclass == ""

    for w in m["origin"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line1"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C"])
    assert m["line1"].name == "line1"
    assert m["line1"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line1"].line_type == None
    assert m["line1"].length == 0.001 * 1000  # units = km
    assert m["line1"].from_element == "node1"
    assert m["line1"].to_element == "node2"
    assert m["line1"].is_fuse == 1
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line1"].impedance_matrix == [
        [
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.470000000000001e-05j),
            (4.013333e-05 + 9.470000000000001e-05j),
        ],
        [
            (4.013333e-05 + 9.470000000000001e-05j),
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.470000000000001e-05j),
        ],
        [
            (4.013333e-05 + 9.470000000000001e-05j),
            (4.013333e-05 + 9.470000000000001e-05j),
            (9.813333e-05 + 0.0002153j),
        ],
    ]  # units = km
    assert m["line1"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (-0.0006 + 0j), (0.0028 + 0j)],
    ]  # units = km
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None
    assert m["line1"].nameclass == "line1"

    for w in m["line1"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line2"].wires) == 1  # Number of wires
    # Phases of the different wires
    assert m["line2"].wires[0].phase == "A"
    assert m["line2"].name == "line2"
    assert m["line2"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line2"].line_type == None
    assert m["line2"].length == 0.001 * 1000  # units = km
    assert m["line2"].from_element == "node1"
    assert m["line2"].to_element == "node3"
    assert m["line2"].is_fuse == 1
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line2"].impedance_matrix == [[(5.8e-05 + 0.0001206j)]]  # units = km
    assert m["line2"].capacitance_matrix == [[(0.0034 + 0j)]]  # units = km
    assert m["line2"].feeder_name == "sourcebus_src"
    assert m["line2"].is_recloser is None
    assert m["line2"].is_breaker is None
    assert m["line2"].nameclass == "line2"

    for w in m["line2"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line3"].wires) == 1
    # Phases of the different wires
    assert m["line3"].wires[0].phase == "C"
    assert m["line3"].name == "line3"
    assert m["line3"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line3"].line_type == None
    assert m["line3"].length == 0.001 * 1000  # units = km
    assert m["line3"].from_element == "node1"
    assert m["line3"].to_element == "node4"
    assert m["line3"].is_fuse == 1
    assert m["line3"].is_switch is None
    assert m["line3"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line3"].impedance_matrix == [[(5.8e-05 + 0.0001206j)]]  # units = km
    assert m["line3"].capacitance_matrix == [[(0.0034 + 0j)]]  # units = km
    assert m["line3"].feeder_name == "sourcebus_src"
    assert m["line3"].is_recloser is None
    assert m["line3"].is_breaker is None
    assert m["line3"].nameclass == "line3"

    for w in m["line3"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line4"].wires) == 2
    # Phases of the different wires
    assert set([w.phase for w in m["line4"].wires]) == set(["B", "C"])
    assert m["line4"].name == "line4"
    assert m["line4"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line4"].line_type == None
    assert m["line4"].length == 0.001 * 1000  # units = km
    assert m["line4"].from_element == "node1"
    assert m["line4"].to_element == "node4"
    assert m["line4"].is_fuse == 1
    assert m["line4"].is_switch is None
    assert m["line4"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line4"].impedance_matrix == [
        [(9.813333e-05 + 0.0002153j), (4.013333e-05 + 9.470000000000001e-05j)],
        [(4.013333e-05 + 9.470000000000001e-05j), (9.813333e-05 + 0.0002153j)],
    ]  # units = km
    assert m["line4"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j)],
    ]  # units = km
    assert m["line4"].feeder_name == "sourcebus_src"
    assert m["line4"].is_recloser is None
    assert m["line4"].is_breaker is None
    assert m["line4"].nameclass == "line4"

    for w in m["line4"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
