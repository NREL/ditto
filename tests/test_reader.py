# -*- coding: utf-8 -*-

"""
test_reader
----------------------------------

Tests for `ditto` module readers
"""
import os
import pytest as pt
from ditto.store import Store

current_directory = os.path.realpath(os.path.dirname(__file__))

gridlabd_models_dir = os.path.join(current_directory, 'data', 'gridlabd')
gridlabd_models = ['13node_simplified.glm',
                   '4node.glm']


@pt.mark.skip()
def test_gld_reader():
    from ditto.readers.gridlabd.read import Reader
    for modelfile in gridlabd_models:
        m = Store()
        r = Reader()
        r.parse(m, os.path.join(gridlabd_models_dir,modelfile))

def test_cyme_reader():
    '''
    TODO
    '''
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store
    cyme_models=[f for f in os.listdir(os.path.join(current_directory, 'data/cyme/')) if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(current_directory, 'data/cyme',model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} parsed.\n'.format(model=model))

@pt.mark.skip()
def test_opendss_reader():
    '''
    TODO
    '''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    opendss_models=[f for f in os.listdir(os.path.join(current_directory, 'data/opendss/')) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(master_file=os.path.join(current_directory, 'data/opendss',model,'master.dss'), buscoordinates_file=os.path.join(current_directory, './data/opendss',model,'buscoord.dss'))
        r.parse(m)
        #TODO: Log properly
        print('>OpenDSS model {model} parsed.\n'.format(model=model))

def test_dew_reader():
    '''
    TODO
    '''
    pass

