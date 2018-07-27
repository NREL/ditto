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
    assert (
        lines[0]
        == "New LineGeometry.Geometry_1 Nconds=4 Nphases=3 Units=km Cond=1 Wire=wire_test_phase Normamps=500.0 Emergamps=1000.0 Cond=2 Wire=wire_test_phase Normamps=500.0 Emergamps=1000.0 Cond=3 Wire=wire_test_phase_1 Normamps=500.0 Emergamps=1000.0 Cond=4 Wire=wire_test_neutral Normamps=500.0 Emergamps=1000.0 Reduce=y\n"
    )


def test_write_linecodes():
    """Test the write_linecodes() method."""
    from ditto.writers.opendss.write import Writer

    line = setup_line_test()
    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    w.write_linecodes([line])
