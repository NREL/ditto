# -*- coding: utf-8 -*-

import os
import OpenDSS_function as OpenDSS
import time

#Import the Gridlab-D reader
from ditto.readers.gridlabd.read import Reader as Reader_glab
from ditto.readers.opendss.read import Reader as Reader_dss

#Import the OpenDSS writer
from ditto.writers.odo_tool.write import Writer as Writer_odo
from ditto.writers.opendss.write import Writer as Writer_dss

#Import Store
from ditto.store import Store
import json_tricks

def main():
    '''
    Conversion example of the IEEE 123 node system.
    Gridlab-D ---> OpenDSS example.
    This example uses the glm file located in tests/data/big_cases/gridlabd/ieee_123node
    '''

    #Path settings (assuming it is run from examples folder)
    #Change this if you wish to use another system
    path = r'C:\Users\rjain\Desktop\BoxSync\NMG\ditto_ODO\ditto\tests\IEEE_13_nodes_origin'

    #################################
    #  STEP 1: READ FROM GRIDLAB-D  #
    #################################
    #
    #Create a Store object
#    print('>>> Creating empty model...')
#    model = Store()
#
#    #Instanciate a GridLab-D Reader object
#    r = Reader_glab(input_file = os.path.join(path, 'The-1069-node-system.glm'))
#
#    #Parse (can take some time for large systems...)
#    print('>>> Reading from Gridlab-D...')
#    start = time.time() #basic timer
#    r.parse(model)
#    end = time.time()
#    print('...Done (in {} seconds'.format(end-start))
#
#    ##############################
#    #  STEP 2: WRITE TO OpenDSS  #
#    ##############################
#    #
#    #Instanciate a Writer object
#    #w = Writer(output_path = './')
#
#    #Write to OpenDSS (can also take some time for large systems...)
#    w = Writer_dss(output_path = './tests/IEEE_13_nodes_out/glab_out')
#
#    print('>>> Writing to OpenDSS...')    
#    start = time.time() #basic timer
#    w.write(model)
#    end = time.time()
#    print('...Done (in {} seconds'.format(end-start))

    
    
    #Create a Store object
    print('>>> Creating empty model...')
    m = Store()

    #Instanciate a OpenDSS Reader object
    r_dss = Reader_dss(master_file='./tests/IEEE_13_nodes_out/glab_out/Master.dss',bus_coordinates_file='./IEEE_13_nodes_origin/ReducedModel/BusCoords.dss')
    print('>>> Reading from OpenDSS...')
    start = time.time() #basic timer
    r_dss.parse(m, verbose=True)

    end = time.time()
    print('...Done (in {} seconds'.format(end-start))

    
    print('>>> Writing to ODO...')
    start = time.time() #basic timer
    
    baseMVA=10
    basekV=13.8
    
    odo_writer=Writer_odo(linecodes_flag=True, output_path='./IEEE_13_nodes_out', basekV=basekV, baseMVA=baseMVA)
    network = odo_writer.write(m, verbose=True)
#    network = odo_writer.write(model, verbose=True)

    end = time.time()


    #network['baseKV'] = 4.16
    #network['baseMVA'] = 10.0
    network['baseKV'] = basekV
    network['baseMVA'] = baseMVA
    network['per_unit'] = bool(1)
    network['multinetwork'] = bool(0)

    with open('network_glabd.json', 'w') as f:
        f.write(json_tricks.dumps(network,allow_nan=True, sort_keys=True, indent = 4))


    Modeldss = OpenDSS.OpenDSS()

    Modeldss.disable_forms()  # Turns off the window dialog boxes for progress bars and errors

    # compile and solve the given model file
    Modeldss.compile(r'C:\Users\rjain\Desktop\BoxSync\NMG\ditto_ODO\ditto\tests\IEEE_13_nodes_origin\master.dss')
    #Modeldss.compile(r'C:\Users\rjain\Desktop\BoxSync\NMG\ditto_ODO\ditto\tests\IEEE_13_nodes_origin\ReducedModel\Master.DSS')
    Modeldss.solve()

    # Get the bus dictionary from OpenDSS_function
    busV = Modeldss.get_buses()

    ## Parsing the bus voltages into a usable format
    busV_dict = {}

    for bus in range(len(busV)):

        bus_id = busV[bus]["name"]
        nodes = busV[bus]["nodes"]
        voltages = busV[bus]["voltages"]
        puVmag = busV[bus]["puVmag"]
        
        busV_dict[bus_id] = {}
        
        temp_varr = [0, 0, 0]
        temp_thetaarr = [0, 0, 0]
        temp_vminarr = [-1, -1, -1]
        
        theta = []
        
        # Calculate angles in radians as atan(Q/P)
        for elem in range(len(nodes)):
            theta.append(math.atan(voltages[2*elem + 1]/voltages[2*elem]))

        # Finalizing the respective vm, va, vmin values given the nodes present
        node_count = 0
        
        for node in nodes:
            temp_thetaarr[node-1] = theta[node_count]
            temp_varr[node-1] = puVmag[node_count]
            temp_vminarr[node-1] = 0.95
            
            node_count += 1
        

        busV_dict[bus_id]["nodes"] = nodes
        busV_dict[bus_id]["vmag"] = temp_varr
        busV_dict[bus_id]["vang"] = temp_thetaarr
        busV_dict[bus_id]["vmin"] = temp_vminarr
        
    for bus in network['bus'].keys():
        temp_bus = network['bus'][bus]["name"]
        
        network['bus'][bus]["vm"] = busV_dict[temp_bus]["vmag"] 
        network['bus'][bus]["va"] = busV_dict[temp_bus]["vang"] 
        network['bus'][bus]["vmin"] = busV_dict[temp_bus]["vmin"] 


    ## Getting the P, Q Solution
    circuit = Modeldss.engine.ActiveCircuit

    circuit.SetActiveElement("Vsource.SOURCE")

    PQsoln = circuit.ActiveElement.Powers

    PSoln = [-1*PQsoln[0]/(1000*network['baseMVA']), -1*PQsoln[2]/(1000*network['baseMVA']), -1*PQsoln[4]/(1000*network['baseMVA'])]
    QSoln = [-1*PQsoln[1]/(1000*network['baseMVA']), -1*PQsoln[3]/(1000*network['baseMVA']), -1*PQsoln[5]/(1000*network['baseMVA'])]

    for source in network['generator'].keys():
        if network['generator'][source]["name"] == "Vsource.source":
            network['generator'][source]["pg"] = PSoln
            network['generator'][source]["qg"] = QSoln
            break




    with open('network_13bus.json', 'w') as f:
        f.write(json_tricks.dumps(network,allow_nan=True, sort_keys=True, indent = 4))




    with open('network_glabd.json', 'w') as f:
        f.write(json_tricks.dumps(network,allow_nan=True, sort_keys=True, indent = 4))

    print('...Done (in {} seconds'.format(end-start))

if __name__ == '__main__':
    main()

