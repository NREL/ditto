from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from ditto.writers.ephasor.write import Writer
from ditto.store import Store
import os

import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))
ditto_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ditto')
input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'..','..','validation','input','opendss','ieee_13_node')


@pt.mark.skip(msg="Skipping ephasor tests")
def test_opendss():
    from ditto.readers.opendss.read import reader
    m = Store()
    _reader = reader()


    gridlabd_models_dir = os.path.join(ditto_dir, 'readers', 'gridlabd')

    modelfile = os.path.join(input_path, 'master.dss')
    modelfile = '../../validation/inputs/opendss/ieee_13_node/master.dss'

    _reader.build_opendssdirect(modelfile)
    _reader.set_dss_file_names({'Nodes': '../../validation/inputs/opendss/ieee_13_node/IEEE13Node_BusXY.csv'})
    _reader.parse(m, verbose=True)
    m.build_networkx()
    m.direct_from_source()
    m.set_node_voltages()
    writer = Writer(output_path="./")

    writer.write(m)


@pt.mark.skip(msg="Skipping ephasor tests")
def test_gridlabd():
    from ditto.readers.gridlabd.read import reader
    m = Store()
    # TODO: Add this file
    modelfile = os.path.join(current_directory, './data/gridlabd/ieee_123_node/ieee_123_node.glm')
    _reader = reader(input_file=modelfile)

    _reader.parse(m)
    writer = Writer(output_path="./")

    writer.write(m)
    # writer.write_bus_coordinates()

if __name__ == '__main__':
    #test_opendss()
    test_gridlabd()
