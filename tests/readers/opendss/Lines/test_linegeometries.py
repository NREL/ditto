# -*- coding: utf-8 -*-

"""
test_linegeometries.py
----------------------------------

Tests for reading LineGeometries from OpenDSS into DiTTo.
"""

import os
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_linegeometries():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_linegeometries.dss"))
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

    # Number of wires
    assert len(m["line1"].wires) == 4  # Line1 should have 4 wires
    # Phases of the different wires
    assert set([w.phase for w in m["line1"].wires]) == set(["A", "B", "C", "N"])
    assert m["line1"].name == "line1"
    assert m["line1"].nominal_voltage == float(4.8) * 10 ** 3
    assert m["line1"].line_type == "underground"
    assert m["line1"].length == 300 * 0.3048  # units = ft
    assert m["line1"].from_element == "bus1"
    assert m["line1"].to_element == "bus2"
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None
    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]
    imp_matrix = [
        [
            (0.00024738133202099736 + 0.0008769514435695538j),
            (5.8098917322834634e-05 + 0.00031932778871391075j),
            (5.72120406824147e-05 + 0.000463759186351706j),
            (5.716135170603674e-05 + 0.0004757342519685039j),
        ],
        [
            (5.8098917322834634e-05 + 0.00031932778871391075j),
            (0.0002491671587926509 + 0.0008750521653543306j),
            (5.8104363517060364e-05 + 0.00031960810367454067j),
            (5.803946850393701e-05 + 0.00031432549212598423j),
        ],
        [
            (5.72120406824147e-05 + 0.000463759186351706j),
            (5.8104363517060364e-05 + 0.00031960810367454067j),
            (0.00024738133202099736 + 0.0008769514435695538j),
            (5.7170767716535434e-05 + 0.0005039970472440944j),
        ],
        [
            (5.716135170603674e-05 + 0.0004757342519685039j),
            (5.803946850393701e-05 + 0.00031432549212598423j),
            (5.7170767716535434e-05 + 0.0005039970472440944j),
            (0.0007530643044619422 + 0.0010085508530183727j),
        ],
    ]
    assert m["line1"].impedance_matrix == imp_matrix
    assert m["line1"].capacitance_matrix == [
        [
            (0.008384708005249344 + 0j),
            (-0.0001470299868766404 + 0j),
            (-0.0019942040682414696 + 0j),
            (-0.0020357719816272964 + 0j),
        ],
        [
            (-0.0001470299868766404 + 0j),
            (0.00994426837270341 + 0j),
            (-0.00014228366141732281 + 0j),
            (-9.78384186351706e-05 + 0j),
        ],
        [
            (-0.0019942040682414696 + 0j),
            (-0.00014228366141732281 + 0j),
            (0.008713290682414698 + 0j),
            (-0.002607346128608924 + 0j),
        ],
        [
            (-0.0020357719816272964 + 0j),
            (-9.78384186351706e-05 + 0j),
            (-0.002607346128608924 + 0j),
            (0.008078645013123359 + 0j),
        ],
    ]
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None
    assert m["line1"].nameclass == ""

    for w in m["line1"].wires:
        assert w.emergency_ampacity == -1
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr == None
        assert w.concentric_neutral_resistance == None
        assert w.concentric_neutral_diameter == None
        assert w.concentric_neutral_outside_diameter == None
        assert w.concentric_neutral_nstrand == None

    phased_wires = {}
    for wire in m["line1"].wires:
        phased_wires[wire.phase] = wire

    # Nameclass
    for p in ["A", "B", "C"]:
        assert phased_wires[p].ampacity == 530
        assert phased_wires[p].nameclass == "wire1"

    assert phased_wires["N"].ampacity == 230
    assert phased_wires["N"].nameclass == "wire2"

    # Positions of the wires
    assert (phased_wires["A"].X, phased_wires["A"].Y) == (-1.2909, 13.716)
    assert (phased_wires["B"].X, phased_wires["B"].Y) == (
        -0.1530096 * 0.3048,
        4.1806368 * 0.3048,
    )
    assert (phased_wires["C"].X, phased_wires["C"].Y) == (0.5737, 13.716)
    assert (phased_wires["N"].X, phased_wires["N"].Y) == (0.0, 14.648)

    # GMR
    for p in ["A", "B", "C"]:
        assert phased_wires[p].gmr == 0.0255 * 0.3048
    assert phased_wires["N"].gmr == 0.00446 * 0.3048

    # Diameter
    for p in ["A", "B", "C"]:
        assert phased_wires[p].diameter == 0.741 * 0.0254
    assert phased_wires["N"].diameter == 0.398 * 0.0254

    # Resistance
    # TODO: Change this once the resistance of a Wire object will no longer be the total
    # resistance, but the per meter resistance...
    #
    for p in ["A", "B", "C"]:
        assert phased_wires[p].resistance == pytest.approx(
            0.306 * 0.000621371 * 300 * 0.3048, 0.00001
        )
    assert phased_wires["N"].resistance == pytest.approx(
        1.12 * 0.000621371 * 300 * 0.3048, 0.00001
    )

    # Number of wires
    assert len(m["line2"].wires) == 3
    # Phases of the different wires
    assert set([w.phase for w in m["line2"].wires]) == set(["A", "B", "C"])
    assert m["line2"].name == "line2"
    assert m["line2"].nominal_voltage == float(4.8) * 10 ** 3
    assert m["line2"].line_type == "underground"
    assert m["line2"].length == 1 * 1609.34  # units = mi
    assert m["line2"].from_element == "bus2"
    assert m["line2"].to_element == "bus3"
    assert m["line2"].is_fuse is None
    assert m["line2"].is_switch is None
    assert m["line2"].faultrate == parsed_values["Line"]["faultrate"]
    assert m["line2"].impedance_matrix == [
        [
            (0.0004969816819317236 + 0.00026779083350938896j),
            (0.0002020738936458424 + 1.0858935961325762e-05j),
            (0.00017973933413697543 - 1.807117203325587e-05j),
        ],
        [
            (0.0002020738936458424 + 1.0858935961325762e-05j),
            (0.0004905287260616153 + 0.000241154572681969j),
            (0.0002020738936458424 + 1.0858935961325762e-05j),
        ],
        [
            (0.00017973933413697543 - 1.807117203325587e-05j),
            (0.0002020738936458424 + 1.0858935961325762e-05j),
            (0.0004969816819317236 + 0.00026779083350938896j),
        ],
    ]
    assert m["line2"].capacitance_matrix == [
        [(0.23857494376576735 + 0j), 0j, 0j],
        [0j, (0.23857494376576735 + 0j), 0j],
        [0j, 0j, (0.23857494376576735 + 0j)],
    ]
    assert m["line2"].feeder_name == "sourcebus_src"
    assert m["line2"].is_recloser is None
    assert m["line2"].is_breaker is None
    assert m["line2"].nameclass == ""

    for w in m["line2"].wires:
        assert w.emergency_ampacity == -1
        assert w.insulation_thickness == 0.0
        assert w.is_open is None
        assert w.concentric_neutral_gmr == 2
        assert w.concentric_neutral_resistance == 2.816666667
        assert w.concentric_neutral_diameter == 0.064
        assert w.concentric_neutral_outside_diameter == 1.16
        assert w.concentric_neutral_nstrand == 13

    phased_wires = {}
    for wire in m["line2"].wires:
        phased_wires[wire.phase] = wire

    # Nameclass
    for p in ["A", "B", "C"]:
        assert phased_wires[p].ampacity == -1
        assert phased_wires[p].nameclass == "cndata1"

    # Positions of the wires
    assert (phased_wires["A"].X, phased_wires["A"].Y) == (-0.5 * 0.3048, -4 * 0.3048)
    assert (phased_wires["B"].X, phased_wires["B"].Y) == (0, -4 * 0.3048)
    assert (phased_wires["C"].X, phased_wires["C"].Y) == (0.5 * 0.3048, -4 * 0.3048)

    # GMR
    for p in ["A", "B", "C"]:
        assert phased_wires[p].gmr == 0.20568 * 0.0254

    # Diameter
    for p in ["A", "B", "C"]:
        assert phased_wires[p].diameter == 0.573 * 0.0254

    for p in ["A", "B", "C"]:
        assert phased_wires[p].resistance == pytest.approx(
            0.076705 * 1609.34 * 0.00328084, 0.00001
        )
