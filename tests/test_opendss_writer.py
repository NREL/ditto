# -*- coding: utf-8 -*-

"""
test_opendss_writer
----------------------------------

Tests for writing functions of the OpenDSS writer
"""
import logging
import os

import six

import tempfile
import pytest
import pytest as pt

logger = logging.getLogger(__name__)


def test_parse_wire():
    from ditto.store import Store
    from ditto.models.wire import Wire
    from ditto.writers.opendss.write import Writer

    m = Store()
    wire_A = Wire(
        m,
        phase="A",
        nameclass="wire_test_phase",
        diameter=5,
        gmr=10,
        ampacity=500,
        emergency_ampacity=1000,
        resistance=5,
    )
    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    parsed_wire = w.parse_wire(wire_A)
    assert parsed_wire["GMRac"] == 10
    assert parsed_wire["Diam"] == 5
    assert parsed_wire["normamps"] == 500
    assert parsed_wire["emergamps"] == 1000
    assert parsed_wire["Rac"] == 5


def test_parse_concentric_neutral_cable():
    """
    Tests the parsing of concentric neutral cables.

    The example used is:

    New CNDATA.250_1/3 k=13 DiaStrand=0.064 Rstrand=2.816666667 epsR=2.3
    ~ InsLayer=0.220 DiaIns=1.06 DiaCable=1.16 Rac=0.076705 GMRac=0.20568 diam=0.573
    ~ Runits=kft Radunits=in GMRunits=in
    """
    from ditto.store import Store
    from ditto.models.wire import Wire
    from ditto.writers.opendss.write import Writer

    m = Store()
    wire = Wire(
        m,
        phase="A",
        nameclass="250_1/3",
        diameter=0.0145542,  # 0.573 inches in meters
        gmr=0.005224272,  # 0.20568 inches in meters
        ampacity=500,
        emergency_ampacity=1000,
        resistance=0.000251656824147,  # 0.076705 ohm/kft in ohm/meter
        concentric_neutral_resistance=0.00924103237205,  # 2.816666667 ohm/kft in ohm/meter
        concentric_neutral_diameter=0.0016256,  # 0.064 inches in meters
        concentric_neutral_outside_diameter=0.029464,  # 1.16 inches in meters
        concentric_neutral_nstrand=13,
    )
    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    parsed_cable = w.parse_cable(wire)
    assert parsed_cable["k"] == 13
    assert parsed_cable["DiaStrand"] == 0.0016256
    assert parsed_cable["Rstrand"] == 0.00924103237205
    assert parsed_cable["Diam"] == 0.0145542
    assert parsed_cable["DiaCable"] == 0.029464
    assert parsed_cable["Rac"] == 0.000251656824147
    assert parsed_cable["GMRac"] == 0.005224272
    assert parsed_cable["Runits"] == "m"
    assert parsed_cable["Radunits"] == "m"
    assert parsed_cable["GMRunits"] == "m"


def setup_line_test():
    """Setup a line with 4 wires."""
    from ditto.store import Store
    from ditto.models.line import Line
    from ditto.models.wire import Wire

    m = Store()
    wire_A = Wire(
        m,
        phase="A",
        nameclass="wire_test_phase",
        diameter=5,
        gmr=10,
        ampacity=500,
        emergency_ampacity=1000,
        resistance=5,
    )
    wire_B = Wire(
        m,
        phase="B",
        nameclass="wire_test_phase",
        diameter=5,
        gmr=10,
        ampacity=500,
        emergency_ampacity=1000,
        resistance=5,
    )
    wire_C = Wire(
        m,
        phase="C",
        nameclass="wire_test_phase",
        diameter=5,  # Missing GMR
        ampacity=500,
        emergency_ampacity=1000,
        resistance=5,
    )
    wire_N = Wire(
        m,
        phase="N",
        nameclass="wire_test_neutral",
        diameter=5,
        gmr=10,
        ampacity=500,
        emergency_ampacity=1000,
        resistance=5,
    )
    line = Line(m, name="l1", wires=[wire_A, wire_B, wire_C, wire_N])

    return line


def test_write_wiredata():
    """Test the method write_wiredata()."""
    from ditto.writers.opendss.write import Writer

    line = setup_line_test()
    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    w.write_wiredata([line])


def get_property_from_dss_string(string, property):
    """Get the value of the given property within the dss string."""
    L = string.split(" ")
    result = []
    for l in L:
        if "=" in l:
            ll = [x.strip() for x in l.split("=")]
            if ll[0].lower() == property.lower():
                result.append(ll[1].lower())
    if len(result) == 1:
        return result[0]
    elif len(result) == 0:
        return None
    else:
        return result


def test_get_property_from_dss_string():
    """Tests the get_property_from_dss_string function."""
    string = (
        "New LineGeometry.Geometry_1 Nconds=4 Nphases=3 Units=km Cond=1 Wire=wire_test_phase Normamps=500.0 Emergamps=1000.0 Cond=2 Wire=wire_test_phase Normamps=500.0 Emergamps=1000.0 Cond=3 Wire=wire_test_phase_1 Normamps=500.0 Emergamps=1000.0 Cond=4 Wire=wire_test_neutral Normamps=500.0 Emergamps=1000.0 Reduce=y\n"
    )
    assert get_property_from_dss_string(string, "reduce") == "y"
    assert get_property_from_dss_string(string, "Nconds") == "4"
    assert get_property_from_dss_string(string, "nphases") == "3"
    assert get_property_from_dss_string(string, "Emergamps") == [
        "1000.0",
        "1000.0",
        "1000.0",
        "1000.0",
    ]
    assert get_property_from_dss_string(string, "crazy_property") is None


def test_write_linegeometry():
    """Test the write_linegeometry() method."""
    from ditto.writers.opendss.write import Writer

    line = setup_line_test()
    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    w.write_wiredata([line])
    w.write_linegeometry([line])
    with open(os.path.join(output_path, "LineGeometry.dss"), "r") as fp:
        lines = fp.readlines()
    assert get_property_from_dss_string(lines[0], "reduce") == "y"
    assert get_property_from_dss_string(lines[0], "nconds") == "4"
    assert get_property_from_dss_string(lines[0], "nphases") == "3"
    assert get_property_from_dss_string(lines[0], "units") == "km"
    assert get_property_from_dss_string(lines[0], "normamps") == [
        "500.0",
        "500.0",
        "500.0",
        "500.0",
    ]
    assert get_property_from_dss_string(lines[0], "Emergamps") == [
        "1000.0",
        "1000.0",
        "1000.0",
        "1000.0",
    ]


def test_write_linecodes():
    """Test the write_linecodes() method."""
    from ditto.writers.opendss.write import Writer

    line = setup_line_test()
    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    w.write_linecodes([line])
