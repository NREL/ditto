# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

#Python import
import math
import sys
import os
import json
import numpy as np
import logging
import time

#OpenDSSdirect import
import opendssdirect as dss

#Ditto imports
from ditto.readers.abstract_reader import abstract_reader
from ditto.store import Store
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.power_source import PowerSource
from ditto.models.position import Position

from ditto.models.feeder_metadata import Feeder_metadata

from ditto.models.base import Unicode


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts))
        return result

    return timed


class reader(abstract_reader):
    '''OpenDSS--->DiTTo reader class.
Use to read and parse an OpenDSS circuit model to DiTTo.

:param log_file: Name/path of the log file. Optional. Default='./OpenDSS_reader.log'
:type log_file: str

**Constructor:**

>>> my_reader=Reader(log_file='./logs/my_log.log')

.. warning::

    The reader uses OpenDSSDirect heavily. <https://github.com/NREL/OpenDSSDirect.py>
    For more information on this package contact Dheepak Krishnamurthy.

'''

    def __init__(self, **kwargs):
        '''Constructor for the OpenDSS reader.

'''
        #Call super
        abstract_reader.__init__(self, **kwargs)

        self.DSS_file_names = {}

        if 'master_file' in kwargs:
            self.DSS_file_names['master'] = kwargs['master_file']
        else:
            self.DSS_file_names['master'] = './master.dss'

        if 'buscoordinates_file' in kwargs:
            self.DSS_file_names['Nodes'] = kwargs['buscoordinates_file']
        else:
            self.DSS_file_names['Nodes'] = './buscoords.dss'

        #self.DSS_file_names={'Nodes': 'buscoords.dss',
        #                     'master': 'master.dss'}

        self.is_opendssdirect_built = False
        self.all_object_names = []
        self.logger.info('OpenDSS--->DiTTo reader instanciated')

    def set_dss_file_names(self, new_names):
        '''Specify the path to some required DSS files.
Because the reader is relying on OpenDSSdirect, we only need the path to the master file and the path to the bus coordinates file.

:param new_names: dictionary with file names: {'Nodes': path_to_file, 'master': path_to_file}
:type new_names: dict
:returns: 1 for sucess, -1 for failure.
:rtype: int

'''
        if not isinstance(new_names, dict):
            self.logger.error('set_dss_file_names() expects a dictionary')
            return -1
        for key, value in new_names.items():
            if key not in ['Nodes', 'master']:
                return -1
            self.DSS_file_names[key] = value
        return 1

    def function(self, string):
        '''Execture the OpenDSS command passed as a string.
Log an error if the commanf cannot be runned.

:param string: String of the OpenDSS command to execute (ex: 'New Transformer.T1 ...')
:type string: str

'''
        try:
            return dss.dss_lib.DSSPut_Command(string.encode('ascii')).decode('ascii')
        except:
            self.logger.error('Unable to execute the following command: \n' + string)

    def phase_mapping(self, dss_phase):
        '''Map the phases of OpenDSS (1, 2, or 3) into DiTTo phases ('A', 'B', or 'C').

**Phase mapping:**

+---------------+-------------+
| OpenDSS phase | DiTTo phase |
+===============+=============+
|    1 or '1'   |     'A'     |
+---------------+-------------+
|    2 or '2'   |     'B'     |
+---------------+-------------+
|    3 or '3'   |     'C'     |
+---------------+-------------+

:param dss_phase: Phase number in OpenDSS format
:type dss_phase: int or str
:returns: Phase in DiTTo format
:rtype: str

.. note:: The function accepts both integers and strings as input (1 or '1' for example).

'''
        #Also make sure that if a phase is already in DiTTo format it does not return a None instead...
        if dss_phase == 1 or dss_phase == '1' or dss_phase == 'A':
            return 'A'
        if dss_phase == 2 or dss_phase == '2' or dss_phase == 'B':
            return 'B'
        if dss_phase == 3 or dss_phase == '3' or dss_phase == 'C':
            return 'C'
        return None

    @timeit
    def build_opendssdirect(self, master_dss_file):
        '''Uses OpenDSSDirect to run the master DSS file.

:param master_dss_file: Path to DSS file responsible for creating the circuit and loading all the OpenDSS objects. (Usually, it looks like a serie of redirect commands).
:type master_dss_file: str
:returns: 1 for success, -1 for failure.
:rtype: int

..note:: After running this function, all circuit elements can be accessed through the openDSSDirect api.

.. warning:: Calling this function before parsing is required.

'''
        self.logger.info('Reading DSS file {name}...'.format(name=master_dss_file))

        try:
            self.function('redirect {master_file}'.format(master_file=master_dss_file))
        except:
            self.logger.error('Unable to redirect master file: {filename}'.format(filename=master_dss_file))
            return -1

        self.is_opendssdirect_built = True

        #Disable Pandas such that we deal only with dictionaries
        #This remove one dependancy
        self.logger.info('Turning off pandas in OpenDSSdirect.')
        dss.utils.is_pandas_installed = False

        self.logger.info('build_opendssdirect succesful')

        return 1

    def parse(self, model, **kwargs):
        '''General parse function.
Responsible for calling the sub-parsers and logging progress.

:param model: DiTTo model
:type model: DiTTo model
:param verbose: Set verbose mode. Optional. Default=False
:type verbose: bool
:returns: 1 for success, -1 for failure
:rtype: int

'''
        start = time.time()
        #In order to parse, we need that opendssdirect was previously run
        if not self.is_opendssdirect_built:
            self.build_opendssdirect(self.DSS_file_names['master'])
            #self.logger.error('Trying to parse before building opendssdirect.')
            #return -1
        end = time.time()
        print('Build OpenDSSdirect= {}'.format(end - start))

        if 'feeder_file' in kwargs:
            self.feeder_file = kwargs['feeder_file']
            self.parse_feeder_metadata(model)

        read_power_source = True
        if 'read_power_source' in kwargs:
            read_power_source = kwargs['read_power_source']
        if read_power_source:
            self.parse_power_source(model) #TODO: push this to abstract reader once power source parsing is stable...

        #Call parse from abstract reader class
        abstract_reader.parse(self, model, **kwargs)

        return 1

    def parse_feeder_metadata(self, model):
        with open(self.feeder_file, 'r') as f:
            lines = f.readlines()
        feeders = {}
        substations = {}
        substation_transformers = {}
        for line in lines[1:]:
            node, sub, feed, sub_trans = list(map(lambda x: x.strip(), line.split(' ')))
            if not feed in feeders:
                feeders[feed] = [node.lower().replace('.', '')]
            else:
                feeders[feed].append(node.lower().replace('.', ''))
            if not feed in substations:
                substations[feed] = sub.lower().replace('.', '')
            if not feed in substation_transformers:
                substation_transformers[feed] = sub.lower().replace('.', '')

        for f_name, f_data in feeders.items():
            api_feeder_metadata = Feeder_metadata(model)
            api_feeder_metadata.name = f_name
            if f_name in substation_transformers:
                api_feeder_metadata.transformer = substation_transformers[f_name]
            if f_name in substations:
                api_feeder_metadata.substation = substations[f_name]

    @timeit
    def parse_power_source(self, model, **kwargs):
        '''Power source parser.

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        sources = dss.utils.class_to_dataframe('Vsource')

        for source_name, source_data in sources.items():

            #Instanciate DiTTo PowerSource object
            try:
                api_power_source = PowerSource(model)
            except:
                continue

            #Set the name of the source
            try:
                api_power_source.name = source_name
            except:
                pass

            #Set the nominal voltage of the source
            try:
                api_power_source.nominal_voltage = float(source_data['basekv']) * 10**3 #DiTTo in volts
            except:
                pass

            #Set the source_bus flag to True
            try:
                api_power_source.is_sourcebus = 1 #We have an external power source here
            except:
                pass

            #Set the rated power of the source
            try:
                api_power_source.rated_power = float(source_data['baseMVA']) * 10**6
            except:
                pass

            #Set the emergency power of the source
            try:
                api_power_source.emergency_power = float(source_data['MVAsc3']) * 10**6
            except:
                pass

            #Zero sequence impedance
            if 'Z0' in source_data and isinstance(source_data['Z0'], list):
                if len(source_data['Z0']) == 2:
                    try:
                        api_power_source.zero_sequence_impedance = complex(float(source_data['Z0'][0]), float(source_data['Z0'][1]))
                    except:
                        pass
            elif 'R0' in source_data and source_data['R0'] != '' and 'X0' in source_data and source_data['X0'] != '':
                try:
                    api_power_source.zero_sequence_impedance = complex(float(source_data['R0']), float(source_data['X0']))
                except:
                    pass

            #Positive sequence impedance
            if 'Z1' in source_data and isinstance(source_data['Z1'], list):
                if len(source_data['Z1']) == 2:
                    try:
                        api_power_source.positive_sequence_impedance = complex(float(source_data['Z1'][0]), float(source_data['Z1'][1]))
                    except:
                        pass
            elif 'R1' in source_data and source_data['R1'] != '' and 'X1' in source_data and source_data['X1'] != '':
                try:
                    api_power_source.positive_sequence_impedance = complex(float(source_data['R1']), float(source_data['X1']))
                except:
                    pass

            #Phase angle
            try:
                api_power_source.phase_angle = float(source_data['angle'])
            except:
                pass

            try:
                if '.' in source_data['bus1']:
                    api_power_source.connecting_element = source_data['bus1'].split('.')[0]
                else:
                    api_power_source.connecting_element = source_data['bus1']
            except:
                pass

        return 1

    @timeit
    def parse_nodes(self, model, **kwargs):
        '''Node parser.

:param model: DiTTo model
:type model: DiTTo model
:param coordinates_delimiter: The character that delimites the fieds in the coordinates file. Optional. Default=','
:type coordinates_delimiter: str
:returns: 1 for success, -1 for failure
:rtype: int

.. note:: This function is a bit different from the other parsers. To get the bus coordinates, it has to read and parse the coordinates file.

.. note:: There is currently no easy way to get the bus data in OpenDSSdirect yet. To get the phase numbers, we loop over the lines and extract the phases from the two end buses.

'''
        #Get the coordinate file
        self.bus_coord_file = self.DSS_file_names['Nodes']

        #Get the delimiter
        if 'coordinates_delimiter' in kwargs and isinstance(kwargs['coordinates_delimiter'], str):
            self.coordinates_delimiter = kwargs['coordinates_delimiter']
        else:
            self.coordinates_delimiter = ','

        with open(self.bus_coord_file, 'r') as g:
            coordinates = g.readlines()

        buses = {}
        for line in coordinates:

            try:
                name, X, Y = list(map(lambda x: x.strip(), line.split(self.coordinates_delimiter)))
                name = name.lower()
            except:
                self.logger.warning('Could not parse line : ' + str(line))
                name = None
                X = None
                Y = None
                pass

            try:
                X = float(X)
                Y = float(Y)
            except:
                self.logger.warning('Could not cast coordinates {X}, {Y} for bus {name}'.format(X=X, Y=Y, name=name))
                pass

            if not name in buses:
                buses[name] = {}
                buses[name]['positions'] = [X, Y]
                if name not in self.all_object_names:
                    self.all_object_names.append(name)
                else:
                    self.logger.warning('Duplicate object Node {name}'.format(name=name))
            else:
                buses[name]['positions'] = [X, Y]

        #Extract the line data
        lines = dss.utils.class_to_dataframe('line')

        #Loop over the lines to get the phases
        for name, data in lines.items():

            #Parse bus1 data
            if '.' in data['bus1']:
                temp = data['bus1'].split('.')
                b1_name = temp[0].strip()
                b1_phases = list(map(lambda x: int(x), temp[1:]))
            elif data['phases'] == '3':
                b1_name = data['bus1'].strip()
                b1_phases = [1, 2, 3]
            else:
                b1_name = None
                b1_phases = None

            #Parse bus2 data
            if '.' in data['bus2']:
                temp = data['bus2'].split('.')
                b2_name = temp[0].strip()
                b2_phases = list(map(lambda x: int(x), temp[1:]))
            elif data['phases'] == '3':
                b2_name = data['bus2'].strip()
                b2_phases = [1, 2, 3]
            else:
                b2_name = None
                b2_phases = None

            #Update the buses dictionary
            if b1_name is not None and not b1_name in buses:
                if b1_name not in self.all_object_names:
                    self.all_object_names.append(b1_name)
                else:
                    self.logger.warning('Duplicate object Node {name}'.format(name=b1_name))
                buses[b1_name] = {}
                buses[b1_name]['positions'] = None
                buses[b1_name]['phases'] = b1_phases
            elif not 'phases' in buses[b1_name]:
                buses[b1_name]['phases'] = b1_phases
            else:
                buses[b1_name]['phases'] += b1_phases
                buses[b1_name]['phases'] = np.unique(buses[b1_name]['phases']).tolist()

            #Update the buses dictionary
            if b2_name is not None and not b2_name in buses:
                if b2_name not in self.all_object_names:
                    self.all_object_names.append(b2_name)
                else:
                    self.logger.warning('Duplicate object Node {name}'.format(name=b2_name))
                buses[b2_name] = {}
                buses[b2_name]['positions'] = None
                buses[b2_name]['phases'] = b2_phases
            elif not 'phases' in buses[b2_name]:
                buses[b2_name]['phases'] = b2_phases
            else:
                buses[b2_name]['phases'] += b2_phases
                buses[b2_name]['phases'] = np.unique(buses[b2_name]['phases']).tolist()

        #Extract the load data
        loads = dss.utils.class_to_dataframe('load')
        #Loop over the loads to get the phases
        for name, data in loads.items():
            #Parse bus1 data
            if '.' in data['bus1']:
                temp = data['bus1'].split('.')
                b1_name = temp[0].strip()
                b1_phases = list(map(lambda x: int(x), temp[1:]))
            elif data['phases'] == '3':
                b1_name = data['bus1'].strip()
                b1_phases = [1, 2, 3]
            else:
                b1_name = None
                b1_phases = None
            #Update the buses dictionary
            if b1_name is not None and not b1_name in buses:
                if b1_name not in self.all_object_names:
                    self.all_object_names.append(b1_name)
                else:
                    self.logger.warning('Duplicate object Node {name}'.format(name=b1_name))
                buses[b1_name] = {}
                buses[b1_name]['positions'] = None
                buses[b1_name]['phases'] = b1_phases
            elif not 'phases' in buses[b1_name]:
                buses[b1_name]['phases'] = b1_phases
            else:
                buses[b1_name]['phases'] += b1_phases
                buses[b1_name]['phases'] = np.unique(buses[b1_name]['phases']).tolist()

        self._nodes = []

        #Loop over the dictionary of nodes and create the DiTTo Node objects
        for name, data in buses.items():

            api_node = Node(model)

            try:
                api_node.name = name
            except:
                pass

            try:
                node_pos = Position(model)
                node_pos.long = data['positions'][0]
                node_pos.lat = data['positions'][1]
                api_node.positions.append(node_pos)
            except:
                pass

            try:
                api_node.phases = list(map(lambda x: Unicode(self.phase_mapping(x)), data['phases']))
            except:
                pass

            self._nodes.append(api_node)

        return 1

    #@timeit
    def parse_lines(self, model):
        '''Line parser.

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        #In order to parse, we need that opendssdirect was previously run
        if not self.is_opendssdirect_built:
            self.build_opendssdirect(self.DSS_file_names['master'])

        #In OpenDSS, fuses are attached to line objects
        #Here, we get all the line names which have a fuse
        fuses = dss.utils.class_to_dataframe('Fuse')
        fuses_names = [d['MonitoredObj'][0].lower().split('.')[1] for name, d in fuses.items()]

        #In the same way, reclosers are also attached to line objects
        reclosers = dss.utils.class_to_dataframe('recloser')
        reclosers_names = [d['MonitoredObj'][0].lower().split('.')[1] for name, d in reclosers.items()]

        start = time.time()
        lines = dss.utils.class_to_dataframe('Line')

        middle = time.time()
        print('Line class to dataframe= {}'.format(middle - start))

        N_lines = len(lines)
        self._lines = []

        for name, data in lines.items():

            api_line = Line(model)
            api_line.name = None
            api_line.nominal_voltage = None #Not mapped
            api_line.line_type = None #Not mapped
            api_line.length = None
            api_line.from_element = None
            api_line.to_element = None
            api_line.is_fuse = None #Not mapped
            api_line.is_banked = None #Not mapped
            api_line.is_switch = None
            api_line.faultrate = None
            api_line.positions = None #Not mapped
            api_line.impedance_matrix = None
            api_line.capacitance_matrix = None

            #Name
            try:
                line_name = name.split('ine.')[1].lower()
                if line_name not in self.all_object_names:
                    self.all_object_names.append(line_name)
                else:
                    self.logger.warning('Duplicate object Line {name}'.format(name=line_name))
                api_line.name = line_name
            except:
                pass

            #Get the linecode if provided
            try:
                linecode = data['linecode']
            except:
                linecode = None

            #Based on naming convention.
            #TODO: Find a cleaner way to get this information
            if 'OH' in linecode:
                api_line.line_type = 'overhead'
            else:
                api_line.line_type = 'underground'

            #If we have a valid linecode, try to get the data
            if linecode is not None:
                linecodes = dss.utils.class_to_dataframe('linecode')
                if 'linecode.' + linecode.lower() in linecodes:
                    linecode_data = linecodes['linecode.' + linecode.lower()]
                else:
                    linecode_data = None
            else:
                linecode_data = None

            #Get the distance unit if provided
            try:
                line_unit = data['units']
            except:
                try:
                    line_unit = linecode_data['units']
                except:
                    self.logger.warning('Could not find the distance unit for line {name}. Using feet instead...'.format(name=name))
                    line_unit = u'ft'
                    pass
                pass

            if line_unit.lower() not in ['ft', 'mi', 'm', 'km', 'kft', 'cm', 'in']:
                line_unit = u'ft'

            #length
            try:
                length = float(data['length'])
                api_line.length = self.convert_to_meters(length, line_unit)
            except:
                pass

            phases_bus1 = []
            #from_element
            try:
                if '.' in data['bus1']:
                    temp = data['bus1'].split('.')
                    api_line.from_element = temp[0]
                    phases_bus1 = list(map(int, temp[1:]))
                else:
                    api_line.from_element = data['bus1'].strip()
                    phases_bus1 = [1, 2, 3]
            except:
                pass

            phases_bus2 = []
            #to_element
            try:
                if '.' in data['bus2']:
                    temp = data['bus2'].split('.')
                    api_line.to_element = temp[0]
                    phases_bus2 = list(map(int, temp[1:]))
                else:
                    api_line.to_element = data['bus2'].strip()
                    phases_bus2 = [1, 2, 3]
            except:
                pass

            if phases_bus1 != phases_bus2:
                self.logger.warning('Phases do not match for line {name}. Bus1={b1}. Bus2={b2}'.format(name=name, b1=data['bus1'], b2=data['bus2']))

            #is_switch
            #try:
            #    api_line.is_switch=int(data['Switch'])
            #except:
            #    pass

            #is_fuse
            if line_name in fuses_names:
                api_line.is_fuse = 1
            #is_recloser
            elif line_name in reclosers_names or 'recloser' in line_name:
                api_line.is_recloser = 1
            elif 'breaker' in line_name:
                api_line.is_breaker = 1
            elif 'Switch' in data and data['Switch']:
                api_line.is_switch = 1

            #faultrate
            if 'faultrate' in data:
                try:
                    api_line.faultrate = float(data['faultrate'])
                except:
                    pass
            elif linecode_data is not None and 'faultrate' in linecode_data:
                try:
                    api_line.faultrate = float(linecode_data['faultrate'])
                except:
                    pass

            #impedance_matrix
            #We have the Rmatrix and Xmatrix
            if 'rmatrix' in data and 'xmatrix' in data:
                Rmatrix = data['rmatrix']
                Xmatrix = data['xmatrix']
            elif 'rmatrix' in linecode_data and 'xmatrix' in linecode_data:
                Rmatrix = linecode_data['rmatrix']
                Xmatrix = linecode_data['xmatrix']
            else:
                Rmatrix = None
                Xmatrix = None

            #Matrices are in Ohms per some unit distance which is the unit defined in the line
            if line_unit is not None and Rmatrix is not None and Xmatrix is not None:
                try:
                    if isinstance(Rmatrix, list) and len(Rmatrix) == 1 and '|' in Rmatrix[0]:
                        rowsR = Rmatrix[0].split('|')
                        rowsR = list(map(lambda x: x.strip(), rowsR))
                        new_Rmatrix = []
                        for rowR in rowsR:
                            new_Rmatrix.append([])
                            new_Rmatrix[-1] += list(map(lambda x: self.convert_to_meters(float(x.strip()), line_unit, inverse=True), rowR.split(' ')))
                        new_Rmatrix = self.symmetrize(new_Rmatrix)
                    else:
                        new_Rmatrix = list(map(lambda x: self.convert_to_meters(float(x), line_unit, inverse=True), Rmatrix))

                    if isinstance(Xmatrix, list) and len(Xmatrix) == 1 and '|' in Xmatrix[0]:
                        rowsX = Xmatrix[0].split('|')
                        rowsX = list(map(lambda x: x.strip(), rowsX))
                        new_Xmatrix = []
                        for rowX in rowsX:
                            new_Xmatrix.append([])
                            new_Xmatrix[-1] += list(map(lambda x: self.convert_to_meters(float(x.strip()), line_unit, inverse=True), rowX.split(' ')))
                        new_Xmatrix = self.symmetrize(new_Xmatrix)
                    else:
                        new_Xmatrix = list(map(lambda x: self.convert_to_meters(float(x), line_unit, inverse=True), Xmatrix))

                    new_Rmatrix = np.array(new_Rmatrix)
                    new_Xmatrix = np.array(new_Xmatrix)
                    Z = new_Rmatrix + 1j * new_Xmatrix
                    if Z.ndim == 1:
                        Z = [Z.tolist()]
                    else:
                        Z = Z.tolist()
                    api_line.impedance_matrix = Z
                except:
                    pass

            if 'cmatrix' in data:
                Cmatrix = data['cmatrix']
            elif 'cmatrix' in linecode_data:
                Cmatrix = linecode_data['cmatrix']
            else:
                Cmatrix = None
            if Cmatrix is not None:
                #capacitance matrix
                try:
                    if isinstance(Cmatrix, list) and len(Cmatrix) == 1 and '|' in Cmatrix[0]:
                        rowsC = Cmatrix[0].split('|')
                        rowsC = list(map(lambda x: x.strip(), rowsC))
                        new_Cmatrix = []
                        for rowC in rowsC:
                            new_Cmatrix.append([])
                            new_Cmatrix[-1] += list(map(lambda x: self.convert_to_meters(float(x.strip()), line_unit, inverse=True), rowC.split(' ')))
                        new_Cmatrix = self.symmetrize(new_Cmatrix)
                    else:
                        new_Cmatrix = list(map(lambda x: self.convert_to_meters(float(x), line_unit, inverse=True), Cmatrix))
                    new_Cmatrix = np.array(new_Cmatrix)
                    if new_Cmatrix.ndim == 1:
                        new_Cmatrix = [new_Cmatrix.tolist()]
                    else:
                        new_Cmatrix = new_Cmatrix.tolist()
                    api_line.capacitance_matrix = new_Cmatrix
                except:
                    pass

            #Number of phases
            try:
                N_phases = int(data['phases'])
            except:
                N_phases = 3
                pass

            #if N_phases!=len(phases_bus1) or N_phases!=len(phases_bus2):
            #    self.logger.warning('N_phases and the number of phases do not match for line {name}'.format(name=name))

            #Try to get the geometry code if it exists
            try:
                line_geometry_code = data['geometry']
            except:
                line_geometry_code = None
                pass

            #If it is an empty string, convert it to None
            if line_geometry_code == '':
                line_geometry_code = None

            #If we have a geometry code, try to get the corresponding data
            if line_geometry_code is not None:
                try:
                    line_geometries = dss.utils.class_to_dataframe('linegeometry')
                    this_line_geometry = line_geometries[line_geometry_code]
                except:
                    self.logger.warning(
                        'Could not get the geometry {line_geom} data of line {line_name}'.format(line_geom=line_geometry_code, line_name=name)
                    )
                    this_line_geometry = None
                    pass
            else:
                this_line_geometry = None

            #wires
            wires = []
            #As many wires as phases plus neutral
            for p in range(N_phases + 1):

                wires.append(Wire(model))
                #Initialize everything to Nones and modify if possible
                wires[p].phase = None
                wires[p].nameclass = None
                wires[p].X = None
                wires[p].Y = None
                wires[p].diameter = None
                wires[p].gmr = None
                wires[p].ampacity = None
                wires[p].ampacity_emergency = None
                wires[p].resistance = None

                if name in fuses_names:
                    wires[p].is_fuse = 1
                else:
                    wires[p].is_fuse = 0

                if api_line.is_switch == 1:
                    wires[p].is_switch = 1
                else:
                    wires[p].is_switch = 0

                if api_line.is_breaker == 1:
                    wires[p].is_breaker = 1
                else:
                    wires[p].is_breaker = 0

                if api_line.is_recloser == 1:
                    wires[p].is_recloser = 1
                else:
                    wires[p].is_recloser = 0

                wires[p].is_open = None #Not mapped
                wires[p].fuse_limit = None #Not mapped
                wires[p].concentric_neutral_gmr = None #Not mapped
                wires[p].concentric_neutral_resistance = None #Not mapped
                wires[p].concentric_neutral_diameter = None #Not mapped

                #phase
                try:
                    wires[p].phase = self.phase_mapping(phases_bus1[p])
                except:
                    #Handles the neutral
                    if p >= len(phases_bus1):
                        wires[p].phase = 'N'
                    pass

                #If we have linegeometry data, we can do something
                if this_line_geometry is not None:

                    #nameclass
                    try:
                        wires[p].nameclass = this_line_geometry['cncable']
                    except:
                        pass

                    #Get the unit for the distances
                    try:
                        line_geometry_unit = this_line_geometry['units']
                    #If not present, assume the same unit as the line
                    except:
                        self.logger('Could not find the lineGeometry distance unit for line {name}.'.format(name=name))
                        if unit is not None:
                            self.logger.info('Using the line unit instead: {unit}'.format(unit=unit))
                            line_geometry_unit = unit
                        #If we do not have units for the line either, then w'd rather set everything to None...
                        else:
                            line_geometry_unit = None
                        pass

                    #X
                    #If we have a valid distance unit
                    if line_geometry_unit is not None:
                        try:
                            wires[p].X = self.convert_to_meters(this_line_geometry['X'], line_geometry_unit)
                        except:
                            pass

                    #Y
                    #If we have a valid distance unit
                    if line_geometry_unit is not None:
                        try:
                            wires[p].Y = self.convert_to_meters(this_line_geometry['H'], line_geometry_unit)
                        except:
                            pass

                    #Check if we have wireData that we can use
                    try:
                        this_line_wireData_code = this_line_geometry['wire']
                    except:
                        this_line_wireData_code = None

                    #If empty, convert it to None
                    if this_line_wireData_code == '':
                        this_line_wireData_code = None

                    #Try to get the Wire data for this lineGeometry
                    if this_line_wireData_code is not None:
                        try:
                            all_wire_data = dss.utils.class_to_dataframe('wiredata')
                            this_line_wireData = all_wire_data[this_line_wireData_code]
                        except:
                            self.logger.warning(
                                'Could not get the wireData {wiredata} of lineGeometry {line_geom}'.format(
                                    wiredata=this_line_wireData_code, line_geom=this_line_geometry
                                )
                            )
                            pass
                    else:
                        this_line_wireData = None

                    #If we have valid WireData
                    if this_line_wireData is not None:

                        #Get the unit for the radius distance
                        try:
                            wire_radius_unit = this_line_wireData['Radunits']
                        #If not present, assume the same unit as the lineGeometry
                        except:
                            self.logger('Could not find the wireData radius distance unit for Wiredata {name}.'.format(name=this_line_wireData_code))
                            if line_geometry_unit is not None:
                                self.logger.info('Using the lineGeometry unit instead: {unit}'.format(unit=line_geometry_unit))
                                wire_radius_unit = line_geometry_unit
                            #If we do not have units for the line either, then w'd rather set everything to None...
                            else:
                                wire_radius_unit = None
                            pass

                        #diameter
                        #If we have valid wiredata radius distance unit
                        if wire_radius_unit is not None:
                            try:
                                wires[p].diameter = self.convert_to_meters(this_line_wireData['Diam'], wire_radius_unit)
                            except:
                                pass

                        #Get the unit for the GMR
                        try:
                            wire_gmr_unit = this_line_wireData['GMRunits']
                        #If not present, assume the same unit as the lineGeometry
                        except:
                            self.logger('Could not find the wireData GMR distance unit for Wiredata {name}.'.format(name=this_line_wireData_code))
                            if line_geometry_unit is not None:
                                self.logger.info('Using the lineGeometry unit instead: {unit}'.format(unit=line_geometry_unit))
                                wire_gmr_unit = line_geometry_unit
                            #If we do not have units for the line either, then w'd rather set everything to None...
                            else:
                                wire_gmr_unit = None
                            pass

                        #gmr
                        #If we have valid wiredata GMR distance unit
                        if wire_gmr_unit is not None:
                            try:
                                wires[p].gmr = self.convert_to_meters(this_line_wireData['GMRac'], wire_gmr_unit)
                            except:
                                pass

                        #ampacity
                        try:
                            wires[p].ampacity = this_line_wireData['Normamps']
                        except:
                            pass

                        #ampacity emergency
                        try:
                            wires[p].ampacity_emergency = this_line_wireData['Emergamps']
                        except:
                            pass

                        #resistance
                        #Should be Rac*length_of_line
                        #Rac is in ohms per Runits
                        #We have to make sure that the line length is in the same unit
                        #
                        #First, check if we have a valid line length, otherwise there is no point...
                        if length is not None:
                            #Try to get the per unit resistance
                            try:
                                Rac = this_line_wireData['Rac']
                            except:
                                Rac = None
                                pass
                            #If we succeed...
                            if Rac is not None:
                                #Try to get the distance unit for the resistance
                                try:
                                    Runits = this_line_wireData['Runits']
                                #If not present, assume it is the same as the line unit
                                #But log this, because it might not be the case. Assume the user is responsible here....
                                except:
                                    self.logger.warning('Could not find the resistance unit for wire {wire}'.format(wire=this_line_wireData_code))
                                    if unit is not None:
                                        self.logger.info('Using line length unit instead: {unit}'.format(unit=unit))
                                        Runits = unit
                                    else:
                                        Runits = None
                                    pass
                                #If we have a valid unit for the resistance
                                if Runits is not None:
                                    try:
                                        #Convert the length of the line to the right unit
                                        #(99.9999% of the time they should match, but just for safety...)
                                        new_length = self.unit_conversion(length, unit, Runits)
                                        wires[p].resistance = Rac * new_length
                                    except:
                                        pass

                    if wires[p].ampacity is None and 'normamps' in data:
                        try:
                            wires[p].ampacity = float(data['normamps'])
                        except:
                            pass

                    if wires[p].ampacity_emergency is None and 'emergamps' in data:
                        try:
                            wires[p].ampacity_emergency = float(data['emergamps'])
                        except:
                            pass

                    #is_switch
                    wires[p].is_switch = api_line.is_switch

            api_line.wires = wires
            self._lines.append(api_line)

        end = time.time()
        print('rest= {}'.format(end - middle))
        return 1

    @timeit
    def parse_transformers(self, model):
        '''Transformer parser.

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        transformers = dss.utils.class_to_dataframe('transformer')
        self._transformers = []

        for name, data in transformers.items():

            api_transformer = PowerTransformer(model)
            api_transformer.name = None
            api_transformer.rated_power = None

            #emergency_power removed from powerTransformer and added to Winding by Tarek
            #api_transformer.emergency_power=None

            api_transformer.install_type = None #Not mapped
            api_transformer.noload_loss = None
            api_transformer.phase_shift = None #Not mapped
            api_transformer.from_element = None
            api_transformer.to_element = None
            api_transformer.reactances = None
            api_transformer.position = None #Not mapped

            #Name
            try:
                trans_name = name.split('ransformer.')[1].lower()
                if trans_name not in self.all_object_names:
                    self.all_object_names.append(trans_name)
                else:
                    self.logger.warning('Duplicate object Transformer {name}'.format(name=transformer_name))
                api_transformer.name = trans_name
            except:
                pass

            #rated power
            #rated_power removed from powerTransformer and added to Winding by Nicolas
            #try:
            #    api_transformer.rated_power=sum(map(lambda x:float(x), data['kVAs']))*10**3 #DiTTo in volt ampere
            #except:
            #    pass

            #emergency power
            #emergency_power removed from powerTransformer and added to Winding by Tarek
            #try:
            #    api_transformer.emergency_power=float(data['emerghkVA'])*10**3 #DiTTo in volt ampere
            #except:
            #    pass

            #Loadloss
            try:
                api_transformer.loadloss = float(data['%loadloss']) #DiTTo in volt ampere
            except:
                pass

            try:
                if data['sub'] == 'Yes':
                    api_transformer.is_substation = 1
            except:
                pass

            #normhkva
            try:
                api_transformer.normhkva = float(data['normhkVA']) #DiTTo in volt ampere
            except:
                pass

            #noload_loss
            try:
                api_transformer.noload_loss = float(data['%noloadloss'])
            except:
                pass

            #from_element and to_element
            try:
                bus_data = data['buses']
                if len(bus_data) == 2:
                    b1, b2 = bus_data
                    if '.' in b1:
                        temp = b1.split('.')
                        b1_name = temp[0]
                        b1_phases = temp[1:]
                    else:
                        b1_name = b1
                        b1_phases = [1, 2, 3]
                    if '.' in b2:
                        temp = b2.split('.')
                        b2_name = temp[0]
                        b2_phases = temp[1:]
                    else:
                        b2_name = b2
                        b2_phases = [1, 2, 3]
                if len(bus_data) == 3:
                    b1, b2, b3 = bus_data
                    if '.' in b1:
                        temp = b1.split('.')
                        b1_name = temp[0]
                        b1_phases = temp[1:]
                    else:
                        b1_name = b1
                        b1_phases = [1, 2, 3]
                    if '.' in b2:
                        temp = b2.split('.')
                        b2_name = temp[0]
                        b2_phases = temp[1:]
                    else:
                        b2_name = b2
                        b2_phases = [1, 2, 3]
                    if '.' in b3:
                        temp = b3.split('.')
                        b3_name = temp[0]
                        b3_phases = temp[1:]
                    else:
                        b3_name = b3
                        b2_phases = [1, 2, 3]
                api_transformer.from_element = b1_name
                api_transformer.to_element = b2_name
            except:
                pass

            #windings
            windings = []
            try:
                N_windings = int(data['windings'])
            except:
                N_windings = 2
                pass

            #reactances
            if 'Xscarray' in data:
                try:
                    api_transformer.reactances = list(map(lambda x: float(x), data['Xscarray']))
                except:
                    pass

            elif N_windings == 1 and 'XHL' in data:
                api_transformer.reactances = [float(data['XHL'])]
            elif N_windings == 2:
                api_transformer.reactances = []
                if 'XHL' in data:
                    api_transformer.reactances.append(float(data['XHL']))
                if 'XLT' in data:
                    api_transformer.reactances.append(float(data['XLT']))
                if 'XHT' in data:
                    api_transformer.reactances.append(float(data['XHT']))
            #Number of phases
            try:
                N_phases = int(data['phases'])
            except:
                N_phases = 3
                pass

            #If we have a one phase 3 winding transformer in OpenDSS, it should represent a 2 winding center tap transformer
            if N_windings == 3 and N_phases == 1:
                api_transformer.is_center_tap = 1

            if not 1 <= N_phases <= 3:
                self.logger.warning('Number of phases should be between 1 and 3, got {N} for transformer {name}'.format(N=N_phases, name=name))

            for w in range(N_windings):

                windings.append(Winding(model))
                windings[w].connection_type = None
                windings[w].nominal_voltage = None
                windings[w].voltage_limit = None #Not mapped
                windings[w].resistance = None
                windings[w].reverse_resistance = None #Not mapped

                #connection type
                try:
                    if data['conns'][w].lower() == 'wye':
                        windings[w].connection_type = 'Y'
                    elif data['conns'][w].lower() == 'delta':
                        windings[w].connection_type = 'D'
                except:
                    pass

                #rated power
                #rated_power removed from powerTransformer and added to Winding by Nicolas
                try:
                    windings[w].rated_power = float(data['kVAs'][w]) * 10**3 #DiTTo in volt ampere
                except:
                    windings[w].rated_power = None
                    pass

                #emergency_power
                #emergency_power removed from powerTransformer and added to Winding by Tarek
                try:
                    windings[w].emergency_power = float(data['emerghkVA']) * 10**3 #DiTTo in volt ampere
                except:
                    windings[w].emergency_power = None
                    pass

                #nominal_voltage
                try:
                    windings[w].nominal_voltage = float(data['kVs'][w]) * 10**3 #DiTTo in Volts
                except:
                    pass

                #resistance
                try:
                    windings[w].resistance = float(data['%Rs'][w])
                except:
                    pass

                phase_windings = []
                for p in range(N_phases):

                    phase_windings.append(PhaseWinding(model))
                    phase_windings[p].tap_position = None
                    phase_windings[p].phase = None
                    phase_windings[p].compensator_r = None
                    phase_windings[p].compensator_x = None

                    #tap position
                    if 'taps' in data:
                        try:
                            phase_windings[p].tap_position = float(data['taps'][w])
                        except:
                            pass
                    elif 'tap' in data:
                        try:
                            phase_windings[p].tap_position = float(data['tap'])
                        except:
                            pass

                    #phase
                    try:
                        phase_windings[p].phase = self.phase_mapping(b1_phases[p])
                    except:
                        pass

                    regulators = dss.utils.class_to_dataframe('RegControl')
                    for reg_name, reg_data in regulators.items():

                        if 'transformer' in reg_data and reg_data['transformer'].lower() == api_transformer.name.lower():
                            if 'R' in reg_data:
                                phase_windings[p].compensator_r = float(reg_data['R'])
                            if 'X' in reg_data:
                                phase_windings[p].compensator_x = float(reg_data['X'])

                #Store the phase winding objects in the winding objects
                windings[w].phase_windings = phase_windings

            #Store the winding objects in the transformer object
            api_transformer.windings = windings
            self._transformers.append(api_transformer)

        return 1

    @timeit
    def parse_regulators(self, model):
        '''Regulator parser.

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        regulators = dss.utils.class_to_dataframe('RegControl')
        transformers = dss.utils.class_to_dataframe('Transformer')
        self._regulators = []

        for name, data in regulators.items():

            api_regulator = Regulator(model)
            #Initialize the data as Nones and update with real values if possible
            api_regulator.name = None
            api_regulator.delay = None
            api_regulator.highstep = None
            api_regulator.lowstep = None #Not mapped
            api_regulator.pt_ratio = None
            api_regulator.ct_ratio = None #Not mapped
            api_regulator.phase_shift = None #Not mapped
            api_regulator.ltc = None #Not mapped
            api_regulator.bandwidth = None
            api_regulator.bandcenter = None
            api_regulator.voltage_limit = None
            api_regulator.connected_transformer = None
            api_regulator.from_element = None
            api_regulator.to_element = None
            api_regulator.reactances = None
            api_regulator.pt_phase = None
            api_regulator.windings = None
            api_regulator.winding = None
            api_regulator.noload_loss = None

            #Name
            try:
                reg_name = name.split('.')[1].lower()
                if reg_name not in self.all_object_names:
                    self.all_object_names.append(reg_name)
                else:
                    self.logger.warning('Duplicate object Regulator {name}'.format(name=reg_name))
                api_regulator.name = reg_name
            except:
                pass

            #winding(number of the winding of the transformer element that the RegControl is monitoring)
            try:
                winding = int(data['winding'])
                api_regulator.winding = winding
            except:
                pass

            #windings (The actual Windings Ditto objects)
            #
            #We need the transformer data first
            if 'transformer' in data and 'Transformer.{}'.format(data['transformer'].lower()) in transformers:
                trans = transformers['Transformer.{}'.format(data['transformer'].lower())]

                #Total number of windings
                N_windings = int(trans['windings'])

                #Initialize the list of Windings
                api_regulator.windings = [Winding(model) for _ in range(N_windings)]

                #Connection type
                for w in range(N_windings):
                    if 'conns' in trans:
                        try:
                            api_regulator.windings[w].connection_type = trans['conns'][w]
                        except:
                            pass

                #nominal_voltage
                for w in range(N_windings):
                    if 'kVs' in trans:
                        try:
                            api_regulator.windings[w].nominal_voltage = float(trans['kVs'][w]) * 10**3 #DiTTo in Volts
                        except:
                            pass

                #resistance
                for w in range(N_windings):
                    if '%Rs' in trans:
                        try:
                            api_regulator.windings[w].resistance = float(trans['%Rs'][w])
                        except:
                            pass

                #rated_power
                for w in range(N_windings):
                    if 'kVAs' in trans:
                        try:
                            api_regulator.windings[w].rated_power = float(trans['kVAs'][w]) * 10**3 #DiTTo in volt ampere
                        except:
                            pass

                #emergency_power
                for w in range(N_windings):
                    if 'emerghkVA' in trans:
                        try:
                            api_regulator.windings[w].emergency_power = float(trans['emerghkVA'][w]) * 10**3 #DiTTo in volt ampere
                        except:
                            pass

                #phase_windings
                for w in range(N_windings):
                    #Get the phase
                    if 'buses' in trans:
                        try:
                            bus = trans['buses'][w]
                        except:
                            pass
                        if '.' in bus:
                            temp = bus.split('.')
                            bus_name, phases = temp[0], temp[1:]
                        else:
                            phases = ['1', '2', '3']
                    else:
                        phases = ['1', '2', '3']

                    api_regulator.windings[w].phase_windings = [PhaseWinding(model) for _ in phases]

                    for p, phase in enumerate(phases):
                        #phase
                        api_regulator.windings[w].phase_windings[p].phase = self.phase_mapping(phase)

                        #tap_position
                        if 'taps' in trans:
                            api_regulator.windings[w].phase_windings[p].tap_position = float(trans['taps'][w])

                        #compensator_r
                        if 'R' in data:
                            try:
                                api_regulator.windings[w].phase_windings[p].compensator_r = float(data['R'])
                            except:
                                pass

                        #compensator_x
                        if 'X' in data:
                            try:
                                api_regulator.windings[w].phase_windings[p].compensator_x = float(data['X'])
                            except:
                                pass

            else:
                self.logger.warning('Could not find the transformer data for regulator {name}'.format(name=name))

            #CTprim
            try:
                api_regulator.ct_prim = float(data['CTprim'])
            except:
                pass

            #noload_loss
            try:
                api_regulator.noload_loss = float(data['%noloadloss'])
            except:
                pass

            #delay
            try:
                api_regulator.delay = float(data['delay'])
            except:
                pass

            #highstep
            try:
                api_regulator.highstep = int(data['maxtapchange'])
            except:
                pass

            #pt_ratio
            try:
                api_regulator.pt_ratio = float(data['ptratio'])
            except:
                pass

            #bandwidth
            try:
                api_regulator.bandwidth = float(data['band'])
            except:
                pass

            #bandcenter
            try:
                api_regulator.bandcenter = float(data['vreg'])
            except:
                pass

            #voltage_limit
            try:
                api_regulator.voltage_limit = float(data['vlimit'])
            except:
                pass

            #connected_transformer
            try:
                api_regulator.connected_transformer = data['transformer'].lower()
            except:
                pass

            #Some data needed in ditto can only be accessed through the connected transformer.
            #Therefore, transformers need to be parsed first.
            #Searching for the transformer object:
            if api_regulator.connected_transformer is not None:
                for trans in self._transformers:
                    if trans.name == api_regulator.connected_transformer:
                        #from_element
                        api_regulator.from_element = trans.from_element

                        #to_element
                        api_regulator.to_element = trans.to_element

                        #reactances
                        api_regulator.reactances = trans.reactances

                        break

            #pt_phase
            try:
                api_regulator.pt_phase = self.phase_mapping(phases[int(data['PTphase']) - 1])
            except:
                pass

            self._regulators.append(api_regulator)

        return 1

    @timeit
    def parse_capacitors(self, model):
        '''Capacitor parser.

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        capacitors = dss.utils.class_to_dataframe('capacitor')
        cap_control = dss.utils.class_to_dataframe('CapControl')
        self._capacitors = []

        for name, data in capacitors.items():

            api_capacitor = Capacitor(model)
            #Initialize the data as Nones and update with real values if possible
            api_capacitor.name = None
            api_capacitor.nominal_voltage = None
            api_capacitor.connection_type = None
            api_capacitor.delay = None
            api_capacitor.mode = None
            api_capacitor.low = None
            api_capacitor.high = None
            api_capacitor.resistance = None
            api_capacitor.resistance0 = None #Not mapped
            api_capacitor.resistance = None
            api_capacitor.reactance0 = None #Not mapped
            api_capacitor.susceptance = None #Not mapped
            api_capacitor.susceptance0 = None #Not mapped
            api_capacitor.conductance = None #Not mapped
            api_capacitor.conductance0 = None #Not mapped
            api_capacitor.pt_ratio = None
            api_capacitor.ct_ratio = None
            api_capacitor.pt_phase = None
            api_capacitor.connecting_element = None
            api_capacitor.positions = None #Not mapped
            api_capacitor.phase_capacitors = None

            #Name
            try:
                cap_name = name.split('apacitor.')[1].lower()
                if cap_name not in self.all_object_names:
                    self.all_object_names.append(cap_name)
                else:
                    self.logger.warning('Duplicate object Capacitor {name}'.format(name=cap_name))
                api_capacitor.name = cap_name
            except:
                pass

            #Nominal voltage
            try:
                api_capacitor.nominal_voltage = float(data['kv']) * 10**3 #DiTTo in volts
            except:
                pass

            #connection_type
            try:
                if data['conn'].lower() == 'wye':
                    api_capacitor.connection_type = 'Y'
                elif data['conn'].lower() == 'delta':
                    api_capacitor.connection_type = 'D'
            except:
                pass

            control_id = None
            #Find the capControl that corresponds to the capacitor if any
            for capc_name, capc_data in cap_control.items():
                if capc_data['capacitor'].lower() == api_capacitor.name:
                    control_id = capc_name
                    break

            #delay
            try:
                api_capacitor.delay = float(cap_control[control_id]['Delay'])
            except:
                pass

            #Measuring element
            try:
                api_capacitor.measuring_element = cap_control[control_id]['element']
            except:
                pass

            #mode
            try:
                if cap_control[control_id]['type'] == 'volt':
                    api_capacitor.mode = 'voltage'
                elif cap_control[control_id]['type'] == 'current':
                    api_capacitor.mode = 'currentFlow'
                elif cap_control[control_id]['type'] == 'kvar':
                    api_capacitor.mode = 'reactivePower'
                elif cap_control[control_id]['type'] == 'PF':
                    api_capacitor.mode = None
                elif cap_control[control_id]['type'] == 'time':
                    api_capacitor.mode = 'timeScheduled'
            except:
                pass

            #low
            if control_id is not None:
                try:
                    api_capacitor.low = float(cap_control[control_id]['Vmin'])
                except:
                    pass

            #High
            if control_id is not None:
                try:
                    api_capacitor.high = float(cap_control[control_id]['Vmax'])
                except:
                    pass

            #resistance
            try:
                api_capacitor.resistance = sum(map(lambda x: float(x), data['R']))
            except:
                pass

            #reactance
            try:
                api_capacitor.reactance = sum(map(lambda x: float(x), data['XL']))
            except:
                pass

            #PT ratio
            if control_id is not None:
                try:
                    api_capacitor.pt_ratio = float(cap_control[control_id]['PTratio'])
                except:
                    pass

            #CT ratio
            if control_id is not None:
                try:
                    api_capacitor.ct_ratio = float(cap_control[control_id]['CTratio'])
                except:
                    pass

            #PT phase
            if control_id is not None:
                try:
                    api_capacitor.pt_phase = self.phase_mapping(int(cap_control[control_id]['PTPhase']))
                except:
                    pass

            #connecting element
            try:
                if '.' in data['bus1']:
                    temp = data['bus1'].split('.')
                    b_name = temp[0]
                    phases = temp[1:]
                else:
                    b_name = data['bus1']
                    phases = [1, 2, 3]
                api_capacitor.connecting_element = b_name
            except:
                b_name = None
                phases = None
                pass

            #N_phases
            try:
                N_phases = int(data['phases'])
            except:
                N_phases = None
                pass

            if phases is None and N_phases == 3:
                phases = [1, 2, 3]

            if N_phases is None and api_capacitor.pt_phase is not None:
                N_phases = 1

            if phases is not None and N_phases is not None:

                #Phase capacitors
                phase_capacitors = []
                for p, pha in enumerate(phases):
                    phase_capacitors.append(PhaseCapacitor(model))
                    phase_capacitors[p].phase = None
                    phase_capacitors[p].var = None
                    phase_capacitors[p].switch = None #Not mapped
                    phase_capacitors[p].sections = None #Not mapped
                    phase_capacitors[p].normalsections = None #Not mapped

                    #phase
                    if api_capacitor.pt_phase is not None and api_capacitor.pt_phase == self.phase_mapping(pha):
                        phase_capacitors[p].phase = api_capacitor.pt_phase
                    else:
                        phase_capacitors[p].phase = self.phase_mapping(pha)

                    #var
                    list_data = data['kvar']
                    if isinstance(list_data, list) and len(list_data) == len(phases):
                        try:
                            phase_capacitors[p].var = float(list_data[p]) * 10**3 #DiTTo in var
                        except:
                            pass
                    elif isinstance(list_data, list):
                        try:
                            phase_capacitors[p].var = float(list_data[0]) / float(N_phases) * 10**3 #DiTTo in var
                        except:
                            pass
                    else:
                        try:
                            phase_capacitors[p].var = float(list_data) / float(N_phases) * 10**3 #DiTTo in var
                        except:
                            pass

                api_capacitor.phase_capacitors = phase_capacitors

            self._capacitors.append(api_capacitor)

        return 1

    @timeit
    def parse_loads(self, model):
        '''Load parser.

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        loads = dss.utils.class_to_dataframe('Load')
        self._loads = []

        for name, data in loads.items():

            api_load = Load(model)
            api_load.name = None
            api_load.nominal_voltage = None
            api_load.connection_type = None
            api_load.vmin = None
            api_load.vmax = None
            api_load.phase_loads = None
            api_load.positions = None #Not mapped
            api_load.connecting_element = None
            api_load.rooftop_area = None #Not mapped
            api_load.peak_p = None #Not mapped
            api_load.peak_q = None #Not mapped
            api_load.peak_coincident_p = None #Not mapped
            api_load.peak_coincident_q = None #Not mapped
            api_load.yearly_energy = None #Not mapped
            api_load.num_levels = None #Not mapped

            #Name
            try:
                #load_name=name.split('oad.')[1].lower()
                load_name = 'load_' + name.split('oad.')[1].lower()
                if load_name not in self.all_object_names:
                    self.all_object_names.append(load_name)
                else:
                    self.logger.warning('Duplicate object Load {name}'.format(name=load_name))
                api_load.name = load_name
            except:
                pass

            #Connecting_element
            try:
                api_load.connecting_element = data['bus1']
            except:
                pass

            #nominal voltage
            try:
                api_load.nominal_voltage = float(data['kV']) * 10**3 #DiTTo in volts
            except:
                pass

            try:
                api_load.num_users = float(data['NumCust'])
            except:
                pass

            #connection_type
            try:
                conn = data['conn']
                if conn.lower() == 'wye':
                    api_load.connection_type = 'Y'
                elif conn.lower() == 'delta':
                    api_load.connection_type = 'D'
            except:
                pass

            #vmin
            try:
                api_load.vmin = float(data['Vminpu'])
            except:
                pass

            #vmax
            try:
                api_load.vmax = float(data['Vmaxpu'])
            except:
                pass

            #Get the number of phases
            try:
                N_phases = int(data['phases'])
            except:
                N_phases = 1
                pass

            #Get the actual phase numbers (in the connection data)
            try:
                if '.' in data['bus1']:
                    temp = data['bus1'].split('.')
                    bus = temp[0]
                    phases = list(map(lambda x: int(x), temp[1:]))
                else:
                    bus = data['bus1']
                    phases = ['A', 'B', 'C']
                api_load.connecting_element = bus
            except:
                bus = None
                phases = []
                pass

            #Now, we can have N_phases different from len(phases) for 3 reasons:
            #    - There is an error (in this case, raise an error...)
            #    - One of them is None because not given by the model
            #      There are 3 subcases:
            #            - N_phases=None AND phases=None ==> raise an error...
            #            - N_phases=None ==> just reset N_phases=len(phases)
            #            - phases=None   ==> if N_phases==3, then phases=[A,B,C], otherwise
            #                                raise an error because we cannot just guess the correct phases...
            #    - The connection is Delta
            #        In this case, we should create the correct number of phase loads and make sure
            #        the connection information will be handled correctly

            if N_phases != len(phases):
                if N_phases is None and phases is None:
                    self.logger.warning('No Phase information for load {name}'.format(name=name))
                elif N_phases is None and phases is not None:
                    N_phases = len(phases)
                elif phases is None and N_phases == 3:
                    phases = ['A', 'B', 'C']
                elif phases is None and N_phases != 3:
                    self.logger.warning('No Phase information for load {name}'.format(name=name))
                elif api_load.connection_type == 'D':
                    phases = phases[:N_phases]
                else:
                    self.logger.warning('Phases do not match for load {name}'.format(name=name))

            #Get the kW if present
            try:
                kW = float(data['kW'])
            except:
                kW = None
                pass

            #Get the kva if present
            try:
                kva = float(data['kVA'])
            except:
                kva = None
                pass

            #Get the power factor if present
            try:
                pf = float(data['pf'])
            except:
                pf = None
                pass

            try:
                load_model = int(data['model'])
            except:
                load_model = None
                pass

            #Phase Loads
            kW /= float(len(phases)) #Load assumed balanced
            kva /= float(len(phases)) #Load assumed balanced

            _phase_loads = []

            for i, p in enumerate(phases):

                _phase_loads.append(PhaseLoad(model))
                _phase_loads[i].phase = self.phase_mapping(p)
                _phase_loads[i].p = None
                _phase_loads[i].q = None
                _phase_loads[i].use_zip = None
                _phase_loads[i].ppercentcurrent = None
                _phase_loads[i].qpercentcurrent = None
                _phase_loads[i].ppercentpower = None
                _phase_loads[i].qpercentpower = None
                _phase_loads[i].ppercentimpedance = None
                _phase_loads[i].qpercentimpedance = None

                #Case one: KW and pf
                if kW is not None and pf is not None:
                    _phase_loads[i].p = kW * 10**3 #DiTT0 in watts
                    _phase_loads[i].q = (kW * 10**3 * np.sqrt(1 - pf**2)) / pf #DiTT0 in var

                #Case two: kvar and pf
                elif kva is not None and pf is not None:
                    #Handle the special case where pf=1
                    if pf == 1:
                        #in this case, pure reactive power
                        _phase_loads[i].p = 0.0
                    else:
                        _phase_loads[i].p = (pf * kvar * 10**3) / np.sqrt(1 - pf**2) #DiTT0 in watts
                    _phase_loads[i].q = kva * 10**3 #DiTT0 in var

                #Case three kW and kvar
                elif kW is not None and kva is not None:
                    _phase_loads[i].p = kW * 10**3 #DiTT0 in Watts
                    _phase_loads[i].q = kvar * 10**3 #DiTT0 in var

                #Try to get the model
                try:
                    _model = int(data['model'])
                except:
                    _model = None
                    pass

                if load_model is not None:
                    _phase_loads[i].model = load_model

                #ZIPV model (model==8)
                if _model == 8:
                    #Try to get the ZIPV coefficients
                    try:
                        ZIPV = list(map(lambda x: float(data['ZIPV'])))
                    except:
                        ZIPV = None
                        pass

                    #If we have valid coefficients
                    if ZIPV is not None:
                        _phase_loads[i].use_zip = True

                        if not np.allclose(sum(ZIPV[:2]), 1.0) or not np.allclose(sum(ZIPV[3:-1]), 1.0):
                            self.logger.warning('ZIPV coefficients for load {name} do not sum properly'.format(name=name))

                        _phase_loads[i].ppercentcurrent = ZIPV[1] * 100
                        _phase_loads[i].qpercentcurrent = ZIPV[4] * 100
                        _phase_loads[i].ppercentpower = ZIPV[2] * 100
                        _phase_loads[i].qpercentpower = ZIPV[5] * 100
                        _phase_loads[i].ppercentimpedance = ZIPV[0] * 100
                        _phase_loads[i].qpercentimpedance = ZIPV[3] * 100
                else:
                    _phase_loads[i].use_zip = False

            api_load.phase_loads = _phase_loads
            self._loads.append(api_load)

        return 1
