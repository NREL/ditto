
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
from ditto.readers.windmil_ascii.mw_reader import WM_reader


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
        self.windmil_folder = r'C:\Users\alatif\Desktop\DiTTo\ditto\readers\windmil_ascii\Network'

        if 'network_folder' in kwargs:
            self.windmil_folder = kwargs['network_folder']

    def filter_edged_by_class(self, class_name):
        relevant_edges = ((u, v) for u, v, d in self.nxGraph.edges(data=True) if d['class'] == class_name)
        return relevant_edges

    def get_file_content(self):
        """
            Windmil generates multiple xml(Multispeak format) files for a single project. The code below
            reads all the xml files in a given folder and merges them to form 1 dictionary
        """
        try:
            wm_data = WM_reader(self.windmil_folder)
            self.nxGraph = wm_data.nxGraph
        except:
            raise ValueError('Unable to open project from {name}'.format(name=self.windmil_folder))
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
        for node_name in self.nxGraph.nodes():
            node = Node(model)
            node.name = node_name
            if 'x' in self.nxGraph.node[node_name]:
                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node_name]['x'])
                node_pos.lat = float(self.nxGraph.node[node_name]['y'])
                node.positions.append(node_pos)

    def parse_lines(self, model):
        lines = self.filter_edged_by_class('line')
        OHcables = self.nxGraph.graph['OH cables']
        UGcables = self.nxGraph.graph['UG cables']
        Layout = self.nxGraph.graph['Wire layouts']
        for line in lines:
            node1, node2 = line
            line = Line(model)

            line.name = node2.replace('node_', '')
            line.from_element = node1
            line.to_element = node2
            line.is_breaker = False
            line.is_recloser = False
            line.is_banked = False
            line.is_fuse = False
            line.is_sectionalizer = False
            line.is_switch = False
            line.length = self.convert_to_meters(float(self.nxGraph[node1][node2]['length']), 'ft')
            line.nominal_voltage = float(self.nxGraph[node1][node2]['kv'])
            line.line_type = self.nxGraph[node1][node2]['type']
            line.feeder_name = '' if isinstance(self.nxGraph[node1][node2]['feeder'], float) else \
                                self.nxGraph[node1][node2]['feeder']
            line.substation_name =  '' if isinstance(self.nxGraph[node1][node2]['substation'], float) else \
                                    self.nxGraph[node1][node2]['substation']

            for node_name in [node1, node2]:
                if 'x' in self.nxGraph.node[node_name]:
                    node_pos = Position(model)
                    node_pos.long = float(self.nxGraph.node[node_name]['x'])
                    node_pos.lat = float(self.nxGraph.node[node_name]['y'])
                    line.positions.append(node_pos)

            for phase, conductor_name in self.nxGraph[node1][node2]['wires'].items():
                phase_wire = Wire(model)
                phase_wire.nameclass = conductor_name.replace('.', '_').replace(' ', '_')
                phase_wire.phase = phase
                phase_wire.is_switch = False
                phase_wire.is_fuse = False
                phase_wire.is_recloser = False
                phase_wire.is_breaker = False
                phase_wire.is_open = False
                phase_wire.X = -1 if phase is 'A' else 1 if  phase is 'C' else 0
                phase_wire.Y = 10 if phase is not 'N' else 8

                if self.nxGraph[node1][node2]['type'] == 'overhead':
                    cond_data = OHcables[OHcables['name'] == conductor_name]
                    if len(cond_data):
                        phase_wire.gmr = self.convert_to_meters(float(cond_data['GMR - feet'].iloc[0]), 'ft')
                        phase_wire.diameter = self.convert_to_meters(float(cond_data['dia - in'].iloc[0]), 'in')
                        phase_wire.ampacity = float(cond_data['amps'].iloc[0])
                        phase_wire.resistance = self.convert_from_meters(float(cond_data['R-50 - ohm/mi'].iloc[0]), 'mi')

                elif self.nxGraph[node1][node2]['type'] == 'underground':
                    cond_data = UGcables[UGcables['name'] == conductor_name]
                    if len(cond_data):
                        phase_wire.gmr = self.convert_to_meters(float(cond_data['GMRphase - feet'].iloc[0]), 'ft')
                        phase_wire.concentric_neutral_gmr = self.convert_to_meters(
                            float(cond_data['GMRneut - feet'].iloc[0]), 'ft')
                        phase_wire.diameter = self.convert_to_meters(
                            float(cond_data['diaCond - feet'].iloc[0]), 'ft')
                        phase_wire.insulation_thickness = self.convert_to_meters(
                            float(cond_data['diaInsul - feet'].iloc[0]), 'ft')
                        phase_wire.concentric_neutral_diameter = self.convert_to_meters(
                            float(cond_data['diaNeut - feet'].iloc[0]), 'ft')
                        phase_wire.ampacity = float(cond_data['amps'].iloc[0])
                        phase_wire.resistance = self.convert_from_meters(
                            float(cond_data['Rphase - ohm/mi '].iloc[0]), 'mi')
                        phase_wire.concentric_neutral_resistance = self.convert_from_meters(
                            float(cond_data['Rneut - ohm/mi '].iloc[0]), 'ft')

                if phase_wire.resistance == None:
                    phase_wire.resistance = 0
                if phase_wire.gmr == None or phase_wire.gmr == 0:
                    phase_wire.gmr = 1.0

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
                print(Dmatrix)
                if line.wires:
                    Z = self.get_primitive_impedance_matrix(Dmatrix, GMRs, Rs)
                    if 'N' in Phases or 'n' in Phases:
                        Z = self.kron_reduction(Z)
                    line.impedance_matrix = Z.tolist()
