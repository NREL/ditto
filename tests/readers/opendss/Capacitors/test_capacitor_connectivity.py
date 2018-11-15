# -*- coding: utf-8 -*-

"""
test_capacitor_connectivity.py
----------------------------------

Tests for parsing all the attributes of Capacitors when reading from OpenDSS to Ditto
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_capacitor_connectivity():
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_capacitor_connectivity.dss")
    )
    r.parse(m)
    m.set_names()

    assert len(m["cap1"].phase_capacitors) == 3  # Cap1 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["cap1"].phase_capacitors]
    ) == pytest.approx(600 * 10 ** 3, 0.0001)
    assert m["cap1"].nominal_voltage == float(4.16) * 10 ** 3
    #    assert m["cap1"].connection_type is None # Default is set as Y
    assert m["cap1"].delay is None
    assert m["cap1"].mode is None
    assert m["cap1"].low is None
    assert m["cap1"].high is None
    #    assert m["cap1"].resistance is None # 0.0
    assert m["cap1"].resistance0 is None
    #    assert m["cap1"].reactance is None # 0.0
    assert m["cap1"].reactance0 is None
    assert m["cap1"].susceptance is None
    assert m["cap1"].susceptance0 is None
    assert m["cap1"].conductance is None
    assert m["cap1"].conductance0 is None
    assert m["cap1"].pt_ratio is None
    assert m["cap1"].ct_ratio is None
    assert m["cap1"].pt_phase is None
    assert m["cap1"].connecting_element == "bus1"
    #    assert m["cap1"].positions is None # []
    assert m["cap1"].measuring_element is None
    #    assert m["cap1"].substation_name is None # ''
    assert m["cap1"].feeder_name == "sourcebus_src"
    assert m["cap1"].is_substation == 0

    assert set([pc.phase for pc in m["cap1"].phase_capacitors]) == set(["A", "B", "C"])
    assert [
        phase_capacitor.switch for phase_capacitor in m["cap1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.sections for phase_capacitor in m["cap1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.normalsections for phase_capacitor in m["cap1"].phase_capacitors
    ] == [None, None, None]

    assert len(m["cap2"].phase_capacitors) == 1  # Cap2 is a one phase capacitor
    assert m["cap2"].phase_capacitors[0].var == 100 * 10 ** 3

    assert len(m["cap3"].phase_capacitors) == 1  # Cap3 is a one phase capacitor
    assert m["cap3"].phase_capacitors[0].var == 200.37 * 10 ** 3

    assert len(m["cap4"].phase_capacitors) == 2  # Cap4 is a two phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["cap4"].phase_capacitors]
    ) == pytest.approx(400 * 10 ** 3, 0.0001)

    #  Capacitors from epri_j1
    assert len(m["b4909-1"].phase_capacitors) == 3  # b4909-1 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["b4909-1"].phase_capacitors]
    ) == pytest.approx(900 * 10 ** 3, 0.0001)
    assert m["b4909-1"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["b4909-1"].connection_type == "Y"
    assert m["b4909-1"].delay == 30
    assert m["b4909-1"].mode == "voltage"
    # assert m["b4909-1"].low is None # 115.0
    # assert m["b4909-1"].high is None # 126.0
    # assert m["b4909-1"].resistance is None # 0.0
    assert m["b4909-1"].resistance0 is None
    # assert m["b4909-1"].reactance is None # 0.0
    assert m["b4909-1"].reactance0 is None
    assert m["b4909-1"].susceptance is None
    assert m["b4909-1"].susceptance0 is None
    assert m["b4909-1"].conductance is None
    assert m["b4909-1"].conductance0 is None
    assert m["b4909-1"].pt_ratio == 60
    # assert m["b4909-1"].ct_ratio is None # 60
    assert m["b4909-1"].pt_phase == "B"
    assert m["b4909-1"].connecting_element == "b4909"
    #    assert m["b4909-1"].positions is None # []
    assert m["b4909-1"].measuring_element == "Line.OH_B4904"
    #    assert m["b4909-1"].substation_name is None # ''
    assert m["b4909-1"].feeder_name == "sourcebus_src"
    assert m["b4909-1"].is_substation == 0

    assert set([pc.phase for pc in m["b4909-1"].phase_capacitors]) == set(
        ["A", "B", "C"]
    )
    assert [
        phase_capacitor.switch for phase_capacitor in m["b4909-1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.sections for phase_capacitor in m["b4909-1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.normalsections
        for phase_capacitor in m["b4909-1"].phase_capacitors
    ] == [None, None, None]
    # oh_b4904
    # assert len(m["oh_b4904"].wires) == 4  # Number of wires # Neutral wire is not counted. TBD
    #    Phases of the different wires
    #    assert set([w.phase for w in m["oh_b4904"].wires]) == set(["A", "B", "C", "N"]) # Neutral wire is not counted. TBD
    assert (
        m["oh_b4904"].nameclass == "OH-3X_477AAC_4/0AAACN"
    )  # Linecode is OH-3X_477AAC_4/0AAACN
    assert m["oh_b4904"].line_type == "overhead"  # OH in lincecode
    assert m["oh_b4904"].from_element == "b4909"
    assert m["oh_b4904"].to_element == "b4904"
    assert m["oh_b4904"].length == pytest.approx(161.84879)
    assert m["oh_b4904"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["oh_b4904"].is_fuse is None
    assert m["oh_b4904"].is_switch is None
    assert m["oh_b4904"].is_banked is None
    assert m["oh_b4904"].faultrate == 0.1
    #    assert m["oh_b4904"].positions is None # []
    # assert m["oh_b4904"].impedance_matrix == None # Fill in later # [[(0.09813333+0.2153j), (0.04013333+0.0947j), (0.04013333+0.0947j)], [(0.04013333+0.0947j), (0.09813333+0.2153j), (0.04013333+0.0947j)], [(0.04013333+0.0947j), (0.04013333+0.0947j), (0.09813333+0.2153j)]]
    # assert m["oh_b4904"].capacitance_matrix == None # [[(2.8+0j), (-0.6+0j), (-0.6+0j)], [(-0.6+0j), (2.8+0j), (-0.6+0j)], [(-0.6+0j), (-0.6+0j), (2.8+0j)]]
    assert m["oh_b4904"].substation_name is None
    assert m["oh_b4904"].feeder_name == "sourcebus_src"
    assert m["oh_b4904"].is_recloser is None
    assert m["oh_b4904"].is_breaker is None
    assert m["oh_b4904"].is_sectionalizer is None
    assert m["oh_b4904"].is_substation == 0
    assert m["oh_b4904"].is_network_protector is None

    for w in m["oh_b4904"].wires:
        assert w.nameclass == "4/0AAACN"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        # assert w.ampacity == float(732) # 400.0
        # assert w.emergency_ampacity == float(871) # 600.0
        assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
        # assert w.is_fuse is None # 0
        # assert w.is_switch is None # 0
        assert w.is_open is None
        assert w.interrupting_rating is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
        assert w.drop == 0
        # assert w.is_recloser is None # 0
        # assert w.is_breaker is None # 0
        assert w.is_network_protector is None
        assert w.is_sectionalizer is None

    assert (
        len(m["b18944-1"].phase_capacitors) == 3
    )  # b18944-1 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["b18944-1"].phase_capacitors]
    ) == pytest.approx(1200 * 10 ** 3, 0.0001)
    assert m["b18944-1"].nominal_voltage == float(12.47) * 10 ** 3
    assert m["b18944-1"].connection_type == "Y"
    assert m["b18944-1"].delay == 31
    assert m["b18944-1"].mode == "voltage"
    # assert m["b18944-1"].low is None # 115.0
    # assert m["b18944-1"].high is None # 126.0
    # assert m["b18944-1"].resistance is None # 0.0
    assert m["b18944-1"].resistance0 is None
    # assert m["b18944-1"].reactance is None # 0.0
    assert m["b18944-1"].reactance0 is None
    assert m["b18944-1"].susceptance is None
    assert m["b18944-1"].susceptance0 is None
    assert m["b18944-1"].conductance is None
    assert m["b18944-1"].conductance0 is None
    assert m["b18944-1"].pt_ratio == 60
    # assert m["b18944-1"].ct_ratio is None # 60.0
    # assert m["b18944-1"].pt_phase == "B" # A
    assert m["b18944-1"].connecting_element == "b18941"
    #    assert m["b18944-1"].positions is None # []
    assert m["b18944-1"].measuring_element == "Line.OH_B18944"
    #    assert m["b18944-1"].substation_name is None # ''
    assert m["b18944-1"].feeder_name == "sourcebus_src"
    assert m["b18944-1"].is_substation == 0

    assert set([pc.phase for pc in m["b18944-1"].phase_capacitors]) == set(
        ["A", "B", "C"]
    )
    assert [
        phase_capacitor.switch for phase_capacitor in m["b18944-1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.sections for phase_capacitor in m["b18944-1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.normalsections
        for phase_capacitor in m["b18944-1"].phase_capacitors
    ] == [None, None, None]
    # oh_b18944
    # assert len(m["oh_b18944"].wires) == 4  # Number of wires # Neutral wire is not counted. TBD
    #    Phases of the different wires
    #    assert set([w.phase for w in m["oh_b18944"].wires]) == set(["A", "B", "C", "N"]) # Neutral wire is not counted. TBD
    assert m["oh_b18944"].nameclass == "OH-3X_4CU_4CUN"  # Linecode is OH-3X_4CU_4CUN
    assert m["oh_b18944"].line_type == "overhead"  # OH in lincecode
    assert m["oh_b18944"].from_element == "b18941"
    assert m["oh_b18944"].to_element == "b18944"
    assert m["oh_b18944"].length == pytest.approx(141.1224)
    assert m["oh_b18944"].nominal_voltage == float(4.16) * 10 ** 3
    assert m["oh_b18944"].is_fuse is None
    assert m["oh_b18944"].is_switch is None
    assert m["oh_b18944"].is_banked is None
    assert m["oh_b18944"].faultrate == 0.1
    #    assert m["oh_b18944"].positions is None # []
    # assert m["oh_b18944"].impedance_matrix == None # Fill in later # [[(0.09813333+0.2153j), (0.04013333+0.0947j), (0.04013333+0.0947j)], [(0.04013333+0.0947j), (0.09813333+0.2153j), (0.04013333+0.0947j)], [(0.04013333+0.0947j), (0.04013333+0.0947j), (0.09813333+0.2153j)]]
    # assert m["oh_b18944"].capacitance_matrix == None # [[(2.8+0j), (-0.6+0j), (-0.6+0j)], [(-0.6+0j), (2.8+0j), (-0.6+0j)], [(-0.6+0j), (-0.6+0j), (2.8+0j)]]
    assert m["oh_b18944"].substation_name is None
    assert m["oh_b18944"].feeder_name == "sourcebus_src"
    assert m["oh_b18944"].is_recloser is None
    assert m["oh_b18944"].is_breaker is None
    assert m["oh_b18944"].is_sectionalizer is None
    assert m["oh_b18944"].is_substation == 0
    assert m["oh_b18944"].is_network_protector is None

    for w in m["oh_b18944"].wires:
        assert w.nameclass == "4CUN"
        assert w.X is None
        assert w.Y is None
        assert w.diameter is None
        assert w.gmr is None
        assert w.ampacity == float(142)  # 400.0
        # assert w.emergency_ampacity == float(142) # 600.0
        # assert w.resistance is None
        # assert w.insulation_thickness is None # 0.0
        # assert w.is_fuse is None # 0
        # assert w.is_switch is None # 0
        assert w.is_open is None
        assert w.interrupting_rating is None
        assert w.concentric_neutral_gmr is None
        assert w.concentric_neutral_resistance is None
        assert w.concentric_neutral_diameter is None
        assert w.concentric_neutral_outside_diameter is None
        assert w.concentric_neutral_nstrand is None
        assert w.drop == 0
        # assert w.is_recloser is None # 0
        # assert w.is_breaker is None # 0
        assert w.is_network_protector is None
        assert w.is_sectionalizer is None

    #  Capacitors from ieee 8500-node test feeder

    assert (
        len(m["capbank0a"].phase_capacitors) == 1
    )  # capbank0a is a single phase capacitor
    assert m["capbank0a"].phase_capacitors[0].var == 400 * 10 ** 3
    assert m["capbank0a"].nominal_voltage == float(7.2) * 10 ** 3
    assert m["capbank0a"].connection_type == "Y"
    assert m["capbank0a"].delay == None
    assert m["capbank0a"].mode == None
    assert m["capbank0a"].low is None
    assert m["capbank0a"].high is None
    # assert m["capbank0a"].resistance is None # 0.0
    assert m["capbank0a"].resistance0 is None
    # assert m["capbank0a"].reactance is None # 0.0
    assert m["capbank0a"].reactance0 is None
    assert m["capbank0a"].susceptance is None
    assert m["capbank0a"].susceptance0 is None
    assert m["capbank0a"].conductance is None
    assert m["capbank0a"].conductance0 is None
    assert m["capbank0a"].pt_ratio == None
    assert m["capbank0a"].ct_ratio is None
    assert m["capbank0a"].pt_phase == None
    assert m["capbank0a"].connecting_element == "r42246"
    #    assert m["capbank0a"].positions is None # []
    assert m["capbank0a"].measuring_element == None
    #    assert m["capbank0a"].substation_name is None # ''
    assert m["capbank0a"].feeder_name == "sourcebus_src"
    assert m["capbank0a"].is_substation == 0

    assert m["capbank0a"].phase_capacitors[0].phase == "A"
    assert m["capbank0a"].phase_capacitors[0].switch == None
    assert m["capbank0a"].phase_capacitors[0].sections == None
    assert m["capbank0a"].phase_capacitors[0].normalsections == None

    assert (
        len(m["capbank0b"].phase_capacitors) == 1
    )  # capbank0b is a single phase capacitor
    assert m["capbank0b"].phase_capacitors[0].var == 400 * 10 ** 3
    assert m["capbank0b"].nominal_voltage == float(7.2) * 10 ** 3
    assert m["capbank0b"].connection_type == "Y"
    assert m["capbank0b"].delay == None
    assert m["capbank0b"].mode == None
    assert m["capbank0b"].low is None
    assert m["capbank0b"].high is None
    # assert m["capbank0b"].resistance is None # 0.0
    assert m["capbank0b"].resistance0 is None
    # assert m["capbank0b"].reactance is None # 0.0
    assert m["capbank0b"].reactance0 is None
    assert m["capbank0b"].susceptance is None
    assert m["capbank0b"].susceptance0 is None
    assert m["capbank0b"].conductance is None
    assert m["capbank0b"].conductance0 is None
    assert m["capbank0b"].pt_ratio == None
    assert m["capbank0b"].ct_ratio is None
    assert m["capbank0b"].pt_phase == None
    assert m["capbank0b"].connecting_element == "r42246"
    #    assert m["capbank0b"].positions is None # []
    assert m["capbank0b"].measuring_element == None
    #    assert m["capbank0b"].substation_name is None # ''
    assert m["capbank0b"].feeder_name == "sourcebus_src"
    assert m["capbank0b"].is_substation == 0

    assert m["capbank0b"].phase_capacitors[0].phase == "B"
    assert m["capbank0b"].phase_capacitors[0].switch == None
    assert m["capbank0b"].phase_capacitors[0].sections == None
    assert m["capbank0b"].phase_capacitors[0].normalsections == None

    assert (
        len(m["capbank0c"].phase_capacitors) == 1
    )  # capbank0c is a single phase capacitor
    assert m["capbank0c"].phase_capacitors[0].var == 400 * 10 ** 3
    assert m["capbank0c"].nominal_voltage == float(7.2) * 10 ** 3
    assert m["capbank0c"].connection_type == "Y"
    assert m["capbank0c"].delay == None
    assert m["capbank0c"].mode == None
    assert m["capbank0c"].low is None
    assert m["capbank0c"].high is None
    # assert m["capbank0c"].resistance is None # 0.0
    assert m["capbank0c"].resistance0 is None
    # assert m["capbank0c"].reactance is None # 0.0
    assert m["capbank0c"].reactance0 is None
    assert m["capbank0c"].susceptance is None
    assert m["capbank0c"].susceptance0 is None
    assert m["capbank0c"].conductance is None
    assert m["capbank0c"].conductance0 is None
    assert m["capbank0c"].pt_ratio == None
    assert m["capbank0c"].ct_ratio is None
    assert m["capbank0c"].pt_phase == None
    assert m["capbank0c"].connecting_element == "r42246"
    #    assert m["capbank0c"].positions is None # []
    assert m["capbank0c"].measuring_element == None
    #    assert m["capbank0c"].substation_name is None # ''
    assert m["capbank0c"].feeder_name == "sourcebus_src"
    assert m["capbank0c"].is_substation == 0

    assert m["capbank0c"].phase_capacitors[0].phase == "C"
    assert m["capbank0c"].phase_capacitors[0].switch == None
    assert m["capbank0c"].phase_capacitors[0].sections == None
    assert m["capbank0c"].phase_capacitors[0].normalsections == None

    #  This is a 3-phase capacitor bank
    assert (
        len(m["capbank3"].phase_capacitors) == 3
    )  # capbank3 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["capbank3"].phase_capacitors]
    ) == pytest.approx(900 * 10 ** 3, 0.0001)
    assert m["capbank3"].nominal_voltage == float(12.47112) * 10 ** 3
    assert m["capbank3"].connection_type == "Y"
    assert m["capbank3"].delay == None
    assert m["capbank3"].mode == None
    assert m["capbank3"].low is None
    assert m["capbank3"].high is None
    # assert m["capbank3"].resistance is None # 0.0
    assert m["capbank3"].resistance0 is None
    # assert m["capbank3"].reactance is None # 0.0
    assert m["capbank3"].reactance0 is None
    assert m["capbank3"].susceptance is None
    assert m["capbank3"].susceptance0 is None
    assert m["capbank3"].conductance is None
    assert m["capbank3"].conductance0 is None
    assert m["capbank3"].pt_ratio == None
    assert m["capbank3"].ct_ratio is None
    assert m["capbank3"].pt_phase == None
    assert m["capbank3"].connecting_element == "r18242"
    #    assert m["capbank3"].positions is None # []
    assert m["capbank3"].measuring_element == None
    #    assert m["capbank3"].substation_name is None # ''
    assert m["capbank3"].feeder_name == "sourcebus_src"
    assert m["capbank3"].is_substation == 0

    assert set([pc.phase for pc in m["capbank3"].phase_capacitors]) == set(
        ["A", "B", "C"]
    )
    assert [
        phase_capacitor.switch for phase_capacitor in m["capbank3"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.sections for phase_capacitor in m["capbank3"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.normalsections
        for phase_capacitor in m["capbank3"].phase_capacitors
    ] == [None, None, None]

    # 3-phase capacitor with number of phases mentioned
    assert (
        len(m["capbank3-1"].phase_capacitors) == 3
    )  # capbank3-1 is a three phase capacitor
    assert sum(
        [phase_capacitor.var for phase_capacitor in m["capbank3-1"].phase_capacitors]
    ) == pytest.approx(900 * 10 ** 3, 0.0001)
    assert m["capbank3-1"].nominal_voltage == float(12.47112) * 10 ** 3
    assert m["capbank3-1"].connection_type == "Y"
    assert m["capbank3-1"].delay == None
    assert m["capbank3-1"].mode == None
    assert m["capbank3-1"].low is None
    assert m["capbank3-1"].high is None
    # assert m["capbank3-1"].resistance is None # 0.0
    assert m["capbank3-1"].resistance0 is None
    # assert m["capbank3-1"].reactance is None # 0.0
    assert m["capbank3-1"].reactance0 is None
    assert m["capbank3-1"].susceptance is None
    assert m["capbank3-1"].susceptance0 is None
    assert m["capbank3-1"].conductance is None
    assert m["capbank3-1"].conductance0 is None
    assert m["capbank3-1"].pt_ratio == None
    assert m["capbank3-1"].ct_ratio is None
    assert m["capbank3-1"].pt_phase == None
    assert m["capbank3-1"].connecting_element == "r18242"
    #    assert m["capbank3-1"].positions is None # []
    assert m["capbank3-1"].measuring_element == None
    #    assert m["capbank3-1"].substation_name is None # ''
    assert m["capbank3-1"].feeder_name == "sourcebus_src"
    assert m["capbank3-1"].is_substation == 0

    assert set([pc.phase for pc in m["capbank3-1"].phase_capacitors]) == set(
        ["A", "B", "C"]
    )
    assert [
        phase_capacitor.switch for phase_capacitor in m["capbank3-1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.sections for phase_capacitor in m["capbank3-1"].phase_capacitors
    ] == [None, None, None]
    assert [
        phase_capacitor.normalsections
        for phase_capacitor in m["capbank3-1"].phase_capacitors
    ] == [None, None, None]
