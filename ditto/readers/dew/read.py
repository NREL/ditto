
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging
import os
import math

import numpy as np
import pandas as pd
import itertools

from ditto.readers.abstract_reader import AbstractReader
from ditto.store import Store
from ditto.models.node import Node
from ditto.models.regulator import Regulator
from ditto.models.base import Unicode
from ditto.models.phase_winding import PhaseWinding
from ditto.models.winding import Winding
from ditto.models.powertransformer import PowerTransformer
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.capacitor import Capacitor
from ditto.models.wire import Wire
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.position import Position
from ditto.models.feeder_metadata import Feeder_metadata

logger = logging.getLogger(__name__)

class Reader(AbstractReader):
    def __init__(self, **kwargs):
        if "dew_file" in kwargs:
            fp = open(kwargs['dew_file'],'r')
            self.dew_data = fp.readlines()
            fp.close()
        else:
            raise ValueError("No DEW file provided")

        if "database_path" in kwargs:

            #Read all the sheets in the excel document into an ordered dictionary keyed by the sheet names
            self.database = pd.read_excel(kwargs['database_path'],sheet_name=None) 
        else:
            raise ValueError("No Excel file for the DEW database provided")

        if "projection" in kwargs:
            self.projection = kwargs["projection"]
        else:
            self.projection = None
            print("Warning - using state-plane co-ordinate system provided by DEW for locations")


        self.small_resistance = 0.0000001

        ###
        #Indexes used by DEW. Modify these if DEW formats changed in future versions

        self.database_lines = 'PTLINESPC'
        self.dbase_line_index = 'IPTROW'
        self.database_conductors = 'PTLINECOND'
        self.database_cables = 'PTCABCOND'
        self.database_switches = 'PTSWT'
        self.database_protection = 'PTPRODEV'
        self.database_transformers = 'PTXFMR'
        self.database_transformer_api = 'APIXFRMCONIDX'

        self.dbase_line_neutral_oh_x = 'DXNEU'
        self.dbase_line_phase1_oh_x = 'DXPH1ORR1'
        self.dbase_line_phase2_oh_x = 'DXPH2ORR0'
        self.dbase_line_phase3_oh_x = 'DXPH3ORY0'
        self.dbase_line_neutral_oh_y = 'DYNEU'
        self.dbase_line_phase1_oh_y = 'DYPH1ORX1'
        self.dbase_line_phase2_oh_y = 'DYPH2ORX0'
        self.dbase_line_phase3_oh_y = 'DYPH3ORY1'
        self.dbase_conductor_name = 'STNAM'
        self.dbase_conductor_index = 'IWIRE'
        self.dbase_conductor_diameter = 'DRADCONDSUL'
        self.dbase_conductor_gmr = 'DGMRSUL'
        self.dbase_conductor_ampacity = 'DRATAMBTEMP1A'
        self.dbase_conductor_resistance = 'DROHMPRLUL'

        # TODO: CHECK UNITS!
        self.dbase_cable_name = 'STNAM'
        self.dbase_cable_index = 'ICAB'
        self.dbase_cable_diameter = 'DRADCONDSUL'
        self.dbase_cable_ampacity = 'DRATA2'
        self.dbase_cable_resistance = 'DROHMPRLUL'
        self.dbase_cable_gmr = 'DGMRSUL'

        self.dbase_cable_concentric_neutral_gmr = 'DNEUSTRNDGMRSUL'
        self.dbase_cable_concentric_neutral_resistance = 'DNEUSTRNDROHM'
        self.dbase_cable_concentric_neutral_diameter = 'DRADSTRNDSUL'
        self.dbase_cable_concentric_neutral_outside_diameter = 'DINSULSUL'
        self.dbase_cable_concentric_neutral_nstrand = 'SNUMNEUSTRND'

        #TODO: Complete all the information I need for OpenDSS in here

        self.dbase_switch_name = 'STNAM'
        self.dbase_switch_index = 'IPTROW'
        self.dbase_switch_ampacity = 'DCURTRATA'

        self.dbase_protection_name = 'STNAM'
        self.dbase_protection_index = 'IDEV'

        self.dbase_transformer_index = 'IPTROW'
        self.dbase_transformer_name = 'STNAM'
        self.dbase_transformer_noload_loss = 'DCORELOSSW'
        self.dbase_transformer_winding_loss = 'DWINDLOSSW'
        self.dbase_transformer_connection = 'IXFRMCON'
        self.dbase_transformer_config_index = 'IXFRMCON'
        self.dbase_transformer_power = 'DNOMKVA'
        self.dbase_transformer_kv_high = 'DPRIKV'
        self.dbase_transformer_kv_low = 'DSECKV'
        self.dbase_transformer_config_name = 'STNAM'
        self.dbase_transformer_qcomp = 'QCOMPEXISTS'
        self.dbase_transformer_resistance = 'DISAT0A_REF' # with a zero
        self.dbase_transformer_reactance = 'DVSAT0PC_REF' # with a zero
        self.dbase_transformer_resistance1 = 'DISAT1A_REF' # with a one
        self.dbase_transformer_reactance1 = 'DVSAT1PC_REF' # with a one

        self.cmp_componant_index = 19
        self.cmp_type_index = 6
        self.cmp_dbase_index = 7 #Index of element in PCLINESPC, PTXFRM etc.
        self.cmp_phase_index = 8
        self.trace_index = 1
        self.cmp_parent_index = 33

        self.cmp_types = { '1': 'source',
                           '4': 'switch', # disconnect switch
                           '5': 'switch', # load break switch
                           '7': 'fuse', # cutout fuse
                           '8': 'fuse',
                           '9': 'recloser', 
                           '13': 'breaker',
                           '22': 'regulator',
                           '24': 'capacitor',
                           '36': 'oh_line-3p',
                           '37': 'oh_line-2p',
                           '38': 'oh_line-1p',
                           '40': 'oh_cable-3p',
                           '41': 'oh_cable-2p',
                           '42': 'oh_cable-1p',
                           '44': 'ug_cable-3p',
                           '45': 'ug_cable-2p',
                           '46': 'ug_cable-1p',
                           '58': 'switch', # elbow switch
                           '61': 'oh_transformer-1p',
                           '65': 'pv',
                           '66': 'ug_transformer-3p',
                           '68': 'ug_transformer-1p',
                           '100': 'fuse',
                           '115': 'load',
                           '98': 'switch', #GOAB
                           '92': 'feeder'
        }
        self.cmp_componants = { 'protection': ['2','6'],
                                'transformer': ['16'],    
                                'capacitor':['32','40'],
                                'line': ['65'],
                                'cable': ['129'],
                                'switch': ['258'],
                                'circuit': ['1024']
        }

        self.cmp_flag = "$CMP"
        self.cmp_name_flag = "$CMPNAM"
        self.cmp_circuit_flag = "$CMPASBUILT"
        self.line_feeder_index = 1

        # Line specific information
        self.cmp_length_flag = "$PCMPLENDATA"
        self.cmp_conductor_flag = "$PCMPCONDDATA"
        self.cmp_open_flag = "$CMPOPER"
        self.cmp_coord_flag = "$PCMPCOORDDATA"
        self.line_trace_index = 1
        self.line_name_index = 1
        self.line_length_index = 2
        self.line_active_index = 2
        self.line_neutral_index = 3
        self.line_first_phase_index = 7
        self.line_has_neutral_index = 10
        #self.line_x_index = 14
        #self.line_y_index = 15
        self.line_x_index = 39
        self.line_y_index = 40
        self.line_x_index2 = 41
        self.line_y_index2 = 42
        self.line_open_index = 5

        # Load specific information
        self.cmp_load_flag = "$PCMPLDDATA"
        self.load_phase_a_p_index = 13
        self.load_phase_b_p_index = 14
        self.load_phase_c_p_index = 15
        self.load_phase_a_q_index = 16
        self.load_phase_b_q_index = 17
        self.load_phase_c_q_index = 18
        self.load_delta_index = 19
        

        # Transformer specific information
        self.transformer_center_tap_names = set(['SinglePh : 3-wireSec'])

        ###

        self.load_types = set(['load'])
        self.transformer_types = set(['oh_transformer-1p','ug_transformer-3p','ug_transformer-1p'])

        self.line_types = set(['switch','fuse','recloser','breaker','oh_line-3p','oh_line-2p','oh_line-1p','oh_cable-3p','oh_cable-2p','oh_cable-1p','ug_cable-3p','ug_cable-2p','ug_cable-1p'])
        self.line_indices = set()
        for idx,name in self.cmp_types.items():
            if name in self.line_types:
                self.line_indices.add(idx)

        self.transformer_indices = set()
        for idx,name in self.cmp_types.items():
            if name in self.transformer_types:
                self.transformer_indices.add(idx)

        self.load_indices = set()
        for idx,name in self.cmp_types.items():
            if name in self.load_types:
                self.load_indices.add(idx)



        super(Reader,self).__init__(**kwargs)

    # Map the name of each componant to the name of it's parent element
    def find_parents(self,model,**kwargs):
        self.node_names = set()
        self.parent_map = {}
        name_trace_map = {}
        for row_idx in range(len(self.dew_data)):
            row = self.dew_data[row_idx]
            entries = [x.strip() for x in row.split(',')]
            if entries[0] == self.cmp_flag:
                trace_index = entries[self.trace_index]
                parent_index = entries[self.cmp_parent_index]

                # Get name
                name_row_idx = row_idx + 1
                name = None
                while True:
                    name_row = self.dew_data[name_row_idx]
                    name_entries = [x.strip() for x in name_row.split(',')]
                    if name_entries[0] == self.cmp_name_flag:
                        name = name_entries[self.line_name_index].strip('"')
                        break
                    elif name_entries[0] == self.cmp_flag:
                        break
                    name_row_idx +=1
                name_trace_map[trace_index] = name

        for row_idx in range(len(self.dew_data)):
            row = self.dew_data[row_idx]
            entries = [x.strip() for x in row.split(',')]
            if entries[0] == self.cmp_flag:
                trace_index = entries[self.trace_index]
                parent_index = entries[self.cmp_parent_index]
                cmp_type = entries[self.cmp_componant_index]


                # Get name
                name_row_idx = row_idx + 1
                name = None
                while True:
                    name_row = self.dew_data[name_row_idx]
                    name_entries = [x.strip() for x in name_row.split(',')]
                    if name_entries[0] == self.cmp_name_flag:
                        name = name_entries[self.line_name_index].strip('"')
                        break
                    elif name_entries[0] == self.cmp_flag:
                        break
                    name_row_idx +=1


                if cmp_type in self.cmp_componants['circuit']:
                    node = Node(model)
                    node.name = name+'_node'
                    node.feeder_name = name #Assume this standard 
                    node.is_substation_connection = True
                    node.setpoint = 1.05
                    self.node_names.add(node.name)
                    meta = Feeder_metadata(model)
                    meta.headnode = node.name
                    

                elif parent_index != '-1':
                    self.parent_map[name] = name_trace_map[parent_index]

#        for componant in self.parent_map.keys():
#            node = Node(model)
#            node.name = 
                        
            


    def parse(self, model, **kwargs):
    
        self.find_parents(model,**kwargs)

        # Call parse from abstract reader class
        super(Reader, self).parse(model, **kwargs)
        return 1

    def parse_transformers(self, model, **kwargs):
        for row_idx in range(len(self.dew_data)):
            row = self.dew_data[row_idx]
            entries = [x.strip() for x in row.split(',')]
            if entries[0] == self.cmp_flag and entries[self.cmp_type_index] in self.transformer_indices:
                x_coord = float(entries[self.line_x_index])
                y_coord = float(entries[self.line_y_index])
                parent_idx = entries[self.cmp_parent_index]
                transformer_index = entries[self.cmp_dbase_index]
                transformer_dbase = self.database[self.database_transformers][self.database[self.database_transformers][self.dbase_transformer_index]== int(transformer_index)]

                transformer = PowerTransformer(model)


                #4 is C, 2 is B, 1 is A => CBA = 7
                transformer_phases = list(map(int,list(format(int(entries[self.cmp_phase_index]),'03b')))) #Map the numbers 1-7 into whether C,B or A phases used.
                transformer_phases = list(itertools.compress(['C','B','A'],transformer_phases))

                # Get feeder name
                feeder_row_idx = row_idx + 1
                while True:
                    feeder_row = self.dew_data[feeder_row_idx]
                    feeder_entries = [x.strip() for x in feeder_row.split(',')]
                    if feeder_entries[0] == self.cmp_circuit_flag:
                        transformer.feeder_name = feeder_entries[self.line_feeder_index].strip('"')
                        break
                    elif feeder_entries[0] == self.cmp_flag:
                        break
                    feeder_row_idx +=1

                # Get transformer name
                name_row_idx = row_idx + 1
                name = None
                while True:
                    name_row = self.dew_data[name_row_idx]
                    name_entries = [x.strip() for x in name_row.split(',')]
                    if name_entries[0] == self.cmp_name_flag:
                        name = name_entries[self.line_name_index].strip('"')
                        break
                    elif name_entries[0] == self.cmp_flag:
                        break
                    name_row_idx +=1

                if name is None:
                    raise ValueError("Transformer with no name found. Aborting.")

                transformer.name = name
                parent = self.parent_map[name]
                parent_node = parent+'_node'
                if not parent_node in self.node_names:
                    node = Node(model)
                    node.name = parent_node
                    position = Position(model)
                    position.lat = x_coord
                    position.long = y_coord
                    node.positions = [position]
                    node.feeder_name = transformer.feeder_name
                self.node_names.add(parent_node) # may already exist in the set but that's ok
                transformer.from_element = parent_node
                transformer.to_element = name+'_node'
                if not transformer.to_element in self.node_names:
                    node = Node(model)
                    node.name = transformer.to_element
                    position = Position(model)
                    position.lat = x_coord
                    position.long = y_coord
                    node.positions = [position]
                    node.feeder_name = transformer.feeder_name
                self.node_names.add(transformer.to_element)

                transformer.noload_loss = float(transformer_dbase[self.dbase_transformer_noload_loss].values[0])/1000.0 # Load loss is in kW
                transformer.load_loss = transformer.noload_loss + float(transformer_dbase[self.dbase_transformer_winding_loss].values[0])/1000.0 # Load loss is in kW in DiTTo I believe (TODO: check this)

                rated_power = float(transformer_dbase[self.dbase_transformer_power].values[0])*1000
                low_voltage = float(transformer_dbase[self.dbase_transformer_kv_low].values[0])*1000
                high_voltage = float(transformer_dbase[self.dbase_transformer_kv_high].values[0])*1000
                qcomp_value = float(transformer_dbase[self.dbase_transformer_qcomp].values[0]) # Not sure why different transformers are created with this parameter
                resistance_value = float(transformer_dbase[self.dbase_transformer_resistance].values[0])
                reactance_value = float(transformer_dbase[self.dbase_transformer_reactance].values[0])

                resistance_value1 = float(transformer_dbase[self.dbase_transformer_resistance1].values[0])
                reactance_value1 = float(transformer_dbase[self.dbase_transformer_reactance1].values[0])

                if qcomp_value == 2:
                    resistance = resistance_value * math.cos(math.radians(reactance_value))
                    reactance = resistance_value * math.sin(math.radians(reactance_value))
                    resistance1 = resistance_value1 * math.cos(math.radians(reactance_value1))
                    reactance1 = resistance_value1 * math.sin(math.radians(reactance_value1))
                else:
                    resistance = resistance_value
                    reactance = reactance_values
                    resistance1 = resistance_value1
                    reactance1 = reactance_values1


                # Configuration index referenced in a different database table
                config_index = float(transformer_dbase[self.dbase_transformer_connection].values[0])
                transformer_dbase_config = self.database[self.database_transformer_api][self.database[self.database_transformer_api][self.dbase_transformer_config_index]== config_index]
                transformer_config_name = transformer_dbase_config[self.dbase_transformer_config_name].values[0]
                windings = []
                if transformer_config_name in self.transformer_center_tap_names:
                    num_windings = 3
                    transformer.is_center_tap = True
                    windings.append(Winding(model))
                    windings.append(Winding(model))
                    windings.append(Winding(model))
                    transformer.reactances = [reactance1+reactance,reactance1,reactance1] #XHL, XLT, XHT. Need to double check this.
                else:
                    num_windings = 2
                    transformer.is_center_tap = False
                    windings.append(Winding(model))
                    windings.append(Winding(model))
                    transformer.reactances = [reactance]
                for w_idx in range(len(windings)):
                    w = windings[w_idx]
                    phase_windings = []
                    for phase in transformer_phases:
                        pw = PhaseWinding(model)
                        pw.phase = phase
                        phase_windings.append(pw)
                    w.phase_windings = phase_windings

                    w.rated_power = rated_power
                    if num_windings == 2:
                        w.resistance = resistance/num_windings
                    if num_windings == 3:
                        if w_idx == 0:
                            w.resistance = resistance/2.0
                        else:
                            w.resistance = resistance
                    if w_idx == 0:
                        w.nominal_voltage = high_voltage
                    else:
                        w.nominal_voltage = low_voltage

                # Assume that the configuration is separated by a ":"
                w1_config = 'Y'
                w2_config = 'Y'

                # Currently don't consider more complicated transformer configurations or Delta-Open etc.
                if 'Del' in transformer_config_name.split(':')[0]:
                    w1_config = 'D'
                if 'Del' in transformer_config_name.split(':')[1]:
                    w2_config = 'D'

                windings[0].connection_type = w1_config
                windings[1].connection_type = w2_config
                if num_windings == 3:
                    windings[2].connection_type = 'Y'
                
                transformer.windings = windings
                




    def parse_loads(self,model, **kwargs):
        for row_idx in range(len(self.dew_data)):
            row = self.dew_data[row_idx]
            entries = [x.strip() for x in row.split(',')]
            if entries[0] == self.cmp_flag and entries[self.cmp_type_index] in self.load_indices:
                parent_idx = entries[self.cmp_parent_index]
                
                #4 is C, 2 is B, 1 is A => CBA = 7
                load_phases = list(map(int,list(format(int(entries[self.cmp_phase_index]),'03b')))) #Map the numbers 1-7 into whether C,B or A phases used.
                load_phases = list(itertools.compress(['C','B','A'],load_phases))

                load = Load(model)

                # Get feeder name
                feeder_row_idx = row_idx + 1
                while True:
                    feeder_row = self.dew_data[feeder_row_idx]
                    feeder_entries = [x.strip() for x in feeder_row.split(',')]
                    if feeder_entries[0] == self.cmp_circuit_flag:
                        load.feeder_name = feeder_entries[self.line_feeder_index].strip('"')
                        break
                    elif feeder_entries[0] == self.cmp_flag:
                        break
                    feeder_row_idx +=1

                # Get load name
                name_row_idx = row_idx + 1
                name = None
                while True:
                    name_row = self.dew_data[name_row_idx]
                    name_entries = [x.strip() for x in name_row.split(',')]
                    if name_entries[0] == self.cmp_name_flag:
                        name = name_entries[self.line_name_index].strip('"')
                        break
                    elif name_entries[0] == self.cmp_flag:
                        break
                    name_row_idx +=1

                # Get spot loads
                load_row_idx = row_idx + 1
                p_a = None
                p_b = None
                p_c = None
                q_a = None
                q_b = None
                q_c = None
                is_delta = False
                while True:
                    load_row = self.dew_data[load_row_idx]
                    load_entries = [x.strip() for x in load_row.split(',')]
                    if load_entries[0] == self.cmp_load_flag:
                        p_a = float(load_entries[self.load_phase_a_p_index].strip('"'))
                        p_b = float(load_entries[self.load_phase_b_p_index].strip('"'))
                        p_c = float(load_entries[self.load_phase_c_p_index].strip('"'))
                        p_a = float(load_entries[self.load_phase_a_q_index].strip('"'))
                        p_b = float(load_entries[self.load_phase_b_q_index].strip('"'))
                        p_c = float(load_entries[self.load_phase_c_q_index].strip('"'))
                        is_delta = bool(load_entries[self.load_delta_index].strip('"'))
                        break
                    elif load_entries[0] == self.cmp_flag:
                        break
                    load_row_idx +=1


                if name is None:
                    raise ValueError("Load with no name found. Aborting.")
                parent = self.parent_map[name]
                parent_node = parent+'_node'
                self.node_names.add(parent_node) # may already exist in the set but that's ok
                load.connecting_element = parent_node
                load.name = name

                if is_delta:
                    load.connection_type = "D"
                else:
                    load.connection_type = "Y"

                phase_loads = []
                for phase in load_phases:
                    phase_load = PhaseLoad(model)
                    phase_load.phase = phase
                    if phase == "A":
                        phase_load.p = p_a
                        phase_load.q = q_a
                    if phase == "B":
                        phase_load.p = p_b
                        phase_load.q = q_b
                    if phase == "C":
                        phase_load.p = p_c
                        phase_load.q = q_c
                    phase_loads.append(phase_load)
                load.phase_loads = phase_loads


    def parse_lines(self,model,**kwargs):
        for row_idx in range(len(self.dew_data)):
            row = self.dew_data[row_idx]
            entries = [x.strip() for x in row.split(',')]

            # Check if it statisfies condition for line. We use the icmp element rather than the bCmpTyp since it contains more information
            if entries[0] == self.cmp_flag and entries[self.cmp_type_index] in self.line_indices: 

                # Whether it's a line, cable or switch
                line_type = entries[self.cmp_componant_index] 
                line = Line(model)

                #Used for switches or when wire information is not available. 4 is C, 2 is B, 1 is A => CBA = 7
                line_phases = list(map(int,list(format(int(entries[self.cmp_phase_index]),'03b')))) #Map the numbers 1-7 into whether C,B or A phases used.
                line_phases = list(itertools.compress(['C','B','A'],line_phases))
                num_phases = len(line_phases)
                line_index = entries[self.cmp_dbase_index]
                line_dbase = self.database[self.database_lines][self.database[self.database_lines][self.dbase_line_index] == int(line_index)]
            
                #TODO: save these
                x_coord = float(entries[self.line_x_index])
                y_coord = float(entries[self.line_y_index])
                x_coord2 = float(entries[self.line_x_index2])
                y_coord2 = float(entries[self.line_y_index2])
                parent = entries[self.cmp_parent_index]
                trace_index = entries[self.line_trace_index]

                # Get line name
                name_row_idx = row_idx + 1
                while True:
                    name_row = self.dew_data[name_row_idx]
                    name_entries = [x.strip() for x in name_row.split(',')]
                    if name_entries[0] == self.cmp_name_flag:
                        line.name = name_entries[self.line_name_index].strip('"')
                        break
                    elif name_entries[0] == self.cmp_flag:
                        break
                    name_row_idx +=1
                        
                # Get line length
                length_row_idx = row_idx + 1
                while True:
                    length_row = self.dew_data[length_row_idx]
                    length_entries = [x.strip() for x in length_row.split(',')]
                    if length_entries[0] == self.cmp_length_flag:
                        line.length = float(length_entries[self.line_length_index])*1000/3.28084 #Length is in thousands of feet. Convert to feet then meters
                        break
                    elif length_entries[0] == self.cmp_flag:
                        break
                    length_row_idx +=1
                        
                # Get feeder name
                feeder_row_idx = row_idx + 1
                while True:
                    feeder_row = self.dew_data[feeder_row_idx]
                    feeder_entries = [x.strip() for x in feeder_row.split(',')]
                    if feeder_entries[0] == self.cmp_circuit_flag:
                        line.feeder_name = feeder_entries[self.line_feeder_index].strip('"')
                        break
                    elif feeder_entries[0] == self.cmp_flag:
                        break
                    feeder_row_idx +=1

                # Get operating status of switch
                open_row_idx = row_idx + 1
                is_open = False
                while True:
                    open_row = self.dew_data[open_row_idx]
                    open_entries = [x.strip() for x in open_row.split(',')]
                    if open_entries[0] == self.cmp_open_flag:
                        is_open = open_entries[self.line_open_index]
                        break
                    elif open_entries[0] == self.cmp_flag:
                        break
                    open_row_idx +=1

                # Get intermediate co-ordinate data
                coord_row_idx = row_idx+1
                all_positions = []
                started_coord = False
                while True:
                    coord_row = self.dew_data[coord_row_idx]
                    coord_entries = [x.strip() for x in coord_row.split(',')]
                    if coord_entries[0] == self.cmp_coord_flag:
                        started_coord = True
                        coord_x = coord_entries[1] # hardcoded these ones
                        coord_y = coord_entries[2] # hardcoded these ones
                        position = Position(model)
                        position.lat = float(coord_x)
                        position.long = float(coord_y)
                        all_positions.append(position)
                    elif started_coord or coord_entries[0] == self.cmp_flag: # Account for having not found any coordinates and having finished the list
                        break
                    coord_row_idx+=1
                line.positions = all_positions

                # Get wire database lookups
                dbase_row_idx = row_idx + 1
                dbase_phase_lookup = -1
                dbase_neutral_lookup = -1
                phases = []
                has_neutral = None
                while True:
                    dbase_row = self.dew_data[dbase_row_idx]
                    dbase_entries = [x.strip() for x in dbase_row.split(',')]
                    if dbase_entries[0] == self.cmp_conductor_flag:
                        dbase_phase_lookup = dbase_entries[self.line_active_index]
                        dbase_neutral_lookup = dbase_entries[self.line_neutral_index]
                        if float(dbase_entries[self.line_neutral_index]) >0:
                            has_neutral = dbase_entries[self.line_has_neutral_index]
                        else:
                            has_neutral = False
                        for idx in range(self.line_first_phase_index,self.line_first_phase_index+3):
                            if int(dbase_entries[idx])!=-1:
                                phases.append(chr(ord('A')+int(dbase_entries[idx])))
                        if len(phases) != num_phases:
                            print('Warning - number of phases in conductor data different from phases in componant listing for '+line.name)
                        break
                    elif dbase_entries[0] == self.cmp_flag:
                        break
                    dbase_row_idx +=1
        

                parent = self.parent_map[line.name]
                parent_node = parent+'_node'
                if not parent_node in self.node_names:
                    node = Node(model)
                    node.name = parent_node
                    node.feeder_name = line.feeder_name
                    if len(line.positions)>0:
                        position = Position(model)
                        position.lat = x_coord
                        position.long = y_coord
                        node.positions = [position]
                self.node_names.add(parent_node) # may already exist in the set but that's ok
                line.from_element = parent_node
                line.to_element = line.name+'_node'
                if not line.to_element in self.node_names:
                    node = Node(model)
                    node.name = line.to_element
                    node.feeder_name = line.feeder_name
                    if len(line.positions)>0:
                        position = Position(model)
                        position.lat = x_coord2
                        position.long = y_coord2
                        node.positions = [position]
                self.node_names.add(line.to_element)



                wires = []
                if line_type in self.cmp_componants['line']:
                    ph_cnt = 0
                    for phase in phases:
                        if int(dbase_phase_lookup) != -1:
                            ph_cnt+=1
                            wire = Wire(model)
                            wire_dbase = self.database[self.database_conductors][self.database[self.database_conductors][self.dbase_conductor_index]==int(dbase_phase_lookup)]
                            wire.nameclass = wire_dbase[self.dbase_conductor_name].values[0]
                            wire.nameclass = wire.nameclass.replace(' ','_')
                            wire.gmr = float(wire_dbase[self.dbase_conductor_gmr].values[0])
                            wire.diameter = 2*float(wire_dbase[self.dbase_conductor_diameter].values[0])
                            wire.ampacity = float(wire_dbase[self.dbase_conductor_ampacity].values[0])
                            wire.resistance = float(wire_dbase[self.dbase_conductor_resistance].values[0])
                            wire.is_switch = 0
                            wire.phase = phase
                            if ph_cnt ==1:
                                wire.X = 0.3048*(float(line_dbase[self.dbase_line_phase1_oh_x]))
                                wire.Y = 0.3048*(float(line_dbase[self.dbase_line_phase1_oh_y]))
                            if ph_cnt ==2:
                                wire.X = 0.3048*(float(line_dbase[self.dbase_line_phase2_oh_x])-float(line_dbase[self.dbase_line_phase1_oh_x]))
                                wire.Y = 0.3048*(float(line_dbase[self.dbase_line_phase2_oh_y])-float(line_dbase[self.dbase_line_phase1_oh_y]))
                            if ph_cnt ==3:
                                wire.X = 0.3048*(float(line_dbase[self.dbase_line_phase3_oh_x])-float(line_dbase[self.dbase_line_phase1_oh_x]))
                                wire.Y = 0.3048*(float(line_dbase[self.dbase_line_phase3_oh_y])-float(line_dbase[self.dbase_line_phase1_oh_y]))

                            wires.append(wire)
                        else:
                            print('Warning - No database information provided for wire')
                    if int(dbase_neutral_lookup) !=-1:
                        wire = Wire(model)
                        wire_dbase = self.database[self.database_conductors][self.database[self.database_conductors][self.dbase_conductor_index]==int(dbase_neutral_lookup)]
                        wire.nameclass = wire_dbase[self.dbase_conductor_name].values[0]
                        wire.nameclass = wire.nameclass.replace(' ','_')
                        wire.gmr = float(wire_dbase[self.dbase_conductor_gmr].values[0])
                        wire.diameter = float(wire_dbase[self.dbase_conductor_diameter].values[0])
                        wire.ampacity = float(wire_dbase[self.dbase_conductor_ampacity].values[0])
                        wire.resistance = float(wire_dbase[self.dbase_conductor_resistance].values[0])
                        wire.is_switch = 0
                        wire.phase = 'N'
                        wire.X = 0.3048*(float(line_dbase[self.dbase_line_neutral_oh_x]) - float(line_dbase[self.dbase_line_phase1_oh_x]))
                        wire.Y = 0.3048*(float(line_dbase[self.dbase_line_neutral_oh_y]) - float(line_dbase[self.dbase_line_phase1_oh_y]))
                        wires.append(wire)

                if line_type in self.cmp_componants['cable']:
                    line.line_type = 'underground'
                    ph_cnt = 0
                    for phase in phases:
                        if int(dbase_phase_lookup) >0:
                            ph_cnt+=1
                            wire = Wire(model)
                            wire_dbase = self.database[self.database_cables][self.database[self.database_cables][self.dbase_cable_index]==int(dbase_phase_lookup)]
                            wire.nameclass = wire_dbase[self.dbase_cable_name].values[0]
                            wire.nameclass = wire.nameclass.replace(' ','_')
                            wire.gmr = float(wire_dbase[self.dbase_cable_gmr].values[0])
                            wire.diameter = 2*float(wire_dbase[self.dbase_cable_diameter].values[0])
                            wire.ampacity = float(wire_dbase[self.dbase_cable_ampacity].values[0])
                            wire.resistance = float(wire_dbase[self.dbase_cable_resistance].values[0])
                            wire.concentric_neutral_gmr = float(wire_dbase[self.dbase_cable_concentric_neutral_gmr].values[0])
                            wire.concentric_neutral_resistance = float(wire_dbase[self.dbase_cable_concentric_neutral_resistance].values[0])
                            wire.concentric_neutral_diameter = float(wire_dbase[self.dbase_cable_concentric_neutral_diameter].values[0])
                            wire.concentric_neutral_outside_diameter = float(wire_dbase[self.dbase_cable_concentric_neutral_outside_diameter].values[0])
                            wire.concentric_neutral_nstrand = int(wire_dbase[self.dbase_cable_concentric_neutral_nstrand].values[0])
                            wire.is_switch = 0
                            wire.phase = phase
                            if ph_cnt ==1:
                                wire.X = 0.3048*(float(line_dbase[self.dbase_line_phase1_oh_x]))
                                wire.Y = 0.3048*(float(line_dbase[self.dbase_line_phase1_oh_y]))
                            if ph_cnt ==2:
                                wire.X = 0.3048*(float(line_dbase[self.dbase_line_phase2_oh_x])-float(line_dbase[self.dbase_line_phase1_oh_x]))
                                wire.Y = 0.3048*(float(line_dbase[self.dbase_line_phase2_oh_y])-float(line_dbase[self.dbase_line_phase1_oh_y]))
                            if ph_cnt ==3:
                                wire.X = 0.3048*(float(line_dbase[self.dbase_line_phase3_oh_x])-float(line_dbase[self.dbase_line_phase1_oh_x]))
                                wire.Y = 0.3048*(float(line_dbase[self.dbase_line_phase3_oh_y])-float(line_dbase[self.dbase_line_phase1_oh_y]))
                            wires.append(wire)
                        else:
                            print('Warning - No database information provided for wire')

                    if int(dbase_neutral_lookup) >0:
                        wire = Wire(model)
                        wire_dbase = self.database[self.database_cables][self.database[self.database_cables][self.dbase_cable_index]==int(dbase_neutral_lookup)]
                        wire.nameclass = wire_dbase[self.dbase_cable_name].values[0]
                        wire.nameclass = wire.nameclass.replace(' ','_')
                        wire.gmr = float(wire_dbase[self.dbase_cable_gmr].values[0])
                        wire.diameter = float(wire_dbase[self.dbase_cable_diameter].values[0])
                        wire.ampacity = float(wire_dbase[self.dbase_cable_ampacity].values[0])
                        wire.resistance = float(wire_dbase[self.dbase_cable_resistance].values[0])
                        wire.concentric_neutral_gmr = float(wire_dbase[self.dbase_cable_concentric_neutral_gmr].values[0])
                        wire.concentric_neutral_resistance = float(wire_dbase[self.dbase_cable_concentric_neutral_resistance].values[0])
                        wire.concentric_neutral_diameter = float(wire_dbase[self.dbase_cable_concentric_neutral_diameter].values[0])
                        wire.concentric_neutral_outside_diameter = float(wire_dbase[self.dbase_cable_concentric_neutral_outside_diameter].values[0])
                        wire.concentric_neutral_nstrand = int(wire_dbase[self.dbase_cable_concentric_neutral_nstrand].values[0])
                        wire.is_switch = 0
                        wire.phase = 'N'
                        wire.X = 0.3048*(float(line_dbase[self.dbase_line_neutral_oh_x]) - float(line_dbase[self.dbase_line_phase1_oh_x]))
                        wire.Y = 0.3048*(float(line_dbase[self.dbase_line_neutral_oh_y]) - float(line_dbase[self.dbase_line_phase1_oh_y]))
                        wires.append(wire)

                if line_type in self.cmp_componants['switch']:
                    switch_dbase = self.database[self.database_switches][self.database[self.database_switches][self.dbase_switch_index]== int(line_type)]
                    line.is_switch = True
                    line.length = 0.1
                    for phase in line_phases:
                        wire = Wire(model)
                        wire.phase = phase
                        wire.is_switch = 1
                        line.is_switch = 1
                        wire.nameclass = switch_dbase[self.dbase_switch_name].values[0]
                        wire.ampacity = float(switch_dbase[self.dbase_switch_ampacity].values[0])
                        wire.is_open = bool(is_open)
                        wire.resistance = self.small_resistance
                        if self.cmp_types[entries[self.cmp_type_index]] == 'fuse':
                            wire.is_fuse = 1
                            line.is_fuse = 1
                        else:
                            wire.is_fuse = 0
                            line.is_fuse = 0

                    pass
                line.wires = wires
                if line_type in self.cmp_componants['protection']:
                    print('Protection not implemented yet. Include as required')
                    pass

