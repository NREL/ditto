# -*- coding: utf-8 -*-

"""
test_cyme_to_gridlabd
----------------------------------

Test the Cyme to GridlabD conversion.
"""
import os

def test_cyme_to_gridlabd():
    '''
        Test the Cyme to GridlabD conversion.
    '''
    from ditto.store import Store
    from ditto.readers.cyme.read import reader as Reader
    from ditto.writers.gridlabd.write import writer as Writer 

    cyme_models=[f for f in os.listdir('./data/cyme/') if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join('./data/cyme',model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} red...'.format(model=model)) 
        w = Writer()
        w.write(m)
        #TODO: Log properly
        print('>...and written to GridLabD.\n')

