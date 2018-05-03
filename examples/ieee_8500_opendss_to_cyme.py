# -*- coding: utf-8 -*-

import os
import time

#Import the OpenDSS reader
from ditto.readers.opendss.read import Reader

#Import the Cyme writer
from ditto.writers.cyme.write import Writer

#Import Store
from ditto.store import Store

def main():
    '''
        Conversion example of a relatively large test system: the IEEE 8500 node.
        OpenDSS ---> CYME example.
        This example uses the dss files located in tests/data/big_cases/opendss/ieee_8500node
    '''

    #Path settings (assuming it is run from examples folder)
    #Change this if you wish to use another system
    path = '../tests/data/big_cases/opendss/ieee_8500node'

    ###############################
    #  STEP 1: READ FROM OPENDSS  #
    ###############################
    #
    #Create a Store object
    print('>>> Creating empty model...')
    model = Store()

    #Instanciate a Reader object
    r = Reader(master_file = os.path.join(path, 'Master-unbal.dss'),
               buscoordinates_file = os.path.join(path, 'buscoord.dss'))

    #Parse (can take some time for large systems...)
    print('>>> Reading from OpenDSS...')
    start = time.time() #basic timer
    r.parse(model)
    end = time.time()
    print('...Done (in {} seconds'.format(end-start))

    ###########################
    #  STEP 2: WRITE TO CYME  #
    ###########################
    #
    #Instanciate a Writer object
    w = Writer(output_path = './')

    #Write to CYME (can also take some time for large systems...)
    print('>>> Writing to CYME...')
    start = time.time() #basic timer
    w.write(model)
    end = time.time()
    print('...Done (in {} seconds'.format(end-start))

if __name__ == '__main__':
    main()

