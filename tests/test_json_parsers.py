# -*- coding: utf-8 -*-

"""
test_JSON
----------------------------------

Tests for JSON parsers.
"""
import os
import six
import pytest as pt
from ditto.store import Store
if six.PY2:
    from backports import tempfile
else:
    import tempfile

current_directory = os.path.realpath(os.path.dirname(__file__))

def test_opendss_to_json():
    '''Test the JSON writer with OpenDSS models as input.'''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.json.write import Writer

    opendss_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/opendss/')) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
            buscoordinates_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
        )
        r.parse(m)
        m.set_names()
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=os.path.join(output_path.name,'test.json'))
        w.write(m)

def test_cyme_to_json():
    '''Test the JSON writer with CYME models as input.'''
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store
    from ditto.writers.json.write import Writer

    cyme_models=[f for f in os.listdir(os.path.join(current_directory, 'data/small_cases/cyme/')) if not f.startswith('.')]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(current_directory, 'data/small_cases/cyme',model))
        r.parse(m)
        m.set_names()
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=os.path.join(output_path.name,'test.json'))
        w.write(m)

def test_json_reader():
    '''Test the JSON reader.'''
    #TODO
    pass

def test_json_serialize_deserialize():
    '''Write a model to JSON, read it back in, and test that both models match.'''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.json.write import Writer
    from ditto.readers.json.read import Reader as json_reader

    opendss_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/opendss/')) if not f.startswith('.')]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
            buscoordinates_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
        )
        r.parse(m)
        m.set_names()
        w = Writer(output_path='./test.json')
        w.write(m)
        jr = json_reader(input_file='./test.json')
        jr.parse()
        assert m == jr.model
    os.remove('./test.json')
