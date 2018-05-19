# coding: utf8

import numpy as np
import math
import cmath
from datetime import datetime
import copy
import networkx as nx
from functools import reduce
import logging

#DiTTo imports
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.power_source import PowerSource
from ditto.models.feeder_metadata import Feeder_metadata

from ditto.network.network import Network

from ditto.writers.abstract_writer import AbstractWriter

logger = logging.getLogger(__name__)

class Writer(AbstractWriter):
    '''
        DiTTo--->CYME Writer class

        Author: Nicolas Gensollen. October 2017

    '''
    def __init__(self, **kwargs):
        '''
            Class CONSTRUCTOR.
        '''

        #Call super
        super(Writer, self).__init__(**kwargs)


        self.logger.info('DiTTo--->CYME writer successfuly instanciated.')

    def connection_configuration_mapping(self, value):
        '''
            Map the connection configuration from DiTTo to CYME.

            **Mapping:**

            +----------+----------------+------------+
            |   Value  |       CYME     |  DiTTo     |
            +==========+================+============+
            | 0 or '0' |       'Yg'     |   'Y'      |
            +----------+----------------+------------+
            | 2 or '2' |     'Delta'    |   'D'      |
            +----------+----------------+------------+
            | 5 or '5' |      'Zg'      |   'Z'      |
            +----------+----------------+------------+
        '''
        if value=='Y':return '0'
        elif value=='D':return '2'
        elif value=='Z':return '5'
        else: raise ValueError('Unknown configuration {}'.format(value))


    def transformer_connection_configuration_mapping(self, value1, value2):
        '''
            Map the connection configuration for transformer (2 windings) objects from CYME to DiTTo.

            :param value: CYME value (either string or id)
            :type value: int or str
            :param winding: Number of the winding (0 or 1)
            :type winding: int
            :returns: DiTTo connection configuration for the requested winding
            :rtype: str

            **Mapping:**

            +----------+----------------+------------+
            |   Value  |       CYME     |  DiTTo     |
            +----------+----------------+-----+------+
            |          |                | 1st | 2nd  |
            +==========+================+=====+======+
            | 0 or '0' |      'Y_Y'     | 'Y' | 'Y'  |
            +----------+----------------+-----+------+
            | 1 or '1' |      'D_Y'     | 'D' | 'Y'  |
            +----------+----------------+-----+------+
            | 2 or '2' |      'Y_D'     | 'Y' | 'D'  |
            +----------+----------------+-----+------+
            | 4 or '4' |      'D_D'     | 'D' | 'D'  |
            +----------+----------------+-----+------+
            |11 or '11'|     'Yg_Zg'    | 'Y' | 'Z'  |
            +----------+----------------+-----+------+
            |12 or '12'|     'D_Zg'     | 'D' | 'Z'  |
            +----------+----------------+-----+------+
        '''
        #if 'Z' not in value1 and 'Z' not in value2:
        #    return value1+'_'+value2
        if value1=='Y' and value2=='Y':
            return '0'
        elif value1=='D' and value2=='Y':
            return '1'
        elif value1=='Y' and value2=='D':
            return '2'
        elif value1=='D' and value2=='D':
            return '4'
        elif value1=='Y' and value2=='Z':
            return '11'#return 'Yg_Zg'
        elif value1=='D' and value2=='Z':
            return '12'#return 'D_Zg'
        else:
            raise ValueError('Unknown connection configuration for {v1} (wdg1) and {v2} (wdg2)'.format(v1=value1, v2=value2))



    def merge_regulators(self, regulators):
        '''
            Merge a list of regulator strings such that there is only one regulator per section.
            The purpose of this is to merge all the single phase regulators on the same sections into multi-phase regulators.
        '''
        section_reg={}
        for reg in regulators:
            if reg.split(',')[0] in section_reg:
                section_reg[reg.split(',')[0]]=self.merge(section_reg[reg.split(',')[0]],reg)
            else:
                section_reg[reg.split(',')[0]]=reg

        return section_reg.values()



    def merge(self, string1,string2):
        '''
            Helper function for merge_regulators.
        '''
        s1=string1.split(',')
        s2=string2.split(',')
        if len(s1)!=len(s2):
            raise ValueError('Unable to merge {s1} and {s2}'.format(s1=s1,s2=s2))
        new_string=''
        phase_combinations=['A','B','C','AB','AC','BA','BC','CB','CA']
        for x,y in zip(s1,s2):
            if x==y: new_string+=x
            elif x in phase_combinations and y in phase_combinations: new_string+=''.join(sorted(x+y))
            elif x=='0' and y!='0': new_string+=y
            elif y=='0' and x!='0': new_string+=x
            new_string+=','

        return new_string[:-1]


    def get_center_tap_impedances(self,R0,R1,R2,XHL,XHT,XLT,KVA_BASE):
        '''
            Computes the impedance and XR ratio for center tap transformers modelled as three windings transformers.
        '''
        RT=R0*2.0
        #RT=R0*4.0 #Shell type
        X0=(XHL+XHT-XLT)/2.0
        XT=10.0/8.0*X0
        #XT=-1.0/0.6*X0 #Shell type
        _ZT_=math.sqrt(RT**2+XT**2)
        #perct_ZT=(100*_ZT_)/float(KVA_BASE)
        return XT/RT,_ZT_



    def write(self, model, **kwargs):
        '''
            General write function. Responsible for calling the sub-parsers.

            .. note::

            write_network_file must be called before write_equipment_file since the linecodes dictionary is built here and is needed for the equipment file.
        '''
        self.section_line_list=[]
        self.node_string_list=[]
        self.nodeID_list=[]
        self.sectionID_list=[]
        self.section_feeder_mapping={}
        self.section_line_feeder_mapping={}
        self.section_headnode_mapping={}

        #Verbose print the progress
        if 'verbose' in kwargs and isinstance(kwargs['verbose'], bool):
            self.verbose=kwargs['verbose']
        else:
            self.verbose=False

        #Writing the load file
        if self.verbose: self.logger.info('Writing the load file...')
        self.write_load_file(model, **kwargs)

        #Writing the network file
        if self.verbose: logger.info('Writing the network file...')
        self.write_network_file(model, **kwargs)

        #Writing the equipment file
        if self.verbose: logger.info('Writing the equipment file...')
        self.write_equipment_file(model, **kwargs)



    def write_network_file(self, model, **kwargs):
        '''
            Loop over DiTTo objects and write the corresponding CYME network file.

            .. note::

            This must be called before write_equipment_file since the linecodes dictionary is built here and is needed for the equipment file.
        '''
        model.set_names()
        #Output network file
        output_file=self.output_path+'/network.txt'

        #Lists for storing strings
        source_string_list=[]
        overhead_string_list=[]
        overhead_byphase_string_list = []
        underground_string_list=[]
        switch_string_list=[]
        fuse_string_list=[]
        recloser_string_list=[]
        breaker_string_list=[]
        capacitor_string_list=[]
        two_windings_transformer_string_list=[]
        three_windings_transformer_string_list=[]
        regulator_string_list=[]

        #The linecodes dictionary is used to group lines which have the same properties
        #(impedance matrix, ampacity...)
        #This dictionary will be outputed in write_equipment_file
        ID=0
        self.linecodes_overhead={}
        ID_cable=0
        self.cablecodes={}
        ID_cap=0
        self.capcodes={}
        ID_trans=0
        self.two_windings_trans_codes={}
        ID_reg=0
        self.reg_codes={}
        ID_trans_3w=0
        self.three_windings_trans_codes={}
        ID_cond=0
        self.conductors={}
        self.switchcodes = {}
        self.fusecodes = {}
        self.reclosercodes = {}
        self.breakercodes = {}

        intermediate_nodes=[]

        self.sources={}

        self.substations=[]

        #Open the output file...
        with open(output_file, 'w') as f:

            #before doing anything, we need to get all transformers that have a regulator connected to them
            #In CYME, Regulators do not need to have a transformer object, so we need to ignore the transformers with regulators
            self.transformers_to_ignore=[i.connected_transformer for i in model.models if isinstance(i, Regulator)]

            #Loop over the DiTTo objects
            for i in model.models:

                if hasattr(i,'drop') and i.drop==1:
                    continue

                #If we get a PowerSource object
                #
                if isinstance(i, PowerSource):
                    #Check that the PowerSouce object is an external power source
                    if hasattr(i, 'is_sourcebus') and i.is_sourcebus==1:
                        #Empty new source string
                        new_source_string=''
                        self.substations.append({})

                        if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                            self.sources[i.connecting_element]=None
                            new_source_string+=i.connecting_element
                            self.substations[-1]['connecting_element']=i.connecting_element
                        else:
                            continue

                        if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                            new_source_string+=','+str(i.nominal_voltage*10**-3)
                            self.sources[i.connecting_element]=str(i.nominal_voltage*10**-3)
                            self.substations[-1]['KVLL']=str(i.nominal_voltage*10**-3)
                        else:
                            new_source_string+=','

                        if hasattr(i, 'phase_angle') and i.phase_angle is not None:
                            new_source_string+=','+str(i.phase_angle)
                            new_source_string+=','+str(i.phase_angle-120)
                            new_source_string+=','+str(i.phase_angle+120)
                            self.substations[-1]['phase_angle']=str(i.phase_angle)
                        else:
                            new_source_string+=',,,'

                        if hasattr(i, 'positive_sequence_impedance') and i.positive_sequence_impedance is not None:
                            new_source_string+=','+str(i.positive_sequence_impedance.real)+','+str(i.positive_sequence_impedance.imag)
                            self.substations[-1]['R1']=str(i.positive_sequence_impedance.real)
                            self.substations[-1]['X1']=str(i.positive_sequence_impedance.imag)
                        else:
                            new_source_string+=',,'

                        if hasattr(i, 'zero_sequence_impedance') and i.zero_sequence_impedance is not None:
                            new_source_string+=','+str(i.zero_sequence_impedance.real)+','+str(i.zero_sequence_impedance.imag)
                            self.substations[-1]['R0']=str(i.zero_sequence_impedance.real)
                            self.substations[-1]['X0']=str(i.zero_sequence_impedance.imag)
                        else:
                            new_source_string+=',,'

                        if hasattr(i, 'negative_sequence_impedance') and i.negative_sequence_impedance is not None:
                            new_source_string+=','+str(i.negative_sequence_impedance.real)+','+str(i.negative_sequence_impedance.imag)
                        elif hasattr(i, 'zero_sequence_impedance') and i.zero_sequence_impedance is not None:
                            new_source_string+=','+str(i.zero_sequence_impedance.real)+','+str(i.zero_sequence_impedance.imag)
                        else:
                            new_source_string+=',,'

                        #OperatingVoltages
                        try:
                            new_source_string+=',{v},{v},{v},0'.format(v=i.nominal_voltage*10**-3)
                        except:
                            new_source_string+=',,,,0'
                            pass

                        if hasattr(i, 'rated_power') and i.rated_power is not None:
                            self.substations[-1]['MVA']=str(i.rated_power*10**-6)

                        if new_source_string!='':
                            source_string_list.append(new_source_string)


                #If we get a Node object
                #
                if isinstance(i, Node):

                    #Empty new node string
                    new_node_string=''

                    #Name
                    if hasattr(i, 'name') and i.name is not None:
                        new_node_string+=i.name
                        self.nodeID_list.append(i.name)
                    else:
                        continue

                    #CoordX and CoordY
                    if hasattr(i, 'positions') and i.positions is not None:
                        try:
                            new_node_string+=','+str(i.positions[0].long)
                        except:
                            new_node_string+=',0'
                            pass

                        try:
                            new_node_string+=','+str(i.positions[0].lat)
                        except:
                            new_node_string+=',0'
                            pass
                    else:
                        new_node_string+=',0,0'

                    #Add the node string to the list
                    if new_node_string!='':
                        self.node_string_list.append(new_node_string)



                #If we get a Line object
                #
                if isinstance(i, Line):

                    matching_list={'overhead': overhead_string_list,
                                   'by_phase': overhead_byphase_string_list,
                                   'underground': underground_string_list,
                                   'switch': switch_string_list,
                                   'fuse': fuse_string_list,
                                   'recloser': recloser_string_list,
                                   'breaker': breaker_string_list,
                                   }

                    #Empty new strings for sections and overhead lines
                    new_section_line=''
                    new_line_string=''
                    line_type='overhead' #Line type is set to overhead by default

                    #Name
                    if hasattr(i, 'name') and i.name is not None:

                        #Get the type
                        #
                        #(In DiTTo, a line object can be used to represent overhead and underground lines,
                        # as well as switches and fuses).
                        #
                        if hasattr(i, 'line_type'):

                            #if i.line_type is None:

                            #Fuses and reclosers are modelled in OpenDSS as an object monitoring a line.
                            #In RNM, this dummy line is actually a switch, meaning that we have in DiTTo
                            #line objects where is_switch==1 AND is_fuse==1 (or is_recloser==1)
                            #We want to output these as fuses or reclosers, not as switches
                            #Hence the following:
                            #if hasattr(i, 'is_fuse') and i.is_fuse==1:
                            #    line_type='fuse'

                            #elif hasattr(i, 'is_recloser') and i.is_recloser==1:
                            #    line_type='recloser'
                            #ONLY if line is not a fuse nor a recloser, but is a switch do we output a switch...
                            #elif hasattr(i, 'is_switch') and i.is_switch==1:
                            #    line_type='switch'

                            if i.line_type.lower()=='underground':
                                line_type='underground'

                        if hasattr(i, 'is_fuse') and i.is_fuse==1:
                            line_type='fuse'

                        elif hasattr(i, 'is_recloser') and i.is_recloser==1:
                            line_type='recloser'

                        elif hasattr(i, 'is_breaker') and i.is_breaker==1:
                            line_type = 'breaker'

                        #ONLY if line is not a fuse nor a recloser, but is a switch do we output a switch...
                        elif hasattr(i, 'is_switch') and i.is_switch==1:
                            line_type='switch'


                        #From element for sections
                        if hasattr(i, 'from_element') and i.from_element is not None and hasattr(i, 'to_element') and i.to_element is not None:
                            new_sectionID='{f}_{t}'.format(f=i.from_element,t=i.to_element)
                            new_line_string+=new_sectionID
                            new_section_line='{id},{f},{t}'.format(id=new_sectionID,f=i.from_element,t=i.to_element)
                            if hasattr(i, 'feeder_name') and i.feeder_name is not None:
                                if i.feeder_name in self.section_feeder_mapping:
                                    self.section_feeder_mapping[i.feeder_name].append(new_sectionID)
                                else:
                                    self.section_feeder_mapping[i.feeder_name]=[new_sectionID]
                                if hasattr(i, 'substation_name') and i.substation_name is not None:
                                    self.section_headnode_mapping[i.feeder_name]=i.substation_name
                        else:
                            raise ValueError('Line {name} does not have from and to.'.format(name=i.name))

                        if hasattr(i, 'positions') and i.positions is not None and len(i.positions)>0:
                            for seg_number,position in enumerate(i.positions):
                                intermediate_nodes.append([new_sectionID,seg_number,position.long,position.lat])

                        #Phases of the section
                        #
                        new_section_line+=','
                        phases=[]
                        cond_id={}
                        if hasattr(i, 'wires') and i.wires is not None:
                            i.wires=[w for w in i.wires if w.drop!=1]
                            for wire in i.wires:

                                if hasattr(wire, 'phase') and wire.phase is not None:
                                    #Do not count the neutral(s)...
                                    if wire.phase in ['A','B','C']:
                                        new_section_line+=wire.phase
                                        phases.append(wire.phase)

                                new_code=''
                                if hasattr(wire, 'diameter') and wire.diameter is not None:
                                    new_code+=',{}'.format(wire.diameter)
                                else:
                                    new_code+=','

                                if hasattr(wire, 'gmr') and wire.gmr is not None:
                                    new_code+=',{}'.format(wire.gmr)
                                else:
                                    new_code+=','

                                if hasattr(wire, 'ampacity') and wire.ampacity is not None:
                                    new_code+='{},'.format(wire.ampacity)
                                else:
                                    new_code+=','

                                if hasattr(wire, 'emergency_ampacity') and wire.emergency_ampacity is not None:
                                    new_code+='{}'.format(wire.emergency_ampacity)

                                #if line_type=='underground':
                                #If we have a name for the wire, we use it as the equipment id
                                if hasattr(wire,'nameclass') and wire.nameclass is not None:
                                    wire_name=wire.nameclass
                                    #If not already in the conductors dictionary, add it
                                    if wire_name not in self.conductors:
                                        self.conductors[wire_name]=new_code
                                    cond_id[wire.phase]=wire_name
                                #If we do not have a name for the wire, we create one:
                                #The IDs will be wire_1, wire_2,...
                                else:
                                    found=False
                                    #Try to find if we already have the conductor stored
                                    for key,value in self.conductors.items():
                                        if value==new_code:
                                            cond_id[wire.phase]=key
                                            found=True
                                    #If not, create it
                                    if not found:
                                        ID_cond+=1
                                        self.conductors['conductor_{}'.format(ID_cond)]=new_code
                                        cond_id[wire.phase]=ID_cond

                        #Impedance matrix
                        #
                        #Here, we group lines that have the same characteristics:
                        #R0,R1,X0,X1,ampacity
                        #We create am ID for these lines (Here a simple integer)
                        #
                        #If we have a switch, we just use default because there is no way (to my knowledge)
                        #to provide the impedance matrix for a switch in CYME
                        if line_type=='switch':
                            if i.nameclass is not None and i.nameclass!='' and i.wires[0].ampacity is not None and i.nominal_voltage is not None:
                                new_code2 = '{amps},{amps},{amps},{amps},{amps},{kvll},0,,,,,,,,0,0,0,0,0,'.format(amps=i.wires[0].ampacity,kvll=i.nominal_voltage*10**-3)

                                if i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity)) not in self.switchcodes:
                                    self.switchcodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                                elif self.switchcodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]!=new_code2:
                                    found = False
                                    for k,v in self.switchcodes.items():
                                        if new_code2==v:
                                            new_line_string+=','+str(k)
                                            found = True
                                    if not found:
                                        self.switchcodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                        new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))
                                else:
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                            else:
                                new_line_string+=',DEFAULT'

                        elif line_type=='fuse':
                            if i.nameclass is not None and i.nameclass!='' and i.wires[0].ampacity is not None and i.nominal_voltage is not None:
                                new_code2 = '{amps},{amps},{amps},{amps},{amps},{kvll},0,600.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,0,,,,'.format(amps=i.wires[0].ampacity,kvll=i.nominal_voltage*10**-3)

                                if i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity)) not in self.fusecodes:
                                    self.fusecodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                                elif self.fusecodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]!=new_code2:
                                    found = False
                                    for k,v in self.fusecodes.items():
                                        if new_code2==v:
                                            new_line_string+=','+str(k)
                                            found = True
                                    if not found:
                                        self.fusecodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                        new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))
                                else:
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                            else:
                                new_line_string+=',DEFAULT'

                        elif line_type=='recloser':
                            if i.nameclass is not None and i.nameclass!='' and i.wires[0].ampacity is not None and i.nominal_voltage is not None:
                                new_code2 = '{amps},{amps},{amps},{amps},{amps},{kvll},0,600.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,0,0,0,0,,1,,'.format(amps=i.wires[0].ampacity,kvll=i.nominal_voltage*10**-3)

                                if i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity)) not in self.reclosercodes:
                                    self.reclosercodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                                elif self.reclosercodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]!=new_code2:
                                    found = False
                                    for k,v in self.reclosercodes.items():
                                        if new_code2==v:
                                            new_line_string+=','+str(k)
                                            found = True
                                    if not found:
                                        self.reclosercodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                        new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))
                                else:
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                            else:
                                new_line_string+=',DEFAULT'

                        elif line_type=='breaker':
                            if i.nameclass is not None and i.nameclass!='' and i.wires[0].ampacity is not None and i.nominal_voltage is not None:
                                new_code2 = '{amps},{amps},{amps},{amps},{amps},{kvll},0,600.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,0,0,0,0,'.format(amps=i.wires[0].ampacity,kvll=i.nominal_voltage*10**-3)

                                if i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity)) not in self.breakercodes:
                                    self.breakercodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                                elif self.breakercodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]!=new_code2:
                                    found = False
                                    for k,v in self.breakercodes.items():
                                        if new_code2==v:
                                            new_line_string+=','+str(k)
                                            found = True
                                    if not found:
                                        self.breakercodes[i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))]=new_code2
                                        new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))
                                else:
                                    new_line_string+=','+i.nameclass+'_'+str(int(i.nominal_voltage))+'_'+str(int(i.wires[0].ampacity))

                            else:
                                new_line_string+=',DEFAULT'

                        elif line_type=='underground':
                            tt={}
                            if hasattr(i, 'impedance_matrix') and i.impedance_matrix is not None:
                                try:
                                    zero_seq_imp=i.impedance_matrix[0][0]
                                except:
                                    try:
                                        zero_seq_imp=i.impedance_matrix[0]
                                    except:
                                        raise ValueError('Cannot get a value from impedance matrix for line {}'.format(i.name))
                                coeff=10**3
                                tt['R0']=zero_seq_imp.real*coeff
                                tt['X0']=zero_seq_imp.imag*coeff
                                try:
                                    pos_seq_imp=i.impedance_matrix[1][1]
                                    tt['R1']=pos_seq_imp.real*coeff
                                    tt['X1']=pos_seq_imp.imag*coeff
                                except:
                                    tt['R1']=tt['R0']
                                    tt['X1']=tt['X0']
                                    pass
                                try:
                                    neg_seq_imp=i.impedance_matrix[2][2]
                                    tt['R2']=neg_seq_imp.real*coeff
                                    tt['X2']=neg_seq_imp.imag*coeff
                                except:
                                    tt['R2']=tt['R1']
                                    tt['X2']=tt['X1']
                                    pass
                                tt['B1']=0
                                tt['B0']=0
                                try:
                                    tt['amps']=i.wires[0].ampacity
                                except:
                                    tt['amps']=0
                                    pass

                                if hasattr(i.wires[0],'nameclass') and i.wires[0].nameclass is not None:
                                        cable_name=i.wires[0].nameclass
                                        self.cablecodes[cable_name]=tt
                                        new_line_string+=','+cable_name
                                else:
                                    if len(self.cablecodes)==0:
                                        ID_cable+=1
                                        self.cablecodes['cable'+str(ID_cable)]=tt
                                        new_line_string+=',cable_'+str(ID_cable)
                                    else:
                                        found=False
                                        for k,v in self.cablecodes.items():
                                            if v==tt:
                                                new_line_string+=',cable_'+str(k)
                                                found=True
                                        if not found:
                                            ID_cable+=1
                                            self.cablecodes['cable'+str(ID_cable)]=tt
                                            new_line_string+=',cable_'+str(ID_cable)

                        elif hasattr(i, 'impedance_matrix') and i.impedance_matrix is not None:
                            #try:
                            tt={}
                            if 'A' in cond_id:
                                tt['CondID_A']=cond_id['A']
                            else:
                                tt['CondID_A']='NONE'
                            if 'B' in cond_id:
                                tt['CondID_B']=cond_id['B']
                            else:
                                tt['CondID_B']='NONE'
                            if 'C' in cond_id:
                                tt['CondID_C']=cond_id['C']
                            else:
                                tt['CondID_C']='NONE'
                            if 'N' in cond_id:
                                tt['CondID_N']=cond_id['N']
                            else:
                                tt['CondID_N']='NONE'
                            if 'N1' in cond_id:
                                tt['CondID_N1']=cond_id['N1']
                            else:
                                tt['CondID_N1']='NONE'
                            if 'N2' in cond_id:
                                tt['CondID_N2']=cond_id['N2']
                            else:
                                tt['CondID_N2']='NONE'

                            if hasattr(i, 'wires') and i.wires is not None:
                                for wire in i.wires:
                                    if hasattr(wire, 'phase') and str(wire.phase) in ['A','B','C']:
                                        p=str(wire.phase)
                                        if hasattr(wire, 'ampacity') and wire.ampacity is not None:
                                            try:
                                                tt['Amps{}'.format(p)]=wire.ampacity
                                            except:
                                                tt['Amps{}'.format(p)]='DEFAULT'
                                                pass


                            #If we have 3 phases, use OVERHEADLINE SETTING
                            if len(phases)==3:

                                tt.update({'SpacingID':'DEFAULT','Ba':0,'Bb':0,'Bc':0,'UserDefinedImpedances':1})

                                for k,p1 in enumerate(phases):
                                    for j,p2 in enumerate(phases):
                                        if j==k:
                                            tt['R{p}'.format(p=p1)]=i.impedance_matrix[k][j].real*10**3
                                            tt['X{p}'.format(p=p1)]=i.impedance_matrix[k][j].imag*10**3
                                        elif j>k:
                                            if p1=='A' and p2=='C':
                                                tt['MutualResistanceCA']=i.impedance_matrix[k][j].real*10**3
                                                tt['MutualReactanceCA']=i.impedance_matrix[k][j].imag*10**3
                                            else:
                                                tt['MutualResistance{p1}{p2}'.format(p1=p1,p2=p2)]=i.impedance_matrix[k][j].real*10**3
                                                tt['MutualReactance{p1}{p2}'.format(p1=p1,p2=p2)]=i.impedance_matrix[k][j].imag*10**3

                                if hasattr(i,'nameclass') and i.nameclass is not None:
                                    line_nameclass=i.nameclass
                                    self.linecodes_overhead[line_nameclass]=tt
                                    new_line_string+=','+line_nameclass
                                else:
                                    #If the linecode dictionary is empty, just add the new element
                                    if len(self.linecodes_overhead)==0:
                                        ID+=1
                                        self.linecodes_overhead[ID]=tt
                                        new_line_string+=',line_'+str(ID)

                                    #Otherwise, loop over the dict to find a matching linecode
                                    else:
                                        found=False
                                        for k,v in self.linecodes_overhead.items():
                                            if v==tt:
                                                new_line_string+=',line_'+str(k)
                                                found=True
                                        if not found:
                                            ID+=1
                                            self.linecodes_overhead['line_'+str(ID)]=tt
                                            new_line_string+=',line_'+str(ID)

                            #If we have less than 3 phases, then use a BY_PHASE configuration
                            else:
                                line_type = 'by_phase' #Change the line_type to write the line under the proper header

                                #Add device number and phase conductor IDs
                                new_line_string += ',{device},{condIDA},{condIDB},{condIDC}'.format(device=new_sectionID, condIDA=tt['CondID_A'], condIDB=tt['CondID_B'], condIDC=tt['CondID_C'])
                                
                                #Add neutral conductor IDs
                                #
                                #If we have valid IDs for BOTH N1 and N2, then use that
                                if tt['CondID_N1'] != 'NONE' and tt['CondID_N2'] != 'NONE':
                                    new_line_string += ',{condIDN1},{condIDN2}'.format(condIDN1=tt['CondID_N1'], condIDN2=tt['CondID_N2'])
                                #Otherwise, if we have a valid ID for N, then use that as condIDN1 and use whatever we have for N2
                                elif tt['CondID_N'] != 'NONE':
                                    new_line_string += ',{condIDN1},{condIDN2}'.format(condIDN1=tt['CondID_N'], condIDN2=tt['CondID_N2'])
                                #Otherwise, do as for case 1
                                else:
                                    new_line_string += ',{condIDN1},{condIDN2}'.format(condIDN1=tt['CondID_N1'], condIDN2=tt['CondID_N2'])


                                #Use Default spacing 
                                #
                                #TODO: User-defined spacing support
                                #
                                if len(phases) ==1:
                                    new_line_string += ',N_ABOVE_1PH'
                                if len(phases) == 2:
                                    new_line_string += ',N_ABOVE_2PH'
                                if len(phases) == 3:
                                    new_line_string += ',N_ABOVE_3PH'

                            

                        #Length
                        if hasattr(i, 'length') and i.length is not None:
                            if line_type!='switch' and line_type!='fuse' and line_type!='recloser' and line_type!='breaker':
                                try:
                                    new_line_string+=','+str(i.length)
                                except:
                                    new_line_string+=','
                                    pass
                        else:
                            if line_type!='switch' and line_type!='fuse' and line_type!='recloser' and line_type!='breaker':
                                new_line_string+=','


                        if line_type=='switch' or line_type == 'breaker':
                            closed_phase=np.sort([wire.phase for wire in i.wires if wire.is_open==0 and wire.phase not in ['N','N1','N2']])
                            if len(closed_phase)==0:
                                new_line_string+=',M,None,0'
                            else:
                                new_line_string+=',M,{},0'.format(reduce(lambda x,y:x+y,closed_phase))

                        if line_type=='fuse' or line_type=='recloser':
                            closed_phase=np.sort([wire.phase for wire in i.wires if wire.phase not in ['N','N1','N2']])
                            new_line_string+=',M,{},0'.format(reduce(lambda x,y:x+y,closed_phase))


                        #ConnectionStatus
                        new_line_string+=',0' #Assumes the line is connected because there is no connected field in DiTTo

                        #DeviceNumber
                        if line_type=='switch' or line_type=='fuse' or line_type=='recloser' or line_type=='breaker':
                            new_line_string+=','+new_sectionID

                        if line_type=='underground':
                            new_line_string+=',10,2' #DistanceBetweenConductors, CableConfiguration

                        #Add the strings to the lists
                        #
                        if new_section_line!='':
                            try:
                                self.section_line_list.append(new_section_line)
                                if hasattr(i,'feeder_name') and i.feeder_name is not None:
                                    if i.feeder_name in self.section_line_feeder_mapping:
                                        self.section_line_feeder_mapping[i.feeder_name].append(new_section_line)
                                    else:
                                        self.section_line_feeder_mapping[i.feeder_name]=[new_section_line]
                            except:
                                pass

                        if new_line_string!='':
                            try:
                                matching_list[line_type].append(new_line_string)
                            except:
                                pass



                #If we get a Capacitor object
                #
                if isinstance(i, Capacitor):

                    #Empty new capacitor string
                    new_capacitor_line=''
                    new_capacitor_object_line=''

                    #Connecting element
                    #We need to create a new section since there is no physical line connecting
                    #capacitors to the rest of the feeder in DiTTo, but CYME needs a section for this
                    new_section=None
                    if hasattr(i, 'name') and i.name is not None and hasattr(i, 'connecting_element') and i.connecting_element is not None:
                        try:
                            new_section_ID='{f}_{t}'.format(f=i.connecting_element,t=i.name)
                            new_section='{f}_{t},{f},{t},'.format(f=i.connecting_element,t=i.name)
                            new_capacitor_line+=new_section_ID
                            if i.connecting_element not in self.nodeID_list:
                                self.nodeID_list.append(i.connecting_element)
                                self.node_string_list.append('{},0,0'.format(i.connecting_element))
                            if i.name not in self.nodeID_list:
                                if hasattr(i,'positions') and i.positions is not None:
                                    try:
                                        X=i.positions[0].long
                                        Y=i.positions[0].lat
                                    except:
                                        X=0;Y=0
                                        pass
                                else:
                                    X=0;Y=0
                                self.nodeID_list.append(i.name)
                                self.node_string_list.append('{name},{X},{Y}'.format(name=i.name,X=X,Y=Y))
                            if hasattr(i, 'feeder_name') and i.feeder_name is not None:
                                if i.feeder_name in self.section_feeder_mapping:
                                    self.section_feeder_mapping[i.feeder_name].append(new_sectionID)
                                else:
                                    self.section_feeder_mapping[i.feeder_name]=[new_sectionID]
                                if hasattr(i, 'substation_name') and i.substation_name is not None:
                                    self.section_headnode_mapping[i.feeder_name]=i.substation_name
                        except:
                            continue


                    #Connection type
                    if hasattr(i, 'connection_type') and i.connection_type is not None:
                        try:
                            new_capacitor_line+=','+i.connection_type
                        except:
                            new_capacitor_line+=','
                            pass


                    #KVAR and Phase
                    phases=[]
                    if hasattr(i, 'phase_capacitors') and i.phase_capacitors is not None:
                        #new_capacitor_line+=','
                        for phase_capacitor in i.phase_capacitors:
                            if hasattr(phase_capacitor, 'phase') and phase_capacitor.phase is not None:
                                phases.append(phase_capacitor.phase)
                                if new_section is not None:
                                    new_section+=str(phase_capacitor.phase)

                        if hasattr(phase_capacitor, 'var') and phase_capacitor.var is not None:
                            try:
                                new_capacitor_object_line+=str(phase_capacitor.var*10**-3)+','
                            except:
                                new_capacitor_object_line+=','
                                pass


                    #KV
                    if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                        try:
                            if len(phases)==1:
                                new_capacitor_line+=','+str(i.nominal_voltage*10**-3)
                                new_capacitor_object_line+=str(i.nominal_voltage*10**-3)+','
                            else:
                                new_capacitor_line+=','+str(i.nominal_voltage*10**-3/math.sqrt(3))
                                new_capacitor_object_line+=str(i.nominal_voltage*10**-3/math.sqrt(3))+','
                        except:
                            new_capacitor_line+=','
                            new_capacitor_object_line+=','
                            pass

                    found=False
                    for k,d in self.capcodes.items():
                        if d==new_capacitor_object_line:
                            new_capacitor_line+=','+new_section_ID+',capacitor_'+str(k)
                            found=True
                    if not found:
                        ID_cap+=1
                        self.capcodes[ID_cap]=new_capacitor_object_line
                        new_capacitor_line+=','+new_section_ID+',capacitor_'+str(ID_cap)

                    new_capacitor_line+=',S,0' #Location and ConnectionStatus


                    if new_capacitor_line!='':
                        capacitor_string_list.append(new_capacitor_line)

                    if new_section is not None:
                        self.section_line_list.append(new_section)
                        if hasattr(i,'feeder_name') and i.feeder_name is not None:
                            if i.feeder_name in self.section_line_feeder_mapping:
                                self.section_line_feeder_mapping[i.feeder_name].append(new_section)
                            else:
                                self.section_line_feeder_mapping[i.feeder_name]=[new_section]


                #If we get a Regulator
                #
                if isinstance(i, Regulator) and not (hasattr(i,'ltc') and i.ltc is not None and i.ltc):

                    new_regulator_string=''
                    new_regulator_object_line=''

                    #We need to get bus1 and bus2 to create the section bus1_bus2
                    new_section=None
                    new_section_ID=None
                    if hasattr(i, 'from_element') and i.from_element is not None and hasattr(i, 'to_element') and i.to_element is not None:
                        #try:
                        new_section='{f}_{t},{f},{t},'.format(f=i.from_element,t=i.to_element)
                        new_section_ID='{f}_{t}'.format(f=i.from_element,t=i.to_element)
                        if hasattr(i, 'feeder_name') and i.feeder_name is not None:
                            if i.feeder_name in self.section_feeder_mapping:
                                self.section_feeder_mapping[i.feeder_name].append(new_sectionID)
                            else:
                                self.section_feeder_mapping[i.feeder_name]=[new_sectionID]
                            if hasattr(i, 'substation_name') and i.substation_name is not None:
                                self.section_headnode_mapping[i.feeder_name]=i.substation_name
                        #except:
                        #    pass


                    #If we have a regulator with two windings that have different
                    #voltages, we create a new section and a new transformer connected to it
                    #in order to have the voltage change
                    winding1 = None
                    winding2 = None
                    from_element = None
                    to_element = None
                    windings_local = []
                    if (hasattr(i,'connected_transformer') and
                        hasattr(model[i.connected_transformer],'windings') and
                        len(model[i.connected_transformer].windings)>=2 and
                        hasattr(model[i.connected_transformer].windings[0],'nominal_voltage') and
                        hasattr(model[i.connected_transformer].windings[1],'nominal_voltage') and
                        model[i.connected_transformer].windings[0].nominal_voltage is not None and
                        model[i.connected_transformer].windings[1].nominal_voltage is not None):
                        
                        winding1 = model[i.connected_transformer].windings[0]
                        winding2 = model[i.connected_transformer].windings[1]
                        if hasattr(model[i.connected_transformer],'from_element') and model[i.connected_transformer].from_element is not None and hasattr(model[i.connected_transformer],'to_element') and model[i.connected_transformer].to_element is not None:
                            from_element = model[i.connected_transformer].from_element
                            to_element = model[i.connected_transformer].to_element
                    elif hasattr(i, 'windings') and i.windings is not None:
                        if (len(i.windings)>=2 and
                            hasattr(i.windings[0], 'nominal_voltage') and
                            hasattr(i.windings[1], 'nominal_voltage') and
                            i.windings[0].nominal_voltage is not None and
                            i.windings[1].nominal_voltage is not None):
                                winding1 = i.windings[0]
                                winding2 = i.windings[1]
                                if hasattr(i,'from_element') and i.from_element is not None and hasattr(i,'to_element') and i.to_element is not none:
                                    from_element = i.from_element
                                    to_element = i.to_element
                    if winding1 is not None and winding2 is not None:
                        windings_local=[winding1,winding2]
                        if winding1.nominal_voltage!=winding2.nominal_voltage:
                            new_trans_sectionID='{f}_{t}'.format(f=from_element, t=to_element+'_reg')
                            new_trans_section='{f}_{t},{f},{t},'.format(f=from_element, t=to_element+'_reg')
                            new_section='{f}_{t},{f},{t},'.format(f=to_element+'_reg',t=to_element)
                            new_section_ID='{f}_{t}'.format(f=to_element+'_reg',t=to_element)
                            if hasattr(i, 'feeder_name') and i.feeder_name is not None:
                                if i.feeder_name in self.section_feeder_mapping:
                                    self.section_feeder_mapping[i.feeder_name].append(new_sectionID)
                                else:
                                    self.section_feeder_mapping[i.feeder_name]=[new_sectionID]
                                if hasattr(i, 'substation_name') and i.substation_name is not None:
                                    self.section_headnode_mapping[i.feeder_name]=i.substation_name
                            self.nodeID_list.append(to_element+'_reg')
                            self.node_string_list.append('{},0,0'.format(to_element+'_reg'))
                            new_transformer_line=''
                            new_transformer_object_line=''
                            phase_on=''
                            if hasattr(winding1,'phase_windings') and winding1.phase_windings is not None:
                                    for phase_winding in winding1.phase_windings:
                                        if new_trans_section is not None:
                                            if hasattr(phase_winding, 'phase') and phase_winding.phase is not None:
                                                new_trans_section+=str(phase_winding.phase)
                                                phase_on+=str(phase_winding.phase)

                            if new_trans_section is not None and new_trans_section not in self.section_line_list:
                                    self.section_line_list.append(new_trans_section)
                                    if hasattr(i,'feeder_name') and i.feeder_name is not None:
                                        if i.feeder_name in self.section_line_feeder_mapping:
                                            self.section_line_feeder_mapping[i.feeder_name].append(new_trans_section)
                                        else:
                                            self.section_line_feeder_mapping[i.feeder_name]=[new_trans_section]


                            if hasattr(winding1,'phase_windings') and winding1.phase_windings is not None:
                                try:
                                    if len(winding1.phase_windings)==1:
                                        TYPE=1
                                    elif len(winding1.phase_windings)==3:
                                        TYPE=2
                                    else:
                                        TYPE=3
                                except:
                                    TYPE=3
                                    pass
                            else:
                                TYPE=3

                            try:
                                new_transformer_line+=new_trans_sectionID
                            except:
                                pass

                            #CoordX and CoordY
                            if hasattr(i, 'positions') and i.positions is not None:
                                try:
                                    new_transformer_line+=','+str(i.positions[0].long)
                                    new_transformer_line+=','+str(i.positions[0].lat)
                                except:
                                    new_transformer_line+=',,'
                                    pass

                            CONN=''
                            try:
                                new_transformer_line+=','+self.transformer_connection_configuration_mapping(winding1.connection_type,winding2.connection_type)
                                CONN=self.transformer_connection_configuration_mapping(winding1.connection_type,winding2.connection_type)
                            except:
                                new_transformer_line+=','
                                pass

                            phase_shift=0
                            if CONN=='0' or CONN=='4':
                                phase_shift=0
                            if CONN=='1' or CONN=='2':
                                phase_shift=1

                            try:
                                new_transformer_line+=','+phase_on
                            except:
                                new_transformer_line+=','
                                pass

                            if(hasattr(winding1,'resistance') and
                               hasattr(winding2,'resistance') and
                               winding1.resistance is not None and
                               winding2.resistance is not None):
                               #Resistance is given as a percentage of the KVA of the corresponding winding
                               try:
                                   RH=winding1.resistance*10**-2*winding1.rated_power*10**-3
                                   RL=winding2.resistance*10**-2*winding2.rated_power*10**-3
                               except:
                                   RH=0
                                   RL=0
                                   pass

                            #We have ZHL=(RH+RL)+XHLj
                            #
                            #Compute the X over R ratio
                            try:
                                XR=(XHL)/(RH+RL)
                                XR0=XR
                            except:
                                XR=0
                                XR0=0
                                pass
                            #
                            #|ZHL|=sqrt((RH+RL)^2 + XHL^2)
                            try:
                                _ZHL_=math.sqrt((RH+RL)**2 + XHL**2)
                            except:
                                _ZHL_=0
                                pass

                            #
                            #Expressed in percentage of the KVA base
                            try:
                                Z1=_ZHL_*100.0/(winding1.rated_power*10**-3)
                            except:
                                Z1=0
                                pass
                            Z0=Z1


                            #Total kva
                            KVA=0
                            for w,winding in enumerate(windings_local):
                                try:
                                    KVA+=winding.rated_power*10**-3
                                except:
                                    pass

                                if hasattr(winding, 'nominal_voltage'):
                                    try:
                                        if w==0:
                                            KVLLprim=winding.nominal_voltage*10**-3
                                            VoltageUnit=1 #Voltage declared in KV, not in KVLL
                                        elif w==1:
                                            KVLLsec=winding.nominal_voltage*10**-3
                                            VoltageUnit=1 #Voltage declared in KV, not in KVLL
                                    except:
                                        pass
                                #NoLoadLosses
                                if hasattr(i, 'noload_loss') and i.noload_loss is not None:
                                    #TODO: Make sure noloadlosses is in % in DiTTo, or change what is next.
                                    NoLoadLosses=i.noload_loss/100.0*KVA
                                else:
                                    NoLoadLosses=''


                            new_transformer_object_line+='{type},{kva},{voltageunit},{kvllprim},{kvllsec},{Z1},{Z0},{XR},{XR0},{Conn},{WindingType},{noloadloss},{phaseshift}'.format(type=TYPE,kva=KVA,voltageunit=VoltageUnit,kvllprim=KVLLprim,kvllsec=KVLLsec,Conn=CONN,Z1=Z1,Z0=Z0,XR=XR,XR0=XR0,WindingType=1,noloadloss=NoLoadLosses,phaseshift=phase_shift)

                            found=False
                            for k,d in self.two_windings_trans_codes.items():
                                if d==new_transformer_object_line:
                                    new_transformer_line+=',transformer_'+str(k)+',transformer_'+str(k)
                                    found=True
                            if not found:
                                ID_trans+=1
                                self.two_windings_trans_codes[ID_trans]=new_transformer_object_line
                                new_transformer_line+=',transformer_'+str(ID_trans)+',transformer_'+str(ID_trans)

                            new_transformer_line+=',{PhaseShiftType},M,100,100,None,0'.format(PhaseShiftType=phase_shift)#Phase shift, Location, PrimTap,SecondaryTap, ODPrimPh, and ConnectionStatus

                            if new_transformer_line!='':
                                two_windings_transformer_string_list.append(new_transformer_line)


                        if hasattr(winding1, 'phase_windings'):
                            for phase_winding in winding1.phase_windings:
                                try:
                                    new_section+=str(phase_winding.phase)
                                except:
                                    pass

                    if new_section is not None and new_section not in self.section_line_list:
                        self.section_line_list.append(new_section)
                        if hasattr(i,'feeder_name') and i.feeder_name is not None:

                            if i.feeder_name in self.section_line_feeder_mapping:
                                self.section_line_feeder_mapping[i.feeder_name].append(new_section)
                            else:
                                self.section_line_feeder_mapping[i.feeder_name]=[new_section]

                    try:
                        new_regulator_string+=new_section_ID
                    except:
                        pass

                    #CoordX and CoordY
                    if hasattr(i, 'positions') and i.positions is not None:
                        try:
                            new_regulator_string+=','+str(i.positions[0].long)
                            new_regulator_string+=','+str(i.positions[0].lat)
                        except:
                            new_regulator_string+=',,'
                            pass
                    else:
                        new_regulator_string+=','

                    if hasattr(i, 'pt_phase') and i.pt_phase is not None:
                        try:
                            new_regulator_string+=','+str(i.pt_phase)
                        except:
                            new_regulator_string+=','
                            pass
                    else:
                        new_regulator_string+=','

                    _KVA=0
                    _KVLN=0
                    _Rset={'A':0,'B':0,'C':0}
                    _Xset={'A':0,'B':0,'C':0}
                    if len(windings_local) >=2:
                        for winding in windings_local:
                            try:
                                _KVA+=winding.rated_power*10**-3
                            except:
                                pass
                        _KVLN=winding.nominal_voltage*10**-3

                        if hasattr(winding1, 'phase_windings') and winding1.phase_windings is not None:
                            for phase_winding in winding1.phase_windings:
                                try:
                                    _Rset[phase_winding.phase]=phase_winding.compensator_r
                                    _Xset[phase_winding.phase]=phase_winding.compensator_x
                                except:
                                    pass

                    _band=None
                    if hasattr(i, 'bandwidth') and i.bandwidth is not None:
                        try:
                            new_regulator_string+=','+str(i.bandwidth)
                            _band=str(i.bandwidth)
                        except:
                            new_regulator_string+=','
                            pass
                    else:
                        new_regulator_string+=','

                    _CT=None
                    if hasattr(i, 'ct_prim') and i.ct_prim is not None:
                        try:
                            new_regulator_string+=','+str(i.ct_prim)
                            _CT=str(i.ct_prim)
                        except:
                            new_regulator_string+=','
                    else:
                        new_regulator_string+=','


                    _PT=None
                    if hasattr(i, 'pt_ratio') and i.pt_ratio is not None:
                        try:
                            new_regulator_string+=','+str(i.pt_ratio)
                            _PT=str(i.pt_ratio)
                        except:
                            new_regulator_string+=','
                    else:
                        new_regulator_string+=','

                    if hasattr(i, 'bandcenter') and i.bandcenter is not None:
                        try:
                            if str(i.pt_phase)=='A':
                                new_regulator_string+=','+str(i.bandcenter)+',0,0'
                            elif str(i.pt_phase)=='B':
                                new_regulator_string+=',0,'+str(i.bandcenter) +',0'
                            elif str(i.pt_phase)=='C':
                                new_regulator_string+=',0,0,'+str(i.bandcenter)
                        except:
                            new_regulator_string+=','
                            pass

                    new_regulator_object_line='{kva},{band},{ct},{pt},{Type},{KVLN},{MaxBuck},{MaxBoost},{Taps},{Reversible}'.format(kva=_KVA,band=_band,ct=_CT,pt=_PT,Type=0,KVLN=_KVLN,MaxBuck=10,MaxBoost=10,Taps=0,Reversible=0)

                    found=False
                    for k,d in self.reg_codes.items():
                        if d==new_regulator_object_line:
                            new_regulator_string+=',regulator_{id},{secid}'.format(id=k,secid=new_section_ID)
                            found=True
                    if not found:
                        ID_reg+=1
                        self.reg_codes[ID_reg]=new_regulator_object_line
                        new_regulator_string+=',regulator_{id},{secid}'.format(id=ID_reg,secid=new_section_ID)


                    #Location, MaxBuck, MaxBoost, SettingOption, RsetA, RsetB, RsetC, XsetA,
                    # XsetB, XsetC, TapA, TapB, TapC, and ConnectionStatus
                    new_regulator_string+=',M,10,10,T,{RsetA},{RsetB},{RsetC},{XsetA},{XsetB},{XsetC},0,0,0,0'.format(RsetA=_Rset['A'],RsetB=_Rset['B'],RsetC=_Rset['C'],XsetA=_Xset['A'],XsetB=_Xset['B'],XsetC=_Xset['C'])

                    if new_regulator_string!='':
                        regulator_string_list.append(new_regulator_string)


                #If we get a Transformer object
                #
                if (isinstance(i, PowerTransformer) and (i.name not in self.transformers_to_ignore)) or (isinstance(i,Regulator) and (hasattr(i,'ltc') and i.ltc is not None and i.ltc==1)):

                    transformer_object = i

                    # These are only set if it's an LTC
                    Setpoint = ''
                    ControlType = ''
                    LowerBandwidth = ''
                    UpperBandwidth = ''
                    MaxBoost = ''
                    MaxBuck = ''
                    is_ltc = 0
                    if isinstance(i,Regulator) :
                        is_ltc = 1
                        Setpoint = i.setpoint
                        if hasattr(i,'connected_transformer'):
                            transformer_object = model[i.connected_transformer]
                            ControlType = '0'
                        else:
                            raise ValueError("An LTC regulator needs a connecting transformer")



                    #We need to get bus1 and bus2 to create the section bus1_bus2
                    new_section=None
                    new_section_ID=None
                    if hasattr(transformer_object, 'from_element') and transformer_object.from_element is not None and hasattr(transformer_object, 'to_element') and transformer_object.to_element is not None:
                        try:
                            new_section='{f}_{t},{f},{t},'.format(f=transformer_object.from_element,t=transformer_object.to_element)
                            new_section_ID='{f}_{t}'.format(f=transformer_object.from_element,t=transformer_object.to_element)
                            # If it's a regulator, use the regulator object to find the feeder and substation if they're set
                            if hasattr(i, 'feeder_name') and i.feeder_name is not None:
                                if i.feeder_name in self.section_feeder_mapping:
                                    self.section_feeder_mapping[i.feeder_name].append(new_sectionID)
                                else:
                                    self.section_feeder_mapping[i.feeder_name]=[new_sectionID]
                                if hasattr(i, 'substation_name') and i.substation_name is not None:
                                    self.section_headnode_mapping[i.feeder_name]=i.substation_name
                        except:
                            pass



                    # Set Regulator attributes if its an LTC

                    if hasattr(i,'bandwidth') and i.bandwidth is not None:
                        bandcenter = 0
                        if hasattr(i,'bandcenter') and i.bandcenter is not None:
                            bandcenter = i.bandcenter
                        LowerBandwidth = str(abs(bandcenter - i.bandwidth/2.0 ))
                        UpperBandwidth = str(abs(bandcenter + i.bandwidth/2.0))

                    if hasattr(i,'highstep') and i.highstep is not None:
                        MaxBoost = str(i.highstep)

                    if hasattr(i,'highstep') and i.highstep is not None:
                        MaxBuck = str(i.lowstep)
                        

                    #Find out if we have a two or three windings transformer
                    if hasattr(transformer_object, 'windings') and transformer_object.windings is not None:

                        phase_on=''
                        if hasattr(transformer_object.windings[0],'phase_windings') and transformer_object.windings[0].phase_windings is not None:
                                for phase_winding in transformer_object.windings[0].phase_windings:
                                    if new_section is not None:
                                        if hasattr(phase_winding, 'phase') and phase_winding.phase is not None:
                                            new_section+=str(phase_winding.phase)
                                            phase_on+=str(phase_winding.phase)

                        if new_section is not None and new_section not in self.section_line_list:
                                self.section_line_list.append(new_section)
                                if hasattr(transformer_object,'feeder_name') and transformer_object.feeder_name is not None:

                                    if transformer_object.feeder_name in self.section_line_feeder_mapping:
                                        self.section_line_feeder_mapping[transformer_object.feeder_name].append(new_section)
                                    else:
                                        self.section_line_feeder_mapping[transformer_object.feeder_name]=[new_section]

                        #Case 1: Two Windings
                        #
                        if len(transformer_object.windings)==2 or transformer_object.is_center_tap==1:
                            #Empty new transformer string
                            new_transformer_line=''
                            new_transformer_object_line=''

                            if hasattr(transformer_object.windings[0],'phase_windings') and transformer_object.windings[0].phase_windings is not None:
                                try:
                                    if transformer_object.is_center_tap==1 and len(transformer_object.windings[0].phase_windings)==1:
                                        TYPE=4
                                    elif len(transformer_object.windings[0].phase_windings)==1:
                                        TYPE=1
                                    elif len(transformer_object.windings[0].phase_windings)==3:
                                        TYPE=2
                                    else:
                                        TYPE=3
                                except:
                                    TYPE=3
                                    pass
                            else:
                                TYPE=3

                            try:
                                new_transformer_line+=new_section_ID
                            except:
                                pass

                            #CoordX and CoordY
                            if hasattr(transformer_object, 'positions') and transformer_object.positions is not None:
                                try:
                                    new_transformer_line+=','+str(transformer_object.positions[0].long)
                                    new_transformer_line+=','+str(transformer_object.positions[0].lat)
                                except:
                                    new_transformer_line+=',,'
                                    pass

                            CONN=''
                            try:
                                if TYPE==4:
                                    CONN='15' #Yg_CT
                                    new_transformer_line+=',15'
                                else:
                                    new_transformer_line+=','+self.transformer_connection_configuration_mapping(transformer_object.windings[0].connection_type,transformer_object.windings[1].connection_type)
                                    CONN=self.transformer_connection_configuration_mapping(transformer_object.windings[0].connection_type,transformer_object.windings[1].connection_type)
                            except:
                                new_transformer_line+=','
                                pass

                            phase_shift=0
                            if CONN=='0' or CONN=='4':
                                phase_shift=0
                            if CONN=='1' or CONN=='2':
                                phase_shift=1

                            try:
                                new_transformer_line+=','+phase_on
                            except:
                                new_transformer_line+=','
                                pass

                            #Compute the impedances of center tap transformers. These should be three windings, one phase transformers in DiTTo
                            #with the is_center_tap flag set to 1
                            if TYPE==4:
                                if hasattr(transformer_object,'reactances') and transformer_object.reactances is not None and len(i.reactances)==3:
                                    XHL,XHT,XLT=transformer_object.reactances
                                    if(hasattr(transformer_object.windings[0],'resistance') and
                                       hasattr(transformer_object.windings[1],'resistance') and
                                       hasattr(transformer_object.windings[2],'resistance') and
                                       transformer_object.windings[0].resistance is not None and
                                       transformer_object.windings[1].resistance is not None and
                                       transformer_object.windings[2].resistance is not None):
                                       R0,R1,R2=[w.resistance for w in transformer_object.windings]
                                       KVA_BASE=transformer_object.windings[0].rated_power*10**-3
                                       XR,Z1=self.get_center_tap_impedances(R0,R1,R2,XHL,XHT,XLT,KVA_BASE)
                                       XR0=XR
                                       Z0=Z1

                            else:
                                if hasattr(transformer_object,'reactances') and transformer_object.reactances is not None and len(transformer_object.reactances)==1:
                                    XHL_perct=transformer_object.reactances[0]
                                    #XHL is in percentage of the KVA of the FIRST winding
                                    try:
                                        XHL=XHL_perct*10**-2*transformer_object.windings[0].rated_power*10**-3
                                    except:
                                        XHL=0
                                        pass

                                if(hasattr(transformer_object.windings[0],'resistance') and
                                   hasattr(transformer_object.windings[1],'resistance') and
                                   transformer_object.windings[0].resistance is not None and
                                   transformer_object.windings[1].resistance is not None):
                                   #Resistance is given as a percentage of the KVA of the corresponding winding
                                   try:
                                       RH=transformer_object.windings[0].resistance*10**-2*transformer_object.windings[0].rated_power*10**-3
                                       RL=transformer_object.windings[1].resistance*10**-2*transformer_object.windings[1].rated_power*10**-3
                                   except:
                                       RH=0
                                       RL=0
                                       pass

                                #We have ZHL=(RH+RL)+XHLj
                                #
                                #Compute the X over R ratio
                                try:
                                    XR=(XHL)/(RH+RL)
                                    XR0=XR
                                except:
                                    XR=0
                                    XR0=0
                                    pass
                                #
                                #|ZHL|=sqrt((RH+RL)^2 + XHL^2)
                                try:
                                    _ZHL_=math.sqrt((RH+RL)**2 + XHL**2)
                                except:
                                    _ZHL_=0
                                    pass

                                #
                                #Expressed in percentage of the KVA base
                                try:
                                    Z1=_ZHL_*100.0/(transformer_object.windings[0].rated_power*10**-3)
                                except:
                                    Z1=0
                                    pass
                                Z0=Z1


                            #Total kva
                            try:
                                KVA=transformer_object.windings[0].rated_power*10**-3
                            except:
                                KVA='DEFAULT'
                                pass

                            for w,winding in enumerate(transformer_object.windings):
                                #try:
                                #    KVA+=winding.rated_power*10**-3
                                #except:
                                #    pass

                                if hasattr(winding, 'nominal_voltage'):
                                    #If we have a one phase transformer, we specify voltage in KV, not in KVLL
                                    #This is done by setting the voltageUnit keyword to 1
                                    if len(transformer_object.windings[0].phase_windings)==1:
                                        if w==0:
                                            KVLLprim=winding.nominal_voltage*10**-3
                                            voltageUnit=1 #Voltage declared in KV, not in KVLL
                                        elif w==1:
                                            #In addition, if we have a center tap, we need to add the secondary and tertiary voltages here
                                            if TYPE==4:
                                                try:
                                                    KVLLsec=winding.nominal_voltage*10**-3+transformer_object.windings[2].nominal_voltage*10**-3
                                                    voltageUnit=1 #Voltage declared in KV, not in KVLL
                                                except:
                                                    KVLLsec='DEFAULT'
                                                    pass
                                            else:
                                                KVLLsec=winding.nominal_voltage*10**-3
                                                voltageUnit=1 #Voltage declared in KV, not in KVLL
                                    #If we have a three phase transformer, we need to specify the voltage in KVLL.
                                    #This is done by setting the voltageUnit to 0, and multiplying the voltage by sqrt(3)
                                    #Note: If we have three phases, the transformer shouln't be a center tap
                                    elif len(transformer_object.windings[0].phase_windings)==3:
                                        if w==0:
                                            KVLLprim=winding.nominal_voltage*10**-3#*math.sqrt(3)
                                            voltageUnit=0
                                        if w==1:
                                            KVLLsec=winding.nominal_voltage*10**-3#*math.sqrt(3)
                                            voltageUnit=0


                            #NoLoadLosses
                            if hasattr(transformer_object, 'noload_loss') and transformer_object.noload_loss is not None:
                                #TODO: Make sure noloadlosses is in % in DiTTo, or change what is next.
                                NOLOADLOSS=transformer_object.noload_loss/100.0*KVA
                            else:
                                NOLOADLOSS=''

                            new_transformer_object_line+='{type},{kva},{voltageUnit},{kvllprim},{kvllsec},{Z1},{Z0},{XR},{XR0},{Conn},{WindingType},{noloadloss},{phaseshift},{isltc}'.format(phaseshift=phase_shift,type=TYPE,kva=KVA,voltageUnit=voltageUnit,kvllprim=KVLLprim,kvllsec=KVLLsec,Conn=CONN,Z1=Z1,Z0=Z0,XR=XR,XR0=XR0,WindingType=1,noloadloss=NOLOADLOSS,isltc=is_ltc)

                            found=False
                            for k,d in self.two_windings_trans_codes.items():
                                if d==new_transformer_object_line:
                                    new_transformer_line+=',transformer_'+str(k)+','+new_section_ID
                                    found=True
                            if not found:
                                ID_trans+=1
                                self.two_windings_trans_codes[ID_trans]=new_transformer_object_line
                                new_transformer_line+=',transformer_'+str(ID_trans)+','+new_section_ID

                            new_transformer_line+=',M,100,100,None,0'#.format(PhaseShiftType=phase_shift)#Phase shift, Location, PrimTap,SecondaryTap, ODPrimPh, and ConnectionStatus

                            try:
                                TAP=1.0/float(transformer_object.windings[1].phase_windings[0].tap_position)
                                new_transformer_line+=',{}'.format(TAP)
                            except:
                                new_transformer_line+=','
                                pass



                            # Apply the LTC settings. These are empty if it's just a transformer
                            new_transformer_line+=',{setpoint},{controltype},{lowerbandwidth},{upperbandwidth},{maxbuck},{maxboost}'.format(setpoint=Setpoint,controltype=ControlType,lowerbandwidth=LowerBandwidth,upperbandwidth=UpperBandwidth,maxbuck=MaxBuck,maxboost=MaxBoost)

                            if new_transformer_line!='':
                                two_windings_transformer_string_list.append(new_transformer_line)


                        #Case 2: Three Windings
                        #
                        elif len(transformer_object.windings)==3:
                            #Empty new transformer string
                            new_transformer_line=''
                            new_transformer_object_line=''

                            #Name
                            if hasattr(transformer_object, 'name') and transformer_object.name is not None:
                                try:
                                    new_transformer_line+=new_section_ID
                                except:
                                    pass

                            #CoordX and CoordY
                            if hasattr(transformer_object, 'positions') and transformer_object.positions is not None:
                                try:
                                    new_transformer_line+=','+str(transformer_object.positions[0].long)
                                    new_transformer_line+=','+str(transformer_object.positions[0].lat)
                                except:
                                    new_transformer_line+=',,'
                                    pass

                            _primary_rated_capacity=None
                            _secondary_rated_capacity=None
                            _tertiary_rated_capacity=None
                            _primary_voltage=None
                            _secondary_voltage=None
                            _tertiary_voltage=None
                            _primary_connection=None
                            _secondary_connection=None
                            _tertiary_connection=None
                            R={}
                            XHL_perct,XLT_perct,XHT_perct=None,None,None
                            for w,winding in enumerate(transformer_object.windings):
                                if hasattr(winding, 'rated_power') and winding.rated_power is not None:
                                    if w==0: _primary_rated_capacity  =str(winding.rated_power*10**-3)
                                    if w==1: _secondary_rated_capacity=str(winding.rated_power*10**-3)
                                    if w==2: _tertiary_rated_capacity =str(winding.rated_power*10**-3)

                                if hasattr(winding, 'connection_type') and winding.connection_type is not None:
                                    if w==0: _primary_connection  =winding.connection_type
                                    if w==1: _secondary_connection=winding.connection_type
                                    if w==2: _tertiary_connection =winding.connection_type

                                if hasattr(winding, 'nominal_voltage') and winding.nominal_voltage is not None:
                                    try:
                                        new_transformer_line+=','+str(winding.nominal_voltage*10**-3)
                                    except:
                                        new_transformer_line+=','
                                        pass
                                    if w==0: _primary_voltage=str(winding.nominal_voltage*10**-3)
                                    if w==1: _secondary_voltage=str(winding.nominal_voltage*10**-3)
                                    if w==2: _tertiary_voltage=str(winding.nominal_voltage*10**-3)

                                else:
                                    new_transformer_line+=','

                                if hasattr(winding, 'resistance') and winding.resistance is not None:
                                    try:
                                        R[w]=winding.resistance*winding.rated_power*10**-3
                                    except:
                                        R[w]=None
                                        pass

                            if hasattr(transformer_object, 'reactances') and i.reactances is not None:
                                try:
                                    XHL_perct,XLT_perct,XHT_perct=i.reactances
                                except:
                                    pass

                            if XHL_perct is not None:
                                try:
                                    XHL=XHL_perct*10**-2*transformer_object.windings[0].rated_power*10**-3
                                except:
                                    XHL=None
                                    pass
                            if XLT_perct is not None:
                                try:
                                    XLT=XLT_perct*10**-2*transformer_object.windings[0].rated_power*10**-3
                                except:
                                    XLT=None
                                    pass
                            if XHT_perct is not None:
                                try:
                                    XHT=XHT_perct*10**-2*transformer_object.windings[0].rated_power*10**-3
                                except:
                                    XHT=None
                                    pass

                            if sum([x is None for x in R])==0 and XHL is not None and XLT is not None and XHT is not None:
                                ZHL=complex(R[0]+R[1],XHL)
                                ZLT=complex(R[1]+R[2],XLT)
                                ZHT=complex(R[0]+R[2],XHT)

                                _PrimaryToSecondaryXR1=ZHL.imag/ZHL.real
                                _PrimaryToSecondaryXR0=_PrimaryToSecondaryXR1

                                _PrimaryToTertiaryXR1=ZHT.imag/ZHT.real
                                _PrimaryToTertiaryXR0=_PrimaryToTertiaryXR1

                                _SecondaryToTertiaryXR1=ZLT.imag/ZLT.real
                                _SecondaryToTertiaryXR0=_SecondaryToTertiaryXR1

                                _PrimaryToSecondaryZ1=math.sqrt(ZHL.real**2+ZHL.imag**2)*100.0/(transformer_object.windings[0].rated_power*10**-3)
                                _PrimaryToSecondaryZ0=_PrimaryToSecondaryZ1

                                _PrimaryToTertiaryZ1=math.sqrt(ZHT.real**2+ZHT.imag**2)*100.0/(transformer_object.windings[0].rated_power*10**-3)
                                _PrimaryToTertiaryZ0=_PrimaryToTertiaryZ1

                                _SecondaryToTertiaryZ1=math.sqrt(ZLT.real**2+ZLT.imag**2)*100.0/(transformer_object.windings[0].rated_power*10**-3)
                                _SecondaryToTertiaryZ0=_SecondaryToTertiaryZ1

                            #NoLoadLosses
                            if hasattr(transformer_object, 'noload_loss') and transformer_object.noload_loss is not None:
                                #TODO: Make sure noloadlosses is in % in DiTTo, or change what is next.
                                NOLOADLOSS=transformer_object.noload_loss/100.0*KVA
                            else:
                                NOLOADLOSS=''

                            new_transformer_object_line='{kva1},{kv1},{conn1},,,,,,,{kva2},{kv2},{conn2},{kva3},{kv3},{conn3},'.format(
                                                                kva1=_primary_rated_capacity,
                                                                kv1=_primary_voltage,
                                                                conn1=_primary_connection,
                                                                kva2=_secondary_rated_capacity,
                                                                kv2=_secondary_voltage,
                                                                conn2=_secondary_connection,
                                                                kva3=_tertiary_rated_capacity,
                                                                kv3=_tertiary_voltage,
                                                                conn3=_tertiary_connection)
                            new_transformer_object_line+='{PrimaryToSecondaryZ1},{PrimaryToSecondaryZ0},{PrimaryToSecondaryXR1},{PrimaryToSecondaryXR0},{PrimaryToTertiaryZ1},{PrimaryToTertiaryZ0},{PrimaryToTertiaryXR1},{PrimaryToTertiaryXR0},{SecondaryToTertiaryZ1},{SecondaryToTertiaryZ0}'.format(
                                                                PrimaryToSecondaryZ1=_PrimaryToSecondaryZ1,
                                                                PrimaryToSecondaryZ0=_PrimaryToSecondaryZ0,
                                                                PrimaryToSecondaryXR1=_PrimaryToSecondaryXR1,
                                                                PrimaryToSecondaryXR0=_PrimaryToSecondaryXR0,
                                                                PrimaryToTertiaryZ1=_PrimaryToTertiaryZ1,
                                                                PrimaryToTertiaryZ0=_PrimaryToTertiaryZ0,
                                                                PrimaryToTertiaryXR1=_PrimaryToTertiaryXR1,
                                                                PrimaryToTertiaryXR0=_PrimaryToTertiaryXR0,
                                                                SecondaryToTertiaryZ1=_SecondaryToTertiaryZ1,
                                                                SecondaryToTertiaryZ0=_SecondaryToTertiaryZ0)
                            new_transformer_object_line+=',{SecondaryToTertiaryXR1},{SecondaryToTertiaryXR0},{SecondaryCapacityLimit1},{SecondaryCapacityLimit2},{TertiaryCapacityLimit1},{TertiaryCapacityLimit2},{TertiaryConnection},{noloadloss}'.format(
                                                                SecondaryToTertiaryXR1=_SecondaryToTertiaryXR1,
                                                                SecondaryToTertiaryXR0=_SecondaryToTertiaryXR0,
                                                                SecondaryCapacityLimit1=0,
                                                                SecondaryCapacityLimit2=0,
                                                                TertiaryCapacityLimit1=0,
                                                                TertiaryCapacityLimit2=0,
                                                                TertiaryConnection=0,
                                                                noloadloss=NOLOADLOSS)

                            found=False
                            for k,d in self.three_windings_trans_codes.items():
                                if d==new_transformer_object_line:
                                    new_transformer_line+=',3_wdg_transformer_'+str(k)+','+new_section_ID
                                    found=True
                            if not found:
                                ID_trans_3w+=1
                                self.three_windings_trans_codes[ID_trans_3w]=new_transformer_object_line
                                new_transformer_line+=',3_wdg_transformer_'+str(ID_trans_3w)+','+new_section_ID

                            new_transformer_line+=',{Location},{tertiarynodeID},{PrimaryFixedTapSetting},{SecondaryFixedTapSetting},{ConnectionStatus}'.format(Location='M',tertiarynodeID=0,PrimaryFixedTapSetting=0,SecondaryFixedTapSetting=0,ConnectionStatus=0)

                            try:
                                TAP=1.0/float(transformer_object.windings[1].phase_windings[0].tap_position)
                                new_transformer_line+=',{}'.format(TAP)
                            except:
                                new_transformer_line+=','
                                pass

                            if new_transformer_line!='':
                                three_windings_transformer_string_list.append(new_transformer_line)






            #Write everything to the network file
            #
            #HEADER
            #
            f.write('[GENERAL]\n')

            #DATE
            #
            current_date = datetime.now().strftime('%B %d, %Y at %H:%M:%S')
            f.write('DATE={}\n'.format(current_date))

            #CYME version
            #
            f.write('CYME_VERSION=8.02\n')

            #Unit system
            #
            f.write('\n[SI]\n')

            #Nodes
            #
            f.write('\n[NODE]\n')
            f.write('FORMAT_NODE=NodeID,CoordX,CoordY\n')

            for node_string in self.node_string_list:
                f.write(node_string+'\n')

            #Intermediate nodes
            #
            f.write('\n[INTERMEDIATE NODES]\n')
            f.write('FORMAT_INTERMEDIATENODE=SectionID,SeqNumber,CoordX,CoordY\n')

            for inter in intermediate_nodes:
                f.write('{SectionID},{SegNumber},{CoordX},{CoordY}\n'.format(SectionID=inter[0],SegNumber=inter[1],CoordX=inter[2],CoordY=inter[3]))

            #Sources
            #
            f.write('\n[SOURCE]\n')
            f.write('FORMAT_SOURCE=SourceID,DeviceNumber,NodeID,NetworkID\n')
            k=0
            self.substation_IDs={}
            for _source,_voltage in self.sources.items():
                k+=1
                for j,sub in enumerate(self.substations):
                    if sub['connecting_element']==_source:
                        self.substations[j]['sub_ID']='sub_'+str(k)
                self.substation_IDs[_source]='sub{}'.format(k)
                f.write('sub_{k},sub_{k},{source},{NetID}\n'.format(source=_source, k=k, NetID='subtransmission'))

            f.write('\n[HEADNODES]\n')
            f.write('FORMAT_HEADNODES=NodeID,NetworkID\n')
            #k=0
            #for source_string in source_string_list:
            #    k+=1
            #    nodeID=source_string.split(',')[0]
            #    f.write('{nodeID},{NetID}\n'.format(nodeID=nodeID, NetID=k))
            for f_name,section_l in self.section_line_feeder_mapping.items():
#                for kk in model.models:
#                   if isinstance(kk,Feeder_metadata):
#                       print(kk.name, kk.headnode)
#import pdb;pdb.set_trace()
                head=model[f_name].headnode#self.section_headnode_mapping[f_name]
                f.write('{nodeID},{NetID}\n'.format(nodeID=head, NetID=f_name))

            #Source equivalent
            #
            f.write('\n[SOURCE EQUIVALENT]\n')
            f.write('FORMAT_SOURCEEQUIVALENT=NodeID,Voltage,OperatingAngle1,OperatingAngle2,OperatingAngle3,PositiveSequenceResistance,PositiveSequenceReactance,ZeroSequenceResistance,ZeroSequenceReactance,NegativeSequenceResistance,NegativeSequenceReactance,OperatingVoltage1,OperatingVoltage2,OperatingVoltage3,ImpedanceUnit\n')

            id_from_source=[]
            for source_string in source_string_list:
                id_from_source.append(source_string.split(',')[0])
                f.write(source_string+'\n')

            for f_name,section_l in self.section_line_feeder_mapping.items():
                if f_name!='subtransmission':
                    temp=model[f_name]
                    if hasattr(temp,'nominal_voltage') and temp.nominal_voltage is not None:
                        volt=temp.nominal_voltage*10**-3
                    else:
                        volt=model[temp.headnode].nominal_voltage*10**-3
                    if temp.headnode not in id_from_source:
                        f.write('{node_id},{voltage},{angle1},{angle2},{angle3},{R1},{X1},{R0},{X0},{R2},{X2},{voltage},{voltage},{voltage},0\n'.format(
                                       node_id=temp.headnode, voltage=volt, angle1=temp.operating_angle1, angle2=temp.operating_angle2,
                                       angle3=temp.operating_angle3, R1=temp.positive_sequence_resistance, X1=temp.positive_sequence_reactance,
                                       R0=temp.zero_sequence_resistance, X0=temp.zero_sequence_reactance, R2=temp.negative_sequence_resistance,
                                       X2=temp.negative_sequence_reactance))

            #Sections
            #
            f.write('\n[SECTION]\n')
            f.write('FORMAT_SECTION=SectionID,FromNodeID,ToNodeID,Phase\n')
            f.write('FORMAT_FEEDER=NetworkID,HeadNodeID,CoordSet\n')

            #k=0
            #for source_string in source_string_list:
            #    k+=1
            #    f.write('FEEDER={NetID},{HeadNodeID},{coordset}\n'.format(NetID=k,HeadNodeID=source_string.split(',')[0],coordset=0))

            #    section_list=self.merge_regulators(self.section_line_list)
            #    for section_line in section_list:
            #        f.write(section_line+'\n')
            for f_name,section_l in self.section_line_feeder_mapping.items():
                head=model[f_name].headnode#self.section_headnode_mapping[f_name]
                f.write('FEEDER={NetID},{HeadNodeID},{coordset}\n'.format(NetID=f_name,HeadNodeID=head,coordset=1))
                for sec in section_l:
                    f.write(sec+'\n')


            #Overhead lines
            #
            if len(overhead_string_list)>0:
                f.write('\n[OVERHEADLINE SETTING]\n')
                f.write('FORMAT_OVERHEADLINESETTING=SectionID,LineCableID,Length,ConnectionStatus\n')
                for overhead_string in overhead_string_list:
                    f.write(overhead_string+'\n')

            #Overhead by phase lines
            #
            if len(overhead_byphase_string_list)>0:
                f.write('\n[OVERHEAD BYPHASE SETTING]\n')
                f.write('FORMAT_OVERHEADBYPHASESETTING=SectionID,DeviceNumber,CondID_A,CondID_B,CondID_C,CondID_N1,CondID_N2,SpacingID,Length,ConnectionStatus\n')
                for overhead_byphase_string in overhead_byphase_string_list:
                    f.write(overhead_byphase_string+'\n')

            #Underground lines
            #
            if len(underground_string_list)>0:
                f.write('\n[UNDERGROUNDLINE SETTING]\n')
                f.write('FORMAT_UNDERGROUNDLINESETTING=SectionID,LineCableID,Length,ConnectionStatus,DistanceBetweenConductors,CableConfiguration\n')
                for underground_string in underground_string_list:
                    f.write(underground_string+'\n')

            #Switches
            #
            if len(switch_string_list)>0:
                f.write('\n[SWITCH SETTING]\n')
                f.write('FORMAT_SWITCHSETTING=SectionID,EqID,Location,ClosedPhase,Locked,ConnectionStatus,DeviceNumber\n')
                for switch_string in switch_string_list:
                    f.write(switch_string+'\n')

            #Fuses
            #
            if len(fuse_string_list)>0:
                f.write('\n[FUSE SETTING]\n')
                f.write('FORMAT_FUSESETTING=SectionID,EqID,Location,ClosedPhase,Locked,ConnectionStatus,DeviceNumber\n')
                for fuse_string in fuse_string_list:
                    f.write(fuse_string+'\n')

            #Reclosers
            #
            if len(recloser_string_list)>0:
                f.write('\n[RECLOSER SETTING]\n')
                f.write('FORMAT_RECLOSERSETTING=SectionID,EqID,Location,ClosedPhase,Locked,ConnectionStatus,DeviceNumber\n')
                for recloser_string in recloser_string_list:
                    f.write(recloser_string+'\n')

            #Breakers
            #
            if len(recloser_string_list)>0:
                f.write('\n[BREAKER SETTING]\n')
                f.write('FORMAT_BREAKERSETTING=SectionID,EqID,Location,ClosedPhase,Locked,ConnectionStatus,DeviceNumber\n')
                for breaker_string in breaker_string_list:
                    f.write(breaker_string+'\n')

            #Capacitors
            #
            if len(capacitor_string_list)>0:
                f.write('\n[SHUNT CAPACITOR SETTING]\n')
                f.write('FORMAT_SHUNTCAPACITORSETTING=SectionID,Connection,KV,DeviceNumber,ShuntCapacitorID,Location,ConnectionStatus\n')
                for capacitor_string in capacitor_string_list:
                    f.write(capacitor_string+'\n')

            #Transformers
            #
            #2 WINDINGS
            #
            if len(two_windings_transformer_string_list)>0:
                f.write('\n[TRANSFORMER SETTING]\n')
                f.write('FORMAT_TRANSFORMERSETTING=SectionID,CoordX,CoordY,Conn,PhaseON,EqID,DeviceNumber,Location,PrimTap,SecondaryTap,ODPrimPh,ConnectionStatus,Tap,SetPoint,ControlType,LowerBandwidth,UpperBandwidth,Maxbuck,Maxboost\n')
                for transformer_string in two_windings_transformer_string_list:
                    f.write(transformer_string+'\n')

            #3 WINDINGS
            #
            if len(three_windings_transformer_string_list)>0:
                f.write('\n[THREE WINDING TRANSFORMER SETTING]\n')
                f.write('FORMAT_THREEWINDINGTRANSFORMERSETTING=SectionID,CoordX,CoordY,PrimaryBaseVoltage,SecondaryBaseVoltage,TertiaryBaseVoltage,EqID,DeviceNumber,Location,TertiaryNodeID,PrimaryFixedTapSetting,SecondaryFixedTapSetting,ConnectionStatus,Tap\n')
                for transformer_string in three_windings_transformer_string_list:
                    f.write(transformer_string+'\n')

            #Regulators
            if len(regulator_string_list)>0:
                #Merge the Regulators
                regulator_string_list_merged=self.merge_regulators(regulator_string_list)
                f.write('\n[REGULATOR SETTING]\n')
                f.write('FORMAT_REGULATORSETTING=SectionID,CoordX,CoordY,PhaseON,BandWidth,CT,PT,VsetA,VsetB,VsetC,EqID,DeviceNumber,Location,MaxBuck,MaxBoost,SettingOption,RsetA,RsetB,RsetC,XsetA,XsetB,XsetC,TapA,TapB,TapC,ConnectionStatus\n')
                for regulator_string in regulator_string_list_merged:
                    f.write(regulator_string+'\n')




    def write_equipment_file(self, model, **kwargs):
        '''
            Write the equipment file.
        '''
        output_file=self.output_path+'/equipment.txt'

        with open(output_file, 'w') as f:

            #Header
            f.write('[GENERAL]\n')
            current_date = datetime.now().strftime('%B %d, %Y at %H:%M:%S')
            f.write('DATE={}\n'.format(current_date))
            f.write('CYME_VERSION=8.02\n')
            f.write('\n[SI]\n')

            #Substations
            #
            if len(self.substations)>0:
                f.write('\n[SUBSTATION]\n')
                f.write('FORMAT_SUBSTATION=ID,MVA,KVLL,KVLLdesired,R1,X1,R0,X0,R2,X2,PhaseAngle,MVA_1,MVA_2,MVA_3,MVA_4,Conn,PrimaryEquivalentType,SubEqVal1,SubEqVal2,SubEqVal3,SubEqVal4,SubPrimaryLLVoltage,SecondaryFaultReactance,TxfoConnection,HarmonicEnveloppe,BackgroundHarmonicVoltage,BaseMVA,ImpedanceUnit,BranchID_1,PrimProtDevID_1,PrimProtDevNum_1,TransformerID_1,TransformerNum_1,SubXs_1,SecProtDevID_1,SecProtDevNum_1,BranchStatus_1,BranchID_2,PrimProtDevID_2,PrimProtDevNum_2,TransformerID_2,TransformerNum_2,SubXs_2,SecProtDevID_2,SecProtDevNum_2,BranchStatus_2,BranchID_3,PrimProtDevID_3,PrimProtDevNum_3,TransformerID_3,TransformerNum_3,SubXs_3,SecProtDevID_3,SecProtDevNum_3,BranchStatus_3,BranchID_4,PrimProtDevID_4,PrimProtDevNum_4,TransformerID_4,TransformerNum_4,SubXs_4,SecProtDevID_4,SecProtDevNum_4,BranchStatus_4,BranchID_5,PrimProtDevID_5,PrimProtDevNum_5,TransformerID_5,TransformerNum_5,SubXs_5,SecProtDevID_5,SecProtDevNum_5,BranchStatus_5,FailRate,TmpFailRate,MajorRepairTime,')
                f.write('MinorRepairTime,MajorFailureProportion,SymbolID,Favorite,Flags,Comments\n')

                for sub in self.substations:
                    if 'sub_ID' in sub:
                        f.write(sub['sub_ID']+',')
                        if 'MVA' in sub:
                            f.write(sub['MVA']+',')
                        else:
                            f.write(',')
                        if 'KVLL' in sub:
                            #NOTE: Setting the voltage to 1.05pu at the feeder head is raw coded here
                            #TODO: Come up with a less dirty way to have 1.05pu at the substation
                            f.write('{a},{b},'.format(a=sub['KVLL'],b=float(sub['KVLL'])*1.00))#*1.05))
                        else:
                            f.write(',,')
                        #
                        #TODO: automatically detect if default or real values should be used for source impedance
                        #
                        #if sub.has_key('R1'):
                            #f.write(sub['R1']+',')
                        f.write('DEFAULT,')
                        #else:
                        #    f.write(',')
                        #if sub.has_key('X1'):
                        #    f.write(sub['X1']+',')
                        f.write('DEFAULT,')
                        #else:
                        #    f.write(',')
                        #if sub.has_key('R0'):
                        #    f.write(sub['R0']+',')
                        f.write('DEFAULT,')
                        #else:
                        #    f.write(',')
                        #if sub.has_key('X0'):
                        #    f.write(sub['X0']+',')
                        f.write('DEFAULT,')
                        #else:
                        #    f.write(',')
                        #if sub.has_key('R2'):
                        #    f.write(sub['R2']+',')
                        f.write('DEFAULT,')
                        #elif sub.has_key('R0'):
                        #    f.write(sub['R0']+',')
                        #else:
                        #    f.write(',')
                        #if sub.has_key('X2'):
                        #    f.write(sub['X2']+',')
                        f.write('DEFAULT,')
                        #elif sub.has_key('X0'):
                        #    f.write(sub['X0']+',')
                        #else:
                        #    f.write(',')
                        if 'phase_angle' in sub:
                            f.write(sub['phase_angle']+',')
                        else:
                            f.write(',')

                        f.write(',,,,,,,,,,,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,')
                        f.write('\n')


            #Switches
            #
            #Writing default values for switches
            #
            f.write('\n[SWITCH]\n')
            f.write('FORMAT_SWITCH=ID,Amps,Amps_1,Amps_2,Amps_3,Amps_4,KVLL,Reversible,FailRate,TmpFailRate,MajorRepairTime,MinorRepairTime,MajorFailureProportion,StuckProbability,SwitchTime,SymbolOpenID,SymbolCloseID,SinglePhaseLocking,RemoteControlled,Automated,Comments\n')
            f.write('DEFAULT,100.000000,100.000000,100.000000,100.000000,100.000000,25.000000,0,,,,,,,,0,0,0,0,0,\n')
            for ID,data in self.switchcodes.items():
                f.write(str(ID)+',')
                f.write(data)
                f.write('\n')

            #Fuses
            #
            #Writing default values for fuses
            #
            f.write('\n[FUSE]\n')
            f.write('FORMAT_FUSE=ID,Amps,Amps_1,Amps_2,Amps_3,Amps_4,KVLL,Reversible,InterruptingRating,FailRate,TmpFailRate,MajorRepairTime,MinorRepairTime,MajorFailureProportion,StuckProbability,SwitchTime,SymbolOpenID,SymbolCloseID,SinglePhaseLocking,Comments,Manufacturer,Model,TCCRating\n')
            f.write('DEFAULT,100.000000,100.000000,100.000000,100.000000,100.000000,25.000000,0,600.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,0,,,,\n')
            for ID,data in self.fusecodes.items():
                f.write(str(ID)+',')
                f.write(data)
                f.write('\n')

            #Reclosers
            #
            #Writing default values for reclosers
            #
            f.write('\n[RECLOSER]\n')
            f.write('FORMAT_RECLOSER=ID,Amps,Amps_1,Amps_2,Amps_3,Amps_4,KVLL,Reversible,InterruptingRating,FailRate,TmpFailRate,MajorRepairTime,MinorRepairTime,MajorFailureProportion,StuckProbability,SwitchTime,SymbolOpenID,SymbolCloseID,SinglePhaseLocking,SinglePhaseTripping,RemoteControlled,Automated,Comments,RecloserType,ControlType,Model\n')
            f.write('DEFAULT,100.000000,100.000000,100.000000,100.000000,100.000000,25.000000,0,600.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,0,0,0,0,,1,,\n')
            for ID,data in self.reclosercodes.items():
                f.write(str(ID)+',')
                f.write(data)
                f.write('\n')

            #Breakers
            #
            #Writing default values for breakers
            #
            f.write('\n[BREAKER]\n')
            f.write('FORMAT_BREAKER=ID,Amps,Amps_1,Amps_2,Amps_3,Amps_4,KVLL,Reversible,InterruptingRating,FailRate,TmpFailRate,MajorRepairTime,MinorRepairTime,MajorFailureProportion,StuckProbability,SwitchTime,SymbolOpenID,SymbolCloseID,SinglePhaseLocking,SinglePhaseTripping,RemoteControlled,Automated,Comments\n')
            f.write('DEFAULT,100.000000,100.000000,100.000000,100.000000,100.000000,25.000000,0,600.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,0,0,0,0,\n')
            for ID,data in self.breakercodes.items():
                f.write(str(ID)+',')
                f.write(data)
                f.write('\n')

            #Cables
            #
            f.write('\n[CABLE]\n')
            f.write('FORMAT_CABLE=ID,R1,R0,X1,X0,B1,B0,Amps,UserDefinedImpedances,Frequency,Temperature\n')
            f.write('DEFAULT,0.040399,0.055400,0.035900,0.018200,0.000000,0.000000,447.000000,1,60.000000,25.000000\n')
            for ID,data in self.cablecodes.items():
                f.write(str(ID))
                for key in ['R1','R0','X1','X0','B1','B0','amps']:
                    if key in data:
                        f.write(','+str(data[key]))
                    else:
                        f.write(',')
                f.write(',1,60.0000,25.00000\n')

            #Lines
            #
            if len(self.linecodes_overhead)>0:
                f.write('\n[LINE UNBALANCED]\n')
                f.write('FORMAT_LINEUNBALANCED=ID,Ra,Rb,Rc,Xa,Xb,Xc,MutualResistanceAB,MutualResistanceBC,MutualResistanceCA,MutualReactanceAB,MutualReactanceBC,MutualReactanceCA,CondID_A,CondID_B,CondID_C,CondID_N1,CondID_N2,SpacingID,Ba,Bb,Bc,AmpsA,AmpsB,AmpsC,UserDefinedImpedances,Transposed\n')

                for ID,data in self.linecodes_overhead.items():
                    f.write(str(ID))
                    for key in ['RA','RB','RC','XA','XB','XC','MutualResistanceAB','MutualResistanceBC','MutualResistanceCA','MutualReactanceAB','MutualReactanceBC','MutualReactanceCA','CondID_A','CondID_B','CondID_C','CondID_N1','CondID_N2','SpacingID','Ba','Bb','Bc','AmpsA','AmpsB','AmpsC','UserDefinedImpedances']:
                        if key in data:
                            f.write(','+str(data[key]))
                        else:
                            if key in ['CondID_A','CondID_B','CondID_C','CondID_N1','CondID_N2','SpacingID']:
                                f.write('NONE,')
                            else:
                                f.write(',0')
                    f.write(',0\n')

            #Conductors
            #
            f.write('\n[CONDUCTOR]\n')
            f.write('FORMAT_CONDUCTOR=ID,Diameter,GMR,Amps,WithstandRating\n')
            f.write('DEFAULT,1.000001,1.000001,2000.000000,2000.000000\n')
            if len(self.conductors)>0:
                for ID,data in self.conductors.items():
                    f.write(ID+',')
                    f.write(data)
                    f.write('\n')


            #Spacing table
            #
            f.write('\n[SPACING TABLE FOR LINE]\n')
            f.write('FORMAT_SPACINGTABLEFORLINE=ID,GMDPh-Ph,GMDPh-N,AvgPhCondHeight,AvgNeutralHeight,PosOfCond1_X,PosOfCond1_Y,PosOfCond2_X,PosOfCond2_Y,PosOfCond3_X,PosOfCond3_Y,PosOfNeutralCond_X,PosOfNeutralCond_Y,PosOfNeutralCond_N2_X,PosOfNeutralCond_N2_Y,BundleDistance,NBPhasesPerCircuit,NBConductorsPerPhase,NBNeutrals,TowerType,DistanceA,DistanceB,DistanceC,DistanceD,DistanceE,ConductorStatusN1,ConductorStatusN2,FootingResistanceN1,FootingResistanceN2,TowerSpanN1,TowerSpanN2,Favorite,Flags,Comments\n')
            f.write('DEFAULT,,,,,-0.609600,10.058400,0.000000,8.839200,0.609600,10.058400,0.000000,11.277600,,,0.010000,3,1,1,0,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,1.000000,1.000000,300.000000,300.000000,0,0,\n')


            f.write('N_ABOVE_1PH,,,,,0.000000,9.601200,,,,,0.000000,10.363200,,,0.010000,1,1,1,0,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,1.000000,1.000000,300.000000,300.000000,0,0,\n')
            f.write('N_ABOVE_2PH,,,,,-1.127760,9.601200,1.127760,9.601200,,,0.000000,10.363200,,,0.010000,2,1,1,0,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,1.000000,1.000000,300.000000,300.000000,0,0,\n')
            f.write('N_ABOVE_3PH,,,,,-1.127760,9.601200,0.000000,9.601200,1.127760,9.601200,0.000000,10.363200,,,0.010000,3,1,1,0,0.000000,0.000000,0.000000,0.000000,0.000000,0,0,1.000000,1.000000,300.000000,300.000000,0,0,\n')


            #TODO
            #Add the user-defined spacing tables here

            #Capacitors
            #
            if len(self.capcodes)>0:
                f.write('\n[SHUNT CAPACITOR]\n')
                f.write('FORMAT_SHUNTCAPACITOR=ID,KVAR,KV,CostForFixedBank,CostForSwitchedBank,Type\n')

                for ID,data in self.capcodes.items():
                    f.write('capacitor_'+str(ID)+',')
                    f.write(data.strip(','))
                    f.write(',0,0,0')
                    f.write('\n')


            #Two winding transformers
            #
            if len(self.two_windings_trans_codes)>0:
                f.write('\n[TRANSFORMER]\n')
                f.write('FORMAT_TRANSFORMER=ID,Type,KVA,VoltageUnit,KVLLprim,KVLLsec,Z1,Z0,XR,XR0,Conn,WindingType,NoLoadLosses,PhaseShift,IsLTC\n')

                for ID,data in self.two_windings_trans_codes.items():
                    f.write('transformer_'+str(ID)+',')
                    f.write(data.strip(','))
                    f.write('\n')


            #Three winding transformers
            #
            if len(self.three_windings_trans_codes)>0:
                f.write('\n[THREE WINDING TRANSFORMER]\n')
                f.write('FORMAT_THREEWINDINGTRANSFORMER=ID,PrimaryRatedCapacity,PrimaryVoltage,PrimaryConnection,PrimaryToSecondaryZ1,PrimaryToSecondaryZ0,PrimaryToSecondaryXR1,PrimaryToSecondaryXR0,PrimaryToTertiaryZ1,PrimaryToTertiaryZ0,PrimaryToTertiaryXR1,PrimaryToTertiaryXR0,SecondaryToTertiaryZ1,SecondaryToTertiaryZ0,SecondaryToTertiaryXR1,SecondaryToTertiaryXR0,SecondaryCapacityLimit1,SecondaryCapacityLimit2,TertiaryCapacityLimit1,TertiaryCapacityLimit2,TertiaryConnection,NoLoadLosses\n')
                for ID,data in self.three_windings_trans_codes.items():
                    f.write('3_wdg_transformer_'+str(ID)+',')
                    f.write(data.strip(','))
                    f.write('\n')

            #Regulators
            #
            if len(self.reg_codes)>0:
                f.write('\n[REGULATOR]\n')
                f.write('FORMAT_REGULATOR=ID,KVA,Bandwidth,CT,PT,Type,KVLN,MaxBuck,MaxBoost,Taps,Reversible\n')

                for ID,data in self.reg_codes.items():
                    f.write('regulator_'+str(ID)+',')
                    f.write(data.strip(','))
                    f.write('\n')




    def write_load_file(self, model, **kwargs):
        '''
            Loop over the DiTTo objects and write the CYME load file.
        '''
        #Output load file
        output_file=self.output_path+'/loads.txt'


        customer_load_string_list=[]
        load_string_list=[]

        with open(output_file, 'w') as f:

            for i in model.models:
                if isinstance(i, Load):

                    new_customer_load_string=''
                    new_load_string=''

                    #Name/SectionID
                    new_section=None
                    if  hasattr(i, 'name') and i.name is not None and hasattr(i, 'connecting_element') and i.connecting_element is not None:
                        #try:
                        new_section_ID='{f}_{t}'.format(f=i.connecting_element,t=i.name)
                        new_section='{f}_{t},{f},{t},'.format(f=i.connecting_element,t=i.name)
                        if hasattr(i, 'feeder_name') and i.feeder_name is not None:
                            if i.feeder_name in self.section_feeder_mapping:
                                self.section_feeder_mapping[i.feeder_name].append(new_section_ID)
                            else:
                                self.section_feeder_mapping[i.feeder_name]=[new_section_ID]
                            if hasattr(i, 'substation_name') and i.substation_name is not None:
                                self.section_headnode_mapping[i.feeder_name]=i.substation_name
                        new_customer_load_string+=new_section_ID+','+new_section_ID
                        new_load_string+=new_section_ID+','+new_section_ID
                        if i.name not in self.nodeID_list:
                            self.nodeID_list.append(i.name)
                            if hasattr(i,'positions') and i.positions is not None:
                                try:
                                    X=i.positions[0].long
                                    Y=i.positions[0].lat
                                except:
                                    X=0;Y=0
                                    pass
                            else:
                                X=0;Y=0
                            self.node_string_list.append('{name},{X},{Y}'.format(name=i.name,X=X,Y=Y))
                        #except:
                        #    continue

                    #Currently only spot loads implemented in DiTTo
                    new_customer_load_string+=',SPOT'
                    new_load_string+=',SPOT'

                    if hasattr(i, 'connection_type') and i.connection_type is not None:
                        try:
                            new_load_string+=','+self.connection_configuration_mapping(i.connection_type)
                        except:
                            new_load_string+=','
                            pass

                    phases=''
                    if hasattr(i, 'phase_loads') and i.phase_loads is not None:
                        P=0; Q=0
                        i.phase_loads=[p for p in i.phase_loads if p.drop!=1]
                        #new_customer_load_string+=','
                        for phase_load in i.phase_loads:
                            if hasattr(phase_load, 'phase') and phase_load.phase is not None:
                                phases+=phase_load.phase
                                if new_section is not None:
                                    new_section+=str(phase_load.phase)
                                if hasattr(phase_load,'p') and phase_load.p is not None:
                                    try:
                                        P+=float(phase_load.p)*10**-3
                                    except:
                                        pass
                                if hasattr(phase_load,'q') and phase_load.q is not None:
                                    try:
                                        Q+=float(phase_load.q)*10**-3
                                    except:
                                        pass

                        #Take care of delta connections.
                        #In this case, the corresponding section should be two phase
                        if len(i.phase_loads)==1 and hasattr(i, 'connection_type') and i.connection_type=='D':
                            mapp={'A':'B','B':'C','C':'A'}
                            try:
                                new_section=new_section[:-1]+''.join(sorted(new_section[-1]+mapp[i.phase_loads[0].phase]))
                            except:
                                pass
                        #Value type is set to P and Q
                        try:
                            new_customer_load_string+=',0'
                        except:
                            new_customer_load_string+=','
                            pass

                        #Load phase
                        try:
                            new_customer_load_string+=','+phases
                        except:
                            new_customer_load_string+=','
                            pass

                        #Value1=P
                        try:
                            new_customer_load_string+=','+str(P)
                        except:
                            new_customer_load_string+=','
                            pass

                        #Value2=P
                        try:
                            new_customer_load_string+=','+str(Q)
                        except:
                            new_customer_load_string+=','
                            pass

                    #Location
                    new_load_string+=',0'

                    #CustomerNumber, CustomerType, ConnectionStatus
                    new_customer_load_string+=',0,PQ,0'

                    if new_customer_load_string!='':
                        customer_load_string_list.append(new_customer_load_string)

                    if new_load_string!='':
                        load_string_list.append(new_load_string)

                    if new_section is not None:
                        self.section_line_list.append(new_section)
                        if hasattr(i,'feeder_name') and i.feeder_name is not None:
                            if i.feeder_name in self.section_line_feeder_mapping:
                                self.section_line_feeder_mapping[i.feeder_name].append(new_section)
                            else:
                                self.section_line_feeder_mapping[i.feeder_name]=[new_section]

            f.write('[GENERAL]\n')
            current_date = datetime.now().strftime('%B %d, %Y at %H:%M:%S')
            f.write('DATE={}\n'.format(current_date))
            f.write('CYME_VERSION=8.02\n')
            f.write('\n[SI]\n')

            f.write('\n[LOADS]\n')
            f.write('FORMAT_LOADS=SectionID,DeviceNumber,LoadType,Connection,Location\n')

            for load_string in load_string_list:
                f.write(load_string+'\n')

            f.write('\n[CUSTOMER LOADS]\n')
            f.write('FORMAT_CUSTOMERLOADS=SectionID,DeviceNumber,LoadType,ValueType,LoadPhase,Value1,Value2,CustomerNumber,CustomerType,ConnectionStatus\n')

            for customer_load_string in customer_load_string_list:
                f.write(customer_load_string+'\n')
