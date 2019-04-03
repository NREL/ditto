# -*- coding: utf-8 -*-

"""
test_regulators.py
----------------------------------

Tests for parsing all values of Regulators from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_regulators():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_regulators.dss"))
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

    # ! Regulator No. 1 from IEEE 8500 test case
    assert m["vreg2_a"].name == "vreg2_a"
    assert len(m["vreg2_a"].windings) == 2  # Transformer vreg2_a should have 2 Windings
    assert m["vreg2_a"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["vreg2_a"].windings[1].nominal_voltage == 7.2 * 10 ** 3

    assert len(m["vreg2_b"].windings) == 2  # Transformer VREG_B should have 2 Windings
    assert m["vreg2_b"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["vreg2_b"].windings[1].nominal_voltage == 7.2 * 10 ** 3

    assert len(m["vreg2_c"].windings) == 2  # Transformer VREG_C should have 2 Windings
    assert m["vreg2_c"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["vreg2_c"].windings[1].nominal_voltage == 7.2 * 10 ** 3

    assert m["vreg2_a"].feeder_name == "sourcebus_src"
    assert m["vreg2_a"].noload_loss == 0.0
    assert m["vreg2_a"].loadloss == 0.01
    assert m["vreg2_a"].phase_shift == 0
    assert m["vreg2_a"].normhkva == 11000.0
    assert m["vreg2_a"].from_element == "regxfmr_190-8593"
    assert m["vreg2_a"].to_element == "190-8593"
    assert m["vreg2_a"].reactances == [0.1]
    assert m["vreg2_a"].is_center_tap == 0

    assert m["vreg2_a"].windings[0].connection_type == "Y"
    assert m["vreg2_a"].windings[1].connection_type == "Y"

    assert m["vreg2_a"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["vreg2_a"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["vreg2_a"].windings[0].emergency_power == 15000000.0
    assert m["vreg2_a"].windings[1].emergency_power == 15000000.0

    assert m["vreg2_a"].windings[0].resistance == 0.005
    assert m["vreg2_a"].windings[1].resistance == 0.005

    assert m["vreg2_a"].windings[0].voltage_type == None
    assert m["vreg2_a"].windings[1].voltage_type == None

    assert m["vreg2_a"].windings[0].voltage_limit == None
    assert m["vreg2_a"].windings[1].voltage_limit == None

    assert m["vreg2_a"].windings[0].reverse_resistance == None
    assert m["vreg2_a"].windings[1].reverse_resistance == None

    assert m["vreg2_a"].windings[0].phase_windings[0].tap_position == 1.0

    assert m["vreg2_a"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["vreg2_a"].windings[0].phase_windings[0].phase == "A"

    assert m["vreg2_a"].windings[1].phase_windings[0].phase == "A"

    assert m["vreg2_a"].windings[0].phase_windings[0].compensator_r == 0.0

    assert m["vreg2_a"].windings[1].phase_windings[0].compensator_r == 0.0

    assert m["vreg2_a"].windings[0].phase_windings[0].compensator_x == 0.0

    assert m["vreg2_a"].windings[1].phase_windings[0].compensator_x == 0.0

    assert m["regulator_vreg2_a"].name == "regulator_vreg2_a"
    assert m["regulator_vreg2_a"].winding == 2
    assert m["regulator_vreg2_a"].ct_prim == parsed_values["Regulator"]["ct_prim"]
    assert m["regulator_vreg2_a"].noload_loss == None
    assert m["regulator_vreg2_a"].delay == parsed_values["Regulator"]["delay"]
    assert m["regulator_vreg2_a"].highstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_vreg2_a"].lowstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_vreg2_a"].pt_ratio == parsed_values["Regulator"]["pt_ratio"]
    assert m["regulator_vreg2_a"].ct_ratio == None
    assert m["regulator_vreg2_a"].bandwidth == 2
    assert m["regulator_vreg2_a"].bandcenter == 125
    assert m["regulator_vreg2_a"].voltage_limit == 8.0
    assert m["regulator_vreg2_a"].connected_transformer == "vreg2_a"
    assert m["regulator_vreg2_a"].from_element == "regxfmr_190-8593"
    assert m["regulator_vreg2_a"].to_element == "190-8593"
    assert m["regulator_vreg2_a"].pt_phase == "A"
    assert m["regulator_vreg2_a"].reactances == [0.1]
    assert m["regulator_vreg2_a"].phase_shift == 0
    assert m["regulator_vreg2_a"].feeder_name == "sourcebus_src"
    assert m["regulator_vreg2_a"].setpoint == 125

    assert m["regulator_vreg2_a"].windings[0].connection_type == "Y"
    assert m["regulator_vreg2_a"].windings[1].connection_type == "Y"

    assert m["regulator_vreg2_a"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["regulator_vreg2_a"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["regulator_vreg2_a"].windings[0].emergency_power == 15000 * 10 ** 3
    assert m["regulator_vreg2_a"].windings[1].emergency_power == 15000 * 10 ** 3

    assert m["regulator_vreg2_a"].windings[0].resistance == 0.005
    assert m["regulator_vreg2_a"].windings[1].resistance == 0.005

    assert m["regulator_vreg2_a"].windings[0].voltage_type == None
    assert m["regulator_vreg2_a"].windings[1].voltage_type == None

    assert m["regulator_vreg2_a"].windings[0].voltage_limit == None
    assert m["regulator_vreg2_a"].windings[1].voltage_limit == None
    assert m["regulator_vreg2_a"].windings[0].reverse_resistance == None
    assert m["regulator_vreg2_a"].windings[1].reverse_resistance == None
    assert m["regulator_vreg2_a"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regulator_vreg2_a"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["regulator_vreg2_a"].windings[0].phase_windings[0].phase == "A"
    assert m["regulator_vreg2_a"].windings[1].phase_windings[0].phase == "A"
    assert m["regulator_vreg2_a"].windings[0].phase_windings[0].compensator_r == 0.0
    assert m["regulator_vreg2_a"].windings[1].phase_windings[0].compensator_r == 0.0
    assert m["regulator_vreg2_a"].windings[0].phase_windings[0].compensator_x == 0.0
    assert m["regulator_vreg2_a"].windings[1].phase_windings[0].compensator_x == 0.0

    assert m["vreg2_b"].name == "vreg2_b"
    assert m["vreg2_b"].feeder_name == "sourcebus_src"
    assert m["vreg2_b"].noload_loss == 0.0
    assert m["vreg2_b"].loadloss == 0.01
    assert m["vreg2_b"].phase_shift == 0
    assert m["vreg2_b"].normhkva == 11000.0
    assert m["vreg2_b"].from_element == "regxfmr_190-8593"
    assert m["vreg2_b"].to_element == "190-8593"
    assert m["vreg2_b"].reactances == [0.1]
    assert m["vreg2_b"].is_center_tap == 0

    assert m["vreg2_b"].windings[0].connection_type == "Y"
    assert m["vreg2_b"].windings[1].connection_type == "Y"

    assert m["vreg2_b"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["vreg2_b"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["vreg2_b"].windings[0].emergency_power == 15000 * 10 ** 3
    assert m["vreg2_b"].windings[1].emergency_power == 15000 * 10 ** 3

    assert m["vreg2_b"].windings[0].resistance == 0.005
    assert m["vreg2_b"].windings[1].resistance == 0.005

    assert m["vreg2_b"].windings[0].voltage_type == None
    assert m["vreg2_b"].windings[1].voltage_type == None

    assert m["vreg2_b"].windings[0].voltage_limit == None
    assert m["vreg2_b"].windings[1].voltage_limit == None

    assert m["vreg2_b"].windings[0].reverse_resistance == None
    assert m["vreg2_b"].windings[1].reverse_resistance == None

    assert m["vreg2_b"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["vreg2_b"].windings[1].phase_windings[0].tap_position == 0.98125
    assert m["vreg2_b"].windings[0].phase_windings[0].phase == "B"
    assert m["vreg2_b"].windings[1].phase_windings[0].phase == "B"
    assert m["vreg2_b"].windings[0].phase_windings[0].compensator_r == 0.0
    assert m["vreg2_b"].windings[1].phase_windings[0].compensator_r == 0.0
    assert m["vreg2_b"].windings[0].phase_windings[0].compensator_x == 0.0
    assert m["vreg2_b"].windings[1].phase_windings[0].compensator_x == 0.0

    assert m["regulator_vreg2_b"].name == "regulator_vreg2_b"
    assert m["regulator_vreg2_b"].winding == 2
    assert m["regulator_vreg2_b"].ct_prim == parsed_values["Regulator"]["ct_prim"]
    assert m["regulator_vreg2_b"].noload_loss == None
    assert m["regulator_vreg2_b"].delay == parsed_values["Regulator"]["delay"]
    assert m["regulator_vreg2_b"].highstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_vreg2_b"].lowstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_vreg2_b"].pt_ratio == parsed_values["Regulator"]["pt_ratio"]
    assert m["regulator_vreg2_b"].ct_ratio == None
    assert m["regulator_vreg2_b"].bandwidth == 2
    assert m["regulator_vreg2_b"].bandcenter == 125
    assert m["regulator_vreg2_b"].voltage_limit == 0.0
    assert m["regulator_vreg2_b"].connected_transformer == "vreg2_b"
    assert m["regulator_vreg2_b"].from_element == "regxfmr_190-8593"
    assert m["regulator_vreg2_b"].to_element == "190-8593"
    assert m["regulator_vreg2_b"].pt_phase == "B"
    assert m["regulator_vreg2_b"].reactances == [0.1]
    assert m["regulator_vreg2_b"].phase_shift == 0
    assert m["regulator_vreg2_b"].feeder_name == "sourcebus_src"
    assert m["regulator_vreg2_b"].setpoint == 125

    assert m["regulator_vreg2_b"].windings[0].connection_type == "Y"
    assert m["regulator_vreg2_b"].windings[1].connection_type == "Y"

    assert m["regulator_vreg2_b"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["regulator_vreg2_b"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["regulator_vreg2_b"].windings[0].emergency_power == 15000 * 10 ** 3
    assert m["regulator_vreg2_b"].windings[1].emergency_power == 15000 * 10 ** 3

    assert m["regulator_vreg2_b"].windings[0].resistance == 0.005
    assert m["regulator_vreg2_b"].windings[1].resistance == 0.005

    assert m["regulator_vreg2_b"].windings[0].voltage_type == None
    assert m["regulator_vreg2_b"].windings[1].voltage_type == None

    assert m["regulator_vreg2_b"].windings[0].voltage_limit == None
    assert m["regulator_vreg2_b"].windings[1].voltage_limit == None

    assert m["regulator_vreg2_b"].windings[0].reverse_resistance == None
    assert m["regulator_vreg2_b"].windings[1].reverse_resistance == None

    assert m["regulator_vreg2_b"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regulator_vreg2_b"].windings[1].phase_windings[0].tap_position == 0.98125

    assert m["regulator_vreg2_b"].windings[0].phase_windings[0].phase == "B"
    assert m["regulator_vreg2_b"].windings[1].phase_windings[0].phase == "B"
    assert m["regulator_vreg2_b"].windings[0].phase_windings[0].compensator_r == 0.0
    assert m["regulator_vreg2_b"].windings[1].phase_windings[0].compensator_r == 0.0
    assert m["regulator_vreg2_b"].windings[0].phase_windings[0].compensator_x == 0.0
    assert m["regulator_vreg2_b"].windings[1].phase_windings[0].compensator_x == 0.0

    assert m["vreg2_c"].name == "vreg2_c"
    assert m["vreg2_c"].feeder_name == "sourcebus_src"
    assert m["vreg2_c"].noload_loss == 0.0
    assert m["vreg2_c"].loadloss == 0.01
    assert m["vreg2_c"].phase_shift == 0
    assert m["vreg2_c"].normhkva == 11000.0
    assert m["vreg2_c"].from_element == "regxfmr_190-8593"
    assert m["vreg2_c"].to_element == "190-8593"
    assert m["vreg2_c"].reactances == [0.1]
    assert m["vreg2_c"].is_center_tap == 0

    assert m["vreg2_c"].windings[0].connection_type == "Y"
    assert m["vreg2_c"].windings[1].connection_type == "Y"

    assert m["vreg2_c"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["vreg2_c"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["vreg2_c"].windings[0].emergency_power == 15000 * 10 ** 3
    assert m["vreg2_c"].windings[1].emergency_power == 15000 * 10 ** 3

    assert m["vreg2_c"].windings[0].resistance == 0.005
    assert m["vreg2_c"].windings[1].resistance == 0.005

    assert m["vreg2_c"].windings[0].voltage_type == None
    assert m["vreg2_c"].windings[1].voltage_type == None

    assert m["vreg2_c"].windings[0].voltage_limit == None
    assert m["vreg2_c"].windings[1].voltage_limit == None

    assert m["vreg2_c"].windings[0].reverse_resistance == None
    assert m["vreg2_c"].windings[1].reverse_resistance == None

    assert m["vreg2_c"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["vreg2_c"].windings[1].phase_windings[0].tap_position == 1.0125
    assert m["vreg2_c"].windings[0].phase_windings[0].phase == "C"
    assert m["vreg2_c"].windings[1].phase_windings[0].phase == "C"
    assert m["vreg2_c"].windings[0].phase_windings[0].compensator_r == 0.0
    assert m["vreg2_c"].windings[1].phase_windings[0].compensator_r == 0.0
    assert m["vreg2_c"].windings[0].phase_windings[0].compensator_x == 0.0
    assert m["vreg2_c"].windings[1].phase_windings[0].compensator_x == 0.0

    assert m["regulator_vreg2_c"].name == "regulator_vreg2_c"
    assert m["regulator_vreg2_c"].winding == 2
    assert m["regulator_vreg2_c"].ct_prim == parsed_values["Regulator"]["ct_prim"]
    assert m["regulator_vreg2_c"].noload_loss == None
    assert m["regulator_vreg2_c"].delay == parsed_values["Regulator"]["delay"]
    assert m["regulator_vreg2_c"].highstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_vreg2_c"].lowstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_vreg2_c"].pt_ratio == parsed_values["Regulator"]["pt_ratio"]
    assert m["regulator_vreg2_c"].ct_ratio == None
    assert m["regulator_vreg2_c"].bandwidth == 2
    assert m["regulator_vreg2_c"].bandcenter == 125
    assert m["regulator_vreg2_c"].voltage_limit == 0.0
    assert m["regulator_vreg2_c"].connected_transformer == "vreg2_c"
    assert m["regulator_vreg2_c"].from_element == "regxfmr_190-8593"
    assert m["regulator_vreg2_c"].to_element == "190-8593"
    assert m["regulator_vreg2_c"].pt_phase == "C"
    assert m["regulator_vreg2_c"].reactances == [0.1]
    assert m["regulator_vreg2_c"].phase_shift == 0
    assert m["regulator_vreg2_c"].feeder_name == "sourcebus_src"
    assert m["regulator_vreg2_c"].setpoint == 125

    assert m["regulator_vreg2_c"].windings[0].connection_type == "Y"
    assert m["regulator_vreg2_c"].windings[1].connection_type == "Y"

    assert m["regulator_vreg2_c"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["regulator_vreg2_c"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["regulator_vreg2_c"].windings[0].emergency_power == 15000 * 10 ** 3
    assert m["regulator_vreg2_c"].windings[1].emergency_power == 15000 * 10 ** 3

    assert m["regulator_vreg2_c"].windings[0].resistance == 0.005
    assert m["regulator_vreg2_c"].windings[1].resistance == 0.005

    assert m["regulator_vreg2_c"].windings[0].voltage_type == None
    assert m["regulator_vreg2_c"].windings[1].voltage_type == None

    assert m["regulator_vreg2_c"].windings[0].voltage_limit == None
    assert m["regulator_vreg2_c"].windings[1].voltage_limit == None

    assert m["regulator_vreg2_c"].windings[0].reverse_resistance == None
    assert m["regulator_vreg2_c"].windings[1].reverse_resistance == None

    assert m["regulator_vreg2_c"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regulator_vreg2_c"].windings[1].phase_windings[0].tap_position == 1.0125

    assert m["regulator_vreg2_c"].windings[0].phase_windings[0].phase == "C"
    assert m["regulator_vreg2_c"].windings[1].phase_windings[0].phase == "C"

    assert m["regulator_vreg2_c"].windings[0].phase_windings[0].compensator_r == 0.0
    assert m["regulator_vreg2_c"].windings[1].phase_windings[0].compensator_r == 0.0
    assert m["regulator_vreg2_c"].windings[0].phase_windings[0].compensator_x == 0.0
    assert m["regulator_vreg2_c"].windings[1].phase_windings[0].compensator_x == 0.0

    # Regulator No. 2 from IEEE 8500 test case
    assert m["regxfmr_b18865"].name == "regxfmr_b18865"
    assert (
        len(m["regxfmr_b18865"].windings) == 2
    )  # Transformer regxfmr_b18865 should have 2 Windings
    assert m["regxfmr_b18865"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["regxfmr_b18865"].windings[1].nominal_voltage == 7.2 * 10 ** 3

    assert m["regxfmr_b18865"].feeder_name == "sourcebus_src"
    assert m["regxfmr_b18865"].noload_loss == 0.0
    assert m["regxfmr_b18865"].loadloss == 0.4
    assert m["regxfmr_b18865"].phase_shift == 0
    assert m["regxfmr_b18865"].normhkva == 11000.0
    assert m["regxfmr_b18865"].from_element == "b18865"
    assert m["regxfmr_b18865"].to_element == "b18865reg"
    assert m["regxfmr_b18865"].reactances == [0.01]
    assert m["regxfmr_b18865"].is_center_tap == 0

    assert m["regxfmr_b18865"].windings[0].connection_type == "Y"
    assert m["regxfmr_b18865"].windings[1].connection_type == "Y"

    assert m["regxfmr_b18865"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["regxfmr_b18865"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["regxfmr_b18865"].windings[0].emergency_power == 15000 * 10 ** 3
    assert m["regxfmr_b18865"].windings[1].emergency_power == 15000 * 10 ** 3

    assert m["regxfmr_b18865"].windings[0].resistance == 0.2
    assert m["regxfmr_b18865"].windings[1].resistance == 0.2

    assert m["regxfmr_b18865"].windings[0].voltage_type == None
    assert m["regxfmr_b18865"].windings[1].voltage_type == None

    assert m["regxfmr_b18865"].windings[0].voltage_limit == None
    assert m["regxfmr_b18865"].windings[1].voltage_limit == None

    assert m["regxfmr_b18865"].windings[0].reverse_resistance == None
    assert m["regxfmr_b18865"].windings[1].reverse_resistance == None

    assert m["regxfmr_b18865"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regxfmr_b18865"].windings[1].phase_windings[0].tap_position == 1.01875

    assert m["regxfmr_b18865"].windings[0].phase_windings[0].phase == "C"
    assert m["regxfmr_b18865"].windings[1].phase_windings[0].phase == "C"
    assert m["regxfmr_b18865"].windings[0].phase_windings[0].compensator_r == 0.0
    assert m["regxfmr_b18865"].windings[1].phase_windings[0].compensator_r == 0.0
    assert m["regxfmr_b18865"].windings[1].phase_windings[0].compensator_x == 0.0
    assert m["regxfmr_b18865"].windings[0].phase_windings[0].compensator_x == 0.0

    assert m["regulator_regxfmr_b18865_ctrl"].name == "regulator_regxfmr_b18865_ctrl"
    assert m["regulator_regxfmr_b18865_ctrl"].winding == 2
    assert m["regulator_regxfmr_b18865_ctrl"].ct_prim == 0.12
    assert m["regulator_regxfmr_b18865_ctrl"].noload_loss == None
    assert m["regulator_regxfmr_b18865_ctrl"].delay == 45
    assert (
        m["regulator_regxfmr_b18865_ctrl"].highstep
        == parsed_values["Regulator"]["highstep"]
    )
    assert (
        m["regulator_regxfmr_b18865_ctrl"].lowstep
        == parsed_values["Regulator"]["highstep"]
    )
    assert (
        m["regulator_regxfmr_b18865_ctrl"].pt_ratio
        == parsed_values["Regulator"]["pt_ratio"]
    )
    assert m["regulator_regxfmr_b18865_ctrl"].ct_ratio == None
    assert m["regulator_regxfmr_b18865_ctrl"].bandwidth == 2
    assert m["regulator_regxfmr_b18865_ctrl"].bandcenter == 124
    assert m["regulator_regxfmr_b18865_ctrl"].voltage_limit == 0.0
    assert m["regulator_regxfmr_b18865_ctrl"].connected_transformer == "regxfmr_b18865"
    assert m["regulator_regxfmr_b18865_ctrl"].from_element == "b18865"
    assert m["regulator_regxfmr_b18865_ctrl"].to_element == "b18865reg"
    assert m["regulator_regxfmr_b18865_ctrl"].pt_phase == "C"
    assert m["regulator_regxfmr_b18865_ctrl"].reactances == [0.01]
    assert m["regulator_regxfmr_b18865_ctrl"].phase_shift == 0
    assert m["regulator_regxfmr_b18865_ctrl"].feeder_name == "sourcebus_src"
    assert m["regulator_regxfmr_b18865_ctrl"].setpoint == 124

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].connection_type == "Y"
    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].connection_type == "Y"

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].rated_power == 10000 * 10 ** 3

    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[0].emergency_power
        == 15000 * 10 ** 3
    )
    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[1].emergency_power
        == 15000 * 10 ** 3
    )

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].resistance == 0.2
    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].resistance == 0.2

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].voltage_type == None
    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].voltage_type == None

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].voltage_limit == None
    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].voltage_limit == None

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].reverse_resistance == None
    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].reverse_resistance == None

    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[0].phase_windings[0].tap_position
        == 1.0
    )
    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[1].phase_windings[0].tap_position
        == 1.01875
    )

    assert m["regulator_regxfmr_b18865_ctrl"].windings[0].phase_windings[0].phase == "C"

    assert m["regulator_regxfmr_b18865_ctrl"].windings[1].phase_windings[0].phase == "C"

    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[0].phase_windings[0].compensator_r
        == 0.0
    )

    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[1].phase_windings[0].compensator_r
        == 0.0
    )

    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[0].phase_windings[0].compensator_x
        == 0.0
    )

    assert (
        m["regulator_regxfmr_b18865_ctrl"].windings[1].phase_windings[0].compensator_x
        == 0.0
    )

    # Substation regulator from SMART-DS P4U region
    assert m["sb5_p4uhs0_4_trans_439"].name == "sb5_p4uhs0_4_trans_439"
    assert (
        len(m["sb5_p4uhs0_4_trans_439"].windings) == 2
    )  # Transformer sb5_p4uhs0_4_trans_439 should have 2 Windings
    assert m["sb5_p4uhs0_4_trans_439"].windings[0].nominal_voltage == 69.0 * 10 ** 3
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].nominal_voltage == 4.0 * 10 ** 3

    assert m["sb5_p4uhs0_4_trans_439"].feeder_name == "sourcebus_src"
    assert m["sb5_p4uhs0_4_trans_439"].noload_loss == 0.0
    assert m["sb5_p4uhs0_4_trans_439"].loadloss == 0.9616652
    assert m["sb5_p4uhs0_4_trans_439"].phase_shift == -30
    assert m["sb5_p4uhs0_4_trans_439"].normhkva == 8800.0
    assert m["sb5_p4uhs0_4_trans_439"].from_element == "sb5_p4uhs0_4_node_5_12"
    assert m["sb5_p4uhs0_4_trans_439"].to_element == "sb5_p4uhs0_4_node_5_13"
    assert m["sb5_p4uhs0_4_trans_439"].reactances == [pytest.approx(0.9616652224137047)]
    assert m["sb5_p4uhs0_4_trans_439"].is_center_tap == 0

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].connection_type == "D"
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].connection_type == "Y"

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].rated_power == 8000 * 10 ** 3
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].rated_power == 8000 * 10 ** 3

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].emergency_power == 12000 * 10 ** 3
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].emergency_power == 12000 * 10 ** 3

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].resistance == pytest.approx(
        0.4808326112068522
    )
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].resistance == pytest.approx(
        0.4808326112068522
    )

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].voltage_type == None
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].voltage_type == None

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].voltage_limit == None
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].voltage_limit == None

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].reverse_resistance == None
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].reverse_resistance == None

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].tap_position == 1.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].tap_position == 1.0

    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].tap_position == 1.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].tap_position == 1.0

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].phase == "A"
    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[1].phase == "B"
    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[2].phase == "C"

    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[0].phase == "A"
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].phase == "B"
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].phase == "C"

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].compensator_r == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[1].compensator_r == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[2].compensator_r == 0.0
    )

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[0].compensator_r == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].compensator_r == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].compensator_r == 0.0
    )

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].compensator_x == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[1].compensator_x == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[2].compensator_x == 0.0
    )

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[0].compensator_x == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].compensator_x == 0.0
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].compensator_x == 0.0
    )

    assert m["regulator_sb5_p4uhs0_4_reg_439"].name == "regulator_sb5_p4uhs0_4_reg_439"
    assert m["regulator_sb5_p4uhs0_4_reg_439"].winding == 2
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].ct_prim
        == parsed_values["Regulator"]["ct_prim"]
    )
    assert m["regulator_sb5_p4uhs0_4_reg_439"].noload_loss == None
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].delay == parsed_values["Regulator"]["delay"]
    )
    assert m["regulator_sb5_p4uhs0_4_reg_439"].highstep == 10
    assert m["regulator_sb5_p4uhs0_4_reg_439"].lowstep == 10
    assert m["regulator_sb5_p4uhs0_4_reg_439"].pt_ratio == 19
    assert m["regulator_sb5_p4uhs0_4_reg_439"].ct_ratio == None
    assert m["regulator_sb5_p4uhs0_4_reg_439"].bandwidth == 1.9919999999999998
    assert m["regulator_sb5_p4uhs0_4_reg_439"].bandcenter == 123.60000000000001
    assert m["regulator_sb5_p4uhs0_4_reg_439"].voltage_limit == 0.0
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].connected_transformer
        == "sb5_p4uhs0_4_trans_439"
    )
    assert m["regulator_sb5_p4uhs0_4_reg_439"].from_element == "sb5_p4uhs0_4_node_5_12"
    assert m["regulator_sb5_p4uhs0_4_reg_439"].to_element == "sb5_p4uhs0_4_node_5_13"
    assert m["regulator_sb5_p4uhs0_4_reg_439"].pt_phase == "A"
    assert m["regulator_sb5_p4uhs0_4_reg_439"].reactances == [
        pytest.approx(0.9616652224137047)
    ]
    assert m["regulator_sb5_p4uhs0_4_reg_439"].phase_shift == -30
    assert m["regulator_sb5_p4uhs0_4_reg_439"].feeder_name == "sourcebus_src"
    assert m["regulator_sb5_p4uhs0_4_reg_439"].setpoint == None

    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].connection_type == "D"
    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].connection_type == "Y"

    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].rated_power == 8000 * 10 ** 3
    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].rated_power == 8000 * 10 ** 3

    #    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].emergency_power == 12000000.0
    #    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].emergency_power == 12000000.0

    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].resistance == pytest.approx(
        0.4808326112068522
    )
    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].resistance == pytest.approx(
        0.4808326112068522
    )

    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].voltage_type == None
    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].voltage_type == None

    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].voltage_limit == None
    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].voltage_limit == None

    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].reverse_resistance == None
    assert m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].reverse_resistance == None

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[0].tap_position
        == 1.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[1].tap_position
        == 1.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[2].tap_position
        == 1.0
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[0].tap_position
        == 1.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[1].tap_position
        == 1.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[2].tap_position
        == 1.0
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[0].phase == "A"
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[1].phase == "B"
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[2].phase == "C"
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[0].phase == "A"
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[1].phase == "B"
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[2].phase == "C"
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[0].compensator_r
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[1].compensator_r
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[2].compensator_r
        == 0.0
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[0].compensator_r
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[1].compensator_r
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[2].compensator_r
        == 0.0
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[0].compensator_x
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[1].compensator_x
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[0].phase_windings[2].compensator_x
        == 0.0
    )

    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[0].compensator_x
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[1].compensator_x
        == 0.0
    )
    assert (
        m["regulator_sb5_p4uhs0_4_reg_439"].windings[1].phase_windings[2].compensator_x
        == 0.0
    )

    # Rural regulator from SMART-DS rural region
    assert m["trans_reg_creduladortension"].name == "trans_reg_creduladortension"
    assert (
        len(m["trans_reg_creduladortension"].windings) == 2
    )  # Transformer trans_reg_creduladortension should have 2 Windings
    assert (
        m["trans_reg_creduladortension"].windings[0].nominal_voltage == 12.47 * 10 ** 3
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].nominal_voltage == 12.47 * 10 ** 3
    )

    assert m["trans_reg_creduladortension"].feeder_name == "sourcebus_src"
    assert m["trans_reg_creduladortension"].noload_loss == 0.0
    assert m["trans_reg_creduladortension"].loadloss == 0.4
    assert m["trans_reg_creduladortension"].phase_shift == 0
    assert m["trans_reg_creduladortension"].normhkva == 11000.0
    assert m["trans_reg_creduladortension"].from_element == "rdt222-rdt298x"
    assert m["trans_reg_creduladortension"].to_element == "rdt222"
    assert (
        m["trans_reg_creduladortension"].reactances
        == parsed_values["Transformer"]["reactances"]
    )

    assert m["trans_reg_creduladortension"].is_center_tap == 0

    assert m["trans_reg_creduladortension"].windings[0].connection_type == "Y"
    assert m["trans_reg_creduladortension"].windings[1].connection_type == "Y"

    assert m["trans_reg_creduladortension"].windings[0].rated_power == 10000 * 10 ** 3
    assert m["trans_reg_creduladortension"].windings[1].rated_power == 10000 * 10 ** 3

    assert m["trans_reg_creduladortension"].windings[0].emergency_power == 15000000.0
    assert m["trans_reg_creduladortension"].windings[1].emergency_power == 15000000.0

    assert m["trans_reg_creduladortension"].windings[0].resistance == 0.2
    assert m["trans_reg_creduladortension"].windings[1].resistance == 0.2

    assert m["trans_reg_creduladortension"].windings[0].voltage_type == None
    assert m["trans_reg_creduladortension"].windings[1].voltage_type == None

    assert m["trans_reg_creduladortension"].windings[0].voltage_limit == None
    assert m["trans_reg_creduladortension"].windings[1].voltage_limit == None

    assert m["trans_reg_creduladortension"].windings[0].reverse_resistance == None
    assert m["trans_reg_creduladortension"].windings[1].reverse_resistance == None

    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[0].tap_position
        == 1.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[1].tap_position
        == 1.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[2].tap_position
        == 1.0
    )

    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[0].tap_position
        == 1.0125
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[1].tap_position
        == 1.0125
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[2].tap_position
        == 1.0125
    )

    assert m["trans_reg_creduladortension"].windings[0].phase_windings[0].phase == "A"
    assert m["trans_reg_creduladortension"].windings[0].phase_windings[1].phase == "B"
    assert m["trans_reg_creduladortension"].windings[0].phase_windings[2].phase == "C"

    assert m["trans_reg_creduladortension"].windings[1].phase_windings[0].phase == "A"
    assert m["trans_reg_creduladortension"].windings[1].phase_windings[1].phase == "B"
    assert m["trans_reg_creduladortension"].windings[1].phase_windings[2].phase == "C"

    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[0].compensator_r
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[1].compensator_r
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[2].compensator_r
        == 0.0
    )

    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[0].compensator_r
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[1].compensator_r
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[2].compensator_r
        == 0.0
    )

    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[0].compensator_x
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[1].compensator_x
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[0].phase_windings[2].compensator_x
        == 0.0
    )

    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[0].compensator_x
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[1].compensator_x
        == 0.0
    )
    assert (
        m["trans_reg_creduladortension"].windings[1].phase_windings[2].compensator_x
        == 0.0
    )

    assert (
        m["regulator_reg_creguladortension"].name == "regulator_reg_creguladortension"
    )
    assert m["regulator_reg_creguladortension"].winding == 2
    assert m["regulator_reg_creguladortension"].ct_prim == 0.2
    assert m["regulator_reg_creguladortension"].noload_loss == None
    assert (
        m["regulator_reg_creguladortension"].delay
        == parsed_values["Regulator"]["delay"]
    )
    assert (
        m["regulator_reg_creguladortension"].highstep
        == parsed_values["Regulator"]["highstep"]
    )
    assert (
        m["regulator_reg_creguladortension"].lowstep
        == parsed_values["Regulator"]["highstep"]
    )
    assert (
        m["regulator_reg_creguladortension"].pt_ratio
        == parsed_values["Regulator"]["pt_ratio"]
    )
    assert m["regulator_reg_creguladortension"].ct_ratio == None
    assert m["regulator_reg_creguladortension"].bandwidth == 2.4
    assert m["regulator_reg_creguladortension"].bandcenter == 123.6
    assert m["regulator_reg_creguladortension"].voltage_limit == 12.6
    assert (
        m["regulator_reg_creguladortension"].connected_transformer
        == "trans_reg_creduladortension"
    )
    assert m["regulator_reg_creguladortension"].from_element == "rdt222-rdt298x"
    assert m["regulator_reg_creguladortension"].to_element == "rdt222"
    assert m["regulator_reg_creguladortension"].pt_phase == "A"
    assert m["regulator_reg_creguladortension"].reactances == [7]
    assert m["regulator_reg_creguladortension"].phase_shift == 0
    assert m["regulator_reg_creguladortension"].feeder_name == "sourcebus_src"
    assert m["regulator_reg_creguladortension"].setpoint == None

    assert m["regulator_reg_creguladortension"].windings[0].connection_type == "Y"
    assert m["regulator_reg_creguladortension"].windings[1].connection_type == "Y"

    assert (
        m["regulator_reg_creguladortension"].windings[0].rated_power == 10000 * 10 ** 3
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].rated_power == 10000 * 10 ** 3
    )

    #    assert m["regulator_reg_creguladortension"].windings[0].emergency_power == 15000000.0
    #    assert m["regulator_reg_creguladortension"].windings[1].emergency_power == 15000000.0

    assert m["regulator_reg_creguladortension"].windings[0].resistance == 0.2
    assert m["regulator_reg_creguladortension"].windings[1].resistance == 0.2

    assert m["regulator_reg_creguladortension"].windings[0].voltage_type == None
    assert m["regulator_reg_creguladortension"].windings[1].voltage_type == None

    assert m["regulator_reg_creguladortension"].windings[0].voltage_limit == None
    assert m["regulator_reg_creguladortension"].windings[1].voltage_limit == None

    assert m["regulator_reg_creguladortension"].windings[0].reverse_resistance == None
    assert m["regulator_reg_creguladortension"].windings[1].reverse_resistance == None

    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[0].tap_position
        == 1.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[1].tap_position
        == 1.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[2].tap_position
        == 1.0
    )

    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[0].tap_position
        == 1.0125
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[1].tap_position
        == 1.0125
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[2].tap_position
        == 1.0125
    )

    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[0].phase == "A"
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[1].phase == "B"
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[2].phase == "C"
    )

    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[0].phase == "A"
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[1].phase == "B"
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[2].phase == "C"
    )

    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[0].compensator_r
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[1].compensator_r
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[2].compensator_r
        == 0.0
    )

    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[0].compensator_r
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[1].compensator_r
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[2].compensator_r
        == 0.0
    )

    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[0].compensator_x
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[1].compensator_x
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[0].phase_windings[2].compensator_x
        == 0.0
    )

    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[0].compensator_x
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[1].compensator_x
        == 0.0
    )
    assert (
        m["regulator_reg_creguladortension"].windings[1].phase_windings[2].compensator_x
        == 0.0
    )

    #  Regulator from IEEE 13 node feeder
    assert m["reg1"].name == "reg1"
    assert len(m["reg1"].windings) == 2  # Transformer reg1 should have 2 Windings
    assert m["reg1"].windings[0].nominal_voltage == 2.4 * 10 ** 3
    assert m["reg1"].windings[1].nominal_voltage == 2.4 * 10 ** 3

    assert m["reg1"].feeder_name == "sourcebus_src"
    assert m["reg1"].noload_loss == 0.0
    assert m["reg1"].loadloss == 0.01
    assert m["reg1"].phase_shift == 0
    assert m["reg1"].normhkva == 1832.6
    assert m["reg1"].from_element == "650"
    assert m["reg1"].to_element == "rg60"
    assert m["reg1"].reactances == [0.01]
    assert m["reg1"].is_center_tap == 0

    assert m["reg1"].windings[0].connection_type == "Y"
    assert m["reg1"].windings[1].connection_type == "Y"

    assert m["reg1"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["reg1"].windings[1].rated_power == 1666 * 10 ** 3

    assert m["reg1"].windings[0].emergency_power == 2499000.0
    assert m["reg1"].windings[1].emergency_power == 2499000.0

    assert m["reg1"].windings[0].resistance == 0.005
    assert m["reg1"].windings[1].resistance == 0.005

    assert m["reg1"].windings[0].voltage_type == None
    assert m["reg1"].windings[1].voltage_type == None

    assert m["reg1"].windings[0].voltage_limit == None
    assert m["reg1"].windings[1].voltage_limit == None

    assert m["reg1"].windings[0].reverse_resistance == None
    assert m["reg1"].windings[1].reverse_resistance == None

    assert m["reg1"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["reg1"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["reg1"].windings[0].phase_windings[0].phase == "A"
    assert m["reg1"].windings[1].phase_windings[0].phase == "A"

    assert m["reg1"].windings[0].phase_windings[0].compensator_r == float(3)
    assert m["reg1"].windings[1].phase_windings[0].compensator_r == float(3)
    assert m["reg1"].windings[0].phase_windings[0].compensator_x == float(9)
    assert m["reg1"].windings[1].phase_windings[0].compensator_x == float(9)

    assert m["regulator_reg1"].name == "regulator_reg1"
    assert m["regulator_reg1"].winding == 2
    assert m["regulator_reg1"].ct_prim == 700
    assert m["regulator_reg1"].noload_loss == None
    assert m["regulator_reg1"].delay == parsed_values["Regulator"]["delay"]
    assert m["regulator_reg1"].highstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_reg1"].lowstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_reg1"].pt_ratio == 20
    assert m["regulator_reg1"].ct_ratio == None
    assert m["regulator_reg1"].bandwidth == 2
    assert m["regulator_reg1"].bandcenter == 122
    assert m["regulator_reg1"].voltage_limit == 0.0
    assert m["regulator_reg1"].connected_transformer == "reg1"
    assert m["regulator_reg1"].from_element == "650"
    assert m["regulator_reg1"].to_element == "rg60"
    assert m["regulator_reg1"].pt_phase == "A"
    assert m["regulator_reg1"].reactances == [0.01]
    assert m["regulator_reg1"].phase_shift == 0
    assert m["regulator_reg1"].feeder_name == "sourcebus_src"
    assert m["regulator_reg1"].setpoint == 122

    assert m["regulator_reg1"].windings[0].connection_type == "Y"
    assert m["regulator_reg1"].windings[1].connection_type == "Y"

    assert m["regulator_reg1"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["regulator_reg1"].windings[1].rated_power == 1666 * 10 ** 3

    #    assert m["regulator_reg1"].windings[0].emergency_power == 2499000.0
    #    assert m["regulator_reg1"].windings[1].emergency_power == 2499000.0

    assert m["regulator_reg1"].windings[0].resistance == 0.005
    assert m["regulator_reg1"].windings[1].resistance == 0.005

    assert m["regulator_reg1"].windings[0].voltage_type == None
    assert m["regulator_reg1"].windings[1].voltage_type == None

    assert m["regulator_reg1"].windings[0].voltage_limit == None
    assert m["regulator_reg1"].windings[1].voltage_limit == None

    assert m["regulator_reg1"].windings[0].reverse_resistance == None
    assert m["regulator_reg1"].windings[1].reverse_resistance == None

    assert m["regulator_reg1"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regulator_reg1"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["regulator_reg1"].windings[0].phase_windings[0].phase == "A"
    assert m["regulator_reg1"].windings[1].phase_windings[0].phase == "A"

    assert m["regulator_reg1"].windings[0].phase_windings[0].compensator_r == float(3)
    assert m["regulator_reg1"].windings[1].phase_windings[0].compensator_r == float(3)
    assert m["regulator_reg1"].windings[0].phase_windings[0].compensator_x == float(9)
    assert m["regulator_reg1"].windings[1].phase_windings[0].compensator_x == float(9)

    assert m["reg2"].name == "reg2"
    assert len(m["reg2"].windings) == 2  # Transformer reg2 should have 2 Windings
    assert m["reg2"].windings[0].nominal_voltage == 2.4 * 10 ** 3
    assert m["reg2"].windings[1].nominal_voltage == 2.4 * 10 ** 3

    assert m["reg2"].feeder_name == "sourcebus_src"
    assert m["reg2"].noload_loss == 0.0
    assert m["reg2"].loadloss == 0.01
    assert m["reg2"].phase_shift == 0
    assert m["reg2"].normhkva == 1832.6
    assert m["reg2"].from_element == "650"
    assert m["reg2"].to_element == "rg60"
    assert m["reg2"].reactances == [0.01]
    assert m["reg2"].is_center_tap == 0

    assert m["reg2"].windings[0].connection_type == "Y"
    assert m["reg2"].windings[1].connection_type == "Y"

    assert m["reg2"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["reg2"].windings[1].rated_power == 1666 * 10 ** 3

    assert m["reg2"].windings[0].emergency_power == 2499000.0
    assert m["reg2"].windings[1].emergency_power == 2499000.0

    assert m["reg2"].windings[0].resistance == 0.005
    assert m["reg2"].windings[1].resistance == 0.005

    assert m["reg2"].windings[0].voltage_type == None
    assert m["reg2"].windings[1].voltage_type == None

    assert m["reg2"].windings[0].voltage_limit == None
    assert m["reg2"].windings[1].voltage_limit == None

    assert m["reg2"].windings[0].reverse_resistance == None
    assert m["reg2"].windings[1].reverse_resistance == None

    assert m["reg2"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["reg2"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["reg2"].windings[0].phase_windings[0].phase == "B"
    assert m["reg2"].windings[1].phase_windings[0].phase == "B"

    assert m["reg2"].windings[0].phase_windings[0].compensator_r == float(3)
    assert m["reg2"].windings[1].phase_windings[0].compensator_r == float(3)
    assert m["reg2"].windings[0].phase_windings[0].compensator_x == float(9)
    assert m["reg2"].windings[1].phase_windings[0].compensator_x == float(9)

    assert m["regulator_reg2"].name == "regulator_reg2"
    assert m["regulator_reg2"].winding == 2
    assert m["regulator_reg2"].ct_prim == 700
    assert m["regulator_reg2"].noload_loss == None
    assert m["regulator_reg2"].delay == parsed_values["Regulator"]["delay"]
    assert m["regulator_reg2"].highstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_reg2"].lowstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_reg2"].pt_ratio == 20
    assert m["regulator_reg2"].ct_ratio == None
    assert m["regulator_reg2"].bandwidth == 2
    assert m["regulator_reg2"].bandcenter == 122
    assert m["regulator_reg2"].voltage_limit == 2.8
    assert m["regulator_reg2"].connected_transformer == "reg2"
    assert m["regulator_reg2"].from_element == "650"
    assert m["regulator_reg2"].to_element == "rg60"
    assert m["regulator_reg2"].pt_phase == "B"
    assert m["regulator_reg2"].reactances == [0.01]
    assert m["regulator_reg2"].phase_shift == 0
    assert m["regulator_reg2"].feeder_name == "sourcebus_src"
    assert m["regulator_reg2"].setpoint == 122

    assert m["regulator_reg2"].windings[0].connection_type == "Y"
    assert m["regulator_reg2"].windings[1].connection_type == "Y"

    assert m["regulator_reg2"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["regulator_reg2"].windings[1].rated_power == 1666 * 10 ** 3

    #    assert m["regulator_reg2"].windings[0].emergency_power == 2499000.0
    #   assert m["regulator_reg2"].windings[1].emergency_power == 2499000.0

    assert m["regulator_reg2"].windings[0].resistance == 0.005
    assert m["regulator_reg2"].windings[1].resistance == 0.005

    assert m["regulator_reg2"].windings[0].voltage_type == None
    assert m["regulator_reg2"].windings[1].voltage_type == None

    assert m["regulator_reg2"].windings[0].voltage_limit == None
    assert m["regulator_reg2"].windings[1].voltage_limit == None

    assert m["regulator_reg2"].windings[0].reverse_resistance == None
    assert m["regulator_reg2"].windings[1].reverse_resistance == None

    assert m["regulator_reg2"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regulator_reg2"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["regulator_reg2"].windings[0].phase_windings[0].phase == "B"
    assert m["regulator_reg2"].windings[1].phase_windings[0].phase == "B"

    assert m["regulator_reg2"].windings[0].phase_windings[0].compensator_r == float(3)
    assert m["regulator_reg2"].windings[1].phase_windings[0].compensator_r == float(3)
    assert m["regulator_reg2"].windings[0].phase_windings[0].compensator_x == float(9)
    assert m["regulator_reg2"].windings[1].phase_windings[0].compensator_x == float(9)

    assert m["reg3"].name == "reg3"
    assert len(m["reg3"].windings) == 2  # Transformer reg3 should have 2 Windings
    assert m["reg3"].windings[0].nominal_voltage == 2.4 * 10 ** 3
    assert m["reg3"].windings[1].nominal_voltage == 2.4 * 10 ** 3

    assert m["reg3"].feeder_name == "sourcebus_src"
    assert m["reg3"].noload_loss == 0.0
    assert m["reg3"].loadloss == 0.01
    assert m["reg3"].phase_shift == 0
    assert m["reg3"].normhkva == 1832.6
    assert m["reg3"].from_element == "650"
    assert m["reg3"].to_element == "rg60"
    assert m["reg3"].reactances == [0.01]
    assert m["reg3"].is_center_tap == 0

    assert m["reg3"].windings[0].connection_type == "Y"
    assert m["reg3"].windings[1].connection_type == "Y"

    assert m["reg3"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["reg3"].windings[1].rated_power == 1666 * 10 ** 3

    assert m["reg3"].windings[0].emergency_power == 2499000.0
    assert m["reg3"].windings[1].emergency_power == 2499000.0

    assert m["reg3"].windings[0].resistance == 0.005
    assert m["reg3"].windings[1].resistance == 0.005

    assert m["reg3"].windings[0].voltage_type == None
    assert m["reg3"].windings[1].voltage_type == None

    assert m["reg3"].windings[0].voltage_limit == None
    assert m["reg3"].windings[1].voltage_limit == None

    assert m["reg3"].windings[0].reverse_resistance == None
    assert m["reg3"].windings[1].reverse_resistance == None

    assert m["reg3"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["reg3"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["reg3"].windings[0].phase_windings[0].phase == "C"
    assert m["reg3"].windings[1].phase_windings[0].phase == "C"

    assert m["reg3"].windings[0].phase_windings[0].compensator_r == float(3)
    assert m["reg3"].windings[1].phase_windings[0].compensator_r == float(3)
    assert m["reg3"].windings[0].phase_windings[0].compensator_x == float(9)
    assert m["reg3"].windings[1].phase_windings[0].compensator_x == float(9)

    assert m["regulator_reg3"].name == "regulator_reg3"
    assert m["regulator_reg3"].winding == 2
    assert m["regulator_reg3"].ct_prim == 700
    assert m["regulator_reg3"].noload_loss == None
    assert m["regulator_reg3"].delay == parsed_values["Regulator"]["delay"]
    assert m["regulator_reg3"].highstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_reg3"].lowstep == parsed_values["Regulator"]["highstep"]
    assert m["regulator_reg3"].pt_ratio == 20
    assert m["regulator_reg3"].ct_ratio == None
    assert m["regulator_reg3"].bandwidth == 2
    assert m["regulator_reg3"].bandcenter == 122
    assert m["regulator_reg3"].voltage_limit == 0.0
    assert m["regulator_reg3"].connected_transformer == "reg3"
    assert m["regulator_reg3"].from_element == "650"
    assert m["regulator_reg3"].to_element == "rg60"
    assert m["regulator_reg3"].pt_phase == "C"
    assert m["regulator_reg3"].reactances == [0.01]
    assert m["regulator_reg3"].phase_shift == 0
    assert m["regulator_reg3"].feeder_name == "sourcebus_src"
    assert m["regulator_reg3"].setpoint == 122

    assert m["regulator_reg3"].windings[0].connection_type == "Y"
    assert m["regulator_reg3"].windings[1].connection_type == "Y"

    assert m["regulator_reg3"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["regulator_reg3"].windings[1].rated_power == 1666 * 10 ** 3

    #    assert m["regulator_reg3"].windings[0].emergency_power == 2499000.0
    #    assert m["regulator_reg3"].windings[1].emergency_power == 2499000.0

    assert m["regulator_reg3"].windings[0].resistance == 0.005
    assert m["regulator_reg3"].windings[1].resistance == 0.005

    assert m["regulator_reg3"].windings[0].voltage_type == None
    assert m["regulator_reg3"].windings[1].voltage_type == None

    assert m["regulator_reg3"].windings[0].voltage_limit == None
    assert m["regulator_reg3"].windings[1].voltage_limit == None

    assert m["regulator_reg3"].windings[0].reverse_resistance == None
    assert m["regulator_reg3"].windings[1].reverse_resistance == None

    assert m["regulator_reg3"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["regulator_reg3"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["regulator_reg3"].windings[0].phase_windings[0].phase == "C"
    assert m["regulator_reg3"].windings[1].phase_windings[0].phase == "C"

    assert m["regulator_reg3"].windings[0].phase_windings[0].compensator_r == float(3)
    assert m["regulator_reg3"].windings[1].phase_windings[0].compensator_r == float(3)
    assert m["regulator_reg3"].windings[0].phase_windings[0].compensator_x == float(9)
    assert m["regulator_reg3"].windings[1].phase_windings[0].compensator_x == float(9)
