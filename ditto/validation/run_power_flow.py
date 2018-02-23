# coding: utf8

import os
import argparse
import opendssdirect as dss


def run_opendss_power_flow(path_to_master, path_to_export):
    '''Run OpenDSS power flow on given feeder.

.. note:: Rely on Opendssdirect.py

'''
    result = dss.dss_lib.DSSPut_Command('redirect {}master.dss'.format(path_to_master))
    if result != '':
        print('Unable to run {}master.dss'.format(path_to_master))
        return
    else:
        print('{}master.dss done.'.format(path_to_master))
    dss.dss_lib.DSSPut_Command('Export voltages {}voltage_profile.csv'.format(path_to_export))


def run_cyme_power_flow():
    '''Run CYME power flow on given feeder.

.. warning:: Not implemented

'''
    #Not implemented
    pass


def main():
    '''Run all requested power flows.

**Usage:**

$ python run_power_flow.py -f ieee_13_node -f ieee_123_node

This will run all power flow analysis on all possible feeder in the validation subfolder (inputs and outputs).
Since we can do this only in OpenDSS for now, this command will run on the following feeders:

    - ./inputs/opendss/ieee_13_node
    - ./inputs/opendss/ieee_123_node
    - ./outputs/from_*/to_opendss/ieee_13_node
    - ./outputs/from_*/to_opendss/ieee_123_node

.. note::

    - The way power flows are computed has to be implemented here.
    - For now, this is possible only in OpenDSS using OpenDSSdirect.py
    - Results are stored in the same folder as the feeder under the name "voltage_profile.csv"

'''
    #Parse the arguments
    parser = argparse.ArgumentParser()

    #Feeder list
    parser.add_argument('-f', action='append', dest='feeder_list', default=[])

    results = parser.parse_args()

    #If nothing is provided, run everything...
    if results.feeder_list == []:
        feeder_list = ['ieee_13_node', 'ieee_123_node']
    else:
        feeder_list = results.feeder_list

    #List of format on which we can run power flow
    available_formats_for_PF = ['opendss'] #Only possible to run power flows in OpenDSS for now...

    #Maps power flow function to format name
    power_flow_functions = {
        'opendss': run_opendss_power_flow
        #TO COMPLETE WITH OTHER SIMULATION TOOLS
    }

    #First, look for all paths for the requested feeder and for the format on which we can run power flows
    path_list = []
    format_list = next(os.walk('../readers'))[1]

    for formatt in available_formats_for_PF:
        for feeder in feeder_list:
            try:
                path_list.append('./inputs/{formatt}/{feeder}/'.format(formatt=formatt, feeder=feeder))
            except:
                pass
            for _from in format_list:
                if 'from_{}'.format(_from) in os.listdir('./outputs/'):
                    path_list.append('./outputs/from_{fromm}/to_{formatt}/{feeder}/'.format(fromm=_from, formatt=formatt, feeder=feeder))

    for path in path_list:
        if 'inputs' in path: _format = path.split('/')[2]
        if 'outputs' in path: _format = path.split('/')[3][3:]
        power_flow_functions[_format](path, path)


if __name__ == '__main__':
    main()
