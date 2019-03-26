# -*- coding: utf-8 -*-

"""
test_linecodes.py
----------------------------------

Tests for checking the line codes
"""
import logging
import os

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
    assert m["line1"].line_type == "underground"  # OH not in linecode
    assert m["line1"].from_element == "bus1"
    assert m["line1"].to_element == "bus2"
    assert m["line1"].length == 10
    assert m["line1"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line1"].impedance_matrix == [
        [
            (0.0004288703 + 0.000716172j),
            (7.997033e-05 + 0.000289974j),
            (7.997033e-05 + 0.000289974j),
        ],
        [
            (7.997033e-05 + 0.000289974j),
            (0.0004288703 + 0.000716172j),
            (7.997033e-05 + 0.000289974j),
        ],
        [
            (7.997033e-05 + 0.000289974j),
            (7.997033e-05 + 0.000289974j),
            (0.0004288703 + 0.000716172j),
        ],
    ]
    assert m["line1"].capacitance_matrix == [
        [(0.008448926 + 0j), (-0.001981957 + 0j), (-0.001981957 + 0j)],
        [(-0.001981957 + 0j), (0.008448926 + 0j), (-0.001981957 + 0j)],
        [(-0.001981957 + 0j), (-0.001981957 + 0j), (0.008448926 + 0j)],
    ]
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None

    for w in m["line1"].wires:
        assert w.nameclass == "T"
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
    assert m["line2"].line_type == "underground"  # OH not in linecode
    assert m["line2"].from_element == "bus2"
    assert m["line2"].to_element == "bus3"
    assert m["line2"].length == 10
    assert m["line2"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line2"].is_fuse is None
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line2"].impedance_matrix == [
        [
            (0.002287847 + 0.000953078j),
            (0.0001316267 + 0.000413666j),
            (0.0001316267 + 0.000413666j),
        ],
        [
            (0.0001316267 + 0.000413666j),
            (0.002287847 + 0.000953078j),
            (0.0001316267 + 0.000413666j),
        ],
        [
            (0.0001316267 + 0.000413666j),
            (0.0001316267 + 0.000413666j),
            (0.002287847 + 0.000953078j),
        ],
    ]
    assert m["line2"].capacitance_matrix == [
        [(0.006878968 + 0j), (-0.001178436 + 0j), (-0.001178436 + 0j)],
        [(-0.001178436 + 0j), (0.006878968 + 0j), (-0.001178436 + 0j)],
        [(-0.001178436 + 0j), (-0.001178436 + 0j), (0.006878968 + 0j)],
    ]
    assert m["line2"].feeder_name == "sourcebus_src"
    assert m["line2"].is_recloser is None
    assert m["line2"].is_breaker is None

    for w in m["line2"].wires:
        assert w.nameclass == "#8N"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(1)
        assert w.emergency_ampacity == float(1)
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["line3"].line_type == "underground"  # OH not in linecode
    assert m["line3"].from_element == "bus2"
    assert m["line3"].to_element == "bus4"
    assert m["line3"].length == 10
    assert m["line3"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line3"].is_fuse is None
    assert m["line3"].is_switch is None
    assert m["line3"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line3"].impedance_matrix == [
        [
            (9.523533e-05 - 1.389833e-05j),
            (2.272133e-05 - 1.495433e-05j),
            (2.272133e-05 - 1.495433e-05j),
        ],
        [
            (2.272133e-05 - 1.495433e-05j),
            (9.523533e-05 - 1.389833e-05j),
            (2.272133e-05 - 1.495433e-05j),
        ],
        [
            (2.272133e-05 - 1.495433e-05j),
            (2.272133e-05 - 1.495433e-05j),
            (9.523533e-05 - 1.389833e-05j),
        ],
    ]
    assert m["line3"].capacitance_matrix == [[0j, 0j, 0j], [0j, 0j, 0j], [0j, 0j, 0j]]
    assert m["line3"].feeder_name == "sourcebus_src"
    assert m["line3"].is_recloser is None
    assert m["line3"].is_breaker is None

    for w in m["line3"].wires:
        assert w.nameclass == "AL-EPR-CD"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(1110)
        assert w.emergency_ampacity == float(1110)
        assert w.resistance is None
        assert w.insulation_thickness == 0.0
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
    assert m["line4"].line_type == "underground"  # OH not in linecode
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
        assert w.nameclass == "acsr397-acsr397-acsr2/0-acsr"
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

    # Line 5
    assert len(m["line5"].wires) == 1  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line5"].wires]) == set(["B"])
    assert (
        m["line5"].nameclass == "1ph-2_acsrxx4_acsr"
    )  # Linecode is 1ph-2_acsrxx4_acsr
    assert m["line5"].line_type == "underground"  # OH not in linecode
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
        assert w.nameclass == "acsr"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
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
    assert m["line6"].line_type == "underground"  # OH not in linecode
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
        assert w.nameclass == "acsrx2-acsr2-acsr"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
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
    assert m["line7"].line_type == "underground"  # OH not in linecode
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
        assert w.nameclass == "750_Triplex"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(580)
        assert w.emergency_ampacity == float(580 * 1.25)
        assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
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
    assert m["line8"].line_type == "underground"  # OH not in linecode
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
        assert w.nameclass == "4/0Triplex"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(156)
        assert w.emergency_ampacity == float(156 * 1.25)
        assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
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
    assert m["line9"].line_type == "underground"  # OH not in linecode
    assert m["line9"].from_element == "bus4"
    assert m["line9"].to_element == "bus10"
    assert m["line9"].length == 10
    assert m["line9"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line9"].is_fuse is None
    assert m["line9"].is_switch is None
    assert m["line9"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line9"].impedance_matrix == [
        [
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.47e-05j),
            (4.013333e-05 + 9.47e-05j),
        ],
        [
            (4.013333e-05 + 9.47e-05j),
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.47e-05j),
        ],
        [
            (4.013333e-05 + 9.47e-05j),
            (4.013333e-05 + 9.47e-05j),
            (9.813333e-05 + 0.0002153j),
        ],
    ]
    assert m["line9"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (-0.0006 + 0j), (0.0028 + 0j)],
    ]
    assert m["line9"].feeder_name == "sourcebus_src"
    assert m["line9"].is_recloser is None
    assert m["line9"].is_breaker is None

    for w in m["line9"].wires:
        assert w.nameclass == "empty"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == parsed_values["Wire"]["ampacity"]
        assert w.emergency_ampacity == parsed_values["Wire"]["emergency_ampacity"]
        assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
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
    assert m["line10"].line_type == "underground"  # OH not in linecode
    assert m["line10"].from_element == "bus10"
    assert m["line10"].to_element == "bus11"
    assert m["line10"].length == 10
    assert m["line10"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line10"].is_fuse is None
    assert m["line10"].is_switch is None
    assert m["line10"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line10"].impedance_matrix == [
        [
            (0.0002920667 + 0.0002153j),
            (-5.683333e-05 + 9.47e-05j),
            (-5.683333e-05 + 9.47e-05j),
        ],
        [
            (-5.683333e-05 + 9.47e-05j),
            (0.0002920667 + 0.0002153j),
            (-5.683333e-05 + 9.47e-05j),
        ],
        [
            (-5.683333e-05 + 9.47e-05j),
            (-5.683333e-05 + 9.47e-05j),
            (0.0002920667 + 0.0002153j),
        ],
    ]
    assert m["line10"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (-0.0006 + 0j), (0.0028 + 0j)],
    ]
    assert m["line10"].feeder_name == "sourcebus_src"
    assert m["line10"].is_recloser is None
    assert m["line10"].is_breaker is None

    for w in m["line10"].wires:
        assert w.nameclass == "r1_only"
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

    # Line 11
    assert len(m["line11"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line11"].wires]) == set(["A", "B", "C"])
    assert m["line11"].nameclass == "r0_only"  # Linecode is r0_only
    assert m["line11"].line_type == "underground"  # OH not in linecode
    assert m["line11"].from_element == "bus11"
    assert m["line11"].to_element == "bus12"
    assert m["line11"].length == 10
    assert m["line11"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line11"].is_fuse is None
    assert m["line11"].is_switch is None
    assert m["line11"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line11"].impedance_matrix == [
        [
            (0.000234937 + 0.0002153j),
            (0.000176937 + 9.47e-05j),
            (0.000176937 + 9.47e-05j),
        ],
        [
            (0.000176937 + 9.47e-05j),
            (0.000234937 + 0.0002153j),
            (0.000176937 + 9.47e-05j),
        ],
        [
            (0.000176937 + 9.47e-05j),
            (0.000176937 + 9.47e-05j),
            (0.000234937 + 0.0002153j),
        ],
    ]
    assert m["line11"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (-0.0006 + 0j), (0.0028 + 0j)],
    ]
    assert m["line11"].feeder_name == "sourcebus_src"
    assert m["line11"].is_recloser is None
    assert m["line11"].is_breaker is None

    for w in m["line11"].wires:
        assert w.nameclass == "r0_only"
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

    # Line 12
    assert len(m["line12"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line12"].wires]) == set(["A", "B", "C"])
    assert m["line12"].nameclass == "x1_only"  # Linecode is x1_only
    assert m["line12"].line_type == "underground"  # OH not in linecode
    assert m["line12"].from_element == "bus12"
    assert m["line12"].to_element == "bus13"
    assert m["line12"].length == 10
    assert m["line12"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line12"].is_fuse is None
    assert m["line12"].is_switch is None
    assert m["line12"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line12"].impedance_matrix == [
        [
            (9.813333e-05 + 0.000419032j),
            (4.013333e-05 - 7.166e-06j),
            (4.013333e-05 - 7.166e-06j),
        ],
        [
            (4.013333e-05 - 7.166e-06j),
            (9.813333e-05 + 0.000419032j),
            (4.013333e-05 - 7.166e-06j),
        ],
        [
            (4.013333e-05 - 7.166e-06j),
            (4.013333e-05 - 7.166e-06j),
            (9.813333e-05 + 0.000419032j),
        ],
    ]
    assert m["line12"].capacitance_matrix == [
        [(0.0028 + 0j), (-0.0006 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (0.0028 + 0j), (-0.0006 + 0j)],
        [(-0.0006 + 0j), (-0.0006 + 0j), (0.0028 + 0j)],
    ]
    assert m["line12"].feeder_name == "sourcebus_src"
    assert m["line12"].is_recloser is None
    assert m["line12"].is_breaker is None

    for w in m["line12"].wires:
        assert w.nameclass == "x1_only"
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

    # Line 13
    assert len(m["line13"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line13"].wires]) == set(["A", "B", "C"])
    assert m["line13"].nameclass == "x0_only"  # Linecode is x0_only
    assert m["line13"].line_type == "underground"  # OH not in linecode
    assert m["line13"].from_element == "bus13"
    assert m["line13"].to_element == "bus14"
    assert m["line13"].length == 10
    assert m["line13"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line13"].is_fuse is None
    assert m["line13"].is_switch is None
    assert m["line13"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line13"].impedance_matrix == [
        [
            (9.813333e-05 + 0.00051244j),
            (4.013333e-05 + 0.00039184j),
            (4.013333e-05 + 0.00039184j),
        ],
        [
            (4.013333e-05 + 0.00039184j),
            (9.813333e-05 + 0.00051244j),
            (4.013333e-05 + 0.00039184j),
        ],
        [
            (4.013333e-05 + 0.00039184j),
            (4.013333e-05 + 0.00039184j),
            (9.813333e-05 + 0.00051244j),
        ],
    ]
    assert m["line13"].capacitance_matrix == [
        [(0.003728338 + 0j), (0.0003283376 + 0j), (0.0003283376 + 0j)],
        [(0.0003283376 + 0j), (0.003728338 + 0j), (0.0003283376 + 0j)],
        [(0.0003283376 + 0j), (0.0003283376 + 0j), (0.003728338 + 0j)],
    ]
    assert m["line13"].feeder_name == "sourcebus_src"
    assert m["line13"].is_recloser is None
    assert m["line13"].is_breaker is None

    for w in m["line13"].wires:
        assert w.nameclass == "x0_only"
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

    # Line 14
    assert len(m["line14"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line14"].wires]) == set(["A", "B", "C"])
    assert m["line14"].nameclass == "c1_only"  # Linecode is c1_only
    assert m["line14"].line_type == "underground"  # OH not in linecode
    assert m["line14"].from_element == "bus14"
    assert m["line14"].to_element == "bus15"
    assert m["line14"].length == 10
    assert m["line14"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line14"].is_fuse is None
    assert m["line14"].is_switch is None
    assert m["line14"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line14"].impedance_matrix == [
        [
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.47e-05j),
            (4.013333e-05 + 9.47e-05j),
        ],
        [
            (4.013333e-05 + 9.47e-05j),
            (9.813333e-05 + 0.0002153j),
            (4.013333e-05 + 9.47e-05j),
        ],
        [
            (4.013333e-05 + 9.47e-05j),
            (4.013333e-05 + 9.47e-05j),
            (9.813333e-05 + 0.0002153j),
        ],
    ]
    assert m["line14"].capacitance_matrix == [
        [(0.007487255 + 0j), (-0.002943627 + 0j), (-0.002943627 + 0j)],
        [(-0.002943627 + 0j), (0.007487255 + 0j), (-0.002943627 + 0j)],
        [(-0.002943627 + 0j), (-0.002943627 + 0j), (0.007487255 + 0j)],
    ]
    assert m["line14"].feeder_name == "sourcebus_src"
    assert m["line14"].is_recloser is None
    assert m["line14"].is_breaker is None

    for w in m["line14"].wires:
        assert w.nameclass == "c1_only"
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

    # Line 15
    assert len(m["line15"].wires) == 3  # Number of wires
    #    Phases of the different wires
    assert set([w.phase for w in m["line15"].wires]) == set(["A", "B", "C"])
    assert m["line15"].nameclass == "c0_only"  # Linecode is c0_only
    assert m["line15"].line_type == "underground"  # OH not in linecode
    assert m["line15"].from_element == "bus15"
    assert m["line15"].to_element == "bus16"
    assert m["line15"].length == 10
    assert m["line15"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["line15"].is_fuse is None
    assert m["line15"].is_switch is None
    assert m["line15"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line15"].impedance_matrix == [
        [(0.09813333 + 0.2153j), (0.04013333 + 0.0947j), (0.04013333 + 0.0947j)],
        [(0.04013333 + 0.0947j), (0.09813333 + 0.2153j), (0.04013333 + 0.0947j)],
        [(0.04013333 + 0.0947j), (0.04013333 + 0.0947j), (0.09813333 + 0.2153j)],
    ]
    assert m["line15"].capacitance_matrix == [
        [(2.8 + 0j), (-0.6 + 0j), (-0.6 + 0j)],
        [(-0.6 + 0j), (2.8 + 0j), (-0.6 + 0j)],
        [(-0.6 + 0j), (-0.6 + 0j), (2.8 + 0j)],
    ]
    assert m["line15"].feeder_name == "sourcebus_src"
    assert m["line15"].is_recloser is None
    assert m["line15"].is_breaker is None

    for w in m["line15"].wires:
        assert w.nameclass == "c0_only"
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
