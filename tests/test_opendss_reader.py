# -*- coding: utf-8 -*-

"""
test_opendss_reader
----------------------------------

Tests for reading functions of the OpenDSS reader
"""
import logging
import os

import six

import tempfile
import pytest
import pytest as pt
import numpy as np

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_disabled_objects():
    """Tests if disabled objects are not parsed."""
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader

    # test on the IEEE 13 node feeder
    m = Store()
    r = Reader(
        master_file=os.path.join(
            current_directory,
            "data/ditto-validation/opendss/disabled_objects/master.dss",
        ),
        buscoordinates_file=os.path.join(
            current_directory,
            "data/ditto-validation/opendss/disabled_objects/buscoord.dss",
        ),
    )
    r.parse(m)
    m.set_names()

    # Check that disabled objects were not parsed
    assert not "load_670b" in m.model_names
    assert "load_670a" in m.model_names
    assert "load_671" not in m.model_names
    assert "load_646" not in m.model_names
    assert "load_692" in m.model_names
    assert "cap2" not in m.model_names
    assert "cap1" in m.model_names
    assert "650632" not in m.model_names
    assert "632670" in m.model_names
    assert "632645" not in m.model_names
    assert "645646" in m.model_names
    assert "reg1" in m.model_names
    assert "reg3" not in m.model_names
    assert "regulator_reg3" not in m.model_names
    assert "regulator_reg2" not in m.model_names
    assert "reg2" in m.model_names
    assert "671692" in m.model_names  # Switch 671692 should exists....
    assert [wire.is_open for wire in m["671692"].wires] == [
        1,
        1,
        1,
    ]  # ...but it should be open on all phases


def test_linegeometries_and_wiredata():
    """
        Test the reading of linegeometries and wiredata.
    """
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.opendss.write import Writer

    m = Store()
    r = Reader(
        master_file=os.path.join(
            current_directory, "data/ditto-validation/opendss/linegeometries/Master.dss"
        )
    )
    r.parse(m)
    m.set_names()

    # Number of wires
    assert len(m["line1"].wires) == 4  # Line1 should have 4 wires

    # Phases of the different wires
    assert [w.phase for w in m["line1"].wires] == ["A", "B", "C", "N"]

    # Nameclass
    assert [w.nameclass for w in m["line1"].wires] == ["ACSR336"] * 3 + ["ACSR1/0"]

    # Positions of the wires
    assert [w.X for w in m["line1"].wires] == [
        -1.2909,
        -0.1530096 * 0.3048,
        0.5737,
        0.0,
    ]
    assert [w.Y for w in m["line1"].wires] == [
        13.716,
        4.1806368 * 0.3048,
        13.716,
        14.648,
    ]

    # GMR
    assert [w.gmr for w in m["line1"].wires] == [0.0255 * 0.3048] * 3 + [
        0.00446 * 0.3048
    ]

    # Diameter
    assert [w.diameter for w in m["line1"].wires] == [0.741 * 0.0254] * 3 + [
        0.398 * 0.0254
    ]

    # Resistance
    # TODO: Change this once the resistance of a Wire object will no longer be the total
    # resistance, but the per meter resistance...
    #
    assert np.allclose(
        [w.resistance for w in m["line1"].wires],
        [0.306 * 0.000621371 * 300 * 0.3048] * 3 + [1.12 * 0.000621371 * 300 * 0.3048],
    )
