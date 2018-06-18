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
