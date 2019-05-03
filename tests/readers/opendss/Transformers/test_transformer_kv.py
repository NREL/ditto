# -*- coding: utf-8 -*-

"""
test_transformer_kv.py
----------------------------------

Tests for parsing nominal voltage values of Transformers from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.default_values.default_values_json import Default_Values

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_transformer_kv():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_transformer_kv.dss"))
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

    # Default values
    # The default value for XHL is 7%
    # The default value for %R (total of both windings) is 0.4%. Hence %Rs = (0.2,0.2) or the %loadloss property, for both windings at once (the resistance will be divided evenly):
    # %loadloss = 0.4
    # normhkva = 1.1 * kva
    # emerghkva = 1.5 * kva
    #

    # Substation is a 115kV/4.16kV step-down two windings transformer
    assert m["substation"].name == "substation"
    assert (
        len(m["substation"].windings) == 2
    )  # Transformer substation should have 2 Windings
    assert m["substation"].windings[0].nominal_voltage == 115 * 10 ** 3
    assert m["substation"].windings[1].nominal_voltage == 4.16 * 10 ** 3
    assert m["substation"].feeder_name == "sourcebus_src"
    assert m["substation"].noload_loss == 0.0
    assert m["substation"].loadloss == 0.001
    assert m["substation"].phase_shift == None
    assert m["substation"].normhkva == 5500.0
    assert m["substation"].from_element == "sourcebus"
    assert m["substation"].to_element == "bus1"
    assert m["substation"].reactances == [0.008]
    assert m["substation"].is_center_tap == 0

    assert m["substation"].windings[0].connection_type == "D"
    assert m["substation"].windings[1].connection_type == "Y"

    assert m["substation"].windings[0].rated_power == 5000 * 10 ** 3
    assert m["substation"].windings[1].rated_power == 5000 * 10 ** 3

    assert m["substation"].windings[0].emergency_power == 7500000.0
    assert m["substation"].windings[1].emergency_power == 7500000.0

    assert m["substation"].windings[0].resistance == 0.0005
    assert m["substation"].windings[1].resistance == 0.0005

    assert m["substation"].windings[0].voltage_type == 0
    assert m["substation"].windings[1].voltage_type == 2

    assert m["substation"].windings[0].voltage_limit == None
    assert m["substation"].windings[1].voltage_limit == None

    assert m["substation"].windings[0].reverse_resistance == None
    assert m["substation"].windings[1].reverse_resistance == None

    assert m["substation"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["substation"].windings[0].phase_windings[1].tap_position == 1.0
    assert m["substation"].windings[0].phase_windings[2].tap_position == 1.0

    assert m["substation"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["substation"].windings[1].phase_windings[1].tap_position == 1.0
    assert m["substation"].windings[1].phase_windings[2].tap_position == 1.0

    assert m["substation"].windings[0].phase_windings[0].phase == "A"
    assert m["substation"].windings[0].phase_windings[1].phase == "B"
    assert m["substation"].windings[0].phase_windings[2].phase == "C"

    assert m["substation"].windings[1].phase_windings[0].phase == "A"
    assert m["substation"].windings[1].phase_windings[1].phase == "B"
    assert m["substation"].windings[1].phase_windings[2].phase == "C"

    assert m["substation"].windings[0].phase_windings[0].compensator_r == None
    assert m["substation"].windings[0].phase_windings[1].compensator_r == None
    assert m["substation"].windings[0].phase_windings[2].compensator_r == None

    assert m["substation"].windings[1].phase_windings[0].compensator_r == None
    assert m["substation"].windings[1].phase_windings[1].compensator_r == None
    assert m["substation"].windings[1].phase_windings[2].compensator_r == None

    assert m["substation"].windings[0].phase_windings[0].compensator_x == None
    assert m["substation"].windings[0].phase_windings[1].compensator_x == None
    assert m["substation"].windings[0].phase_windings[2].compensator_x == None

    assert m["substation"].windings[1].phase_windings[0].compensator_x == None
    assert m["substation"].windings[1].phase_windings[1].compensator_x == None
    assert m["substation"].windings[1].phase_windings[2].compensator_x == None

    # reg1 is a 4.16kV/4.16kV two windings regulator
    assert m["reg1"].name == "reg1"
    assert len(m["reg1"].windings) == 2  # Transformer reg1 should have 2 Windings
    assert m["reg1"].windings[0].nominal_voltage == 4.16 * 10 ** 3
    assert m["reg1"].windings[1].nominal_voltage == 4.16 * 10 ** 3
    assert m["reg1"].feeder_name == "sourcebus_src"
    assert m["reg1"].noload_loss == 0.0
    assert m["reg1"].loadloss == 0.4
    assert m["reg1"].phase_shift == None
    assert m["reg1"].normhkva == 1832.6
    assert m["reg1"].from_element == "bus1"
    assert m["reg1"].to_element == "bus2"
    assert m["reg1"].reactances == pytest.approx(
        parsed_values["Transformer"]["reactances"]
    )
    assert m["reg1"].is_center_tap == 0

    assert (
        m["reg1"].windings[0].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )
    assert (
        m["reg1"].windings[1].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )

    assert m["reg1"].windings[0].rated_power == 1666 * 10 ** 3
    assert m["reg1"].windings[1].rated_power == 1666 * 10 ** 3

    assert m["reg1"].windings[0].emergency_power == 2499000.0
    assert m["reg1"].windings[1].emergency_power == 2499000.0

    assert m["reg1"].windings[0].resistance == 0.2
    assert m["reg1"].windings[1].resistance == 0.2

    assert m["reg1"].windings[0].voltage_type == 0
    assert m["reg1"].windings[1].voltage_type == 2

    assert m["reg1"].windings[0].voltage_limit == None
    assert m["reg1"].windings[1].voltage_limit == None

    assert m["reg1"].windings[0].reverse_resistance == None
    assert m["reg1"].windings[1].reverse_resistance == None

    assert m["reg1"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["reg1"].windings[0].phase_windings[1].tap_position == 1.0
    assert m["reg1"].windings[0].phase_windings[2].tap_position == 1.0

    assert m["reg1"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["reg1"].windings[1].phase_windings[1].tap_position == 1.0
    assert m["reg1"].windings[1].phase_windings[2].tap_position == 1.0

    assert m["reg1"].windings[0].phase_windings[0].phase == "A"
    assert m["reg1"].windings[0].phase_windings[1].phase == "B"
    assert m["reg1"].windings[0].phase_windings[2].phase == "C"

    assert m["reg1"].windings[1].phase_windings[0].phase == "A"
    assert m["reg1"].windings[1].phase_windings[1].phase == "B"
    assert m["reg1"].windings[1].phase_windings[2].phase == "C"

    assert m["reg1"].windings[0].phase_windings[0].compensator_r == None
    assert m["reg1"].windings[0].phase_windings[1].compensator_r == None
    assert m["reg1"].windings[0].phase_windings[2].compensator_r == None

    assert m["reg1"].windings[1].phase_windings[0].compensator_r == None
    assert m["reg1"].windings[1].phase_windings[1].compensator_r == None
    assert m["reg1"].windings[1].phase_windings[2].compensator_r == None

    assert m["reg1"].windings[0].phase_windings[0].compensator_x == None
    assert m["reg1"].windings[0].phase_windings[1].compensator_x == None
    assert m["reg1"].windings[0].phase_windings[2].compensator_x == None

    assert m["reg1"].windings[1].phase_windings[0].compensator_x == None
    assert m["reg1"].windings[1].phase_windings[1].compensator_x == None
    assert m["reg1"].windings[1].phase_windings[2].compensator_x == None

    # xfm1 is a 4.16kV/0.48kV two windings distribution transformer
    assert m["xfm1"].name == "xfm1"
    assert len(m["xfm1"].windings) == 2  # Transformer xfm1 should have 2 Windings
    assert m["xfm1"].windings[0].nominal_voltage == 4.16 * 10 ** 3
    assert m["xfm1"].windings[1].nominal_voltage == 0.48 * 10 ** 3
    assert m["xfm1"].feeder_name == "sourcebus_src"
    assert m["xfm1"].noload_loss == 0.0
    assert m["xfm1"].loadloss == 1.1
    assert m["xfm1"].phase_shift == None
    assert m["xfm1"].normhkva == 550.0
    assert m["xfm1"].from_element == "bus2"
    assert m["xfm1"].to_element == "bus3"
    assert m["xfm1"].reactances == [float(2)]
    assert m["xfm1"].is_center_tap == 0

    assert m["xfm1"].windings[0].connection_type == "D"
    assert m["xfm1"].windings[1].connection_type == "Y"

    assert m["xfm1"].windings[0].rated_power == 500 * 10 ** 3
    assert m["xfm1"].windings[1].rated_power == 500 * 10 ** 3

    assert m["xfm1"].windings[0].emergency_power == 750000.0
    assert m["xfm1"].windings[1].emergency_power == 750000.0

    assert m["xfm1"].windings[0].resistance == 0.55
    assert m["xfm1"].windings[1].resistance == 0.55

    assert m["xfm1"].windings[0].voltage_type == 0
    assert m["xfm1"].windings[1].voltage_type == 2

    assert m["xfm1"].windings[0].voltage_limit == None
    assert m["xfm1"].windings[1].voltage_limit == None

    assert m["xfm1"].windings[0].reverse_resistance == None
    assert m["xfm1"].windings[1].reverse_resistance == None

    assert m["xfm1"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["xfm1"].windings[0].phase_windings[1].tap_position == 1.0

    assert m["xfm1"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["xfm1"].windings[1].phase_windings[1].tap_position == 1.0

    assert m["xfm1"].windings[0].phase_windings[0].phase == "A"
    assert m["xfm1"].windings[0].phase_windings[1].phase == "C"

    assert m["xfm1"].windings[1].phase_windings[0].phase == "A"
    assert m["xfm1"].windings[1].phase_windings[1].phase == "C"

    assert m["xfm1"].windings[0].phase_windings[0].compensator_r == None
    assert m["xfm1"].windings[0].phase_windings[1].compensator_r == None

    assert m["xfm1"].windings[1].phase_windings[0].compensator_r == None
    assert m["xfm1"].windings[1].phase_windings[1].compensator_r == None

    assert m["xfm1"].windings[0].phase_windings[0].compensator_x == None
    assert m["xfm1"].windings[0].phase_windings[1].compensator_x == None

    assert m["xfm1"].windings[1].phase_windings[0].compensator_x == None
    assert m["xfm1"].windings[1].phase_windings[1].compensator_x == None

    # Three phase wye-wye transformer from IEEE 4 node feeder

    # t1 is a 12.47kV/4.16kV two windings distribution transformer
    assert m["t1"].name == "t1"
    assert len(m["t1"].windings) == 2  # Transformer t1 should have 2 Windings
    assert m["t1"].windings[0].nominal_voltage == 12.47 * 10 ** 3
    assert m["t1"].windings[1].nominal_voltage == 4.16 * 10 ** 3

    assert m["t1"].feeder_name == "sourcebus_src"
    assert m["t1"].noload_loss == 0.0
    assert m["t1"].loadloss == 1.0
    assert m["t1"].phase_shift == None
    assert m["t1"].normhkva == 6600.0
    assert m["t1"].from_element == "n2"
    assert m["t1"].to_element == "n3"
    assert m["t1"].reactances == [float(6)]
    assert m["t1"].is_center_tap == 0

    assert m["t1"].windings[0].connection_type == "Y"
    assert m["t1"].windings[1].connection_type == "Y"

    assert m["t1"].windings[0].rated_power == 6000 * 10 ** 3
    assert m["t1"].windings[1].rated_power == 6000 * 10 ** 3

    assert m["t1"].windings[0].emergency_power == 9000000.0
    assert m["t1"].windings[1].emergency_power == 9000000.0

    assert m["t1"].windings[0].resistance == 0.5
    assert m["t1"].windings[1].resistance == 0.5

    assert m["t1"].windings[0].voltage_type == 0
    assert m["t1"].windings[1].voltage_type == 2

    assert m["t1"].windings[0].voltage_limit == None
    assert m["t1"].windings[1].voltage_limit == None

    assert m["t1"].windings[0].reverse_resistance == None
    assert m["t1"].windings[1].reverse_resistance == None

    assert m["t1"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["t1"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["t1"].windings[0].phase_windings[0].phase == "A"
    assert m["t1"].windings[1].phase_windings[0].phase == "A"

    assert m["t1"].windings[0].phase_windings[0].compensator_r == None

    assert m["t1"].windings[1].phase_windings[0].compensator_r == None

    assert m["t1"].windings[0].phase_windings[0].compensator_x == None

    assert m["t1"].windings[1].phase_windings[0].compensator_x == None

    # Three phase Delta-wye substation Transformer from 4kv SMART-DS region P4U
    assert m["sb5_p4uhs0_4_trans_439"].name == "sb5_p4uhs0_4_trans_439"
    assert (
        len(m["sb5_p4uhs0_4_trans_439"].windings) == 2
    )  # Transformer should have 2 Windings
    assert m["sb5_p4uhs0_4_trans_439"].windings[0].nominal_voltage == 69.0 * 10 ** 3
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].nominal_voltage == 4.0 * 10 ** 3

    assert m["sb5_p4uhs0_4_trans_439"].feeder_name == "sourcebus_src"
    assert m["sb5_p4uhs0_4_trans_439"].noload_loss == 0.0
    assert m["sb5_p4uhs0_4_trans_439"].loadloss == 0.9616652
    assert m["sb5_p4uhs0_4_trans_439"].phase_shift == None
    assert m["sb5_p4uhs0_4_trans_439"].normhkva == 8800.0
    assert m["sb5_p4uhs0_4_trans_439"].from_element == "sb5_p4uhs0_4_node_5_12"
    assert m["sb5_p4uhs0_4_trans_439"].to_element == "sb5_p4uhs0_4_node_5_13"
    assert m["sb5_p4uhs0_4_trans_439"].reactances == [pytest.approx(0.9616652224137047)]
    assert m["sb5_p4uhs0_4_trans_439"].is_center_tap == 0

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].connection_type == "D"
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].connection_type == "Y"

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].rated_power == 8000 * 10 ** 3
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].rated_power == 8000 * 10 ** 3

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].emergency_power == 12000000.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].emergency_power == 12000000.0

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].resistance == pytest.approx(
        0.4808326112068522, 0.0000001
    )
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].resistance == pytest.approx(
        0.4808326112068522, 0.0000001
    )

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].voltage_type == 0
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].voltage_type == 2

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].voltage_limit == None
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].voltage_limit == None

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].reverse_resistance == None
    assert m["sb5_p4uhs0_4_trans_439"].windings[1].reverse_resistance == None

    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[1].tap_position == 1.0
    assert m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[2].tap_position == 1.0

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
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].compensator_r == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[1].compensator_r == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[2].compensator_r == None
    )

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[0].compensator_r == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].compensator_r == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].compensator_r == None
    )

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[0].compensator_x == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[1].compensator_x == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[0].phase_windings[2].compensator_x == None
    )

    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[0].compensator_x == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[1].compensator_x == None
    )
    assert (
        m["sb5_p4uhs0_4_trans_439"].windings[1].phase_windings[2].compensator_x == None
    )

    # Three phase Wye-Wye Transformer from 4kV SMART-DS region P4U
    assert m["tr(r:p4udt27-p4udt27lv)"].name == "tr(r:p4udt27-p4udt27lv)"
    assert (
        len(m["tr(r:p4udt27-p4udt27lv)"].windings) == 2
    )  # Transformer should have 2 Windings
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].nominal_voltage == 4.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].nominal_voltage == 0.48 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)"].feeder_name == "sourcebus_src"
    assert m["tr(r:p4udt27-p4udt27lv)"].noload_loss == 0.6
    assert m["tr(r:p4udt27-p4udt27lv)"].loadloss == 1.74408
    assert m["tr(r:p4udt27-p4udt27lv)"].phase_shift == None
    assert m["tr(r:p4udt27-p4udt27lv)"].normhkva == 82.5
    assert m["tr(r:p4udt27-p4udt27lv)"].from_element == "p4udt27"
    assert m["tr(r:p4udt27-p4udt27lv)"].to_element == "p4udt27lv"
    assert m["tr(r:p4udt27-p4udt27lv)"].reactances == [pytest.approx(3.240000000000000)]
    assert m["tr(r:p4udt27-p4udt27lv)"].is_center_tap == 0

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].connection_type == "Y"
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].connection_type == "Y"

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].rated_power == 75.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].rated_power == 75.0 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].emergency_power == 112.5 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].emergency_power == 112.5 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].resistance == 0.87204
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].resistance == 0.87204

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].voltage_type == 0
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].voltage_type == 2

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].voltage_limit == None
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].voltage_limit == None

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].reverse_resistance == None
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].reverse_resistance == None

    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[2].tap_position == 1.0
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[2].tap_position == 1.0
    )

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[2].phase == "C"

    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[2].phase == "C"

    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[0].compensator_r == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[1].compensator_r == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[2].compensator_r == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[0].compensator_r == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[1].compensator_r == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[2].compensator_r == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[0].compensator_x == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[1].compensator_x == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[0].phase_windings[2].compensator_x == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[0].compensator_x == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[1].compensator_x == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)"].windings[1].phase_windings[2].compensator_x == None
    )

    # Three phase Wye-Wye Transformer (modified) from 4kV SMART-DS region P4U
    assert m["tr(r:p4udt27-p4udt27lv)_1"].name == "tr(r:p4udt27-p4udt27lv)_1"
    assert (
        len(m["tr(r:p4udt27-p4udt27lv)_1"].windings) == 2
    )  # Transformer should have 2 Windings
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].nominal_voltage == 4.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].nominal_voltage == 0.48 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_1"].feeder_name == "sourcebus_src"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].noload_loss == 0.6
    assert m["tr(r:p4udt27-p4udt27lv)_1"].loadloss == 1.74408
    assert m["tr(r:p4udt27-p4udt27lv)_1"].phase_shift == None
    assert m["tr(r:p4udt27-p4udt27lv)_1"].normhkva == 82.5
    assert m["tr(r:p4udt27-p4udt27lv)_1"].from_element == "p4udt27"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].to_element == "p4udt27lv"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].reactances == [
        pytest.approx(3.240000000000000)
    ]
    assert m["tr(r:p4udt27-p4udt27lv)_1"].is_center_tap == 0

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].connection_type == "D"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].connection_type == "Y"

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].rated_power == 75.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].rated_power == 75.0 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].emergency_power == 112.5 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].emergency_power == 112.5 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].resistance == 0.87204
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].resistance == 0.87204

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].voltage_type == 0
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].voltage_type == 2

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].voltage_limit == None
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].voltage_limit == None

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].reverse_resistance == None
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].reverse_resistance == None

    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[2].tap_position == 1.0
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[2].tap_position == 1.0
    )

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[2].phase == "C"

    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[2].phase == "C"

    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[0].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[1].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[2].compensator_r
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[0].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[1].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[2].compensator_r
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[0].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[1].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[0].phase_windings[2].compensator_x
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[0].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[1].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_1"].windings[1].phase_windings[2].compensator_x
        == None
    )

    # Three phase Wye-Wye Transformer (modified) from 4kV SMART-DS region P4U
    assert m["tr(r:p4udt27-p4udt27lv)_2"].name == "tr(r:p4udt27-p4udt27lv)_2"
    assert (
        len(m["tr(r:p4udt27-p4udt27lv)_2"].windings) == 2
    )  # Transformer should have 2 Windings
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].nominal_voltage == 4.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].nominal_voltage == 0.48 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_2"].feeder_name == "sourcebus_src"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].noload_loss == 0.6
    assert m["tr(r:p4udt27-p4udt27lv)_2"].loadloss == 1.74408
    assert m["tr(r:p4udt27-p4udt27lv)_2"].phase_shift == None
    assert m["tr(r:p4udt27-p4udt27lv)_2"].normhkva == 82.5
    assert m["tr(r:p4udt27-p4udt27lv)_2"].from_element == "p4udt27"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].to_element == "p4udt27lv"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].reactances == [
        pytest.approx(3.240000000000000)
    ]
    assert m["tr(r:p4udt27-p4udt27lv)_2"].is_center_tap == 0

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].connection_type == "D"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].connection_type == "D"

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].rated_power == 75.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].rated_power == 75.0 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].emergency_power == 112.5 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].emergency_power == 112.5 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].resistance == 0.87204
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].resistance == 0.87204

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].voltage_type == 0
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].voltage_type == 2

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].voltage_limit == None
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].voltage_limit == None

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].reverse_resistance == None
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].reverse_resistance == None

    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[2].tap_position == 1.0
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[2].tap_position == 1.0
    )

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[2].phase == "C"

    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[2].phase == "C"

    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[0].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[1].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[2].compensator_r
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[0].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[1].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[2].compensator_r
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[0].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[1].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[0].phase_windings[2].compensator_x
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[0].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[1].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_2"].windings[1].phase_windings[2].compensator_x
        == None
    )

    # Three phase Wye-Wye Transformer (modified) from 4kV SMART-DS region P4U
    assert m["tr(r:p4udt27-p4udt27lv)_3"].name == "tr(r:p4udt27-p4udt27lv)_3"
    assert (
        len(m["tr(r:p4udt27-p4udt27lv)_3"].windings) == 2
    )  # Transformer should have 2 Windings
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].nominal_voltage == 4.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].nominal_voltage == 0.48 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_3"].feeder_name == "sourcebus_src"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].noload_loss == 0.6
    assert m["tr(r:p4udt27-p4udt27lv)_3"].loadloss == 1.74408
    assert m["tr(r:p4udt27-p4udt27lv)_3"].phase_shift == None
    assert m["tr(r:p4udt27-p4udt27lv)_3"].normhkva == 82.5
    assert m["tr(r:p4udt27-p4udt27lv)_3"].from_element == "p4udt27"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].to_element == "p4udt27lv"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].reactances == [
        pytest.approx(3.240000000000000)
    ]
    assert m["tr(r:p4udt27-p4udt27lv)_3"].is_center_tap == 0

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].connection_type == "Y"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].connection_type == "D"

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].rated_power == 75.0 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].rated_power == 75.0 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].emergency_power == 112.5 * 10 ** 3
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].emergency_power == 112.5 * 10 ** 3

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].resistance == 0.87204
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].resistance == 0.87204

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].voltage_type == 0
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].voltage_type == 2

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].voltage_limit == None
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].voltage_limit == None

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].reverse_resistance == None
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].reverse_resistance == None

    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[2].tap_position == 1.0
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[1].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[2].tap_position == 1.0
    )

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[2].phase == "C"

    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[0].phase == "A"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[1].phase == "B"
    assert m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[2].phase == "C"

    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[0].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[1].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[2].compensator_r
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[0].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[1].compensator_r
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[2].compensator_r
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[0].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[1].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[0].phase_windings[2].compensator_x
        == None
    )

    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[0].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[1].compensator_x
        == None
    )
    assert (
        m["tr(r:p4udt27-p4udt27lv)_3"].windings[1].phase_windings[2].compensator_x
        == None
    )

    # Center Tap Transformer from 4kV SMART-DS region P4U
    assert m["tr(r:p4udt25-p4udt25lv)"].name == "tr(r:p4udt25-p4udt25lv)"
    assert (
        len(m["tr(r:p4udt25-p4udt25lv)"].windings) == 3
    )  # Transformer tr(r:p4udt25-p4udt25lv) should have 3 Windings
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].nominal_voltage == 2.3094 * 10 ** 3
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[1].nominal_voltage == 0.120089 * 10 ** 3
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[2].nominal_voltage == 0.120089 * 10 ** 3
    )

    assert m["tr(r:p4udt25-p4udt25lv)"].feeder_name == "sourcebus_src"
    assert m["tr(r:p4udt25-p4udt25lv)"].noload_loss == 0.472
    assert m["tr(r:p4udt25-p4udt25lv)"].loadloss == 0.798816
    assert m["tr(r:p4udt25-p4udt25lv)"].phase_shift == None
    assert m["tr(r:p4udt25-p4udt25lv)"].normhkva == 27.5
    assert m["tr(r:p4udt25-p4udt25lv)"].from_element == "p4udt25"
    assert m["tr(r:p4udt25-p4udt25lv)"].to_element == "p4udt25lv"
    assert m["tr(r:p4udt25-p4udt25lv)"].reactances == [2.4, 1.6, 2.4]
    assert m["tr(r:p4udt25-p4udt25lv)"].is_center_tap == 1

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].connection_type == "Y"
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].connection_type == "Y"
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].connection_type == "Y"

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].rated_power == 25.0 * 10 ** 3
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].rated_power == 25.0 * 10 ** 3
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].rated_power == 25.0 * 10 ** 3

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].emergency_power == 37.5 * 10 ** 3
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].emergency_power == 37.5 * 10 ** 3
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].emergency_power == 37.5 * 10 ** 3

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].resistance == 0.266272
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].resistance == 0.532544
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].resistance == 0.532544

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].voltage_type == 0
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].voltage_type == 2
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].voltage_type == 2

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].voltage_limit == None
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].voltage_limit == None
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].voltage_limit == None

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].reverse_resistance == None
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].reverse_resistance == None
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].reverse_resistance == None

    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[0].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[1].phase_windings[0].tap_position == 1.0
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[2].phase_windings[0].tap_position == 1.0
    )

    assert m["tr(r:p4udt25-p4udt25lv)"].windings[0].phase_windings[0].phase == "B"
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[1].phase_windings[0].phase == "B"
    assert m["tr(r:p4udt25-p4udt25lv)"].windings[2].phase_windings[0].phase == "B"

    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[0].phase_windings[0].compensator_r == None
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[1].phase_windings[0].compensator_r == None
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[2].phase_windings[0].compensator_r == None
    )

    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[0].phase_windings[0].compensator_x == None
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[1].phase_windings[0].compensator_x == None
    )
    assert (
        m["tr(r:p4udt25-p4udt25lv)"].windings[2].phase_windings[0].compensator_x == None
    )

    # Center Tap Transformer from IEEE 8500 test case
    assert m["t21396254a"].name == "t21396254a"
    assert (
        len(m["t21396254a"].windings) == 3
    )  # Transformer t21396254a should have 3 Windings
    assert m["t21396254a"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["t21396254a"].windings[1].nominal_voltage == 0.12 * 10 ** 3
    assert m["t21396254a"].windings[2].nominal_voltage == 0.12 * 10 ** 3

    assert m["t21396254a"].feeder_name == "sourcebus_src"
    assert m["t21396254a"].noload_loss == 0.2
    assert m["t21396254a"].loadloss == 1.8
    assert m["t21396254a"].phase_shift == None
    assert m["t21396254a"].normhkva == 16.5
    assert m["t21396254a"].from_element == "l2804253"
    assert m["t21396254a"].to_element == "x2804253a"
    assert m["t21396254a"].reactances == [2.04, 2.04, 1.36]
    assert m["t21396254a"].is_center_tap == 1

    assert (
        m["t21396254a"].windings[0].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )
    assert (
        m["t21396254a"].windings[1].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )
    assert (
        m["t21396254a"].windings[2].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )

    assert m["t21396254a"].windings[0].rated_power == 15 * 10 ** 3
    assert m["t21396254a"].windings[1].rated_power == 15 * 10 ** 3
    assert m["t21396254a"].windings[2].rated_power == 15 * 10 ** 3

    assert m["t21396254a"].windings[0].emergency_power == 22500.0
    assert m["t21396254a"].windings[1].emergency_power == 22500.0
    assert m["t21396254a"].windings[2].emergency_power == 22500.0

    assert m["t21396254a"].windings[0].resistance == 0.6
    assert m["t21396254a"].windings[1].resistance == 1.2
    assert m["t21396254a"].windings[2].resistance == 1.2

    assert m["t21396254a"].windings[0].voltage_type == 0
    assert m["t21396254a"].windings[1].voltage_type == 2
    assert m["t21396254a"].windings[2].voltage_type == 2

    assert m["t21396254a"].windings[0].voltage_limit == None
    assert m["t21396254a"].windings[1].voltage_limit == None
    assert m["t21396254a"].windings[2].voltage_limit == None

    assert m["t21396254a"].windings[0].reverse_resistance == None
    assert m["t21396254a"].windings[1].reverse_resistance == None
    assert m["t21396254a"].windings[2].reverse_resistance == None

    assert m["t21396254a"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["t21396254a"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["t21396254a"].windings[2].phase_windings[0].tap_position == 1.0

    assert m["t21396254a"].windings[0].phase_windings[0].phase == "A"
    assert m["t21396254a"].windings[1].phase_windings[0].phase == "A"
    assert m["t21396254a"].windings[2].phase_windings[0].phase == "A"

    assert m["t21396254a"].windings[0].phase_windings[0].compensator_r == None
    assert m["t21396254a"].windings[1].phase_windings[0].compensator_r == None
    assert m["t21396254a"].windings[2].phase_windings[0].compensator_r == None

    assert m["t21396254a"].windings[0].phase_windings[0].compensator_x == None
    assert m["t21396254a"].windings[1].phase_windings[0].compensator_x == None
    assert m["t21396254a"].windings[2].phase_windings[0].compensator_x == None

    # Single phase Wye-Wye Transformer (for regulator) From IEEE 8500 Test case
    assert m["feeder_rega"].name == "feeder_rega"
    assert (
        len(m["feeder_rega"].windings) == 2
    )  # Transformer feeder_rega should have 2 Windings
    assert m["feeder_rega"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["feeder_rega"].windings[1].nominal_voltage == 7.2 * 10 ** 3

    assert m["feeder_rega"].feeder_name == "sourcebus_src"
    assert m["feeder_rega"].noload_loss == 0.0
    assert m["feeder_rega"].loadloss == 0.001
    assert m["feeder_rega"].phase_shift == None
    assert m["feeder_rega"].normhkva == 30250.0
    assert m["feeder_rega"].from_element == "regxfmr_hvmv_sub_lsb"
    assert m["feeder_rega"].to_element == "_hvmv_sub_lsb"
    assert m["feeder_rega"].reactances == [0.1]
    assert m["feeder_rega"].is_center_tap == 0

    assert m["feeder_rega"].windings[0].connection_type == "Y"
    assert m["feeder_rega"].windings[1].connection_type == "Y"

    assert m["feeder_rega"].windings[0].rated_power == 27500 * 10 ** 3
    assert m["feeder_rega"].windings[1].rated_power == 27500 * 10 ** 3

    assert m["feeder_rega"].windings[0].emergency_power == 41250000.0
    assert m["feeder_rega"].windings[1].emergency_power == 41250000.0

    assert m["feeder_rega"].windings[0].resistance == 0.0005
    assert m["feeder_rega"].windings[1].resistance == 0.0005

    assert m["feeder_rega"].windings[0].voltage_type == 0
    assert m["feeder_rega"].windings[1].voltage_type == 2

    assert m["feeder_rega"].windings[0].voltage_limit == None
    assert m["feeder_rega"].windings[1].voltage_limit == None

    assert m["feeder_rega"].windings[0].reverse_resistance == None
    assert m["feeder_rega"].windings[1].reverse_resistance == None

    assert m["feeder_rega"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["feeder_rega"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["feeder_rega"].windings[0].phase_windings[0].phase == "A"
    assert m["feeder_rega"].windings[1].phase_windings[0].phase == "A"

    assert m["feeder_rega"].windings[0].phase_windings[0].compensator_r == None
    assert m["feeder_rega"].windings[1].phase_windings[0].compensator_r == None

    assert m["feeder_rega"].windings[0].phase_windings[0].compensator_x == None
    assert m["feeder_rega"].windings[1].phase_windings[0].compensator_x == None

    # Single phase Wye-Wye Transformers from Epri J-1 Feeder
    assert m["b13659-1c"].name == "b13659-1c"
    assert (
        len(m["b13659-1c"].windings) == 2
    )  # Transformer b13659-1c should have 2 Windings
    assert m["b13659-1c"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["b13659-1c"].windings[1].nominal_voltage == 0.24 * 10 ** 3

    assert m["b13659-1c"].feeder_name == "sourcebus_src"
    assert m["b13659-1c"].noload_loss == 0.34
    assert m["b13659-1c"].loadloss == 1.04
    assert m["b13659-1c"].phase_shift == None
    assert m["b13659-1c"].normhkva == 15
    assert m["b13659-1c"].from_element == "b13659"
    assert m["b13659-1c"].to_element == "x_b13659-c"
    assert m["b13659-1c"].reactances == [1.5]
    assert m["b13659-1c"].is_center_tap == 0

    assert (
        m["b13659-1c"].windings[0].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )
    assert (
        m["b13659-1c"].windings[1].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )

    assert m["b13659-1c"].windings[0].rated_power == 15 * 10 ** 3
    assert m["b13659-1c"].windings[1].rated_power == 15 * 10 ** 3

    assert m["b13659-1c"].windings[1].emergency_power == 21 * 10 ** 3
    assert m["b13659-1c"].windings[1].emergency_power == 21 * 10 ** 3

    assert m["b13659-1c"].windings[0].resistance == 0.52
    assert m["b13659-1c"].windings[1].resistance == 0.52

    assert m["b13659-1c"].windings[0].voltage_type == 0
    assert m["b13659-1c"].windings[1].voltage_type == 2

    assert m["b13659-1c"].windings[0].voltage_limit == None
    assert m["b13659-1c"].windings[1].voltage_limit == None

    assert m["b13659-1c"].windings[0].reverse_resistance == None
    assert m["b13659-1c"].windings[1].reverse_resistance == None

    assert m["b13659-1c"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["b13659-1c"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["b13659-1c"].windings[0].phase_windings[0].phase == "C"
    assert m["b13659-1c"].windings[1].phase_windings[0].phase == "C"

    assert m["b13659-1c"].windings[0].phase_windings[0].compensator_r == None
    assert m["b13659-1c"].windings[1].phase_windings[0].compensator_r == None

    assert m["b13659-1c"].windings[0].phase_windings[0].compensator_x == None
    assert m["b13659-1c"].windings[1].phase_windings[0].compensator_x == None

    # Single phase Wye-Wye Transformers from Epri J-1 Feeder
    assert m["b4551-1a"].name == "b4551-1a"
    assert (
        len(m["b4551-1a"].windings) == 2
    )  # Transformer b4551-1a should have 2 Windings
    assert m["b4551-1a"].windings[0].nominal_voltage == 7.2 * 10 ** 3
    assert m["b4551-1a"].windings[1].nominal_voltage == 0.24 * 10 ** 3

    assert m["b4551-1a"].feeder_name == "sourcebus_src"
    assert m["b4551-1a"].noload_loss == 0.34
    assert m["b4551-1a"].loadloss == 1.04
    assert m["b4551-1a"].phase_shift == None
    assert m["b4551-1a"].normhkva == 15
    assert m["b4551-1a"].from_element == "b4551"
    assert m["b4551-1a"].to_element == "x_b4551-a"
    assert m["b4551-1a"].reactances == [1.5]
    assert m["b4551-1a"].is_center_tap == 0

    assert (
        m["b4551-1a"].windings[0].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )
    assert (
        m["b4551-1a"].windings[1].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )

    assert m["b4551-1a"].windings[0].rated_power == 15 * 10 ** 3
    assert m["b4551-1a"].windings[1].rated_power == 15 * 10 ** 3

    assert m["b4551-1a"].windings[1].emergency_power == 21 * 10 ** 3
    assert m["b4551-1a"].windings[1].emergency_power == 21 * 10 ** 3

    assert m["b4551-1a"].windings[0].resistance == 0.52
    assert m["b4551-1a"].windings[1].resistance == 0.52

    assert m["b4551-1a"].windings[0].voltage_type == 0
    assert m["b4551-1a"].windings[1].voltage_type == 2

    assert m["b4551-1a"].windings[0].voltage_limit == None
    assert m["b4551-1a"].windings[1].voltage_limit == None

    assert m["b4551-1a"].windings[0].reverse_resistance == None
    assert m["b4551-1a"].windings[1].reverse_resistance == None

    assert m["b4551-1a"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["b4551-1a"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["b4551-1a"].windings[0].phase_windings[0].phase == "A"
    assert m["b4551-1a"].windings[1].phase_windings[0].phase == "A"

    assert m["b4551-1a"].windings[0].phase_windings[0].compensator_r == None
    assert m["b4551-1a"].windings[1].phase_windings[0].compensator_r == None

    assert m["b4551-1a"].windings[0].phase_windings[0].compensator_x == None
    assert m["b4551-1a"].windings[1].phase_windings[0].compensator_x == None

    # Three phase Wye-Wye Transformer from 4kV SMART-DS region P4U
    assert m["5865228330a-1abc"].name == "5865228330a-1abc"
    assert (
        len(m["5865228330a-1abc"].windings) == 2
    )  # Transformer should have 2 Windings
    assert m["5865228330a-1abc"].windings[0].nominal_voltage == 12.47 * 10 ** 3
    assert m["5865228330a-1abc"].windings[1].nominal_voltage == 0.416 * 10 ** 3

    assert m["5865228330a-1abc"].feeder_name == "sourcebus_src"
    assert m["5865228330a-1abc"].noload_loss == 0.05
    assert m["5865228330a-1abc"].loadloss == 0.7
    assert m["5865228330a-1abc"].phase_shift == None
    assert m["5865228330a-1abc"].normhkva == 2000.01
    assert m["5865228330a-1abc"].from_element == "5865228330a"
    assert m["5865228330a-1abc"].to_element == "x_5865228330a"
    assert m["5865228330a-1abc"].reactances == [5]
    assert m["5865228330a-1abc"].is_center_tap == 0

    assert (
        m["5865228330a-1abc"].windings[0].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )
    assert (
        m["5865228330a-1abc"].windings[1].connection_type
        == parsed_values["Transformer"]["connection_type"]
    )

    assert m["5865228330a-1abc"].windings[0].rated_power == 2000 * 10 ** 3
    assert m["5865228330a-1abc"].windings[1].rated_power == 2000 * 10 ** 3

    assert m["5865228330a-1abc"].windings[0].emergency_power == 2800 * 10 ** 3
    assert m["5865228330a-1abc"].windings[1].emergency_power == 2800 * 10 ** 3

    assert m["5865228330a-1abc"].windings[0].resistance == 0.35
    assert m["5865228330a-1abc"].windings[1].resistance == 0.35

    assert m["5865228330a-1abc"].windings[0].voltage_type == 0
    assert m["5865228330a-1abc"].windings[1].voltage_type == 2

    assert m["5865228330a-1abc"].windings[0].voltage_limit == None
    assert m["5865228330a-1abc"].windings[1].voltage_limit == None

    assert m["5865228330a-1abc"].windings[0].reverse_resistance == None
    assert m["5865228330a-1abc"].windings[1].reverse_resistance == None

    assert m["5865228330a-1abc"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["5865228330a-1abc"].windings[0].phase_windings[1].tap_position == 1.0
    assert m["5865228330a-1abc"].windings[0].phase_windings[2].tap_position == 1.0

    assert m["5865228330a-1abc"].windings[1].phase_windings[0].tap_position == 1.0
    assert m["5865228330a-1abc"].windings[1].phase_windings[1].tap_position == 1.0
    assert m["5865228330a-1abc"].windings[1].phase_windings[2].tap_position == 1.0

    assert m["5865228330a-1abc"].windings[0].phase_windings[0].phase == "A"
    assert m["5865228330a-1abc"].windings[0].phase_windings[1].phase == "B"
    assert m["5865228330a-1abc"].windings[0].phase_windings[2].phase == "C"

    assert m["5865228330a-1abc"].windings[1].phase_windings[0].phase == "A"
    assert m["5865228330a-1abc"].windings[1].phase_windings[1].phase == "B"
    assert m["5865228330a-1abc"].windings[1].phase_windings[2].phase == "C"

    assert m["5865228330a-1abc"].windings[0].phase_windings[0].compensator_r == None
    assert m["5865228330a-1abc"].windings[0].phase_windings[1].compensator_r == None
    assert m["5865228330a-1abc"].windings[0].phase_windings[2].compensator_r == None

    assert m["5865228330a-1abc"].windings[1].phase_windings[0].compensator_r == None
    assert m["5865228330a-1abc"].windings[1].phase_windings[1].compensator_r == None
    assert m["5865228330a-1abc"].windings[1].phase_windings[2].compensator_r == None

    assert m["5865228330a-1abc"].windings[0].phase_windings[0].compensator_x == None
    assert m["5865228330a-1abc"].windings[0].phase_windings[1].compensator_x == None
    assert m["5865228330a-1abc"].windings[0].phase_windings[2].compensator_x == None

    assert m["5865228330a-1abc"].windings[1].phase_windings[0].compensator_x == None
    assert m["5865228330a-1abc"].windings[1].phase_windings[1].compensator_x == None
    assert m["5865228330a-1abc"].windings[1].phase_windings[2].compensator_x == None

    # Single phase delta-wye transformer. This is a dummy test as we don't expect to see delta configurations on a single phase
    assert m["t1_1"].name == "t1_1"
    assert len(m["t1_1"].windings) == 2  # Transformer t1_1 should have 2 Windings
    assert m["t1_1"].windings[0].nominal_voltage == 12.47 * 10 ** 3
    assert m["t1_1"].windings[1].nominal_voltage == 4.16 * 10 ** 3

    assert m["t1_1"].feeder_name == "sourcebus_src"
    assert m["t1_1"].noload_loss == 0.0
    assert m["t1_1"].loadloss == 1.0
    assert m["t1_1"].phase_shift == None
    assert m["t1_1"].normhkva == 6600.0
    assert m["t1_1"].from_element == "n2"
    assert m["t1_1"].to_element == "n3"
    assert m["t1_1"].reactances == [float(6)]
    assert m["t1_1"].is_center_tap == 0

    assert m["t1_1"].windings[0].connection_type == "D"
    assert m["t1_1"].windings[1].connection_type == "Y"

    assert m["t1_1"].windings[0].rated_power == 6000 * 10 ** 3
    assert m["t1_1"].windings[1].rated_power == 6000 * 10 ** 3

    assert m["t1_1"].windings[0].emergency_power == 9000000.0
    assert m["t1_1"].windings[1].emergency_power == 9000000.0

    assert m["t1_1"].windings[0].resistance == 0.5
    assert m["t1_1"].windings[1].resistance == 0.5

    assert m["t1_1"].windings[0].voltage_type == 0
    assert m["t1_1"].windings[1].voltage_type == 2

    assert m["t1_1"].windings[0].voltage_limit == None
    assert m["t1_1"].windings[1].voltage_limit == None

    assert m["t1_1"].windings[0].reverse_resistance == None
    assert m["t1_1"].windings[1].reverse_resistance == None

    assert m["t1_1"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["t1_1"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["t1_1"].windings[0].phase_windings[0].phase == "C"
    assert m["t1_1"].windings[1].phase_windings[0].phase == "C"

    assert m["t1_1"].windings[0].phase_windings[0].compensator_r == None

    assert m["t1_1"].windings[1].phase_windings[0].compensator_r == None

    assert m["t1_1"].windings[0].phase_windings[0].compensator_x == None

    assert m["t1_1"].windings[1].phase_windings[0].compensator_x == None

    # Single phase wye-delta transformer. This is a dummy test as we don't expect to see delta configurations on a single phase
    assert m["t1_2"].name == "t1_2"
    assert len(m["t1_2"].windings) == 2  # Transformer t1_2 should have 2 Windings
    assert m["t1_2"].windings[0].nominal_voltage == 12.47 * 10 ** 3
    assert m["t1_2"].windings[1].nominal_voltage == 4.16 * 10 ** 3

    assert m["t1_2"].feeder_name == "sourcebus_src"
    assert m["t1_2"].noload_loss == 0.0
    assert m["t1_2"].loadloss == 1.0
    assert m["t1_2"].phase_shift == None
    assert m["t1_2"].normhkva == 6600.0
    assert m["t1_2"].from_element == "n2"
    assert m["t1_2"].to_element == "n3"
    assert m["t1_2"].reactances == [float(6)]
    assert m["t1_2"].is_center_tap == 0

    assert m["t1_2"].windings[0].connection_type == "Y"
    assert m["t1_2"].windings[1].connection_type == "D"

    assert m["t1_2"].windings[0].rated_power == 6000 * 10 ** 3
    assert m["t1_2"].windings[1].rated_power == 6000 * 10 ** 3

    assert m["t1_2"].windings[0].emergency_power == 9000000.0
    assert m["t1_2"].windings[1].emergency_power == 9000000.0

    assert m["t1_2"].windings[0].resistance == 0.5
    assert m["t1_2"].windings[1].resistance == 0.5

    assert m["t1_2"].windings[0].voltage_type == 0
    assert m["t1_2"].windings[1].voltage_type == 2

    assert m["t1_2"].windings[0].voltage_limit == None
    assert m["t1_2"].windings[1].voltage_limit == None

    assert m["t1_2"].windings[0].reverse_resistance == None
    assert m["t1_2"].windings[1].reverse_resistance == None

    assert m["t1_2"].windings[0].phase_windings[0].tap_position == 1.0
    assert m["t1_2"].windings[1].phase_windings[0].tap_position == 1.0

    assert m["t1_2"].windings[0].phase_windings[0].phase == "C"
    assert m["t1_2"].windings[1].phase_windings[0].phase == "C"

    assert m["t1_2"].windings[0].phase_windings[0].compensator_r == None

    assert m["t1_2"].windings[1].phase_windings[0].compensator_r == None

    assert m["t1_2"].windings[0].phase_windings[0].compensator_x == None

    assert m["t1_2"].windings[1].phase_windings[0].compensator_x == None
