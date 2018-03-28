# -*- coding: utf-8 -*-

"""
test_opendss_to_cyme
----------------------------------

Tests for OpenDSS --> Cyme conversion
"""
import os
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

def test_opendss_to_cyme():
    '''
        Test the OpenDSS to Cyme conversion.
    '''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.cyme.write import Writer

    opendss_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/opendss/')) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
            buscoordinates_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
        )
        r.parse(m)
        m.set_names()
        #TODO: Log properly
        print('>OpenDSS model {model} read...'.format(model=model))
        output_path = os.path.join(current_directory, "./")
        w = Writer(output_path=output_path, log_path=output_path)
        w.write(m)
        #TODO: Log properly
        print('>...and written to CYME.\n')