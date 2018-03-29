# -*- coding: utf-8 -*-

"""
test_cyme_to_opendss
----------------------------------

Tests for Cyme --> OpenDSS conversion
"""
import six

if six.PY2:
    from backports import tempfile
else:
    import tempfile
import os
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_cyme_to_opendss():
    '''
        Test the Cyme to OpenDSS conversion.
    '''
    list_of_directories = []
    from ditto.store import Store
    from ditto.readers.cyme.read import Reader
    from ditto.writers.opendss.write import Writer
    import opendssdirect as dss
    cyme_models=[f for f in os.listdir(os.path.join(current_directory, 'data/small_cases/cyme/')) if not f.startswith('.')]
    for model in cyme_models:
        print(model)
        m = Store()
        r = Reader(data_folder_path=os.path.join(current_directory, 'data/small_cases/cyme',model))
        r.parse(m)
        #TODO: Log properly
        # print('>Cyme model {model} read...'.format(model=model))
        output_path = tempfile.TemporaryDirectory()
        list_of_directories.append(output_path)
        w = Writer(output_path=output_path.name)
        w.write(m)
        #TODO: Log properly
        # print('>...and written to OpenDSS.\n')
        print(model)
        dss.run_command("clear")
        # dss.run_command('redirect {master}'.format(master=os.path.join(output_path,'master.dss')))
        # dss.run_command('Solve')
        #TODO: Log properly
        # print('>Circuit {model} solved.\n'.format(model=model))
