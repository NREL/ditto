# -*- coding: utf-8 -*-

"""
test_metric_extraction
----------------------------------

Tests the metric extraction capability of DiTTo
"""
import logging
import os

import six

import tempfile
import pytest
import pytest as pt

current_directory = os.path.realpath(os.path.dirname(__file__))

logger = logging.getLogger(__name__)

def test_metric_extraction():
    '''
        This test reads all small OpenDSS test cases, set the nominal voltages using a 
        system_structure_modifier object and compute all metrics using a network analyzer object. 
        Finally, it exports the metrics to excel and Json formats.
    '''
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.modify.system_structure import system_structure_modifier
    from ditto.metrics.network_analysis import network_analyzer

    opendss_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/opendss/')) if not f.startswith('.')]
    opendss_models.remove('storage_test')

    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
            buscoordinates_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
        )
        r.parse(m)
        m.set_names()

        #Create a modifier object
        modifier = system_structure_modifier(m)

        #And set the nominal voltages of the elements since we don't have it from OpenDSS
        modifier.set_nominal_voltages_recur()
        modifier.set_nominal_voltages_recur_line()

        #Create a Network analyszer object with the modified model
        net = network_analyzer(modifier.model)
        net.model.set_names()

        #Compute all the available metrics
        net.compute_all_metrics()

        output_path = tempfile.gettempdir()

        #Export them to excel
        net.export(os.path.join(output_path,'metrics.xlsx'))

        #Export them to JSON
        net.export_json(os.path.join(output_path,'metrics.json'))