# -*- coding: utf-8 -*-

"""
test_fuses.py
----------------------------------

Tests for fuse attribute of Line
"""
import logging
import os
import numpy as np
from numpy import testing as npt

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

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + rem.imag * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    npt.assert_almost_equal(m["origin"].impedance_matrix, imp_matrix, decimal=5)

    c1 = complex(parsed_values["Line"]["C1"], 0)  # c1 taken from default values
    c0 = complex(parsed_values["Line"]["C0"], 0)  # c0 taken from default values
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 10) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = round(c_rem.real, 10) + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    npt.assert_almost_equal(m["origin"].capacitance_matrix, cap_matrix, decimal=5)
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
    assert m["line1"].is_fuse is True
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]
    npt.assert_almost_equal(m["line1"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["line1"].capacitance_matrix, cap_matrix, decimal=5)
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
    assert m["line2"].is_fuse is True
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = (
        complex(parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]) * 0.001
    )  # Units = km
    imp_matrix = round(imp_matrix.real, 9) + imp_matrix.imag * 1j
    cap_matrix = complex(parsed_values["Line"]["C1"], 0) * 0.001  # Units = km
    npt.assert_almost_equal(m["line2"].capacitance_matrix, cap_matrix, decimal=5)
    npt.assert_almost_equal(m["line2"].impedance_matrix, imp_matrix, decimal=5)
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
    assert m["line3"].is_fuse is True
    assert m["line3"].is_switch is None
    assert m["line3"].faultrate == parsed_values["Line"]["faultrate"]
    npt.assert_almost_equal(m["line3"].capacitance_matrix, cap_matrix, decimal=5)
    npt.assert_almost_equal(m["line3"].impedance_matrix, imp_matrix, decimal=5)
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
    assert m["line4"].is_fuse is True
    assert m["line4"].is_switch is None
    assert m["line4"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + rem.imag * 1j
    imp_matrix = np.zeros((2, 2), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()


    c1 = complex(parsed_values["Line"]["C1"], 0)  # c1 taken from default values
    c0 = complex(parsed_values["Line"]["C0"], 0)  # c0 taken from default values
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 10) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = round(c_rem.real, 10) + c_rem.imag * 1j
    cap_matrix = np.zeros((2, 2), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    npt.assert_almost_equal(m["line4"].capacitance_matrix, cap_matrix, decimal=5)
    npt.assert_almost_equal(m["line4"].impedance_matrix, imp_matrix, decimal=5)

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
