# -*- coding: utf-8 -*-

"""
test_line_connectivity.py
----------------------------------

Tests for checking the line connectivity.
"""
import logging
import os
import numpy as np
import six

import tempfile
import pytest as pt
import json
from ditto.default_values.default_values_json import Default_Values

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_line_connectivity():
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader

    # test on the test_line_connectivity.dss
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_line_connectivity.dss")
    )
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

    # Line1 connects sourcebus to bus1 and should have 3 wires: A, B, C
    assert len(m["line1"].wires) == 3
    #    Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C"])
    assert m["line1"].name == "line1"
    assert m["line1"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line1"].line_type == None
    assert m["line1"].length == 100
    assert m["line1"].from_element == "sourcebus"
    assert m["line1"].to_element == "bus1"
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = (2 * z1 + z0) / 3
    diag = round(diag.real, 8) + round(diag.imag, 4) * 1j
    rem = (z0 - z1) / 3
    rem = round(rem.real, 8) + rem.imag * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line1"].impedance_matrix == imp_matrix

    c1 = complex(parsed_values["Line"]["C1"], 0)  # c1 taken from default values
    c0 = complex(parsed_values["Line"]["C0"], 0)  # c0 taken from default values
    c_diag = (2 * c1 + c0) / 3
    c_diag = round(c_diag.real, 4) + c_diag.imag * 1j
    c_rem = (c0 - c1) / 3
    c_rem = round(c_rem.real, 4) + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    assert m["line1"].capacitance_matrix == cap_matrix
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
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line2 connects bus1 to bus2 and should have 3 wires: A, B, C
    assert len(m["line2"].wires) == 3
    #    Phases of the different wires
    assert set([w.phase for w in m["line2"].wires]) == set(["A", "B", "C"])
    assert m["line2"].name == "line2"
    assert m["line2"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line2"].line_type == None
    assert m["line2"].length == 200
    assert m["line2"].from_element == "bus1"
    assert m["line2"].to_element == "bus2"
    assert m["line2"].is_fuse is None
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]
    assert (
        m["line2"].impedance_matrix == imp_matrix
    )  # Copying the matrix from Line1 as it has 3 wires
    assert (
        m["line2"].capacitance_matrix == cap_matrix
    )  # Copying the matrix from Line1 as it has 3 wires
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
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line3 connects bus2 to bus3 and should have 2 wires: A, B
    assert len(m["line3"].wires) == 2
    #    Phases of the different wires
    assert set([w.phase for w in m["line3"].wires]) == set(["A", "B"])
    assert m["line3"].name == "line3"
    assert m["line3"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line3"].line_type == None
    assert m["line3"].length == 50
    assert m["line3"].from_element == "bus2"
    assert m["line3"].to_element == "bus3"
    assert m["line3"].is_fuse is None
    assert m["line3"].is_switch is None
    assert m["line3"].faultrate == parsed_values["Line"]["faultrate"]
    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = (2 * z1 + z0) / 3
    diag = round(diag.real, 8) + round(diag.imag, 4) * 1j
    rem = (z0 - z1) / 3
    rem = round(rem.real, 8) + rem.imag * 1j
    imp_matrix = np.zeros((2, 2), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line3"].impedance_matrix == imp_matrix

    c1 = complex(parsed_values["Line"]["C1"], 0)  # c1 taken from default values
    c0 = complex(parsed_values["Line"]["C0"], 0)  # c0 taken from default values
    c_diag = (2 * c1 + c0) / 3
    c_diag = round(c_diag.real, 4) + c_diag.imag * 1j
    c_rem = (c0 - c1) / 3
    c_rem = round(c_rem.real, 4) + c_rem.imag * 1j
    cap_matrix = np.zeros((2, 2), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    assert m["line3"].capacitance_matrix == cap_matrix
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
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line4 connects bus3 to bus4 and should have 1 wire: B
    assert len(m["line4"].wires) == 1
    #    Phases of the different wires
    assert set([w.phase for w in m["line4"].wires]) == set(["B"])
    assert m["line4"].name == "line4"
    assert m["line4"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line4"].line_type == None
    assert m["line4"].length == 25
    assert m["line4"].from_element == "bus3"
    assert m["line4"].to_element == "bus4"
    assert m["line4"].is_fuse is None
    assert m["line4"].is_switch is None
    assert m["line4"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = complex(parsed_values["Line"]["R1"], parsed_values["Line"]["X1"])
    imp_matrix = round(imp_matrix.real, 9) + imp_matrix.imag * 1j
    assert m["line4"].impedance_matrix == [[imp_matrix]]
    cap_matrix = complex(parsed_values["Line"]["C1"], 0)
    assert m["line4"].capacitance_matrix == [[cap_matrix]]
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
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line5 connects bus1 to bus5 and should have 2 wires: A, C
    assert len(m["line5"].wires) == 2
    #    Phases of the different wires
    assert set([w.phase for w in m["line5"].wires]) == set(["A", "C"])
    assert m["line5"].name == "line5"
    assert m["line5"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line5"].line_type == None
    assert m["line5"].length == float(1500 * 0.3048)  # units = ft
    assert m["line5"].from_element == "bus1"
    assert m["line5"].to_element == "bus5"
    assert m["line5"].is_fuse is None
    assert m["line5"].is_switch is None
    assert m["line5"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    #    import pdb;pdb.set_trace()
    diag = ((2 * z1 + z0) / 3) / 0.3048  # Units = ft
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) / 0.3048  # Units = ft
    rem = round(rem.real, 11) + rem.imag * 1j
    imp_matrix = np.zeros((2, 2), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    #    assert m["line5"].impedance_matrix == imp_matrix

    c1 = complex(parsed_values["Line"]["C1"], 0)  # c1 taken from default values
    c0 = complex(parsed_values["Line"]["C0"], 0)  # c0 taken from default values
    c_diag = ((2 * c1 + c0) / 3) / 0.3048  # Units = ft
    c_diag = c_diag.real + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) / 0.3048  # Units = ft
    c_rem = c_rem.real + c_rem.imag * 1j
    cap_matrix = np.zeros((2, 2), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    np.testing.assert_array_almost_equal(m["line5"].capacitance_matrix, cap_matrix)
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
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line6 connects bus4 to bus6 and should have 2 wires: B, C
    assert len(m["line6"].wires) == 2
    #    Phases of the different wires
    assert set([w.phase for w in m["line6"].wires]) == set(["B", "C"])
    assert m["line6"].name == "line6"
    assert m["line6"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line6"].line_type == None
    assert m["line6"].length == 110
    assert m["line6"].from_element == "bus4"
    assert m["line6"].to_element == "bus6"
    assert m["line6"].is_fuse is None
    assert m["line6"].is_switch is None
    assert m["line6"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line6"].impedance_matrix == [
        [(0.09813333 + 0.2153j), (0.04013333 + 0.0947j)],
        [(0.04013333 + 0.0947j), (0.09813333 + 0.2153j)],
    ]
    assert m["line6"].capacitance_matrix == [
        [(2.8 + 0j), (-0.6 + 0j)],
        [(-0.6 + 0j), (2.8 + 0j)],
    ]
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
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    #  Line7
    assert len(m["line7"].wires) == 2
    #    Phases of the different wires
    assert set([w.phase for w in m["line7"].wires]) == set(["B", "C"])
    assert m["line7"].name == "line7"
    assert m["line7"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["line7"].line_type == None
    assert m["line7"].length == 100
    assert m["line7"].from_element == "bus1"
    assert m["line7"].to_element == "bus2"
    assert m["line7"].is_fuse is None
    assert m["line7"].is_switch is None
    assert m["line7"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line7"].impedance_matrix == [
        [(0.09813333 + 0.2153j), (0.04013333 + 0.0947j)],
        [(0.04013333 + 0.0947j), (0.09813333 + 0.2153j)],
    ]
    assert m["line7"].capacitance_matrix == [
        [(2.8 + 0j), (-0.6 + 0j)],
        [(-0.6 + 0j), (2.8 + 0j)],
    ]
    assert m["line7"].feeder_name == "sourcebus_src"
    assert m["line7"].is_recloser is None
    assert m["line7"].is_breaker is None
    assert m["line7"].nameclass == ""

    for w in m["line7"].wires:
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
