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

def test_gld_reader():
    gridlabd_models_dir = os.path.join(current_directory, 'data', 'small_cases','gridlabd')
    gridlabd_models = ['123_node.glm','13node_simplified.glm',
                   '4node.glm']
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
    cyme_models_dir = os.path.join(current_directory, 'data', 'small_cases','cyme')
    cyme_models=[f for f in os.listdir(cyme_models_dir) if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(cyme_models_dir,model))
        r.parse(m)
        #TODO: Log properly
        print('>Cyme model {model} parsed.\n'.format(model=model))


@pt.mark.skip("Segfault occurs")
def test_opendss_reader():
    '''
    TODO
    '''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    opendss_models_dir = os.path.join(current_directory, 'data','small_cases','opendss')
    opendss_models=[f for f in os.listdir(opendss_models_dir) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(master_file=os.path.join(opendss_models_dir,model,'master.dss'), buscoordinates_file=os.path.join(opendss_models_dir,model,'buscoord.dss'))
        r.parse(m)
        #TODO: Log properly
        print('>OpenDSS model {model} parsed.\n'.format(model=model))

def test_dew_reader():
    '''
    TODO
    '''
    pass

