# -*- coding: utf-8 -*-

"""
test_line_length.py
----------------------------------

Tests for checking the line length values are all in meters.
"""
import logging
import os

import six

import tempfile
import pytest as pt
import json

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_line_length():
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader
    from ditto.readers.json.read import Reader as json_reader
    from ditto.default_values.default_values_json import Default_Values

    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_line_length.dss"))
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

    # Line 1 is a 100 meters 3 phase line
    assert len(m["line1"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C"])
    assert m["line1"].name == "line1"
    assert m["line1"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line1"].line_type == "underground"
    assert m["line1"].length == float(100)  # Units = meters
    assert m["line1"].from_element == "sourcebus"
    assert m["line1"].to_element == "bus1"
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line1"].impedance_matrix == [
        [(0.09813333 + 0.2153j), (0.04013333 + 0.0947j), (0.04013333 + 0.0947j)],
        [(0.04013333 + 0.0947j), (0.09813333 + 0.2153j), (0.04013333 + 0.0947j)],
        [(0.04013333 + 0.0947j), (0.04013333 + 0.0947j), (0.09813333 + 0.2153j)],
    ]
    assert m["line1"].capacitance_matrix == [
        [(2.8 + 0j), (-0.6 + 0j), (-0.6 + 0j)],
        [(-0.6 + 0j), (2.8 + 0j), (-0.6 + 0j)],
        [(-0.6 + 0j), (-0.6 + 0j), (2.8 + 0j)],
    ]
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None
    assert m["line1"].nameclass == ""

    for w in m["line1"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line 2 is a 83.47 kilo-feet 3 phase line
    assert len(m["line2"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line2"].wires]) == set(["A", "B", "C"])
    assert m["line2"].name == "line2"
    assert m["line2"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line2"].line_type == "underground"
    assert m["line2"].length == float(83.47 * 304.8)  # units = kft
    assert m["line2"].from_element == "bus1"
    assert m["line2"].to_element == "bus2"
    assert m["line2"].is_fuse is None
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line2"].impedance_matrix == [
        [
            (0.0003219597440944882 + 0.0007063648293963254j),
            (0.00013167103018372703 + 0.0003106955380577428j),
            (0.00013167103018372703 + 0.0003106955380577428j),
        ],
        [
            (0.00013167103018372703 + 0.0003106955380577428j),
            (0.0003219597440944882 + 0.0007063648293963254j),
            (0.00013167103018372703 + 0.0003106955380577428j),
        ],
        [
            (0.00013167103018372703 + 0.0003106955380577428j),
            (0.00013167103018372703 + 0.0003106955380577428j),
            (0.0003219597440944882 + 0.0007063648293963254j),
        ],
    ]  # units = kft
    assert m["line2"].capacitance_matrix == [
        [
            (0.009186351706036745 + 0j),
            (-0.001968503937007874 + 0j),
            (-0.001968503937007874 + 0j),
        ],
        [
            (-0.001968503937007874 + 0j),
            (0.009186351706036745 + 0j),
            (-0.001968503937007874 + 0j),
        ],
        [
            (-0.001968503937007874 + 0j),
            (-0.001968503937007874 + 0j),
            (0.009186351706036745 + 0j),
        ],
    ]  # units = kft
    assert m["line2"].feeder_name == "sourcebus_src"
    assert m["line2"].is_recloser is None
    assert m["line2"].is_breaker is None
    assert m["line2"].nameclass == ""

    for w in m["line2"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 3 is a 200 feet 2 phases line
    assert len(m["line3"].wires) == 2
    # Phases of the different wires
    assert set([w.phase for w in m["line3"].wires]) == set(["A", "C"])
    assert m["line3"].name == "line3"
    assert m["line3"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line3"].line_type == "underground"
    assert m["line3"].length == float(200 * 0.3048)  # units = ft
    assert m["line3"].from_element == "bus2"
    assert m["line3"].to_element == "bus3"
    assert m["line3"].is_fuse is None
    assert m["line3"].is_switch is None
    assert m["line3"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line3"].impedance_matrix == [
        [
            (0.3219597440944882 + 0.7063648293963254j),
            (0.13167103018372703 + 0.3106955380577428j),
        ],
        [
            (0.13167103018372703 + 0.3106955380577428j),
            (0.3219597440944882 + 0.7063648293963254j),
        ],
    ]  # units = ft
    assert m["line3"].capacitance_matrix == [
        [(9.186351706036744 + 0j), (-1.9685039370078738 + 0j)],
        [(-1.9685039370078738 + 0j), (9.186351706036744 + 0j)],
    ]  # units = ft
    assert m["line3"].feeder_name == "sourcebus_src"
    assert m["line3"].is_recloser is None
    assert m["line3"].is_breaker is None
    assert m["line3"].nameclass == ""

    for w in m["line3"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line 4 is a 1.01 miles 1 phase line
    assert len(m["line4"].wires) == 1
    # Phases of the different wires
    assert m["line4"].wires[0].phase == "B"
    assert m["line4"].name == "line4"
    assert m["line4"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line4"].line_type == "underground"
    assert m["line4"].length == float(1.01 * 1609.34)  # units = mi
    assert m["line4"].from_element == "bus2"
    assert m["line4"].to_element == "bus4"
    assert m["line4"].is_fuse is None
    assert m["line4"].is_switch is None
    assert m["line4"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line4"].impedance_matrix == [
        [(3.60396187256888e-05 + 7.49375520399667e-05j)]
    ]  # units = mi
    assert m["line4"].capacitance_matrix == [
        [(0.002112667304609343 + 0j)]
    ]  # units = mi
    assert m["line4"].feeder_name == "sourcebus_src"
    assert m["line4"].is_recloser is None
    assert m["line4"].is_breaker is None
    assert m["line4"].nameclass == ""

    for w in m["line4"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line 5 is a 2040.12 centimeters 3 phase line
    assert len(m["line5"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line5"].wires]) == set(["A", "B", "C"])
    assert m["line5"].name == "line5"
    assert m["line5"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line5"].line_type == "underground"
    assert m["line5"].length == float(2040.12 * 0.01)  # units = cm
    assert m["line5"].from_element == "bus2"
    assert m["line5"].to_element == "bus5"
    assert m["line5"].is_fuse is None
    assert m["line5"].is_switch is None
    assert m["line5"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line5"].impedance_matrix == [
        [(9.813333 + 21.529999999999998j), (4.013333 + 9.47j), (4.013333 + 9.47j)],
        [(4.013333 + 9.47j), (9.813333 + 21.529999999999998j), (4.013333 + 9.47j)],
        [(4.013333 + 9.47j), (4.013333 + 9.47j), (9.813333 + 21.529999999999998j)],
    ]  # units = cm
    assert m["line5"].capacitance_matrix == [
        [(280 + 0j), (-60 + 0j), (-60 + 0j)],
        [(-60 + 0j), (280 + 0j), (-60 + 0j)],
        [(-60 + 0j), (-60 + 0j), (280 + 0j)],
    ]  # units = cm
    assert m["line5"].feeder_name == "sourcebus_src"
    assert m["line5"].is_recloser is None
    assert m["line5"].is_breaker is None
    assert m["line5"].nameclass == ""

    for w in m["line5"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line 6 is a 1666.87 inches 1 phase line
    assert len(m["line6"].wires) == 1
    # Phases of the different wires
    assert m["line6"].wires[0].phase == "A"
    assert m["line6"].name == "line6"
    assert m["line6"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line6"].line_type == "underground"
    assert m["line6"].length == float(1666.87 * 0.0254)  # units = in
    assert m["line6"].from_element == "bus2"
    assert m["line6"].to_element == "bus6"
    assert m["line6"].is_fuse is None
    assert m["line6"].is_switch is None
    assert m["line6"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line6"].impedance_matrix == [
        [(2.2834645669291342 + 4.748031496062993j)]
    ]  # units = in
    assert m["line6"].capacitance_matrix == [[(133.85826771653544 + 0j)]]  # units = in
    assert m["line6"].feeder_name == "sourcebus_src"
    assert m["line6"].is_recloser is None
    assert m["line6"].is_breaker is None
    assert m["line6"].nameclass == ""

    for w in m["line6"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line9"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line9"].wires]) == set(["A", "B", "C"])
    assert m["line9"].name == "line9"
    assert m["line9"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line9"].line_type == "underground"
    assert m["line9"].length == 1.01 * 1609.34  # units = mi
    assert m["line9"].from_element == "bus2"
    assert m["line9"].to_element == "bus9"
    assert m["line9"].is_fuse is None
    assert m["line9"].is_switch is None
    assert m["line9"].faultrate == 0
    assert m["line9"].impedance_matrix == [
        [
            (6.0977375818658585e-05 + 0.00013378155020070338j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
        ],
        [
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (6.0977375818658585e-05 + 0.00013378155020070338j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
        ],
        [
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (6.0977375818658585e-05 + 0.00013378155020070338j),
        ],
    ]  # units = mi
    assert m["line9"].capacitance_matrix == [
        [
            (0.001739843662619459 + 0j),
            (-0.00037282364198988404 + 0j),
            (-0.00037282364198988404 + 0j),
        ],
        [
            (-0.00037282364198988404 + 0j),
            (0.001739843662619459 + 0j),
            (-0.00037282364198988404 + 0j),
        ],
        [
            (-0.00037282364198988404 + 0j),
            (-0.00037282364198988404 + 0j),
            (0.001739843662619459 + 0j),
        ],
    ]  # units = mi
    assert m["line9"].feeder_name == "sourcebus_src"
    assert m["line9"].is_recloser is None
    assert m["line9"].is_breaker is None
    assert m["line9"].nameclass == ""

    for w in m["line9"].wires:
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line10"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C"])
    assert m["line10"].name == "line10"
    assert m["line10"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line10"].line_type == "underground"
    assert m["line10"].length == 1.01 * 1609.34  # units = mi
    assert m["line10"].from_element == "bus2"
    assert m["line10"].to_element == "bus10"
    assert m["line10"].is_fuse is None
    assert m["line10"].is_switch is None
    assert m["line10"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line10"].impedance_matrix == [
        [
            (6.0977375818658585e-05 + 0.00013378155020070338j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
        ],
        [
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (6.0977375818658585e-05 + 0.00013378155020070338j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
        ],
        [
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (6.0977375818658585e-05 + 0.00013378155020070338j),
        ],
    ]  # units = mi
    assert m["line10"].capacitance_matrix == [
        [
            (0.001739843662619459 + 0j),
            (-0.00037282364198988404 + 0j),
            (-0.00037282364198988404 + 0j),
        ],
        [
            (-0.00037282364198988404 + 0j),
            (0.001739843662619459 + 0j),
            (-0.00037282364198988404 + 0j),
        ],
        [
            (-0.00037282364198988404 + 0j),
            (-0.00037282364198988404 + 0j),
            (0.001739843662619459 + 0j),
        ],
    ]  # units = mi
    assert m["line10"].feeder_name == "sourcebus_src"
    assert m["line10"].is_recloser is None
    assert m["line10"].is_breaker is None
    assert m["line10"].nameclass == ""

    for w in m["line10"].wires:
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["line11"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C"])
    assert m["line11"].name == "line11"
    assert m["line11"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line11"].line_type == "underground"
    assert m["line11"].length == 1.01 * 1609.34  # units = mi
    assert m["line11"].from_element == "bus2"
    assert m["line11"].to_element == "bus11"
    assert m["line11"].is_fuse is None
    assert m["line11"].is_switch is None
    assert m["line11"].faultrate == 1.0
    assert m["line11"].impedance_matrix == [
        [
            (6.0977375818658585e-05 + 0.00013378155020070338j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
        ],
        [
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (6.0977375818658585e-05 + 0.00013378155020070338j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
        ],
        [
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (2.493775709296979e-05 + 5.884399816073671e-05j),
            (6.0977375818658585e-05 + 0.00013378155020070338j),
        ],
    ]  # units = mi
    assert m["line11"].capacitance_matrix == [
        [
            (0.001739843662619459 + 0j),
            (-0.00037282364198988404 + 0j),
            (-0.00037282364198988404 + 0j),
        ],
        [
            (-0.00037282364198988404 + 0j),
            (0.001739843662619459 + 0j),
            (-0.00037282364198988404 + 0j),
        ],
        [
            (-0.00037282364198988404 + 0j),
            (-0.00037282364198988404 + 0j),
            (0.001739843662619459 + 0j),
        ],
    ]  # units = mi
    assert m["line11"].feeder_name == "sourcebus_src"
    assert m["line11"].is_recloser is None
    assert m["line11"].is_breaker is None
    assert m["line11"].nameclass == ""

    for w in m["line11"].wires:
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
