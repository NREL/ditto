# -*- coding: utf-8 -*-

"""
test_nodes.py
----------------------------------

Tests for checking all the attributes of nodes.
"""
import logging
import os

import six

import tempfile
import pytest as pt

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_nodes():
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader

    # test on the test_nodes.dss
    m = Store()
    r = Reader(
        master_file=os.path.join(current_directory, "test_nodes.dss"),
        buscoordinates_file=os.path.join(current_directory, "buscoord.dss"),
    )
    r.parse(m)
    m.set_names()

    assert (m["bus1"].name) == "bus1"
    assert (m["bus1"].nominal_voltage) == float(12.47) * 10 ** 3
    assert (m["bus1"].positions[0].long) == float(300)
    assert (m["bus1"].positions[0].lat) == float(400)
    assert (m["bus1"].positions[0].elevation) == 0
    assert (m["bus1"].feeder_name) == "sourcebus_src"

    assert (m["sourcebus"].name) == "sourcebus"
    assert (m["sourcebus"].nominal_voltage) == float(12.47) * 10 ** 3
    assert (m["sourcebus"].positions[0].long) == float(1674346.56814483)
    assert (m["sourcebus"].positions[0].lat) == float(12272927.0644858)
    assert (m["sourcebus"].positions[0].elevation) == 0
    assert (m["sourcebus"].feeder_name) == "sourcebus_src"

    assert (m["b1"].name) == "b1"
    assert (m["b1"].nominal_voltage) == float(12.47) * 10 ** 3
    assert (m["b1"].positions[0].long) == float(1578139)
    assert (m["b1"].positions[0].lat) == float(14291312)
    assert (m["b1"].positions[0].elevation) == 0
    assert (m["b1"].feeder_name) == "sourcebus_src"
