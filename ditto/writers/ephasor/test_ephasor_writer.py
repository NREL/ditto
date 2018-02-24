from builtins import super, range, zip, round, map
from __future__ import absolute_import, division, print_function
from ditto.writers.ephasor.write import Writer
from ditto.store import Store
import os

ditto_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ditto')
input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'..','..','validation','input','opendss','ieee_13_node')
def test_opendss():
    from ditto.readers.opendss.read import reader
    m = Store()
    _reader = reader()


    gridlabd_models_dir = os.path.join(ditto_dir, 'readers', 'gridlabd')

    modelfile = os.path.join(input_path, 'master.dss')
    print(input_path)
    modelfile = '../../validation/inputs/opendss/ieee_13_node/master.dss'

    _reader.build_opendssdirect(modelfile)
    _reader.set_dss_file_names({'Nodes': '../../validation/inputs/opendss/ieee_13_node/IEEE13Node_BusXY.csv'})
    _reader.parse(m, verbose=True)
    m.build_networkx()
    m.direct_from_source()
    m.set_node_voltages()
    writer = Writer(output_path="./")

    writer.write(m)


def test_gridlabd():
    from ditto.readers.gridlabd.read import reader
    m = Store()
    modelfile = '../../validation/inputs/gridlabd/ieee_123_node/ieee_123_node.glm'
    modelfile = '../../validation/inputs/gridlabd/ieee_13_node/ieee_13_node.glm'
    modelfile = '../../validation/inputs/gridlabd/RTC-A/model.glm'
    modelfile = '../../validation/inputs/gridlabd/RTC-A/model_raw.glm'
    #modelfile = '../../readers/gridlabd/13node_simplified.glm'
    _reader = reader(input_file=modelfile)

    _reader.parse(m)
    writer = Writer(output_path="./")

    writer.write(m)
    # writer.write_bus_coordinates()

if __name__ == '__main__':
    #test_opendss()
    test_gridlabd()
