from ditto.store import Store
from ditto.readers.synergi.read import Reader as Synergi_Reader
from ditto.readers.opendss.read import Reader as OpenDSS_Reader
from ditto.readers.cyme.read import Reader as Cyme_Reader
from ditto.readers.gridlabd.read import Reader as Gridlabd_Reader
from ditto.writers.opendss.write import Writer as OpenDSS_Writer
from ditto.metrics.network_analysis import NetworkAnalyzer
import opendssdirect as dss
import os, shutil
import matplotlib.pyplot as plt

current_dir = os.path.realpath(os.path.dirname(__file__))
validation_dir = os.path.join(current_dir, "validation_outputs")
small_tests_dir = os.path.join(current_dir, "../../tests/data/small_cases")
small_tests = ["ieee_4node", "ieee_13node"]
for each_test in small_tests:
    case_dir = os.path.join(validation_dir, each_test)
    for dirname in os.listdir(small_tests_dir):
        output_dir = os.path.join(case_dir, dirname + "_output")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            os.mkdir(output_dir)
        test_path = os.path.join(small_tests_dir, dirname, each_test)
        m = Store()
        if dirname == "opendss":
            r1 = OpenDSS_Reader(master_file=os.path.join(test_path, "master.dss"))
            # elif dirname == "synergi":
            # r1 = Synergi_Reader(input_file=os.path.join(test_path, "network.mdb"))
            #    r1 = Synergi_Reader(input_file="ieee4node.mdb")
            print("Not for now")
        elif dirname == "cyme":
            r1 = Cyme_Reader(data_folder_path=os.path.join(test_path))
        elif dirname == "gridlabd":
            r1 = Gridlabd_Reader(input_file=os.path.join(test_path, "node.glm"))
        elif dirname == "cim":
            continue
        r1.parse(m)
        w1 = OpenDSS_Writer(output_path=output_dir)
        w1.write(m, separate_feeders=True)

    comp_values = {}
    for dir in os.listdir(case_dir):
        with open(os.path.join(case_dir, dir, "Master.dss"), "r") as rfile:
            filedata = rfile.read()
        filedata = filedata.replace("Solve", "Solve mode=faultstudy")
        with open(os.path.join(case_dir, dir, "Faultstudy_Master.dss"), "w") as file:
            file.write(filedata)

        dss.run_command(
            "Redirect {}".format(os.path.join(case_dir, dir, "Faultstudy_Master.dss"))
        )
        comp_values[dir] = {}
        for i in dss.Circuit.AllBusNames():
            dss.Circuit.SetActiveBus(i)
            comp_values[dir][dss.Bus.Name()] = dss.Bus.Zsc0() + dss.Bus.Zsc1()
