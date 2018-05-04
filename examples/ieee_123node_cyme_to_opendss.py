# -*- coding: utf-8 -*-

import os
import time

#Import the CYME reader
from ditto.readers.cyme.read import Reader

#Import the OpenDSS writer
from ditto.writers.opendss.write import Writer

#Import Store
from ditto.store import Store

def main():
    '''
        Conversion example of the IEEE 123 node system.
        CYME ---> OpenDSS example.
        This example uses the glm file located in tests/data/big_cases/cyme/ieee_123node
    '''

    #Path settings (assuming it is run from examples folder)
    #Change this if you wish to use another system
    path = '../tests/data/big_cases/cyme/ieee_123node'

    ############################
    #  STEP 1: READ FROM CYME  #
    ############################
    #
    #Create a Store object
    print('>>> Creating empty model...')
    model = Store()

    #Instanciate a Reader object
    r = Reader(data_folder_path = path)

    #Parse (can take some time for large systems...)
    print('>>> Reading from CYME...')
    start = time.time() #basic timer
    r.parse(model)
    end = time.time()
    print('...Done (in {} seconds'.format(end-start))

    ##############################
    #  STEP 2: WRITE TO OpenDSS  #
    ##############################
    #
    #Instanciate a Writer object
    w = Writer(output_path = './')

    #Write to OpenDSS (can also take some time for large systems...)
    print('>>> Writing to OpenDSS...')
    start = time.time() #basic timer
    w.write(model)
    end = time.time()
    print('...Done (in {} seconds'.format(end-start))

if __name__ == '__main__':
    main()

