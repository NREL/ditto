# -*- coding: utf-8 -*-

"""
test_switches.py
----------------------------------

Tests for switch attribute of Line
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


def test_switches():
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader
    from ditto.default_values.default_values_json import Default_Values

    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_switches.dss"))
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
    assert m["origin"].line_type is None
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

    npt.assert_almost_equal(m["origin"].impedance_matrix, imp_matrix, decimal=5)
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

    assert len(m["switch1"].wires) == 3  # Number of wires
    # Phases of the different wires
    assert set([w.phase for w in m["switch1"].wires]) == set(["A", "B", "C"])
    assert m["switch1"].name == "switch1"
    assert m["switch1"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch1"].line_type is None
    assert m["switch1"].length == 0.001 * 1000
    assert m["switch1"].from_element == "node1"
    assert m["switch1"].to_element == "node2"
    assert m["switch1"].is_fuse is None
    assert m["switch1"].is_switch == 1
    assert m["switch1"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]

    c1 = complex(1.1, 0)
    c0 = complex(1, 0)
    c_diag = ((2 * c1 + c0) / 3) * 0.001  # Units = km
    c_diag = round(c_diag.real, 9) + c_diag.imag * 1j
    c_rem = ((c0 - c1) / 3) * 0.001  # Units = km
    c_rem = c_rem.real + c_rem.imag * 1j
    cap_matrix = np.zeros((3, 3), dtype=np.complex_)
    cap_matrix.fill(c_rem)
    np.fill_diagonal(cap_matrix, c_diag)
    cap_matrix = cap_matrix.tolist()

    npt.assert_almost_equal(m["switch1"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch1"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch1"].feeder_name == "sourcebus_src"
    assert m["switch1"].is_recloser is None
    assert m["switch1"].is_breaker is None
    assert m["switch1"].nameclass == ""

    for w in m["switch1"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open == 0
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch2"].wires) == 3  # Number of wires
    # Phases of the different wires
    assert set([w.phase for w in m["switch2"].wires]) == set(["A", "B", "C"])
    assert m["switch2"].name == "switch2"
    assert m["switch2"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch2"].line_type is None
    assert m["switch2"].length == 0.001 * 1000
    assert m["switch2"].from_element == "node1"
    assert m["switch2"].to_element == "node3"
    assert m["switch2"].is_fuse is None
    assert m["switch2"].is_switch == 1
    assert m["switch2"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    cap_matrix = [
        [
            (0.001066667 + 0j),
            (-3.3333330000000004e-05 + 0j),
            (-3.3333330000000004e-05 + 0j),
        ],
        [
            (-3.3333330000000004e-05 + 0j),
            (0.001066667 + 0j),
            (-3.3333330000000004e-05 + 0j),
        ],
        [
            (-3.3333330000000004e-05 + 0j),
            (-3.3333330000000004e-05 + 0j),
            (0.001066667 + 0j),
        ],
    ]
    npt.assert_almost_equal(m["switch2"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch2"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch2"].feeder_name == "sourcebus_src"
    assert m["switch2"].is_recloser is None
    assert m["switch2"].is_breaker is None
    assert m["switch2"].nameclass == ""

    for w in m["switch2"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open == 1
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch3"].wires) == 3  # Number of wires
    # Phases of the different wires
    assert set([w.phase for w in m["switch3"].wires]) == set(["A", "B", "C"])
    assert m["switch3"].name == "switch3"
    assert m["switch3"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch3"].line_type is None
    assert m["switch3"].length == 0.001 * 1000
    assert m["switch3"].from_element == "node1"
    assert m["switch3"].to_element == "node4"
    assert m["switch3"].is_fuse is None
    assert m["switch3"].is_switch == 1
    assert m["switch3"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    cap_matrix = [
        [
            (0.001066667 + 0j),
            (-3.3333330000000004e-05 + 0j),
            (-3.3333330000000004e-05 + 0j),
        ],
        [
            (-3.3333330000000004e-05 + 0j),
            (0.001066667 + 0j),
            (-3.3333330000000004e-05 + 0j),
        ],
        [
            (-3.3333330000000004e-05 + 0j),
            (-3.3333330000000004e-05 + 0j),
            (0.001066667 + 0j),
        ],
    ]
    npt.assert_almost_equal(m["switch3"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch3"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch3"].feeder_name == "sourcebus_src"
    assert m["switch3"].is_recloser is None
    assert m["switch3"].is_breaker is None
    assert m["switch3"].nameclass == ""

    for w in m["switch3"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open == 1
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch4"].wires) == 3  # Number of wires
    # Phases of the different wires
    assert set([w.phase for w in m["switch4"].wires]) == set(["A", "B", "C"])
    assert m["switch4"].name == "switch4"
    assert m["switch4"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch4"].line_type is None
    assert m["switch4"].length == 0.001 * 1000
    assert m["switch4"].from_element == "node1"
    assert m["switch4"].to_element == "node5"
    assert m["switch4"].is_fuse is None
    assert m["switch4"].is_switch == 1
    assert m["switch4"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    cap_matrix = [
        [
            (0.001066667 + 0j),
            (-3.3333330000000004e-05 + 0j),
            (-3.3333330000000004e-05 + 0j),
        ],
        [
            (-3.3333330000000004e-05 + 0j),
            (0.001066667 + 0j),
            (-3.3333330000000004e-05 + 0j),
        ],
        [
            (-3.3333330000000004e-05 + 0j),
            (-3.3333330000000004e-05 + 0j),
            (0.001066667 + 0j),
        ],
    ]
    npt.assert_almost_equal(m["switch4"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch4"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch4"].feeder_name == "sourcebus_src"
    assert m["switch4"].is_recloser is None
    assert m["switch4"].is_breaker is None
    assert m["switch4"].nameclass == ""

    for w in m["switch4"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open == 0
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch5"].wires) == 1
    # Phases of the different wires
    assert m["switch5"].wires[0].phase == "A"
    assert m["switch5"].name == "switch5"
    assert m["switch5"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch5"].line_type is None
    assert m["switch5"].length == 0.001 * 1000
    assert m["switch5"].from_element == "node1"
    assert m["switch5"].to_element == "node6"
    assert m["switch5"].is_fuse is None
    assert m["switch5"].is_switch == 1
    assert m["switch5"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [[(0.001 + 0.001j)]]
    cap_matrix = [[(0.0011 + 0j)]]
    npt.assert_almost_equal(m["switch5"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch5"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch5"].feeder_name == "sourcebus_src"
    assert m["switch5"].is_recloser is None
    assert m["switch5"].is_breaker is None
    assert m["switch5"].nameclass == ""

    for w in m["switch5"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open == 0
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch6"].wires) == 1
    # Phases of the different wires
    assert m["switch6"].wires[0].phase == "C"
    assert m["switch6"].name == "switch6"
    assert m["switch6"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch6"].line_type is None
    assert m["switch6"].length == 0.001 * 1000
    assert m["switch6"].from_element == "node1"
    assert m["switch6"].to_element == "node7"
    assert m["switch6"].is_fuse is None
    assert m["switch6"].is_switch == 1
    assert m["switch6"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [[(0.001 + 0.001j)]]
    cap_matrix = [[(0.0011 + 0j)]]
    npt.assert_almost_equal(m["switch6"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch6"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch6"].feeder_name == "sourcebus_src"
    assert m["switch6"].is_recloser is None
    assert m["switch6"].is_breaker is None
    assert m["switch6"].nameclass == ""

    for w in m["switch6"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.is_open == 1
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch7"].wires) == 2
    # Phases of the different wires
    assert set([w.phase for w in m["switch7"].wires]) == set(["B", "C"])
    assert m["switch7"].name == "switch7"
    assert m["switch7"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch7"].line_type is None
    assert m["switch7"].length == 0.001 * 1000
    assert m["switch7"].from_element == "node1"
    assert m["switch7"].to_element == "node8"
    assert m["switch7"].is_fuse is None
    assert m["switch7"].is_switch == 1
    assert m["switch7"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [(0.001 + 0.001j), 0j],
        [0j, (0.001 + 0.001j)],
    ]
    cap_matrix = [
        [(0.001066667 + 0j), (-3.3333330000000004e-05 + 0j)],
        [(-3.3333330000000004e-05 + 0j), (0.001066667 + 0j)],
    ]
    npt.assert_almost_equal(m["switch7"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch7"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch7"].feeder_name == "sourcebus_src"
    assert m["switch7"].is_recloser is None
    assert m["switch7"].is_breaker is None
    assert m["switch7"].nameclass == ""

    for w in m["switch7"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open == 1
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch8"].wires) == 2
    # Phases of the different wires
    assert set(w.phase for w in m["switch8"].wires) == set(["A", "B"])
    assert m["switch8"].name == "switch8"
    assert m["switch8"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch8"].line_type is None
    assert m["switch8"].length == 0.001 * 1000
    assert m["switch8"].from_element == "node1"
    assert m["switch8"].to_element == "node9"
    assert m["switch8"].is_fuse is None
    assert m["switch8"].is_switch == 1
    assert m["switch8"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [(0.001 + 0.001j), 0j],
        [0j, (0.001 + 0.001j)],
    ]
    cap_matrix = [
        [(0.001066667 + 0j), (-3.3333330000000004e-05 + 0j)],
        [(-3.3333330000000004e-05 + 0j), (0.001066667 + 0j)],
    ]
    npt.assert_almost_equal(m["switch8"].impedance_matrix, imp_matrix, decimal=5)
    npt.assert_almost_equal(m["switch8"].capacitance_matrix, cap_matrix, decimal=5)
    assert m["switch8"].feeder_name == "sourcebus_src"
    assert m["switch8"].is_recloser is None
    assert m["switch8"].is_breaker is None
    assert m["switch8"].nameclass == ""

    for w in m["switch8"].wires:
        assert w.nameclass == ""
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.is_open == 0
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
