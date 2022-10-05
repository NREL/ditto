# -*- coding: utf-8 -*-

"""
test_reader
----------------------------------

Tests for `ditto` module readers
"""
import os
import pytest as pt
from ditto.store import Store
from ditto.models.load import Load

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_gld_reader():
    gridlabd_models_dir = os.path.join(
        current_directory, "data", "small_cases", "gridlabd"
    )
    gridlabd_models = [
        f for f in os.listdir(gridlabd_models_dir) if not f.startswith(".")
    ]
    from ditto.readers.gridlabd.read import Reader

    for model in gridlabd_models:
        m = Store()
        r = Reader(input_file=os.path.join(gridlabd_models_dir, model, "node.glm"))
        r.parse(m)


def test_cyme_reader():
    """
    TODO
    """
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store

    cyme_models_dir = os.path.join(current_directory, "data", "small_cases", "cyme")
    cyme_models = [f for f in os.listdir(cyme_models_dir) if not f.startswith(".")]
    for model in cyme_models:
        m = Store()
        r = Reader(data_folder_path=os.path.join(cyme_models_dir, model))
        r.parse(m)
        # TODO: Log properly
        print(">Cyme model {model} parsed.\n".format(model=model))

        if model == "ieee_13node":
            """ 
            test load base voltage values
            the load nominal voltages are set in the system_structure_modifier.set_nominal_voltages_recur
            (which is only used in the cyme reader)
            the test values are what is expected from the IEEE13 openDSS model
            issues: 
            - perhaps the default load.connection_type should by "Y"?
                - all connection_types are currently set to None in this test
            - currently the nominal voltages are set to the nominal_voltage of the upline transformer, 
                but the upline transformer nominal_voltage is (usu.) the phase to phase voltage
                which is not the correct voltage to use for single phase load connected between 
                phase and ground.
                - can we use Load and PhaseLoad attributes to correctly define the load.nominal_voltage?
            """
            for load in m.iter_models(Load):
                nphases = len(load.phase_loads)
                if load.connection_type in ("Y", None) and nphases == 1:
                    assert round(load.nominal_voltage, 3) in (2400, 277)
                if load.connection_type == "D":
                    assert round(load.nominal_voltage, 3) == 4160


# @pt.mark.skip("Segfault occurs")
def test_opendss_reader():
    """
    TODO
    """
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store

    opendss_models_dir = os.path.join(
        current_directory, "data", "small_cases", "opendss"
    )
    opendss_models = [
        f for f in os.listdir(opendss_models_dir) if not f.startswith(".")
    ]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(opendss_models_dir, model, "master.dss"),
            buscoordinates_file=os.path.join(opendss_models_dir, model, "buscoord.dss"),
        )
        r.parse(m)
        # TODO: Log properly
        print(">OpenDSS model {model} parsed.\n".format(model=model))

        if model == "ieee_13node":
            """ 
            test load base voltage values match expected values
            """
            for load in m.iter_models(Load):
                nphases = len(load.phase_loads)
                if load.connection_type in ("Y", None) and nphases == 1:
                    assert round(load.nominal_voltage, 3) in (2400, 277)
                if load.connection_type == "D":
                    assert round(load.nominal_voltage, 3) == 4160


def test_dew_reader():
    """
    TODO
    """
    pass
