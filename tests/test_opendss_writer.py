# -*- coding: utf-8 -*-

"""
test_opendss_writer
----------------------------------

Tests for writing functions of the OpenDSS writer
"""
import logging
import os

import six

import tempfile
import pytest
import pytest as pt

logger = logging.getLogger(__name__)

def test_parse_wire():
    from ditto.store import Store
    from ditto.models.wire import Wire
    from ditto.writers.opendss.write import Writer
    m = Store()
    wire_A = Wire(m, phase='A', nameclass='wire_test_phase', diameter=5, gmr=10, 
                  ampacity=500, emergency_ampacity=1000, resistance=5)
    t = tempfile.TemporaryDirectory()
    w = Writer(output_path=t.name)
    parsed_wire = w.parse_wire(wire_A)
    assert parsed_wire['GMRac'] == 10
    assert parsed_wire['Diam'] == 5
    assert parsed_wire['normamps'] == 500
    assert parsed_wire['emergamps'] == 1000
    assert parsed_wire['Rac'] == 5

def setup_line_test():
    '''Setup a line with 4 wires.'''
    from ditto.store import Store
    from ditto.models.line import Line
    from ditto.models.wire import Wire

    m = Store()
    wire_A = Wire(m, phase='A', nameclass='wire_test_phase', diameter=5, gmr=10, 
                  ampacity=500, emergency_ampacity=1000, resistance=5)
    wire_B = Wire(m, phase='B', nameclass='wire_test_phase', diameter=5, gmr=10, 
                  ampacity=500, emergency_ampacity=1000, resistance=5)
    wire_C = Wire(m, phase='C', nameclass='wire_test_phase', diameter=5, #Missing GMR 
                  ampacity=500, emergency_ampacity=1000, resistance=5)
    wire_N = Wire(m, phase='N', nameclass='wire_test_neutral', diameter=5, gmr=10, 
                  ampacity=500, emergency_ampacity=1000, resistance=5)
    line = Line(m, name='l1', wires=[wire_A, wire_B, wire_C, wire_N])

    return line


def test_write_wiredata():
    '''Test the method write_wiredata().'''
    from ditto.writers.opendss.write import Writer
    line = setup_line_test()
    t = tempfile.TemporaryDirectory()
    w = Writer(output_path=t.name)
    w.write_wiredata([line])


def test_write_linegeometry():
    '''Test the write_linegeometry() method.'''
    from ditto.writers.opendss.write import Writer
    line = setup_line_test()
    t = tempfile.TemporaryDirectory()
    w = Writer(output_path=t.name)
    w.write_wiredata([line])
    w.write_linegeometry([line])


def test_write_linecodes():
    '''Test the write_linecodes() method.'''
    from ditto.writers.opendss.write import Writer
    line = setup_line_test()
    t = tempfile.TemporaryDirectory()
    w = Writer(output_path=t.name)
    w.write_linecodes([line])
