# -*- coding: utf-8 -*-

"""
test_parsers
----------------------------------
Tests for parsers.
"""
import os
from pint import UnitRegistry
import numpy as np
from numpy.testing import (
    assert_allclose,
    assert_almost_equal,
    assert_array_almost_equal,
)

ureg = UnitRegistry()


def test_parser():
    """
    Test the Parser abstract class.
    """
    from ditto.parsers.parser import Parser

    p = Parser("test_parser")
    assert p.name == "test_parser"
    assert not p.inference
    # Position 1 is (1 meter, 0 meter)
    pos1 = (1.0 * ureg.meter, 0.0 * ureg.meter)
    # Position 2 is (1 meter, 1 meter)
    pos2 = (1.0 * ureg.meter, 1.0 * ureg.meter)
    assert p.distance(pos1, pos2, "m").magnitude == 1.0  # Distance should be 1 meter
    assert p.distance(pos1, pos2, "cm").magnitude == 100.0  # Which is also 100 cm

    # Position 1 is (10 meters, 200 inches)
    pos1 = (10.0 * ureg.meter, 200.0 * ureg.inch)
    # Position 2 is (20 feet, 0.1 mile)
    pos2 = (20.0 * ureg.feet, 0.1 * ureg.mile)
    assert p.distance(pos1, pos2, "m").magnitude == 155.90328801972072  # Not obvious...


def test_line_parser():
    """
    Test the LineParser class.
    """
    from ditto.parsers.line_parser import LineParser

    lp = LineParser("test_line_parser", 3, 4, inference=True)
    assert lp.name == "test_line_parser"
    assert lp.n_phase == 3
    assert lp.n_cond == 4
    assert lp.inference

    # Provide GMR values (one per conductor)
    gmr_phase = 0.0171 * ureg.feet
    gmr_neutral = 0.00208 * ureg.feet
    lp.set_property("GMR", [gmr_phase] * 3 + [gmr_neutral])
    for i in range(3):
        assert lp.GMR[i] == gmr_phase
    assert lp.GMR[3] == gmr_neutral

    # Test self-impedance computation.
    # Based on example from Kersting's book, page 93
    # We need the resistance of the wire, here 336,400 26/7 ACSR: 0.306 Ohm/mi
    r_a = 0.306 * ureg.parse_expression("ohm/mi")
    # We also need the GMR of this wire, 0.0244 ft
    GMR_a = 0.0244 * ureg.feet
    # Compute the self-impedance in Ohm/mi
    assert_almost_equal(
        lp.self_impedance(r_a, GMR_a, "ohm/mi").magnitude, 0.4013 + 1.4133j, decimal=4
    )

    # Test mutual-impedance
    # Using the same reference, compute the mutual impedance between phase A and B
    # Here, we need the distance between the 2 conductors: 2.5 ft
    d_ab = 2.5 * ureg.feet
    assert_almost_equal(
        lp.mutual_impedance(d_ab, "ohm/mi").magnitude, 0.0953 + 0.8515j, decimal=4
    )


def test_underground_line_parser():
    """
    Tests the UndergroundLineParser class.
    """
    from ditto.parsers.underground_line_parser import UndergroundLineParser

    ulp = UndergroundLineParser("test_udg_line_parser", 3, 13)
    assert ulp.name == "test_udg_line_parser"
    assert ulp.n_phase == 3
    assert ulp.n_cond == 6  # Set to twice the number of phases by the constructor
    assert ulp.n_strand == 13.0

    # Test impedance matrix computation
    # Based on the example from Kersting's book, page 99
    # 3 concentric neutral cables of 1.29 inches with 13 neutral strands
    # lying 6 inches from each other
    #
    # Set the outside diameters for the cables.
    # Here, they are all the same. All cables have a diameter of 1.29 inches
    ulp.set_property("outside_diameters", [1.29 * ureg.inch] * 3)
    for i in range(3):
        assert ulp.outside_diameters[i].to(ureg.inch).magnitude == 1.29

    # Set the positions of the cable, 6 inches from each other.
    ulp.set_property(
        "positions",
        [
            (0 * ureg.inch, 0 * ureg.inch),
            (6 * ureg.inch, 0 * ureg.inch),
            (12 * ureg.inch, 0 * ureg.inch),
        ],
    )
    # Distance between cable 1 and 2 should be 6 inches
    assert ulp.distance(ulp.positions[0], ulp.positions[1], "in").magnitude == 6.0
    # Distance between cable 2 and 3 should be also 6 inches, which is also 0.5 feet
    assert ulp.distance(ulp.positions[1], ulp.positions[2], "ft").magnitude == .5
    # Distance between cable 1 and 3 should be 12 inches, or 1 feet
    assert ulp.distance(ulp.positions[0], ulp.positions[2], "in").magnitude == 12.0
    assert ulp.distance(ulp.positions[0], ulp.positions[2], "ft").magnitude == 1.0

    # The phase conductors are all the same: 250,000 AA
    # The neutrals are also all the same: #14 copper neutral strands
    # phase GMR = 0.0171 ft.
    # neutral GMR = 0.00208 ft.
    #
    ulp.set_property("GMR", [0.0171 * ureg.feet] * 3 + [0.00208 * ureg.feet] * 3)
    assert np.all(
        np.array([x.magnitude for x in ulp.GMR])
        == np.array([0.0171] * 3 + [0.00208] * 3)
    )

    # phase Diameter = 0.567 inches
    # neutral diameter = 0.0641 inches
    ulp.set_property("diameters", [0.567 * ureg.inch] * 3 + [0.0641 * ureg.inch] * 3)
    assert np.all(
        np.array([x.magnitude for x in ulp.diameters])
        == np.array([0.567] * 3 + [0.0641] * 3)
    )

    # phase Resistance = 0.4100 Ohm/mile
    # neutral Resistance = 14.8722 Ohm/mile
    ulp.set_property(
        "resistance",
        [0.41 * ureg.parse_expression("ohm/mi")] * 3
        + [14.8722 * ureg.parse_expression("ohm/mi")] * 3,
    )
    assert np.all(
        np.array([x.magnitude for x in ulp.resistance])
        == np.array([0.41] * 3 + [14.8722] * 3)
    )

    # Compute the impedance matrix
    ulp.compute_impedance_matrix("ohm/mi")

    # The result impedance matrix can be found page 101 of Kersting's book
    kersting_result_z_ij = np.array(
        [
            [.5053 + 1.4564j, .0953 + 1.0468j, .0953 + .9627j],
            [.0953 + 1.0468j, .5053 + 1.4564j, .0953 + 1.0468j],
            [.0953 + .9627j, .0953 + 1.0468j, .5053 + 1.4564j],
        ]
    )
    assert_array_almost_equal(ulp.z_ij, kersting_result_z_ij, decimal=4)

    kersting_result_z_in = np.array(
        [
            [.0953 + 1.3236j, .0953 + 1.0468j, .0953 + .9627j],
            [.0953 + 1.0468j, .0953 + 1.3236j, .0953 + 1.0468j],
            [.0953 + .9627j, .0953 + 1.0468j, .0953 + 1.3236j],
        ]
    )
    assert_array_almost_equal(ulp.z_in, kersting_result_z_in, decimal=4)
    assert_array_almost_equal(ulp.z_nj, kersting_result_z_in.T, decimal=4)

    kersting_result_z_nn = np.array(
        [
            [1.2391 + 1.3296j, .0953 + 1.0468j, .0953 + .9627j],
            [.0953 + 1.0468j, 1.2391 + 1.3296j, .0953 + 1.0468j],
            [.0953 + .9627j, .0953 + 1.0468j, 1.2391 + 1.3296j],
        ]
    )
    assert_array_almost_equal(ulp.z_nn, kersting_result_z_nn, decimal=3)

    kersting_result_impedance_matrix = np.array(
        [
            [0.7981 + 0.4463j, 0.3191 + 0.0328j, 0.2849 - 0.0143j],
            [0.3191 + 0.0328j, 0.7891 + 0.4041j, 0.3191 + 0.0328j],
            [0.2849 - 0.0143j, 0.3191 + 0.0328j, 0.7981 + 0.4463j],
        ]
    )
    assert_array_almost_equal(
        ulp.impedance_matrix, kersting_result_impedance_matrix, decimal=4
    )


def test_overhead_line_parser():
    """
    Test the OverheadLineParser class.
    """
    from ditto.parsers.overhead_line_parser import OverheadLineParser

    # Here we use the example for overhead lines from Kersting's book, page 93
    # We have a 3 phase, 4 wires overhead line:
    #
    olp = OverheadLineParser("overhead_test_parser", 3, 4)
    assert olp.name == "overhead_test_parser"
    assert olp.n_phase == 3
    assert olp.n_cond == 4

    # The phase wires are 336,400 26/7 ACSR
    # and the neutral wire is 4/0 6/1 ACSR
    #
    # The GMR of the phase conductors is 0.0244 ft
    # And the GMR of the neutral conductor is 0.00814 ft
    olp.set_property("GMR", [0.0244 * ureg.feet] * 3 + [0.00814 * ureg.feet])
    assert np.all(
        np.array([x.magnitude for x in olp.GMR]) == np.array([0.0244] * 3 + [0.00814])
    )

    # The Resistance of the phase conductors is 0.306 Ohm/mile
    # And the resistance of the neutral conductor is 0.5920 Ohm/mile
    olp.set_property(
        "resistance",
        [0.306 * ureg.parse_expression("ohm/mi")] * 3
        + [0.5920 * ureg.parse_expression("ohm/mi")],
    )
    assert np.all(
        np.array([x.magnitude for x in olp.resistance])
        == np.array([0.306] * 3 + [0.5920])
    )

    # The example gives directly the distances
    # We still provide the positions
    olp.set_property(
        "positions",
        [
            (0 * ureg.feet, (25.0 + 4.0) * ureg.feet),
            (2.5 * ureg.feet, (25.0 + 4.0) * ureg.feet),
            ((4.5 + 2.5) * ureg.feet, (25.0 + 4.0) * ureg.feet),
            ((2.5 + (4.5 - 3.0)) * ureg.feet, 25.0 * ureg.feet),
        ],
    )
    # Check the distance values in feet
    assert olp.distance(olp.positions[0], olp.positions[1], "ft").magnitude == 2.5
    assert olp.distance(olp.positions[0], olp.positions[2], "ft").magnitude == 7.0
    assert_almost_equal(
        olp.distance(olp.positions[0], olp.positions[3], "ft").magnitude,
        5.6569,
        decimal=4,
    )
    assert olp.distance(olp.positions[1], olp.positions[2], "ft").magnitude == 4.5
    assert_almost_equal(
        olp.distance(olp.positions[1], olp.positions[3], "ft").magnitude,
        4.272,
        decimal=4,
    )
    assert olp.distance(olp.positions[2], olp.positions[3], "ft").magnitude == 5.0

    # We have everything we need to compute the impedance matrix
    olp.compute_impedance_matrix("ohm/mi")

    # z_ij
    kersting_result_z_ij = np.array(
        [
            [0.4013 + 1.4133j, 0.0953 + 0.8515j, 0.0953 + 0.7266j],
            [0.0953 + 0.8515j, 0.4013 + 1.4133j, 0.0943 + 0.7802j],
            [0.0953 + 0.7266j, 0.0953 + 0.7802j, 0.4013 + 1.4133j],
        ]
    )
    assert_array_almost_equal(olp.z_ij, kersting_result_z_ij, decimal=3)

    # z_in
    kersting_result_z_in = np.array(
        [[0.0953 + 0.7524j], [0.0953 + 0.7865j], [0.0953 + 0.7674j]]
    )
    assert_array_almost_equal(olp.z_in, kersting_result_z_in, decimal=4)

    # z_nn
    kersting_result_z_nn = np.array([[0.6873 + 1.5465j]])
    assert_array_almost_equal(olp.z_nn, kersting_result_z_nn, decimal=4)

    # z_nj
    kersting_result_z_nj = np.array(
        [[0.0953 + 0.7524j, 0.0953 + 0.7865j, 0.0953 + 0.7674j]]
    )
    assert_array_almost_equal(olp.z_nj, kersting_result_z_nj, decimal=4)

    kersting_result_impedance_matrix = np.array(
        [
            [0.4576 + 1.0780j, 0.1560 + .5017j, 0.1535 + 0.3849j],
            [0.1560 + 0.5017j, 0.4666 + 1.0482j, 0.1580 + 0.4236j],
            [0.1535 + 0.3849j, 0.1580 + 0.4236j, 0.4615 + 1.0651j],
        ]
    )
    assert_array_almost_equal(
        olp.impedance_matrix, kersting_result_impedance_matrix, decimal=4
    )
