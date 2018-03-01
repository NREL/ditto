# -*- coding: utf-8 -*-

"""
test_writer
----------------------------------

Tests for `ditto` module writers
"""
import os

def test_cyme_to_opendss(output_path):
    '''TODO

    '''
    from ditto.store import Store
    from ditto.readers.cyme.read import reader
    from ditto.writers.opendss.write import Writer 
    import opendssdirect as dss

    cyme_models=[f for f in os.listdir('./data/cyme/') if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = reader(data_folder_path=os.path.join('./data/cyme',model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} red...'.format(model=model)) 
        w = Writer(output_path=output_path)
        w.write(m)
        #TODO: Log properly
        print('>...and written to OpenDSS.\n')
        print('redirect {master}'.format(master=os.path.join(output_path,'master.dss')))
        dss.run_command('redirect {master}'.format(master=os.path.join(output_path,'master.dss')))
        dss.run_command('Solve')
        #TODO: Log properly
        print('>Circuit {model} solved.\n'.format(model=model))

