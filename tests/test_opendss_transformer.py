# -*- coding: utf-8 -*-

import os
import pytest as pt
import tempfile

from ditto.readers.opendss.read import Reader
from ditto.store import Store
from ditto.writers.opendss.write import Writer
from ditto.models.powertransformer import PowerTransformer


def test_opendss_center_transformer():

    opendss_test_data = """
    Clear
    new circuit.IEEE13
    ~ basekv=4.16 pu=1.0000 phases=3 bus1=SourceBus
    ~ Angle=0
    ~ MVAsc3=200000 MVASC1=200000    ! stiffen the source to approximate inf source
    New  Transformer.Example1-ph  phases=1  Windings=3
    ~ Xhl=2.04   Xht=2.04   Xlt=1.36  %noloadloss=.2
    ~ Buses=[bus1.1.2  bus2.1.0  bus2.0.2]  ! mid-point of secondary is grounded
    ~ kVs=[12.47  .12  .12]     ! ratings of windings
    ~ kVAs=[25 25 25]
    ~ %Rs = [0.6  1.2  1.2]
    ~ conns=[delta wye wye]
    """

    master_file = tempfile.NamedTemporaryFile(mode="w")

    with open(master_file.name, "w") as f:
        f.write(opendss_test_data)

    m = Store()
    r = Reader(master_file=master_file.name)
    r.parse(m)
    m.set_names()

    for t in m.iter_models(type=PowerTransformer):
        assert len(t.windings) == 3

    output_path = tempfile.TemporaryDirectory()
    w = Writer(output_path=output_path.name)
    w.write(m)

    with open(os.path.join(output_path.name, "Transformers.dss")) as f:
        string = f.read()

    assert "bus1.1.2" in string
    assert "bus2.1.0" in string
    assert "bus2.0.2" in string

def test_opendss_transformer():

    opendss_test_data = """
    Clear
    new circuit.IEEE13
    ~ basekv=4.16 pu=1.0000 phases=3 bus1=SourceBus
    ~ Angle=0
    ~ MVAsc3=200000 MVASC1=200000    ! stiffen the source to approximate inf source
    New Transformer.reg  Phases=3   Windings=2  XHL=0.01
    ~ wdg=1 bus=Sourcebus.1.2.3.0       conn=Wye kv=4.16    kva=5000    %r=0.000498     XHT=.00498
    ~ wdg=2 bus=651.1.2.3       conn=Wye kv=4.16    kva=5000    %r=0.000498   XLT=.00498
    New Transformer.XFM1  Phases=3   Windings=2  XHL=2
    ~ wdg=1 bus=633.1.2.3.0       conn=Wye kv=4.16    kva=500    %r=.55     XHT=1
    ~ wdg=2 bus=634.1.2.3       conn=Wye kv=0.480    kva=500    %r=.55   XLT=1
    """

    master_file = tempfile.NamedTemporaryFile(mode="w")

    with open(master_file.name, "w") as f:
        f.write(opendss_test_data)

    m = Store()
    r = Reader(master_file=master_file.name,)
    r.parse(m)
    m.set_names()

    for t in m.iter_models(type=PowerTransformer):
        assert len(t.windings) == 2

        assert t.windings[0].is_grounded is True
        assert t.windings[1].is_grounded is False

    output_path = tempfile.TemporaryDirectory()
    w = Writer(output_path=output_path.name)
    w.write(m)

    with open(os.path.join(output_path.name, "Transformers.dss")) as f:
        string = f.read()

    assert "sourcebus.1.2.3.0" in string
    assert "651.1.2.3.0" not in string
    assert "651.1.2.3" in string
    assert "633.1.2.3.0" in string
    assert "634.1.2.3.0" not in string
    assert "634.1.2.3" in string
