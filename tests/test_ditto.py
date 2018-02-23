#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_ditto
----------------------------------

Tests for `ditto` module.
"""

import pytest as pt

import os


dir_path = os.path.dirname(os.path.realpath(__file__))


@pt.mark.skip(msg="Core currently disabled")
def test_imports():
    import ditto.environment
    from ditto.environment import ACLineSegment, ACLineSegmentPhase
    from ditto.models.line import Line
    from ditto.store import Store as Store
    print(ditto.environment)
    print(ACLineSegment, ACLineSegmentPhase)
    print(Line)
    print(Store())


@pt.mark.skip(msg="Core currently disabled")
def test_creation():

    from ditto.environment import ACLineSegment, ACLineSegmentPhase
    acls = ACLineSegment()

    assert isinstance(acls, ACLineSegment)

    assert acls.bch is None

    acls.bch = 1

    assert acls.bch == 1

    import pytest

    with pytest.raises(TypeError):
        acls.ACLineSegmentPhases = ACLineSegmentPhase()

    assert acls.ACLineSegmentPhases == tuple()

    acls.ACLineSegmentPhases = (ACLineSegmentPhase(), )

    aclsp = acls.ACLineSegmentPhases[0]

    aclsp.ACLineSegment

    assert aclsp.ACLineSegment is acls


@pt.mark.skip(msg="Core currently disabled")
def test_two_way_binding():

    from ditto.environment import ACLineSegment, BaseVoltage

    bv = BaseVoltage()

    acls1 = ACLineSegment()
    acls2 = ACLineSegment()

    acls1.BaseVoltage

    acls1.BaseVoltage = bv
    acls2.BaseVoltage = bv

    assert len(bv.ConductingEquipment) == 2, "Length of BaseVoltage.ConductingEquipment must be two"

    acls1.BaseVoltage = BaseVoltage()

    assert len(bv.ConductingEquipment) == 1, "Length of BaseVoltage.ConductingEquipment must be one"

    assert acls1 not in bv.ConductingEquipment, "ACLS1 must not be in bv.ConductingEquipment"
    assert acls2 in bv.ConductingEquipment, "ACLS2 must be in bv.ConductingEquipment"

    del acls2.BaseVoltage

    assert acls2 not in bv.ConductingEquipment, "ACLS2 must be in bv.ConductingEquipment"

    assert len(bv.ConductingEquipment) == 0, "Length of BaseVoltage.ConductingEquipment must be zero"


@pt.mark.skip(msg="Core currently disabled")
def read_cim_13_node():
    import lxml

    from lxml import etree

    root = etree.parse(os.path.abspath(os.path.join(dir_path, './data/ieee13.xml')), parser=lxml.etree.XMLParser(remove_comments=True)).getroot()

    from ditto.store import Store as Store

    m = Store()

    def strip(s):
        s = s.replace('{{{}}}'.format(ns['cim']), '')
        return s

    ns = dict(cim='http://iec.ch/TC57/2012/CIM-schema-cim16#')

    for i, e in enumerate(root.iterchildren()):
        f = getattr(m.env, strip(e.tag))
        cim_element = f()

        for c in e.iterchildren():
            if c.text is None:
                continue
            setattr(cim_element, strip(c.tag).split('.')[1], c.text)

    assert len(m.elements)==328
