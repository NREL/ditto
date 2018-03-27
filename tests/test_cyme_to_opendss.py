# -*- coding: utf-8 -*-

"""
test_cyme_to_opendss
----------------------------------

Tests for Cyme --> OpenDSS conversion
"""
import os
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

@pt.mark.skip()
def test_cyme_to_opendss():
    '''
        Test the Cyme to OpenDSS conversion.
    '''
    from ditto.store import Store
    from ditto.readers.cyme.read import Reader
    from ditto.writers.opendss.write import Writer
    import opendssdirect as dss
    output_path = current_directory
    cyme_models=[f for f in os.listdir(os.path.join(current_directory, 'data/cyme/')) if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(current_directory, 'data/cyme',model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} read...'.format(model=model))
        w = Writer(output_path=output_path)
        w.write(m)
        #TODO: Log properly
        print('>...and written to OpenDSS.\n')
        dss.run_command('redirect {master}'.format(master=os.path.join(output_path,'master.dss')))
        dss.run_command('Solve')
        #TODO: Log properly
        print('>Circuit {model} solved.\n'.format(model=model))

    for i in os.listdir(output_path):
        if i.endswith(".dss"):
            try:
                os.remove(os.path.join(output_path, i))
            except:
                pass