# -*- coding: utf-8 -*-

"""
test_opendss_to_gridlabd
----------------------------------

Tests for OpenDSS --> GridlabD conversion
"""
import os
import six

if six.PY2:
    from backports import tempfile
else:
    import tempfile
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

#@pt.mark.skip("Segfault occurs")
def test_opendss_to_gridlabd():
    '''
        Test the OpenDSS to GridlabD conversion.
    '''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.gridlabd.write import Writer

    opendss_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/opendss/')) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
            buscoordinates_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
        )
        r.parse(m)
        #TODO: Log properly
        print('>OpenDSS model {model} red...'.format(model=model))
        t = tempfile.TemporaryDirectory()
        w = Writer(output_path=t.name)
        w.write(m)
        #TODO: Log properly
        print('>...and written to GridLabD.\n')
