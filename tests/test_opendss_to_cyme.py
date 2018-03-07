# -*- coding: utf-8 -*-

"""
test_writer
----------------------------------

Tests for `ditto` module writers
"""
import os

def test_opendss_to_cyme(output_path):
    from ditto.readers.opendss.read import reader
    from ditto.store import Store 
    from ditto.writers.cyme.write import Writer 

    opendss_models=[f for f in os.listdir('./data/opendss/') if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = reader(master_file='./data/opendss/{model}/master.dss'.format(model=model),
                    buscoordinates_file='./data/opendss/{model}/buscoord.dss'.format(model=model))
        r.parse(m)
        m.set_names()
        #TODO: Log properly
        print('>OpenDSS model {model} red...'.format(model=model)) 
        w = Writer(output_path=output_path, log_path=output_path)
        w.write(m)
        #TODO: Log properly
        print('>...and written to CYME.\n')
