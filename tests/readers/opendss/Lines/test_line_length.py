# -*- coding: utf-8 -*-

"""
test_line_length.py
----------------------------------

Tests for checking the line length values are all in meters.
"""
import logging
import os

import six

import tempfile
import pytest as pt

logger = logging.getLogger(__name__)

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_line_length():
    """Tests if line length units are in meters."""
    from ditto.store import Store
    from ditto.readers.opendss.read import Reader

    # test on the test_line_length.dss
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_line_length.dss"))
    r.parse(m)
    m.set_names()

    # Check that line lengths are in meters
    assert (m["line1"].length) == float(100)
    assert (m["line2"].length) == float(83.47 * 304.8)  # units = kft
    assert (m["line3"].length) == float(200 * 0.3048)  # units = ft
    assert (m["line4"].length) == float(1.01 * 1609.34)  # units = mi
    assert (m["line5"].length) == float(2040.12 * 0.01)  # units = cm
    assert (m["line6"].length) == float(1666.87 * 0.0254)  # units = in
