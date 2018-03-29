# -*- coding: utf-8 -*-

"""
test_cyme_to_ephasor
----------------------------------

Tests for Cyme --> Ephasor conversion
"""
import os

import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

def test_cyme_to_ephasor():
    '''
        Test the Cyme to Ephasor conversion.
    '''
    from ditto.store import Store
    from ditto.readers.cyme.read import Reader
    from ditto.writers.ephasor.write import Writer

    cyme_models=[f for f in os.listdir(os.path.join(current_directory, 'data/small_cases/cyme/')) if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(current_directory, 'data/small_cases/cyme',model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} red...'.format(model=model))
        w = Writer()
        w.write(m)
        #TODO: Log properly
        print('>...and written to Ephasor.\n')
