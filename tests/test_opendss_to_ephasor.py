# -*- coding: utf-8 -*-

"""
test_opendss_to_ephasor
----------------------------------

Tests for OpenDSS --> Ephasor conversion
"""
import six

if six.PY2:
    from backports import tempfile
else:
    import tempfile

import os
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

@pt.mark.skip("Segfault occurs")
def test_opendss_to_ephasor():
    '''
        Test the OpenDSS to Ephasor conversion.
    '''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.ephasor.write import Writer

    opendss_models=[f for f in os.listdir(os.path.join(current_directory, 'data/small_cases/opendss/')) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
            buscoordinates_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
        )
        r.parse(m)
        m.build_networkx()
        m.direct_from_source()
        m.set_node_voltages()
        #TODO: Log properly
        print('>OpenDSS model {model} red...'.format(model=model))
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=output_path)
        w.write(m)
        #TODO: Log properly
        print('>...and written to Ephasor.\n')
