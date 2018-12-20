
import pandas as pd
import numpy as np
import logging
import os

import xmltodict


from ditto.readers.abstract_reader import AbstractReader
from ditto.store import Store
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.wire import Wire
from ditto.models.position import Position

logger = logging.getLogger(__name__)
class Reader(AbstractReader):
    '''
        Author: Aadil Latif
        TODO: Add reader details here
    '''
    register_names = ["windmil","Windmil","WM","wm"]
    def __init__(self, **kwargs):
        '''
            Windmil-->class constructor
        '''
        super(Reader, self).__init__(**kwargs)
        self.windmil_folders = {
            'Network'   : './Networks/Angel Fire/',
            'Libraries' : {
                'OHcables'      : './Libraries/Overhead Conductors.xlsx',
                'UGcables'      : './Libraries/Underground Conductors.xlsx',
                'Regulators'    : './Libraries/Regulators.xlsx',
                'Tranformers'   : './Libraries/Transformers.xlsx',
                'Bay'           : './Libraries/Bay.xlsx',
                'Fuse'          : './Libraries/Fuse.xlsx',
                'OCR'           : './Libraries/OCR.xlsx',
                'Recloser'      : './Libraries/Recloser.xlsx',
                'Sectionalizer' : './Libraries/Sectionalizer.xlsx',
            },
        }
        if 'network_folder' in kwargs:
            self.windmil_folders['Network'] = kwargs['network_folder']
        if 'library_folder' in kwargs:
            self.windmil_folders['Libraries'] = kwargs['library_folder']


    def __CreateElmDicts(self, parsed_xml):
        '''
        This function
        :param ParsedXML:
        :return:
        '''

        for object_name, object_dictionary in parsed_xml.items():
            if object_name not in self.elements_by_class:
                self.elements_by_class[object_name] = {}
            if isinstance(object_dictionary, list):
                for ElmDict in object_dictionary:
                    if '@objectID' in ElmDict:
                        self.elements[ElmDict['@objectID']] = ElmDict
                        self.elements_by_class[object_name][ElmDict['@objectID']] = ElmDict
            else:
                if '@objectID' in object_dictionary:
                    self.elements[object_dictionary['@objectID']] = object_dictionary
                    self.elements_by_class[object_name][object_dictionary['@objectID']] = object_dictionary
        return

    def get_file_content(self):
        """
            Windmil generates multiple xml(Multispeak format) files for a single project. The code below
            reads all the xml files in a given folder and merges them to form 1 dictionary
        """
        self.elements = {}
        self.elements_by_class = {}
        multispeak_files = os.listdir(self.windmil_folders['Network'])
        for filename in multispeak_files:
            if '.xml' in filename:
                try:
                    XmlFile = open(self.windmil_folders['Network'] + filename)
                    XmlDict = xmltodict.parse(XmlFile.read())['MultiSpeakMsgHeader']['MultiSpeak']
                    XmlFile.close()
                    self.__CreateElmDicts(XmlDict)
                except:
                    raise ValueError('Unable to open file {name}'.format(name=filename))

        # The code is used to read all the relevant equipment libraries and create a dictionary of DataFrames
        self.libraries = {}
        for library_name, library_path in self.windmil_folders['Libraries'].items():
            try:
                LibData = pd.read_excel(library_path, index_col=0)
                self.libraries[library_name] = LibData.T
            except:
                raise ValueError('Unable to open file {name}'.format(name=library_path))
        return

    def parse(self, model, **kwargs):
        '''
            Parse the xml file and get topological elements
        '''

        if 'verbose' in kwargs and isinstance(kwargs['verbose'], bool):
            self.verbose=kwargs['verbose']
        else:
            self.verbose=False

        #Call parse method of abtract reader    
        super(Reader, self).parse(model, **kwargs)

    def fixStr(self, String):
        BannedChrs = [' ', '.']
        for Chr in BannedChrs:
            String = String.replace(Chr, '_')
        return String.lower()

    def parse_nodes(self, model):

        self.get_file_content() 	
        node_list = []
        for element_name, element_properties in self.elements.items():
            if 'parentSectionID' in element_properties:
                node_from = self.fixStr(element_properties['parentSectionID']['@name'])
                node_to = self.fixStr(element_properties['sectionID'])

                if node_from not in node_list:
                    node = Node(model)
                    node.name = node_from
                    node_list.append(node_from)

                if node_to not in node_list:
                    node = Node(model)
                    node.name = node_to
                    node_list.append(node_to)

    def parse_lines(self, model):
        line_types = ['ohPrimaryLine', 'ugPrimaryLine', 'ohSecondaryLine', 'ugSecondaryLine']
        # self.get_file_content()
        for line_type in line_types:
            lines = self.elements_by_class[line_type]
            for line_name, line_data in lines.items():
                node_from = self.fixStr(line_data['parentSectionID']['@name'])
                node_to = self.fixStr(line_data['sectionID'])
                line = Line(model)

                line.name = self.fixStr(node_from)
                line.from_element = node_from
                line.to_element = node_to
                line.is_breaker = False
                line.is_recloser = False
                line.is_banked = False
                line.is_fuse = False
                line.is_sectionalizer = False
                line.is_switch = False
                line.length = float(line_data['condLength'])
                line.nominal_voltage = float(line_data['operVolt'])
                line.line_type = 'overhead' if 'oh' in line_type else 'underground'
                for xy in line_data['complexLine']['coord']:
                    node_pos = Position(model)
                    node_pos.long = float(xy['X'])
                    node_pos.lat = float(xy['Y'])
                    line.positions.append(node_pos)
                if isinstance(line_data['conductorList'], dict):
                    if not isinstance(line_data['conductorList']['conductor'], list):
                        conductors = [line_data['conductorList']['conductor']]
                    else:
                        conductors = line_data['conductorList']['conductor']
                    for conductor in conductors:
                        conductor_name = conductor['conductorType']
                        conductor_phase = conductor['phase']
                        phase_wire = Wire(model)
                        phase_wire.nameclass = conductor_name
                        phase_wire.phase = conductor_phase
                        phase_wire.is_switch = False
                        phase_wire.is_fuse = False
                        phase_wire.is_recloser = False
                        phase_wire.is_breaker = False
                        phase_wire.is_open = False
                        phase_wire.X = 0 if conductor_phase == 'A' else 2 if conductor_phase == 'B' else 4
                        phase_wire.Y = 0
                        if conductor_name in self.libraries['OHcables']:
                            conductor_data = self.libraries['OHcables'][conductor_name]
                            phase_wire.nameclass = self.fixStr(conductor['conductorType'])
                            phase_wire.gmr = conductor_data['GMR (feet)']
                            phase_wire.diameter = conductor_data['Diameter (inches)']
                            phase_wire.ampacity = conductor_data['Ampacity']
                            phase_wire.resistance = conductor_data['R @ 50 C (ohms/mile)'] # 'R @ 25 C (ohms/mile)'
                        elif conductor_name in self.libraries['UGcables']:
                            conductor_data = self.libraries['UGcables'][conductor_name]
                            phase_wire.nameclass = self.fixStr(conductor['conductorType'])
                            phase_wire.gmr = conductor_data['GMR Phase (feet)']
                            phase_wire.concentric_neutral_gmr = conductor_data['GMR Neutrl (feet)']
                            phase_wire.diameter = conductor_data['Cond Dia (feet)']
                            phase_wire.insulation_thickness = conductor_data['Insul Dia (feet)']
                            phase_wire.concentric_neutral_diameter = conductor_data['Neutrl Dia (feet)']
                            phase_wire.ampacity = conductor_data['Ampacity']
                            phase_wire.resistance = conductor_data['R Phase (ohms/1000ft)']
                            phase_wire.concentric_neutral_resistance = conductor_data['R Ntrl (ohms/1000ft)']
                        else:
                            logger.warning('')
                        if phase_wire.gmr:
                            line.wires.append(phase_wire)

                Dmatrix = np.zeros((len(line.wires), len(line.wires)))
                Phases = []
                GMRs = []
                Rs = []
                for i, wire1 in enumerate(line.wires):
                    Phases.append(wire1.phase)
                    GMRs.append(wire1.gmr)
                    Rs.append(wire1.resistance)
                    for j, wire2 in enumerate(line.wires):
                        distance = self.distance([wire1.X, wire1.Y], [wire2.X, wire2.Y])
                        Dmatrix[i,j] = distance

                if line.wires:
                    Z = self.get_primitive_impedance_matrix(Dmatrix, GMRs, Rs)
                    if 'N' in Phases or 'n' in Phases:
                        Z = self.kron_reduction(Z)
                    line.impedance_matrix = Z.tolist()
