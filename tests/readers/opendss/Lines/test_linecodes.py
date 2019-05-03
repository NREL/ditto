# -*- coding: utf-8 -*-

"""
test_linecodes.py
----------------------------------

Tests for checking the line codes
"""
import logging
import os
import numpy as np

import six

import tempfile
import pytest as pt
from ditto.default_values.default_values_json import Default_Values

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_linecodes():
    """Tests if linecodes are read correctly."""
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader

    # test on the test_linecodes.dss
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_linecodes.dss"))
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

    # Line 1
    assert len(m["line1"].wires) == 3
    #    Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C"])
    assert m["line1"].nameclass == "3-1/0C_2/0CN_T"  # Linecode is 3-1/0C_2/0CN_T
    assert m["line1"].line_type == None
    assert m["line1"].from_element == "bus1"
    assert m["line1"].to_element == "bus2"
    assert m["line1"].length == 10
    assert m["line1"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(0.3489, 0.426198)  # r1,x1 values from linecode
    z0 = complex(0.588811, 1.29612)  # r0,x0 values from linecode
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 10) + diag.imag * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line1"].impedance_matrix == imp_matrix

    c1 = complex(10.4308823411236, 0)  # Value in Linecode
    c0 = complex(4.48501282215346, 0)  # Value in Linecode
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 9) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = round(c_rem.real, 9) + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    assert m["line1"].capacitance_matrix == cap_matrix
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None

    for w in m["line1"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(310)
        assert w.emergency_ampacity == float(310)
        assert w.resistance is None
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 2
    assert len(m["line2"].wires) == 3
    #    Phases of the different wires
    assert set([w.phase for w in m["line2"].wires]) == set(["C", "N"])
    assert m["line2"].nameclass == "1P_#8CU_#8N"  # Linecode is 1P_#8CU_#8N
    assert m["line2"].line_type == None
    assert m["line2"].from_element == "bus2"
    assert m["line2"].to_element == "bus3"
    assert m["line2"].length == 10
    assert m["line2"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line2"].is_fuse is None
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(2.15622, 0.539412)  # r1,x1 values from linecode
    z0 = complex(2.5511, 1.78041)  # r0,x0 values from linecode
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 9) + diag.imag * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 10) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line2"].impedance_matrix == imp_matrix

    c1 = complex(8.05740467479414, 0)  # Value in Linecode
    c0 = complex(4.52209592389387, 0)  # Value in Linecode
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 9) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = round(c_rem.real, 9) + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    assert m["line2"].capacitance_matrix == cap_matrix
    assert m["line2"].feeder_name == "sourcebus_src"
    assert m["line2"].is_recloser is None
    assert m["line2"].is_breaker is None

    for w in m["line2"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(1)
        assert w.emergency_ampacity == float(1)
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 3
    assert len(m["line3"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line3"].wires]) == set(["A", "B", "C"])
    assert (
        m["line3"].nameclass == "3P_3#500_AL_EPR_CD"
    )  # Linecode is 3P_3#500_AL_EPR_CD
    assert m["line3"].line_type == None
    assert m["line3"].from_element == "bus2"
    assert m["line3"].to_element == "bus4"
    assert m["line3"].length == 10
    assert m["line3"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line3"].is_fuse is None
    assert m["line3"].is_switch is None
    assert m["line3"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(0.072514, 0.001056)  # r1,x1 values from linecode
    z0 = complex(0.140678, -0.043807)  # r0,x0 values from linecode
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 11) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 11) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line3"].impedance_matrix == imp_matrix

    assert m["line3"].capacitance_matrix == [[0j, 0j, 0j], [0j, 0j, 0j], [0j, 0j, 0j]]
    assert m["line3"].feeder_name == "sourcebus_src"
    assert m["line3"].is_recloser is None
    assert m["line3"].is_breaker is None

    for w in m["line3"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(1110)
        assert w.emergency_ampacity == float(1110)
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 4
    assert len(m["line4"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line4"].wires]) == set(["A", "B", "C"])
    assert (
        m["line4"].nameclass == "3ph_h-397_acsr397_acsr397_acsr2/0_acsr"
    )  # Linecode is 3ph_h-397_acsr397_acsr397_acsr2/0_acsr
    assert m["line4"].line_type == None
    assert m["line4"].from_element == "bus4"
    assert m["line4"].to_element == "bus5"
    assert m["line4"].length == 10
    assert m["line4"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line4"].is_fuse is None
    assert m["line4"].is_switch is None
    assert m["line4"].faultrate == parsed_values["Line"]["faultrate"]

    actual_impedance_matrix = [
        [
            (0.000270019 + 0.000695974j),
            (0.000109951 + 0.00033351j),
            (0.000113538 + 0.000308271j),
        ],
        [
            (0.000109951 + 0.00033351j),
            (0.000264634 + 0.000708729j),
            (0.000110747 + 0.000350259j),
        ],
        [
            (0.000113538 + 0.000308271j),
            (0.000110747 + 0.000350259j),
            (0.000271698 + 0.000692021j),
        ],
    ]
    assert m["line4"].impedance_matrix == actual_impedance_matrix
    assert m["line4"].capacitance_matrix == [
        [(0.00913606 + 0j), (-0.00266777 + 0j), (-0.00217646 + 0j)],
        [(-0.00266777 + 0j), (0.00962226 + 0j), (-0.00315664 + 0j)],
        [(-0.00217646 + 0j), (-0.00315664 + 0j), (0.00943197 + 0j)],
    ]
    assert m["line4"].feeder_name == "sourcebus_src"
    assert m["line4"].is_recloser is None
    assert m["line4"].is_breaker is None

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

    # Line 5
    assert len(m["line5"].wires) == 1  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line5"].wires]) == set(["B"])
    assert (
        m["line5"].nameclass == "1ph-2_acsrxx4_acsr"
    )  # Linecode is 1ph-2_acsrxx4_acsr
    assert m["line5"].line_type == None
    assert m["line5"].from_element == "bus5"
    assert m["line5"].to_element == "bus6"
    assert m["line5"].length == 10
    assert m["line5"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line5"].is_fuse is None
    assert m["line5"].is_switch is None
    assert m["line5"].faultrate == parsed_values["Line"]["faultrate"]
    actual_impedance_matrix = [[(0.00112339 + 0.000937794j)]]
    assert m["line5"].impedance_matrix == actual_impedance_matrix
    assert m["line5"].capacitance_matrix == [[(0.00649582 + 0j)]]
    assert m["line5"].feeder_name == "sourcebus_src"
    assert m["line5"].is_recloser is None
    assert m["line5"].is_breaker is None

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

    # Line 6
    assert len(m["line6"].wires) == 2  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line6"].wires]) == set(["A", "C"])
    assert (
        m["line6"].nameclass == "2ph_h-2_acsrx2_acsr2_acsr"
    )  # Linecode is 2ph_h-2_acsrx2_acsr2_acsr
    assert m["line6"].line_type == None
    assert m["line6"].from_element == "bus5"
    assert m["line6"].to_element == "bus7"
    assert m["line6"].length == 10
    assert m["line6"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line6"].is_fuse is None
    assert m["line6"].is_switch is None
    assert m["line6"].faultrate == parsed_values["Line"]["faultrate"]
    actual_impedance_matrix = [
        [(0.00113148 + 0.000884886j), (0.000142066 + 0.000366115j)],
        [(0.000142066 + 0.000366115j), (0.00113362 + 0.000882239j)],
    ]
    assert m["line6"].impedance_matrix == actual_impedance_matrix
    assert m["line6"].capacitance_matrix == [
        [(0.00733718 + 0j), (-0.00239809 + 0j)],
        [(-0.00239809 + 0j), (0.00733718 + 0j)],
    ]
    assert m["line6"].feeder_name == "sourcebus_src"
    assert m["line6"].is_recloser is None
    assert m["line6"].is_breaker is None

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
        assert w.interrupting_rating is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 7
    assert len(m["line7"].wires) == 2  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line7"].wires]) == set(["A", "B"])
    assert m["line7"].nameclass == "750_Triplex"  # Linecode is 750_Triplex
    assert m["line7"].line_type == None
    assert m["line7"].from_element == "bus5"
    assert m["line7"].to_element == "bus8"
    assert m["line7"].length == 10
    assert m["line7"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line7"].is_fuse is None
    assert m["line7"].is_switch is None
    assert m["line7"].faultrate == parsed_values["Line"]["faultrate"]
    actual_impedance_matrix = [
        [(0.000163213 + 9.128727e-05j), (7.684242e-05 + 2.19643e-05j)],
        [(7.684242e-05 + 2.19643e-05j), (0.000163213 + 9.128727e-05j)],
    ]  # Converted from meters to kft
    assert m["line7"].impedance_matrix == actual_impedance_matrix
    assert m["line7"].capacitance_matrix == [
        [(0.00984252 + 0j), (-0.007874016 + 0j)],
        [(-0.007874016 + 0j), (0.00984252 + 0j)],
    ]  # Converted from meters to kft
    assert m["line7"].feeder_name == "sourcebus_src"
    assert m["line7"].is_recloser is None
    assert m["line7"].is_breaker is None

    for w in m["line7"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(580)
        assert w.emergency_ampacity == float(580 * 1.25)
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.interrupting_rating is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 8
    assert len(m["line8"].wires) == 2  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line8"].wires]) == set(["B", "C"])
    assert m["line8"].nameclass == "4/0Triplex"  # Linecode is 4/0Triplex
    assert m["line8"].line_type == None
    assert m["line8"].from_element == "bus5"
    assert m["line8"].to_element == "bus9"
    assert m["line8"].length == 10
    assert m["line8"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line8"].is_fuse is None
    assert m["line8"].is_switch is None
    assert m["line8"].faultrate == parsed_values["Line"]["faultrate"]
    actual_impedance_matrix = [
        [(0.001344984 + 0.0005473038j), (0.0003874511 + 0.0004186106j)],
        [(0.0003874511 + 0.0004186106j), (0.001344984 + 0.0005473038j)],
    ]  # Converted from meters to kft
    assert m["line8"].impedance_matrix == actual_impedance_matrix
    assert m["line8"].capacitance_matrix == [
        [(0.00984252 + 0j), (-0.007874016 + 0j)],
        [(-0.007874016 + 0j), (0.00984252 + 0j)],
    ]  # Converted from meters to kft
    assert m["line8"].feeder_name == "sourcebus_src"
    assert m["line8"].is_recloser is None
    assert m["line8"].is_breaker is None

    for w in m["line8"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(156)
        assert w.emergency_ampacity == float(156 * 1.25)
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    # Line 9
    assert len(m["line9"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line9"].wires]) == set(["A", "B", "C"])
    assert m["line9"].nameclass == "empty"  # Linecode is empty
    assert m["line9"].line_type == None
    assert m["line9"].from_element == "bus4"
    assert m["line9"].to_element == "bus10"
    assert m["line9"].length == 10
    assert m["line9"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line9"].is_fuse is None
    assert m["line9"].is_switch is None
    assert m["line9"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line9"].impedance_matrix == imp_matrix

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

    assert m["line9"].capacitance_matrix == cap_matrix
    assert m["line9"].feeder_name == "sourcebus_src"
    assert m["line9"].is_recloser is None
    assert m["line9"].is_breaker is None

    for w in m["line9"].wires:
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

    # Line 10
    assert len(m["line10"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line10"].wires]) == set(["A", "B", "C"])
    assert m["line10"].nameclass == "r1_only"  # Linecode is r1_only
    assert m["line10"].line_type == None
    assert m["line10"].from_element == "bus10"
    assert m["line10"].to_element == "bus11"
    assert m["line10"].length == 10
    assert m["line10"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line10"].is_fuse is None
    assert m["line10"].is_switch is None
    assert m["line10"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        0.3489, parsed_values["Line"]["X1"]
    )  # r1 taken from linecode, x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 10) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line10"].impedance_matrix == imp_matrix

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

    assert m["line10"].capacitance_matrix == cap_matrix
    assert m["line10"].feeder_name == "sourcebus_src"
    assert m["line10"].is_recloser is None
    assert m["line10"].is_breaker is None

    for w in m["line10"].wires:
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

    # Line 11
    assert len(m["line11"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line11"].wires]) == set(["A", "B", "C"])
    assert m["line11"].nameclass == "r0_only"  # Linecode is r0_only
    assert m["line11"].line_type == None
    assert m["line11"].from_element == "bus11"
    assert m["line11"].to_element == "bus12"
    assert m["line11"].length == 10
    assert m["line11"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line11"].is_fuse is None
    assert m["line11"].is_switch is None
    assert m["line11"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        0.588811, parsed_values["Line"]["X0"]
    )  # r0 taken from linecode,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 10) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line11"].impedance_matrix == imp_matrix

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

    assert m["line11"].capacitance_matrix == cap_matrix
    assert m["line11"].feeder_name == "sourcebus_src"
    assert m["line11"].is_recloser is None
    assert m["line11"].is_breaker is None

    for w in m["line11"].wires:
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

    # Line 12
    assert len(m["line12"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line12"].wires]) == set(["A", "B", "C"])
    assert m["line12"].nameclass == "x1_only"  # Linecode is x1_only
    assert m["line12"].line_type == None
    assert m["line12"].from_element == "bus12"
    assert m["line12"].to_element == "bus13"
    assert m["line12"].length == 10
    assert m["line12"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line12"].is_fuse is None
    assert m["line12"].is_switch is None
    assert m["line12"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], 0.426198
    )  # r1 taken from default values, x1 taken from linecode
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line12"].impedance_matrix == imp_matrix

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

    assert m["line12"].capacitance_matrix == cap_matrix
    assert m["line12"].feeder_name == "sourcebus_src"
    assert m["line12"].is_recloser is None
    assert m["line12"].is_breaker is None

    for w in m["line12"].wires:
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

    # Line 13
    assert len(m["line13"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line13"].wires]) == set(["A", "B", "C"])
    assert m["line13"].nameclass == "x0_only"  # Linecode is x0_only
    assert m["line13"].line_type == None
    assert m["line13"].from_element == "bus13"
    assert m["line13"].to_element == "bus14"
    assert m["line13"].length == 10
    assert m["line13"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line13"].is_fuse is None
    assert m["line13"].is_switch is None
    assert m["line13"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], 1.29612
    )  # r0 taken from default values, x0 taken from linecode
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line13"].impedance_matrix == imp_matrix

    assert m["line13"].capacitance_matrix == cap_matrix

    assert m["line13"].feeder_name == "sourcebus_src"
    assert m["line13"].is_recloser is None
    assert m["line13"].is_breaker is None

    for w in m["line13"].wires:
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

    # Line 14
    assert len(m["line14"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line14"].wires]) == set(["A", "B", "C"])
    assert m["line14"].nameclass == "c1_only"  # Linecode is c1_only
    assert m["line14"].line_type == None
    assert m["line14"].from_element == "bus14"
    assert m["line14"].to_element == "bus15"
    assert m["line14"].length == 10
    assert m["line14"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line14"].is_fuse is None
    assert m["line14"].is_switch is None
    assert m["line14"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line14"].impedance_matrix == imp_matrix

    c1 = complex(10.4308823411236, 0)  # c1 taken from linecode
    c0 = complex(parsed_values["Line"]["C0"], 0)  # c0 taken from default values
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 9) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = round(c_rem.real, 9) + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    assert m["line14"].capacitance_matrix == cap_matrix
    assert m["line14"].feeder_name == "sourcebus_src"
    assert m["line14"].is_recloser is None
    assert m["line14"].is_breaker is None

    for w in m["line14"].wires:
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

    # Line 15
    assert len(m["line15"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line15"].wires]) == set(["A", "B", "C"])
    assert m["line15"].nameclass == "c0_only"  # Linecode is c0_only
    assert m["line15"].line_type == None
    assert m["line15"].from_element == "bus15"
    assert m["line15"].to_element == "bus16"
    assert m["line15"].length == 10
    assert m["line15"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line15"].is_fuse is None
    assert m["line15"].is_switch is None
    assert m["line15"].faultrate == parsed_values["Line"]["faultrate"]

    z1 = complex(
        parsed_values["Line"]["R1"], parsed_values["Line"]["X1"]
    )  # r1,x1 taken from default values
    z0 = complex(
        parsed_values["Line"]["R0"], parsed_values["Line"]["X0"]
    )  # r0,x0 taken from default values
    diag = ((2 * z1 + z0) / 3) * 0.001  # Units = km
    diag = round(diag.real, 11) + round(diag.imag, 10) * 1j
    rem = ((z0 - z1) / 3) * 0.001  # Units = km
    rem = round(rem.real, 11) + round(rem.imag, 10) * 1j
    imp_matrix = np.zeros((3, 3), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line15"].impedance_matrix == imp_matrix

    c1 = complex(parsed_values["Line"]["C1"], 0)  # c1 taken from default values
    c0 = complex(4.38501282215346, 0)  # c0 taken from linecode
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 9) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = round(c_rem.real, 10) + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    assert m["line15"].capacitance_matrix == cap_matrix
    assert m["line15"].feeder_name == "sourcebus_src"
    assert m["line15"].is_recloser is None
    assert m["line15"].is_breaker is None

    for w in m["line15"].wires:
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
