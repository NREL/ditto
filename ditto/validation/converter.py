# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

#Imports
import importlib
import os
import datetime
import traceback
from ditto.store import Store


class converter:
    '''Converter class. Use to convert from one format to another through DiTTo.

**Usage:**

>>> converter=converter(feeder_list, from_format, to_format, verbose)

:param feeder_list: List of feeder names
:type feeder_list: List[str]
:param from_format: Format to use as input
:type from_format: str
:param to_format: Format to use as ouput
:type to_format: str
:param verbose: Set verbose mode
:type verbose: bool

.. note::

    - Feeders should be located in ./inputs/{from_format}/{feeder_name}
    - Output will be located in ./outputs/{from_format}/{to_format}/{feeder_name}
    - Readers should be located in ditto/reader/{from_format}/read.py
    - Writers should be located in ditto/writers/{to_format}/write.py

.. warnings::

    - Names should be consistent (be carefull with lower/upper case...)
    - Readers should have a parse method responsible for parsing and a consistent constructor
    - Writers should have a write method responsible for parsing and a consistent constructor

Author: Nicolas Gensollen. October 2017

'''

    def __init__(self, feeder_list, from_format, to_format, verbose=True):
        '''Converter class CONSTRUCTOR.

'''
        #ATHORIZED FORMAT
        #
        #We authorized everything in ditto/readers for readers
        #and everything in ditto/writers for writers
        try:
            authorized_format_reader = next(os.walk('../readers'))[1] #Carefull, relative path...
        except:
            raise ValueError('Unable to get reader format list in ../readers')

        try:
            authorized_format_writer = next(os.walk('../writers'))[1] #Carefull, relative path...
        except:
            raise ValueError('Unable to get writer format list in ../writers')

        #FROM_FORMAT
        #
        #Check that from_format is known
        if from_format not in authorized_format_reader:
            raise ValueError('Unknown format {}'.format(from_format))
        else:
            #Import the right reader
            try:
                self.reader_class = importlib.import_module('ditto.readers.{format}.read'.format(format=from_format))
            except:
                traceback.print_exc()
                raise ValueError('Unable to import ditto.reader.{format}.read'.format(format=from_format))
            self._from = from_format

        #TO_FORMAT
        #
        #Check that to_format is known
        if to_format not in authorized_format_writer:
            raise ValueError('Unknown format {}'.format(to_format))
        else:
            #Import the right writer
            try:
                self.writer_class = importlib.import_module('ditto.writers.{format}.write'.format(format=to_format))
            except:
                traceback.print_exc()
                raise ValueError('Unable to import ditto.writers.{format}.write'.format(format=to_format))
            self._to = to_format

        self.feeder_list = feeder_list

        self.verbose = verbose

        #Create a store object
        try:
            self.m = Store()
        except:
            raise ValueError('Unable to create Store object.')

        #Set time format for log files
        self.time_format = '%H_%M_%d_%m_%Y'

    def get_inputs(self, feeder):
        '''Configure Inputs.

'''
        #Inputs are different accross the format:
        #
        #OpenDSS
        #
        if self._from == 'opendss':
            inputs = {
                'master_file': './inputs/{format}/{feeder}/master.dss'.format(format=self._from, feeder=feeder),
                'buscoordinates_file': './inputs/{format}/{feeder}/buscoords.dss'.format(format=self._from, feeder=feeder),
            }

        #CYME
        #
        elif self._from == 'cyme':
            inputs = {
                'data_folder_path': './inputs/{format}/{feeder}/'.format(format=self._from, feeder=feeder),
                'network_filename': 'network.txt',
                'equipment_filename': 'equipment.txt',
                'load_filename': 'loads.txt'
            }

        #GRIDLABD
        #
        elif self._from == 'gridlabd':
            inputs = {'input_file': './inputs/{format}/{feeder}/{feeder}.glm'.format(format=self._from, feeder=feeder)}

        #DEW
        #
        elif self._from == 'dew':
            inputs = {
                'input_file_path': './inputs/{format}/{feeder}/{feeder}.dew'.format(format=self._from, feeder=feeder),
                'databasepath': '../readers/dew/DataBase/DataBase.xlsx'
            }

        else:
            raise NotImplementedError('Format {} not imlemented.'.format(self._from))

        #Add log information
        log_path = './logs/reader/{format}/{feeder}/'.format(format=self._from, feeder=feeder)

        #If log path does not exist, create it
        if not os.path.exists(log_path):
            self.build_path(log_path)

        #Add filename to the log path
        log_path += '/log_{time}.log'.format(time=self.current_time_string)

        inputs.update({'log_file': log_path})

        return inputs

    def build_path(self, path):
        '''Take a path as input and check that all folders exists as in the path.
If folders are missing, they are created.

.. warning:: Expects a path in the form './folder1/folder2/folder3/'

'''
        #First we need to get all the directories in the given path
        dirs = path.split('/')

        #Loop over the directories and check for existance
        for k, _dir in enumerate(dirs):
            if k != 0:
                _tmp = reduce(lambda x, y: x + '/' + y, dirs[:k])
                if not os.path.exists(_tmp):
                    os.makedirs(_tmp)

        #Test that path exists
        if not os.path.exists(path):
            raise ValueError('Unable to create path {path}'.format(path=path))

    def get_output(self, feeder):
        '''Configure outputs.

'''
        output_path = './outputs/from_{format_from}/to_{format_to}/{feeder}/'.format(format_from=self._from, format_to=self._to, feeder=feeder)
        #If path does not exist yet, create it
        if not os.path.exists(output_path):
            self.build_path(output_path)

        #Add log information
        log_path = './logs/writer/{format}/{feeder}/'.format(format=self._to, feeder=feeder)

        #If log path does not exist, create it
        if not os.path.exists(log_path):
            self.build_path(log_path)

        #Add filename to log path\
        log_path += '/log_{time}.log'.format(time=self.current_time_string)

        return {'output_path': output_path, 'log_file': log_path}

    def configure_reader(self, inputs):
        '''Configure the reader.

'''
        try:
            self.reader = self.reader_class.reader(**inputs)
        except:
            traceback.print_exc()
            raise ValueError('Unable to instanciate reader.')

    def configure_writer(self, output):
        '''Configure the writer.

'''
        try:
            self.writer = self.writer_class.writer(**output)
        except:
            traceback.print_exc()
            raise ValueError('Unable to instanciate writer.')

    def convert(self):
        '''Run the conversion: from_format--->DiTTo--->to_format on all the feeders in feeder_list.

'''
        #Get the time for the log files (all log files created during the same call to convert()
        #will have the same timestamp which makes it easier to analyse them later)
        self.current_time_string = datetime.datetime.now().strftime(self.time_format)

        for feeder in self.feeder_list:

            if self.verbose:
                print('*' * 60)
                print(feeder)
                print('*' * 60)

            if feeder in os.listdir('./inputs/{format}/'.format(format=self._from)):

                inputs = self.get_inputs(feeder)

                self.configure_reader(inputs)

                output = self.get_output(feeder)

                self.configure_writer(output)

                self.reader.parse(self.m)

                self.writer.write(self.m, verbose=self.verbose)

            else:
                print('Input files not available for feeder {feeder} and format {format}'.format(feeder=feeder, format=self._from))
                print('Skip...')
