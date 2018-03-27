# -*- coding: utf-8 -*-

"""
test_cyme_to_gridlabd
----------------------------------

Tests for Cyme --> Gridlabd conversion
"""
import os

import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

def test_cyme_to_gridlabd():
    '''
        Test the Cyme to GridlabD conversion.
    '''
    from ditto.store import Store
    from ditto.readers.cyme.read import Reader
    from ditto.writers.gridlabd.write import Writer

    cyme_models=[f for f in os.listdir(os.path.join(current_directory, 'data/cyme/')) if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(current_directory, 'data/cyme',model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} read...'.format(model=model))
        w = Writer()
        w.write(m)
        #TODO: Log properly
        print('>...and written to GridLabD.\n')

    for i in os.listdir(os.path.join(current_directory, "./")):
        if i.endswith(".glm"):
            try:
                os.remove(os.path.join(os.path.join(current_directory, "./"), i))
            except:
                pass