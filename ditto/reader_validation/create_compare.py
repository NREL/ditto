from ditto.store import Store
from ditto.readers.synergi.read import Reader as Synergi_Reader
from ditto.readers.opendss.read import Reader as OpenDSS_Reader
from ditto.readers.cyme.read import Reader as Cyme_Reader
from ditto.readers.gridlabd.read import Reader as Gridlabd_Reader
from ditto.writers.opendss.write import Writer as OpenDSS_Writer
import opendssdirect as dss
import os, shutil
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict


def create_output_dir(tests_dir):
    """Reading the input from every reader for each test case and creating the Opendss output."""
    # Creating output directory
    current_dir = os.path.realpath(os.path.dirname(__file__))
    validation_dir = os.path.join(current_dir, "validation_outputs")
    if os.path.exists(validation_dir):
        shutil.rmtree(validation_dir)
    for each in os.listdir(tests_dir):
        if each == "cim" or each == "demo":
            continue
        for dirname in os.listdir(os.path.join(tests_dir, each)):
            if dirname == "storage_test":
                continue
            output_dir = os.path.join(validation_dir, dirname, each + "_output")
            test_path = os.path.join(tests_dir, each, dirname)
            m = Store()
            if each == "opendss":
                r1 = OpenDSS_Reader(master_file=os.path.join(test_path, "master.dss"))
            elif each == "synergi":
                if dirname == "ieee_4node":
                    r1 = Synergi_Reader(
                        input_file=os.path.join(test_path, "network.mdb")
                    )
            elif each == "cyme":
                r1 = Cyme_Reader(data_folder_path=os.path.join(test_path))
            elif each == "gridlabd":
                r1 = Gridlabd_Reader(input_file=os.path.join(test_path, "node.glm"))
            r1.parse(m)
            w1 = OpenDSS_Writer(output_path=output_dir)
            w1.write(m, separate_feeders=True)
    return validation_dir


def create_dict(output_dir):
    """Do the fault study for each reader and create a dictonary which contains the sequence impedances for each node.
     These values are used for comparison of fault study of readers"""
    comp_values = defaultdict()
    for case_dir in os.listdir(output_dir):
        comp_values[case_dir] = defaultdict()
        for dir_name in os.listdir(os.path.join(output_dir, case_dir)):
            comp_values[case_dir][dir_name] = {}
            with open(
                os.path.join(output_dir, case_dir, dir_name, "Master.dss"), "r"
            ) as rfile:
                filedata = rfile.read()
            filedata = filedata.replace("Solve", "Solve mode=faultstudy")
            with open(
                os.path.join(output_dir, case_dir, dir_name, "Faultstudy_Master.dss"),
                "w",
            ) as file:
                file.write(filedata)

            dss.run_command(
                "Redirect {}".format(
                    os.path.join(
                        output_dir, case_dir, dir_name, "Faultstudy_Master.dss"
                    )
                )
            )
            for i in dss.Circuit.AllBusNames():
                dss.Circuit.SetActiveBus(i)
                comp_values[case_dir][dir_name][dss.Bus.Name()] = (
                    dss.Bus.Zsc0() + dss.Bus.Zsc1()
                )

    return comp_values
