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


@pytest.mark.xfail(reason="This test fails when opendssdirect v0.5.0 is used.")
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
    assert m["line1"].line_type == "overhead"
    assert m["line1"].length == 300 * 0.3048  # units = ft
    assert m["line1"].from_element == "bus1"
    assert m["line1"].to_element == "bus2"
    assert m["line1"].is_fuse is None
    assert m["line1"].is_switch is None

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
    imp_matrix = np.zeros((4, 4), dtype=np.complex_)
    imp_matrix.fill(rem)
    np.fill_diagonal(imp_matrix, diag)
    imp_matrix = imp_matrix.tolist()

    assert m["line1"].faultrate == parsed_values["Line"]["faultrate"]

    np.testing.assert_array_almost_equal(
        m["line1"].impedance_matrix,
        [
            [
                (0.00024738133202099736 + 0.0008769514435695538j),
                (5.810587270341207e-05 + 0.00031932618110236215j),
                (5.723612204724409e-05 + 0.0004637522965879265j),
                (5.717280183727034e-05 + 0.0004757309711286089j),
            ],
            [
                (5.810587270341207e-05 + 0.00031932618110236215j),
                (0.0002491671587926509 + 0.0008750521653543306j),
                (5.810603674540682e-05 + 0.0003196077099737533j),
                (5.803946850393701e-05 + 0.0003143254593175853j),
            ],
            [
                (5.723612204724409e-05 + 0.0004637522965879265j),
                (5.810603674540682e-05 + 0.0003196077099737533j),
                (0.00024738133202099736 + 0.0008769514435695538j),
                (5.717296587926509e-05 + 0.0005039963910761155j),
            ],
            [
                (5.717280183727034e-05 + 0.0004757309711286089j),
                (5.803946850393701e-05 + 0.0003143254593175853j),
                (5.717296587926509e-05 + 0.0005039963910761155j),
                (0.0007530643044619422 + 0.0010085508530183727j),
            ],
        ],
    )
    np.testing.assert_array_almost_equal(
        m["line1"].capacitance_matrix,
        [
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
        ],
    )
    assert m["line1"].feeder_name == "sourcebus_src"
    assert m["line1"].is_recloser is None
    assert m["line1"].is_breaker is None
    assert m["line1"].nameclass == ""

    for w in m["line1"].wires:
        assert w.emergency_ampacity == 795
        assert w.insulation_thickness == parsed_values["Wire"]["insulation_thickness"]
        assert w.is_open is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None

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
    np.testing.assert_array_almost_equal(
        m["line2"].impedance_matrix,
        [
            [
                (0.0005010314787428386 + 0.00026819845402463124j),
                (0.00020170349335752545 + 1.1288596567537003e-05j),
                (0.00017933407483813242 - 1.766354530428623e-05j),
            ],
            [
                (0.00020170349335752545 + 1.1288596567537003e-05j),
                (0.0004946492350901612 + 0.00024160345234692485j),
                (0.00020170349335752545 + 1.1288596567537003e-05j),
            ],
            [
                (0.00017933407483813242 - 1.766354530428623e-05j),
                (0.00020170349335752545 + 1.1288596567537003e-05j),
                (0.0005010314787428386 + 0.00026819845402463124j),
            ],
        ],
    )

    np.testing.assert_array_almost_equal(
        m["line2"].capacitance_matrix,
        [
            [(0.23857494376576735 + 0j), 0j, 0j],
            [0j, (0.23857494376576735 + 0j), 0j],
            [0j, 0j, (0.23857494376576735 + 0j)],
        ],
    )
    assert m["line2"].feeder_name == "sourcebus_src"
    assert m["line2"].is_recloser is None
    assert m["line2"].is_breaker is None
    assert m["line2"].nameclass == ""

    for w in m["line2"].wires:
        assert w.emergency_ampacity is None
        assert w.insulation_thickness == 0.005588
        assert w.is_open is None
        assert w.concentric_neutral_gmr == 0.0508
        assert w.concentric_neutral_resistance == 858.5200001016
        assert w.concentric_neutral_diameter == 0.0016256
        assert w.concentric_neutral_outside_diameter == 0.029463999999999997
        assert w.concentric_neutral_nstrand == 13

    phased_wires = {}
    for wire in m["line2"].wires:
        phased_wires[wire.phase] = wire

    # Nameclass
    for p in ["A", "B", "C"]:
        assert phased_wires[p].ampacity is None
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
