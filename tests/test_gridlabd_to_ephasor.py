# -*- coding: utf-8 -*-

"""
test_gridlabd_to_ephasor
----------------------------------

Tests for GridlabD --> Ephasor conversion
"""
import os
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

@pt.mark.skip() #currently not running...
def test_gridlabd_to_ephasor():
    '''
        Test the Gridlabd to Ephasor conversion.
    '''
    from ditto.readers.gridlabd.read import Reader
    from ditto.store import Store
    from ditto.writers.ephasor.write import Writer

    gridlabd_models=[f for f in os.listdir(os.path.join(current_directory,'data/gridlabd/')) if not f.startswith('.')]
    for model in gridlabd_models:
        m = Store()
        r = Reader(input_file=os.path.join(current_directory, "data/gridlabd/{model}/model.glm".format(model=model)))
        r.parse(m)
        #TODO: Log properly
        print('>GridlabD model {model} red...'.format(model=model))
        output_path = os.path.join(current_directory, "./")
        w = Writer(output_path="./")
        w.write(m)
        #TODO: Log properly
        print('>...and written to Ephasor.\n')