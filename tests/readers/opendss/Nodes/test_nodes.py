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
    r = Reader(master_file=os.path.join(current_directory, "test_nodes.dss"))
    r.parse(m)
    m.set_names()

    assert (m["st_mat"].name) == "st_mat"
    assert (m["st_mat"].nominal_voltage) == None
    assert (m["st_mat"].phases) == []
    assert (m["st_mat"].positions[0].long) == float(200)
    assert (m["st_mat"].positions[0].lat) == float(400)
    assert (m["st_mat"].positions[0].elevation) == 0
    assert (m["st_mat"].feeder_name) == "st_mat_src"
    # assert (m["st_mat"].substation_name) == None # Not implemented for now
    # assert (m["st_mat"].is_substation) == 0 # Not implemented for now
    # assert (m["st_mat"].is_substation_connection) == 0 # Not implemented for now

    assert (m["bus1"].name) == "bus1"
    assert (m["bus1"].nominal_voltage) == None
    assert (m["bus1"].phases[0].default_value) == "A"
    assert (m["bus1"].phases[1].default_value) == "B"
    assert (m["bus1"].phases[2].default_value) == "C"
    # assert (each.default_value for each in m["bus1"].phases) == set(["A", "B", "C"])
    assert (m["bus1"].positions[0].long) == float(300)
    assert (m["bus1"].positions[0].lat) == float(400)
    assert (m["bus1"].positions[0].elevation) == 0
    assert (m["bus1"].feeder_name) == "st_mat_src"
    # assert (m["bus1"].substation_name) == None # Not implemented for now
    # assert (m["bus1"].is_substation) == 0 # Not implemented for now
    # assert (m["bus1"].is_substation_connection) == 0 # Not implemented for now

    assert (m["sourcebus"].name) == "sourcebus"
    assert (m["sourcebus"].nominal_voltage) == None
    assert (m["sourcebus"].phases[0].default_value) == "A"
    assert (m["sourcebus"].phases[1].default_value) == "B"
    assert (m["sourcebus"].phases[2].default_value) == "C"
    assert (m["sourcebus"].positions[0].long) == float(1674346.56814483)
    assert (m["sourcebus"].positions[0].lat) == float(12272927.0644858)
    assert (m["sourcebus"].positions[0].elevation) == 0
    assert (m["sourcebus"].feeder_name) == "st_mat_src"
    # assert (m["sourcebus"].substation_name) == None # Not implemented for now
    # assert (m["sourcebus"].is_substation) == 0 # Not implemented for now
    # assert (m["sourcebus"].is_substation_connection) == 0 # Not implemented for now

    assert (m["b1"].name) == "b1"
    assert (m["b1"].nominal_voltage) == None
    assert (m["b1"].phases[0].default_value) == "A"
    assert (m["b1"].phases[1].default_value) == "B"
    assert (m["b1"].phases[2].default_value) == "C"
    assert (m["b1"].positions[0].long) == float(1578139)
    assert (m["b1"].positions[0].lat) == float(14291312)
    assert (m["b1"].positions[0].elevation) == 0
    assert (m["b1"].feeder_name) == "st_mat_src"
    # assert (m["b1"].substation_name) == None # Not implemented for now
    # assert (m["b1"].is_substation) == 0 # Not implemented for now
    # assert (m["b1"].is_substation_connection) == 0 # Not implemented for now
