# -*- coding: utf-8 -*-

"""
test_switches.py
----------------------------------

Tests for switch attribute of Line
"""
import logging
import os

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
    assert m["origin"].line_type == "underground"
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
        assert w.insulation_thickness == 0.0
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
    assert m["switch1"].line_type == "underground"
    assert m["switch1"].length == 0.001 * 1000
    assert m["switch1"].from_element == "node1"
    assert m["switch1"].to_element == "node2"
    assert m["switch1"].is_fuse is None
    assert m["switch1"].is_switch == 1
    assert m["switch1"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch1"].impedance_matrix == [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    assert m["switch1"].capacitance_matrix == [
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
    assert m["switch1"].feeder_name == "sourcebus_src"
    assert m["switch1"].is_recloser is None
    assert m["switch1"].is_breaker is None
    assert m["switch1"].nameclass == "switch1"

    for w in m["switch1"].wires:
        assert w.nameclass == "switch1"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["switch2"].line_type == "underground"
    assert m["switch2"].length == 0.001 * 1000
    assert m["switch2"].from_element == "node1"
    assert m["switch2"].to_element == "node3"
    assert m["switch2"].is_fuse is None
    assert m["switch2"].is_switch == 1
    assert m["switch2"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch2"].impedance_matrix == [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    assert m["switch2"].capacitance_matrix == [
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
    assert m["switch2"].feeder_name == "sourcebus_src"
    assert m["switch2"].is_recloser is None
    assert m["switch2"].is_breaker is None
    assert m["switch2"].nameclass == "switch2"

    for w in m["switch2"].wires:
        assert w.nameclass == "switch2"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["switch3"].line_type == "underground"
    assert m["switch3"].length == 0.001 * 1000
    assert m["switch3"].from_element == "node1"
    assert m["switch3"].to_element == "node4"
    assert m["switch3"].is_fuse is None
    assert m["switch3"].is_switch == 1
    assert m["switch3"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch3"].impedance_matrix == [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    assert m["switch3"].capacitance_matrix == [
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
    assert m["switch3"].feeder_name == "sourcebus_src"
    assert m["switch3"].is_recloser is None
    assert m["switch3"].is_breaker is None
    assert m["switch3"].nameclass == "switch3"

    for w in m["switch3"].wires:
        assert w.nameclass == "switch3"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["switch4"].line_type == "underground"
    assert m["switch4"].length == 0.001 * 1000
    assert m["switch4"].from_element == "node1"
    assert m["switch4"].to_element == "node5"
    assert m["switch4"].is_fuse is None
    assert m["switch4"].is_switch == 1
    assert m["switch4"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch4"].impedance_matrix == [
        [(0.001 + 0.001j), 0j, 0j],
        [0j, (0.001 + 0.001j), 0j],
        [0j, 0j, (0.001 + 0.001j)],
    ]
    assert m["switch4"].capacitance_matrix == [
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
    assert m["switch4"].feeder_name == "sourcebus_src"
    assert m["switch4"].is_recloser is None
    assert m["switch4"].is_breaker is None
    assert m["switch4"].nameclass == "switch4"

    for w in m["switch4"].wires:
        assert w.nameclass == "switch4"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["switch5"].line_type == "underground"
    assert m["switch5"].length == 0.001 * 1000
    assert m["switch5"].from_element == "node1"
    assert m["switch5"].to_element == "node6"
    assert m["switch5"].is_fuse is None
    assert m["switch5"].is_switch == 1
    assert m["switch5"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch5"].impedance_matrix == [[(0.001 + 0.001j)]]
    assert m["switch5"].capacitance_matrix == [[(0.0011 + 0j)]]
    assert m["switch5"].feeder_name == "sourcebus_src"
    assert m["switch5"].is_recloser is None
    assert m["switch5"].is_breaker is None
    assert m["switch5"].nameclass == "switch5"

    for w in m["switch5"].wires:
        assert w.nameclass == "switch5"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["switch6"].line_type == "underground"
    assert m["switch6"].length == 0.001 * 1000
    assert m["switch6"].from_element == "node1"
    assert m["switch6"].to_element == "node7"
    assert m["switch6"].is_fuse is None
    assert m["switch6"].is_switch == 1
    assert m["switch6"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch6"].impedance_matrix == [[(0.001 + 0.001j)]]
    assert m["switch6"].capacitance_matrix == [[(0.0011 + 0j)]]
    assert m["switch6"].feeder_name == "sourcebus_src"
    assert m["switch6"].is_recloser is None
    assert m["switch6"].is_breaker is None
    assert m["switch6"].nameclass == "switch6"

    for w in m["switch6"].wires:
        assert w.nameclass == "switch6"
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
    assert m["switch7"].line_type == "underground"
    assert m["switch7"].length == 0.001 * 1000
    assert m["switch7"].from_element == "node1"
    assert m["switch7"].to_element == "node8"
    assert m["switch7"].is_fuse is None
    assert m["switch7"].is_switch == 1
    assert m["switch7"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch7"].impedance_matrix == [
        [(0.001 + 0.001j), 0j],
        [0j, (0.001 + 0.001j)],
    ]
    assert m["switch7"].capacitance_matrix == [
        [(0.001066667 + 0j), (-3.3333330000000004e-05 + 0j)],
        [(-3.3333330000000004e-05 + 0j), (0.001066667 + 0j)],
    ]
    assert m["switch7"].feeder_name == "sourcebus_src"
    assert m["switch7"].is_recloser is None
    assert m["switch7"].is_breaker is None
    assert m["switch7"].nameclass == "switch7"

    for w in m["switch7"].wires:
        assert w.nameclass == "switch7"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == 3000
        assert w.emergency_ampacity == 4000
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
        assert w.is_open == 1
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

    assert len(m["switch8"].wires) == 2
    # Phases of the different wires
    assert set([w.phase for w in m["switch8"].wires]) == set(["A", "B"])
    assert m["switch8"].name == "switch8"
    assert m["switch8"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["switch8"].line_type == "underground"
    assert m["switch8"].length == 0.001 * 1000
    assert m["switch8"].from_element == "node1"
    assert m["switch8"].to_element == "node9"
    assert m["switch8"].is_fuse is None
    assert m["switch8"].is_switch == 1
    assert m["switch8"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["switch8"].impedance_matrix == [
        [(0.001 + 0.001j), 0j],
        [0j, (0.001 + 0.001j)],
    ]
    assert m["switch8"].capacitance_matrix == [
        [(0.001066667 + 0j), (-3.3333330000000004e-05 + 0j)],
        [(-3.3333330000000004e-05 + 0j), (0.001066667 + 0j)],
    ]
    assert m["switch8"].feeder_name == "sourcebus_src"
    assert m["switch8"].is_recloser is None
    assert m["switch8"].is_breaker is None
    assert m["switch8"].nameclass == "switch8"

    for w in m["switch8"].wires:
        assert w.nameclass == "switch8"
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
