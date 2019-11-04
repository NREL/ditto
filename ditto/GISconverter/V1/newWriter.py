"""
author: kapil.duwadi@nrel.gov
created date: 1:41 PM 8/26/2019
"""

import networkx as nx
import pandas as pd
import numpy as np
import shutil
import pathlib, os
import random


class Writer:

    __PhaseDict = {
        1: ['AN',   'BN',   'CN'],
        2: ['ABC',  'ACB',  'BAC',  'BCA',  'CAB',  'CBA'],
        3: ['ABCN', 'ACBN', 'BACN', 'BCAN', 'CABN', 'CBAN' ]
    }

    calendar = {
        'JAN' : 31,
        'FEB' : 28,
        'MAR' : 31,
        'APR' : 30,
        'MAY' : 31,
        'JUN' : 30,
        'JUL' : 31,
        'AUG' : 31,
        'SEP' : 30,
        'OCT' : 31,
        'NOV' : 30,
        'DEC' : 31
    }

    """
    '1Ph Two wire system','1PHASE 2WIRE', '2Ph three wire system', '1PHASE 2WIRW'
    '3Ph Four wire system', '3Ph Five wire system', '3PHASE 4WIRE', '3PHASE 5WIRE', '3PHASE 4WIRE' 
    '3Ph Three wire system' '3PHASE 3WIRE','3PHASE 2 WIRE','3 PHASE 3 WIRE'

    """
    __ConnecDict = {
        'YG'    : 'wye-gnd',
        'Y'     : 'wye',
        'D'     : 'delta'
    }

    __Num2Phase = {
        '1' :   'R',
        '2' :   'Y',
        '3' :   'B'
    }

    __Phase2Num = {
        'R' :   '1',
        'Y' :   '2',
        'B' :   '3'
    }

    def __init__(self, a, path, project_name, penetration_level,PV_cap,rootpath,mapping_dict):
        self.__Files = []
        self._rootpath = rootpath
        self.mapping_dict = mapping_dict
        self.__Freq = 50
        self.__nxGraph = a.NXgraph
        self.FeederHead = a.FeederNode
        self.__whichpath = path
        self.__projectname = project_name
        self.__ClearProjectFolder()
        self.__Create_Line_section()
        self.__Create_wiredata()
        self.__Create_line_geometry()
        self.__CreateLoads()
        self.__CreateBusXYFile()
        self.__Feeder_head()
        self.__PV_scenario_generation_mode(penetration_level, PV_cap)
        self.__CreateCircuit(project_name)

        return


    def __ClearProjectFolder(self):
        print('Creating / cleaning folder: ',  self.__whichpath)
        pathlib.Path(self.__whichpath).mkdir(parents=True, exist_ok=True)
        for root, dirs, files in os.walk(self.__whichpath):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        return

    def __define_line_dict(self,node1,node2,dssDict):
                
        edgeData = self.__nxGraph[node1][node2]
                
        is_neighor_3phwithneutral = 0
        is_neighbor_3ph = 0
        is_neighor_1ph = 0
        
        if edgeData['num_of_cond'] == 4:
            is_neighor_3phwithneutral = 1
        elif edgeData['num_of_cond'] == 3:
            is_neighbor_3ph = 1
        elif edgeData['num_of_cond'] == 2:
            is_neighor_1ph = 1

        if is_neighor_3phwithneutral == 1:
            dssDict['bus1'] = self.__ModifyName(node1) + '.1.2.3.0'
            dssDict['bus2'] = self.__ModifyName(node2) + '.1.2.3.0'
            
        else:
            if is_neighbor_3ph == 1:
                dssDict['bus1'] = self.__ModifyName(node1) + '.1.2.3'
                dssDict['bus2'] = self.__ModifyName(node2) + '.1.2.3'
                    
            else:
                dssDict['bus1']  = self.__ModifyName(node1) + '.' + self.__Phase2Num[self.__nxGraph[node1][node2]['Phase_con']] + '.0'
                dssDict['bus2']  = self.__ModifyName(node2) + '.' + self.__Phase2Num[self.__nxGraph[node1][node2]['Phase_con']] + '.0'

        return dssDict
    
    
    def __ModifyName(self, Name):
        InvalidChars = [' ', ',', '.']
        for InvChar in InvalidChars:
            if InvChar in Name:
                Name = Name.replace(InvChar,'-')
        Name = Name.lower()
        return Name

    def __createxfmrpropname(self, capacity):

        name = 'trans_3ph__' + str(int(capacity))
        return name

    def __Create_wiredata(self):
        condctor_data_sheet = pd.read_csv(self._rootpath + '\\Conductor_data_sheet\\bare_conductor_info.csv')
        D = len(condctor_data_sheet)
        self.wire_info = {}
        for i in range(D):
            dssDict = {
               'diam' : condctor_data_sheet.diam[i],
               'GMRac' : condctor_data_sheet.GMRac[i],
               'GMRunits' : condctor_data_sheet.GMRunits[i],
               'normamps' : condctor_data_sheet.normamps[i],
               'Rac'   : condctor_data_sheet.Rac[i],
               'Runits' : condctor_data_sheet.Runits[i],
               'radunits' : 'mm',
            }
            self.wire_info[self.__ModifyName(condctor_data_sheet.conductor[i])] = dssDict
        self.__toDSS('wiredata', self.wire_info)

    def __Create_line_geometry(self):
        list_of_line_codes  =[]
        for keys, values in self.Lines.items():
            list_of_line_codes.append(values['Geometry'])
        
        unique_geometry = np.unique(list_of_line_codes)
        print(unique_geometry)
        D = len(unique_geometry)
        self.Geometry = {}
        for i in range(D):
            dssDict = {}
            if len(unique_geometry[i].split('__')) == 3:
                which_line = unique_geometry[i].split('__')[2].split('-')[0]
                if unique_geometry[i].split('__')[2].split('-')[2] == '4':
                    nphase = 3 
                elif unique_geometry[i].split('__')[2].split('-')[2] == '3':
                    nphase = 2
                else:
                    nphase  = 1
                phase_cond = unique_geometry[i].split('__')[0].split('_')[0]
                neutral_cond = unique_geometry[i].split('__')[1].split('_')[0]
            else:
                which_line = unique_geometry[i].split('__')[1].split('-')[0]
                if unique_geometry[i].split('__')[1].split('-')[2] == '4':
                    nphase = 3
                elif unique_geometry[i].split('__')[1].split('-')[2] == '3':
                    nphase = 2
                else:
                    nphase  = 1
                phase_cond = unique_geometry[i].split('__')[0].split('_')[0]
                if unique_geometry[i].split('__')[0].split('_')[1] == '2-5':
                    phase_cond = phase_cond + '_2-5'
                elif unique_geometry[i].split('__')[0].split('_')[1] == '4-0':
                    phase_cond = phase_cond + '_4-0'
                neutral_cond = phase_cond

            if which_line == 'lt':
                x = self.mapping_dict["LT_spacing"]
                h = self.mapping_dict["LT_Height"]
            elif which_line == 'ht':
                x  = self.mapping_dict["HT_spacing"]
                h = self.mapping_dict["HT_Height"]
            else:
                x = self.mapping_dict["ST_spacing"]
                h = self.mapping_dict["ST_Height"]
            
            if nphase == 1:
                dssDict = {
                'nconds'  : nphase+1, 'nphases' : nphase,'reduce'  : 'yes', 'cond1': {'cond'   : 1, 'wire': phase_cond, 'x' : x[2], 'h': h, 'units': 'm'}, 'cond2': {'cond': 2, 
                'wire' : neutral_cond,'x' : x[3],'h' : h,'units' : 'm'},
                }
            
            elif nphase == 2:
                dssDict = {
                'nconds'  : nphase+1, 'nphases' : nphase+1,'reduce'  : 'n', 'cond1': {'cond' : 1, 'wire' : phase_cond,'x' : x[1],'h' : h,'units'  : 'm'}, 'cond2' : {'cond'  : 2,
                'wire' : phase_cond,'x' : x[2],'h' : h,'units' : 'm'}, 'cond3': {'cond': 3,'wire': phase_cond,'x':x[3],'h': h,'units': 'm'},
                }
            else:
                 dssDict = {
                'nconds'  : nphase+1, 'nphases' : nphase, 'reduce'  : 'yes','cond1': {'cond'   : 1, 'wire'    : phase_cond,'x' : x[0],'h' : h,'units' : 'm'},'cond2': {'cond'   : 2,
                'wire'    : phase_cond,'x' : x[1],'h' : h,'units': 'm'},'cond3': {'cond' : 3,'wire': phase_cond,'x' : x[2],'h'  : h,'units' : 'm'},
                'cond4': {'cond'   : 4, 'wire'  : neutral_cond,'x' : x[3],'h' : h,'units'  : 'm'},
                }
            self.Geometry[self.__ModifyName(unique_geometry[i])] = dssDict
        self.__toDSS('linegeometry',self.Geometry)
        #self.__Files.append('linegeometry.dss')

    def __Create_Line_section(self):

        self.Lines = {}
        self.Transformers = {}
        self.xfmrnames = []
        index = 0
        for node1, node2 in self.__nxGraph.edges():
            edgeData = self.__nxGraph[node1][node2]
            self.__nxGraph[node1][node2]['Name']  = 'ERODE' + edgeData['Type'] + '_' + str(index)
            if edgeData['Type'] in ['HT line','LT line','Service line']: #  'LT line', 'Service line'              
                if edgeData['Type'] == 'LT line':
                    if edgeData['Cable type neutral'] == 'N' or edgeData['Cable type neutral'] == '2':
                        Geometry = edgeData['Cable type phase'] + '_' + str(edgeData['Cable size phase']) + '__'+ self.__ModifyName(edgeData['Type'])+'-' + str(edgeData['num_of_cond'])
                    else:
                        Geometry = edgeData['Cable type phase'] + '_' + str(edgeData['Cable size phase']) + '__' + edgeData['Cable type neutral'] + '_' + str(edgeData['Cable size neutral']) + '__'+ self.__ModifyName(edgeData['Type']) + '-'+ str(edgeData['num_of_cond']) 
                else:
                    Geometry = edgeData['Cable type phase'] + '_' + str(edgeData['Cable size phase'])+'__'+ self.__ModifyName(edgeData['Type']) + '-'+ str(edgeData['num_of_cond'])
                dssDict = {}
                dssDict =self.__define_line_dict(node1,node2,dssDict)  
                dssDict['length'] = edgeData['Length']
                dssDict['units'] = 'm'
                dssDict['Geometry'] = self.__ModifyName(Geometry)
                dssDict['enabled'] = 'True'

                self.Lines[self.__ModifyName(edgeData['Name'])] =  dssDict
            elif edgeData['Type'] == 'DTs':
                if self.__nxGraph.node[node1]['Type'] == 'HTnode' and self.__nxGraph.node[node2]['Type'] != 'EHTnode': 
                    xfmrpropname = self.__createxfmrpropname(self.__nxGraph[node1][node2]['DT_CC_KVA'])
                    dssDict = {
                        'buses' : '[{0} {1}]'.format(self.__ModifyName(node1) +'.1.2.3', self.__ModifyName(node2) + '.1.2.3.0'),
                        'Xfmrcode' : xfmrpropname,
                        'leadlag'    : 'lead',
                    }
                elif self.__nxGraph.node[node1]['Type'] == 'LTnode':
                    xfmrpropname = self.__createxfmrpropname(self.__nxGraph[node1][node2]['DT_CC_KVA'])
                    dssDict = {
                        'buses' : '[{0} {1}]'.format(self.__ModifyName(node2) +'.1.2.3', self.__ModifyName(node1) + '.1.2.3.0'),
                        'Xfmrcode' : xfmrpropname,
                        'leadlag'    : 'lead',
                    }
                else:
                    if self.__nxGraph.node[node1]['Type'] == 'EHTnode':
                        xfmrpropname = self.__createxfmrpropname(self.mapping_dict["substation_transformer_capacity"])
                        dssDict = {
                        'buses' : '[{0} {1}]'.format(self.__ModifyName(node1) +'.1.2.3', self.__ModifyName(node2) + '.1.2.3.0'),
                        'Xfmrcode' : xfmrpropname,
                        'leadlag'    : 'lead',
                        }
                    else:
                        xfmrpropname = self.__createxfmrpropname(self.mapping_dict["substation_transformer_capacity"])
                        dssDict = {
                        'buses' : '[{0} {1}]'.format(self.__ModifyName(node2) +'.1.2.3', self.__ModifyName(node1) + '.1.2.3.0'),
                        'Xfmrcode' : xfmrpropname,
                        'leadlag'    : 'lead',
                        }   
                self.Transformers[self.__ModifyName(edgeData['Name'])] = dssDict
                self.xfmrnames.append(xfmrpropname)
            index+=1

        self.__toDSS('lines_line',self.Lines)
        self.__toDSS('transformers_transformer', self.Transformers)
        #self.__Files.append('lines.dss')
        #self.__Files.append('transformers.dss')
        self.__create_xfmr_codes()
    
    
    def __create_xfmr_codes(self):
        list_of_unique_codes = np.unique(self.xfmrnames)
        D = len(list_of_unique_codes)
        self.__XFMRcodes = {}
        for i in range(D):
            cap = list_of_unique_codes[i].split('__')[1]
            if int(cap) == self.mapping_dict["substation_transformer_capacity"]:
                dssDict = {
                    'Phases'     : 3,
                        'Windings'   : 2,
                        'conns'      : '[{} {}]'.format(self.mapping_dict["SS_conn"][0],self.mapping_dict["SS_conn"][1]),
                        '%R'         : self.mapping_dict["Transformer_properties"]["%R"],
                        'Xhl'        : self.mapping_dict["Transformer_properties"]["Xhl"],
                        'KVAs'       : '[{} {}]'.format(cap,cap),
                        'kvs'        : '[{} {}]'.format(self.mapping_dict["SS_trans_voltage"][0],self.mapping_dict["SS_trans_voltage"][1]),
                        'maxtap'     : self.mapping_dict["Transformer_properties"]["maxtap"],
                        'mintap'     : self.mapping_dict["Transformer_properties"]["mintap"],
                        'tap'        : self.mapping_dict["Transformer_properties"]["tap"],
                        'numtaps'    : self.mapping_dict["Transformer_properties"]["numtaps"], 
                }
            else:
                dssDict = {
                        'Phases'     : 3,
                        'Windings'   : 2,
                        'conns'      : '[{} {}]'.format(self.mapping_dict["Transformer_properties"]["connection"][0],self.mapping_dict["Transformer_properties"]["connection"][1]),
                        '%R'         : self.mapping_dict["Transformer_properties"]["%R"],
                        'Xhl'        : self.mapping_dict["Transformer_properties"]["Xhl"],
                        'KVAs'       : '[{} {}]'.format(cap,cap),
                        'kvs'        : '[{} {}]'.format(self.mapping_dict["Transformer_properties"]["voltage"][0],self.mapping_dict["Transformer_properties"]["voltage"][1]),
                        'maxtap'     : self.mapping_dict["Transformer_properties"]["maxtap"],
                        'mintap'     : self.mapping_dict["Transformer_properties"]["mintap"],
                        'tap'        : self.mapping_dict["Transformer_properties"]["tap"],
                        'numtaps'    : self.mapping_dict["Transformer_properties"]["numtaps"],
                    }
            
            self.__XFMRcodes[list_of_unique_codes[i]] = dssDict
        self.__toDSS('xfmrcode', self.__XFMRcodes)
        return
    
    
    def __toDSS(self, ElementType, info_dict):
        if '_' in ElementType:
            ElmType = ElementType.split('_')[1]
            FileName = ElementType.split('_')[0]
        else:
            ElmType = ElementType
            FileName = ElementType
        
        print('Writing FIle -' + FileName + '.dss')
        Path = self.__whichpath
        is_dict = 0
        file = open(Path + '/' + FileName + '.dss', 'w')
        for Name, Properties in info_dict.items():
            NewCmd = 'New '+ ElmType + '.' + Name + ' '
            for propName, propValue in Properties.items():
                if isinstance(propValue,dict):
                    file.write(NewCmd.lower()+'\n')
                    is_dict = 1
                    NewCmd = '~ '
                    for key, value in propValue.items():
                         NewCmd += key + '=' + str(value) + ' '
                else:
                    NewCmd += propName + '=' + str(propValue ) + ' '
            if is_dict == 0:
                file.write(NewCmd.lower()+'\n')
            else:
                file.write(NewCmd.lower()+'\n')
            file.write('\n')
        file.close()
    
    def __CreateLoads(self):
        self.__Load = {}
        self.__LOADTEC = {}
        for node in self.__nxGraph.nodes():
            nodedata = self.__nxGraph.node[node]
            if 'loads' in nodedata:
                for keys, values in nodedata['loads'].items():
                    if values['phase'] == 'RYB' and values['voltage'] == self.mapping_dict["HT_voltage"]:
                        bus1code = '.1.2.3'
                    else:
                        if values['phase'] == 'RYB':
                            bus1code = '.1.2.3.0'
                        else:
                            bus1code = '.' + self.__Phase2Num[values['phase']] + '.0'
                    dssDict = {
                        'phases' : 3 if values['phase'] == 'RYB' else 1,
                        'bus1' : self.__ModifyName(node) + bus1code,
                        'kv'   : values['voltage'],
                        'kw'   : values['load'],
                        'pf'   : values['pf'],
                        'yearly' : 'loadmult'
                    }
                    if 'TEC' in values: self.__LOADTEC[self.__ModifyName(keys)] = values['TEC'] 
                    self.__Load[self.__ModifyName(keys)] = dssDict
        
        self.__toDSS('load',self.__Load)
        #self.__Files.append('load.dss')
    
    def __CreateBusXYFile(self):
        print('Writing File - Bus_Coordinates.csv')
        file = open(self.__whichpath + '/Bus_Coordinates.csv', 'w')
        Nodes = self.__nxGraph.nodes()
        for Node in Nodes:
            nodeAttrs = self.__nxGraph.node[Node]
            if 'x' in nodeAttrs and 'y' in nodeAttrs:
                X = nodeAttrs['x']
                Y = nodeAttrs['y']
                file.write(self.__ModifyName(Node) + ', ' + str(X) + ', ' + str(Y) + '\n')
        file.close()
        self.__CoordFileName = 'Bus_Coordinates.csv'
        return

    
    def __Feeder_head(self):
        self.__FeederNode = self.__ModifyName(self.FeederHead)
        print(self.__FeederNode)
    
    def __PV_scenario_generation_mode(self,penetration_level, PV_cap):
        self.__generate_PVShape()
        dict_of_LT_loads = {}
        self.__PVSystem = {}
        list_of_customers = []
        for keys, values in self.__Load.items():
            if values['kv'] != self.mapping_dict["HT_voltage"]:
                dict_of_LT_loads[keys] = values
                list_of_customers.append(keys)

        num_of_LT_customers = len(dict_of_LT_loads)
        customer_ID_list=  list(range(0,num_of_LT_customers))
        num_of_LT_customers_with_PV = int(penetration_level*num_of_LT_customers/100)
        for i in range(num_of_LT_customers_with_PV):
            rand_number = random.choice(customer_ID_list)
            customer_ID_list.remove(rand_number)
            LT_PV = {}
            LT_PV[list_of_customers[rand_number]] = dict_of_LT_loads[list_of_customers[rand_number]]
            for keys, values in LT_PV.items():
                PV_capacity = PV_cap*self.__LOADTEC[keys]/(100*365*24*self.yearly_cap_factor)
                dssDict = {
                'bus1' :values['bus1'],
                'phases': values['phases'],
                'kv' : values['kv'],
                'kva' : PV_capacity*self.mapping_dict["PV_ppt"]["inverter_oversize_factor"] if PV_capacity !=0 else 0.1,
                'irradiance': self.mapping_dict["PV_ppt"]["irradiance"],
                'pmpp': PV_capacity, 
                'kvar': self.mapping_dict["PV_ppt"]["kvar"],
                '%cutin': self.mapping_dict["PV_ppt"]["%cutin"],
                '%cutout': self.mapping_dict["PV_ppt"]["%cutout"],
                'yearly' : 'solarmult'
                }
                if values['phases'] == 3:
                    dssDict['balanced'] = 'yes'
            self.__PVSystem[keys+'PV'] = dssDict
        self.__toDSS('PVSystem',self.__PVSystem)
        self.__create_load_shape()
    
    def __generate_PVShape(self):

        self.__analyze_PV_capacity_factor()
        solar_data = pd.read_csv(self._rootpath+ '\\Solar_CSVs\\solar_data.csv')

        irradiance_data = solar_data.GHI
        irradiance_data = irradiance_data.to_numpy()
        D=len(irradiance_data)
        irr_data=[]

        for i in range(D-1):
            irr_data.append(irradiance_data[i]/1000)
            chunk_size = (irradiance_data[i+1]-irradiance_data[i])/4000.0
            for j in range(3):
                irr_data.append(irradiance_data[i]/1000.0+(j+1)*chunk_size)
                index = i

        irr_data.append(irradiance_data[index+1]/1000)
        for j in range(3):
                irr_data.append(irradiance_data[index+1]/1000.0+(j+1)*chunk_size)
        
        assert len(irr_data) == 35040

    
        where_solar = self.__whichpath + '/solarmult.csv'

        irr_data = pd.DataFrame(irr_data,columns=None)
        irr_data.to_csv(where_solar,index=False)
       

        where_to=  self.__whichpath + '/loadmult.csv'
        which_csv = self._rootpath+ '\\Load_multipliers_csvs\\'+ self.__projectname + '.csv'

        shutil.copy(which_csv, where_to)
        
        return

    
    def __analyze_PV_capacity_factor(self):
        solar_data = pd.read_csv(self._rootpath+'\\Solar_CSVs\\solar_data.csv')

        irradiance_data = solar_data.GHI
        irradiance_data = irradiance_data.to_numpy()

        capacity_factor_X = []
        capacity_factor_Y = []
        count =0

        for key, value in self.calendar.items():
            capacity_factor_X.append(key)
            slice_irrad = irradiance_data[count:count+value*24]
            count += value*24
            cap_fac = sum(slice_irrad)*100/(value*24*max(slice_irrad))
            print(key,cap_fac)
            capacity_factor_Y.append(cap_fac)
        
        print(capacity_factor_Y)

        self.yearly_cap_factor = sum(irradiance_data)/(24*365*max(irradiance_data))
        print('Annual PV capacity factor: ',self.yearly_cap_factor)    
    
    def __create_load_shape(self):
        self.__loadshape = {}
        shapes=['loadmult','solarmult']
        for i in range(len(shapes)):
            dssDict = {
                'npts' : 35040,
                'minterval' : 15,
                'mult': '(file='+ shapes[i] + '.csv)',
            }
            self.__loadshape[shapes[i]] = dssDict
        self.__toDSS('loadshape',self.__loadshape)
    

    def __CreateCircuit(self,CircuitName):
        Z1 = [0.001,0.001]
        Z0 = [0.001,0.001]
        print('Writing File - ' + CircuitName + '.dss')
        file = open(self.__whichpath + '/' + CircuitName + '.dss', 'w')
        file.write('clear\n\n')
        file.write('New circuit.' + CircuitName.lower() + '\n')
        file.write('~ basekv= 110.0 pu=1.02 phases=3 Z1={0} Z0= {1} bus1={2}\n'.format(Z1,Z0,self.__FeederNode+'.1.2.3'))
        #file.write('~ MVAsc3=20 MVASC1=21 \n\n'.lower())
        self.__Files.append('wiredata.dss')
        self.__Files.append('linegeometry.dss')
        self.__Files.append('xfmrcode.dss')
        self.__Files.append('lines.dss')
        self.__Files.append('transformers.dss')
        self.__Files.append('loadshape.dss')
        self.__Files.append('load.dss')
        self.__Files.append('PVSystem.dss')

        for Filename in self.__Files:
            file.write('redirect ' + Filename.lower() + '\n\n')
        
        file.write('Set voltagebases={}\n\n'.format([self.mapping_dict["XHT_voltage"],self.mapping_dict["HT_voltage"],self.mapping_dict["LT_voltage"],self.mapping_dict["LT_phase_voltage"]] ))  
        file.write('Calcv\n\n')
        file.write('set mode = yearly\n\n')
        file.write('set stepsize = 15m\n\n')
        #file.write('plot profile\n\n')
        #file.write('Solve\n\n')
        file.write('BusCoords ' + self.__CoordFileName + '\n\n')
        file.write('plot circuit\n\n')
        file.write('plot profile\n\n')
        file.close()
        