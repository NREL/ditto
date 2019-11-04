"""
Created on Wed Sep 11 1:43:57 2019
@author: kduwadi
"""

import numpy as np 
import pandas as pd
import os
import networkx as nx 
import matplotlib.pyplot as plt
from bokeh.plotting import figure, output_file, show
import matplotlib.colors as colors
from bokeh.core.properties import value
from bokeh.plotting import figure
import copy
from bokeh.layouts import column
import math
import random
import pickle


class Reader:

    code_name = {
        'consumer_ht.csv' : {'code': 'N', 'type': 'Consumer_HT'},
        'consumer_lt.csv' : {'code': 'N', 'type': 'Consumer_LT'},
        'distribution_transformer.csv' : {'code': 'N', 'type': 'DTs'},
        'ht_cable_attributes.csv' : {'code': 'L', 'type': 'HT_cable', 'feature': 'Attribute data'},
        'ht_cable_nodes.csv' : {'code': 'L', 'type': 'HT_cable', 'feature': 'Coordinates'},
        'ht_line_attributes.csv' : {'code': 'L', 'type': 'HT_line', 'feature': 'Attribute data'},
        'ht_line_nodes.csv' : {'code': 'L', 'type': 'HT_line', 'feature': 'Coordinates'},
        'ht_pole.csv' : {'code': 'N', 'type': 'HTpole'},
        'lt_cable_attributes.csv' : {'code': 'L', 'type': 'LT_cable', 'feature': 'Attribute data'},
        'lt_cable_nodes.csv' : {'code': 'L', 'type': 'LT_cable', 'feature': 'Coordinates'},
        'lt_line_attributes.csv' : {'code': 'L', 'type': 'LT_line', 'feature': 'Attribute data'},
        'lt_line_nodes.csv' : {'code': 'L', 'type': 'LT_line', 'feature': 'Coordinates'},
        'lt_pole.csv' : {'code': 'N', 'type': 'LTpole'},
        'power_transformer.csv' : {'code': 'N', 'type': 'PTs'},
        'substation.csv': {'code': 'N', 'type': 'SS'},
    }

    def __init__(self,list_of_files,path, feedername,mapper_dict):
        
        self.filelists = list_of_files
        self.path = path
        self.mapper_dict = mapper_dict
        self.feedername = feedername
        self.__Create_file_dictionary()

        print('\n -------------------------',self.feedername,' Feeder','-----------------------------------------')

        self.Line_data = {}
        for Element, FileDict in self.LineFiles.items():
            CoordinateData = pd.read_csv(os.path.join(path, FileDict['Coordinates']),index_col=None)
            AttributeData = pd.read_csv(os.path.join(path, FileDict['Attribute data']),index_col=None)
            self.Line_data[Element] = {'CD' : CoordinateData, 'ATD' : AttributeData}
        
        self.Node_data = {}
        for Element, Filepath in self.NodeFiles.items():
            NodeData = pd.read_csv(os.path.join(path,Filepath),index_col=None)
            self.Node_data[Element] = NodeData
        
        self.NXgraph = nx.Graph()
        if 'HT_line' in self.LineFiles:
            self.__Create_HT_Edges()
        if 'HT_cable' in self.LineFiles:
            self.__Create_HT_Cables()
        #self.__GetGraphMetrics()
        #self.__visualize_Islands()
        self.__fix_network_islands()
        #self.__GetGraphMetrics()
        #self.__visualize_Islands()
        if 'LT_line' in self.LineFiles:
            self.__Create_LT_Edges()
            self.__change_LT_property()
        if 'LT_cable' in self.LineFiles:
            self.__Create_LT_Cables()
        if 'DTs' in self.NodeFiles:
            self.__add_distribution_transformers_node_to_network()
        #self.__visualize_Islands()
        self.__fix_network_islands()
        self.__fix_phase_issue_in_LT_line()
        #self.__GetGraphMetrics()
        self.__force_all_LT_line_tobe3phase()
        if 'Consumer_LT' in self.NodeFiles:
            #self.__add_LT_loads()
            self.__add_LT_loads_random_phase_allocation()
        if 'Consumer_HT' in self.NodeFiles:
            self.__add_HT_loads()
        #self.__plot_colored_network()
        if 'PTs' in self.NodeFiles:
            self.__add_power_transformers()
        self.__Add_line_edge_property()
        #self.__plot_load_distribution()
        #self.__count_single_phase_customers_connected_to_single_phase_LT_line()
        #self.__plot_colored_network()
        #self.__count_number_of_downstream_customers()
        pickle.dump(self.NXgraph,open(self.feedername+'_network.p',"wb"))
        print('Successfully build the ',feedername, ' Feeder !!!!!!')

        return
    
    def __Create_file_dictionary(self):
        self.LineFiles = {}
        self.NodeFiles = {}
        for i in range(len(self.filelists)):
            this_dict = self.code_name[self.filelists[i]]
            if this_dict['code'] == 'N':
                self.NodeFiles[this_dict['type']] = self.filelists[i]
            else:
                if this_dict['type'] not in self.LineFiles:
                    self.LineFiles[this_dict['type']] = {}
                    self.LineFiles[this_dict['type']][this_dict['feature']] = self.filelists[i]
                else:
                    self.LineFiles[this_dict['type']][this_dict['feature']] = self.filelists[i]
        #print(self.LineFiles)
        #print(self.NodeFiles)
        return
    
    def __Create_HT_Edges(self):
        
        cData = self.Line_data['HT_line']['CD']
        aData = self.Line_data['HT_line']['ATD']
            
        print('Creating HT_edges')
        D = len(aData)
            
        for i in range(D):
            AttData = aData.loc[i]
            shapeID = AttData['shapeid']
            ElmCoordinateData = cData[cData['shapeid'] == shapeID]
            ElmCoordinateData.index = range(len(ElmCoordinateData))
            X1 = ElmCoordinateData['x'][0]
            X2 = ElmCoordinateData['x'][len(ElmCoordinateData)-1]
            Y1 = ElmCoordinateData['y'][0]
            Y2 = ElmCoordinateData['y'][len(ElmCoordinateData)-1]
        
            Attributes = {
                'Type'       : 'HT line',      
                'Length'     : AttData[self.mapper_dict["HT line"]["Length"]],
                'Phase_con'      : AttData[self.mapper_dict["HT line"]["Phase_con"]],
                'Cable size phase'   : AttData[self.mapper_dict["HT line"]["Cable size phase"]],
                'Phase info'  : AttData[self.mapper_dict["HT line"]["Phase info"]],
                'Cable type phase'   : AttData[self.mapper_dict["HT line"]["Cable type phase"]],
                }
            self.NXgraph.add_edge('{}_{}_HT'.format(X1,Y1), '{}_{}_HT'.format(X2,Y2), **Attributes)
            self.NXgraph.node['{}_{}_HT'.format(X1,Y1)]['x'] = X1
            self.NXgraph.node['{}_{}_HT'.format(X1,Y1)]['y'] = Y1
            self.NXgraph.node['{}_{}_HT'.format(X1,Y1)]['Type'] = 'HTnode'
            self.NXgraph.node['{}_{}_HT'.format(X2,Y2)]['x'] = X2
            self.NXgraph.node['{}_{}_HT'.format(X2,Y2)]['y'] = Y2
            self.NXgraph.node['{}_{}_HT'.format(X2,Y2)]['Type'] = 'HTnode'
        return
    
    def __Create_HT_Cables(self):
        
        cData = self.Line_data['HT_cable']['CD']
        aData = self.Line_data['HT_cable']['ATD']
            
        print('Creating HT_Cables')
        D = len(aData)
            
        for i in range(D):
            AttData = aData.loc[i]
            shapeID = AttData['shapeid']
            ElmCoordinateData = cData[cData['shapeid'] == shapeID]
            ElmCoordinateData.index = range(len(ElmCoordinateData))
            X1 = ElmCoordinateData['x'][0]
            X2 = ElmCoordinateData['x'][len(ElmCoordinateData)-1]
            Y1 = ElmCoordinateData['y'][0]
            Y2 = ElmCoordinateData['y'][len(ElmCoordinateData)-1]
        
            Attributes = {
                'Type'       : 'HT cable',      
                'Length'     : AttData[self.mapper_dict["HT cable"]["Length"]],
                'Phase_con'      : self.mapper_dict["HT cable"]["Phase_con"],
                'Cable size phase'   : AttData[self.mapper_dict["HT cable"]["Cable size phase"]],
                'Phase info'  : AttData[self.mapper_dict["HT cable"]["Phase info"]],
                'Cable type phase'   : AttData[self.mapper_dict["HT cable"]["Cable type phase"]],
                }
            self.NXgraph.add_edge('{}_{}_HT'.format(X1,Y1), '{}_{}_HT'.format(X2,Y2), **Attributes)
            self.NXgraph.node['{}_{}_HT'.format(X1,Y1)]['x'] = X1
            self.NXgraph.node['{}_{}_HT'.format(X1,Y1)]['y'] = Y1
            self.NXgraph.node['{}_{}_HT'.format(X1,Y1)]['Type'] = 'HTnode'
            self.NXgraph.node['{}_{}_HT'.format(X2,Y2)]['x'] = X2
            self.NXgraph.node['{}_{}_HT'.format(X2,Y2)]['y'] = Y2
            self.NXgraph.node['{}_{}_HT'.format(X2,Y2)]['Type'] = 'HTnode'
        return
    
    def __GetGraphMetrics(self):

        print('Number of nodes: ' + str(len(self.NXgraph.nodes())))
        self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))
        self.NumIslands = len(self.Islands)
        print('Number of islands: ' + str(len(self.Islands)))
        self.Loops = nx.cycle_basis(self.NXgraph)
        print('Number of loops: ' + str(len(self.Loops)))
        return
    
    def __visualize_Islands(self):
        colors_list = list(colors._colors_full_map.values())

        output_file('Bokeh_plots/'+self.feedername + '_islands.html')

        p = figure(plot_width = 1000, plot_height = 600)

        self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))
        for color_index, island in enumerate(self.Islands):
            for node1, node2 in island.edges():
                edgeData = self.NXgraph[node1][node2]
                N1 = self.NXgraph.node[node1]
                X1 = N1['x']
                Y1 = N1['y']
                N2 = self.NXgraph.node[node2]
                X2 = N2['x']
                Y2 = N2['y']
                p.line([X1, X2], [Y1, Y2], color = colors_list[color_index], line_width = 2.0)
        show(p)

    def __fix_network_islands(self):

        self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))

        for i in range(len(self.Islands)-1):
            D = 99999999
            for node1 in self.Islands[0].nodes():
                X0 = self.Islands[0].node[node1]['x']
                Y0 = self.Islands[0].node[node1]['y']
                for k in range(len(self.Islands)):
                    if k != 0:
                        for node2 in self.Islands[k].nodes():
                            X1 =  self.Islands[k].node[node2]['x']
                            Y1 =  self.Islands[k].node[node2]['y']
                            if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < D:
                                D = np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                                N1 = node1
                                N2 = node2
            self.NXgraph = nx.contracted_nodes(self.NXgraph,N1,N2)
            self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))
    
    def __Create_LT_Edges(self):
        
        cData = self.Line_data['LT_line']['CD']
        aData = self.Line_data['LT_line']['ATD']

        print('Creating LT_edges')

        D = len(aData)
            
        for i in range(D):
            AttData = aData.loc[i]
            shapeID = AttData['shapeid']
            ElmCoordinateData = cData[cData['shapeid'] == shapeID]
            ElmCoordinateData.index = range(len(ElmCoordinateData))
            X1 = ElmCoordinateData['x'][0]
            X2 = ElmCoordinateData['x'][len(ElmCoordinateData)-1]
            Y1 = ElmCoordinateData['y'][0]
            Y2 = ElmCoordinateData['y'][len(ElmCoordinateData)-1]
            
            Attributes = {
                'Type'               : 'LT line', 
                'KV'                 : AttData[self.mapper_dict["LT line"]["KV"]],
                'Phase_con'          : AttData[self.mapper_dict["LT line"]["Phase_con"]],
                'Length'             : AttData[self.mapper_dict["LT line"]["Length"]],
                'Enabled'            : AttData[self.mapper_dict["LT line"]["Enabled"]],
                'Cable ID'           : AttData[self.mapper_dict["LT line"]["Cable ID"]],
                'Phase info'         : AttData[self.mapper_dict["LT line"]["Phase info"]],
                'Cable size phase'   : AttData[self.mapper_dict["LT line"]["Cable size phase"]],
                'Cable size neutral' : AttData[self.mapper_dict["LT line"]["Cable size neutral"]],
                'Cable type phase'   : AttData[self.mapper_dict["LT line"]["Cable type phase"]],
                'Cable type neutral' : AttData[self.mapper_dict["LT line"]["Cable type neutral"]],
                }
            self.NXgraph.add_edge('{}_{}_LT'.format(X1,Y1), '{}_{}_LT'.format(X2,Y2), **Attributes)
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['x'] = X1
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['y'] = Y1
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['Type'] = 'LTnode'
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['x'] = X2
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['y'] = Y2
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['Type'] = 'LTnode'
        return
    
    def __change_LT_property(self):

        '''
        My assumption during modelling: all 1Ph three wire and 2Ph three wire system with voltage 0.44 are considered three phase and phase connection changed to RYB

        '1Ph Three wire system' '1Ph Two wire system' '2Ph Three wire system' '3Ph Five wire system', '3Ph Four wire system'
        '''
        for node1, node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] == 'LT line':
                if edgeData['KV'] == self.mapper_dict["LT_voltage"]:
                    edgeData['Phase_con'] = self.mapper_dict["three_phase_con"]
                    edgeData['Phase info'] = self.mapper_dict["correct_three_phase_name"]

        return

    def __Create_LT_Cables(self):
        
        cData = self.Line_data['LT_cable']['CD']
        aData = self.Line_data['LT_cable']['ATD']

        print('Creating LT_cables')

        D = len(aData)
            
        for i in range(D):
            AttData = aData.loc[i]
            shapeID = AttData['shapeid']
            ElmCoordinateData = cData[cData['shapeid'] == shapeID]
            ElmCoordinateData.index = range(len(ElmCoordinateData))
            X1 = ElmCoordinateData['x'][0]
            X2 = ElmCoordinateData['x'][len(ElmCoordinateData)-1]
            Y1 = ElmCoordinateData['y'][0]
            Y2 = ElmCoordinateData['y'][len(ElmCoordinateData)-1]
            
            Attributes = {
                'Type'               : 'LT cable', 
                'KV'                 : AttData[self.mapper_dict["LT cable"]["KV"]],
                'Phase_con'          : AttData[self.mapper_dict["LT cable"]["Phase_con"]],
                'Length'             : AttData[self.mapper_dict["LT cable"]["Length"]],
                'Enabled'            : AttData[self.mapper_dict["LT cable"]["Enabled"]],
                'Cable ID'           : AttData[self.mapper_dict["LT cable"]["Cable ID"]],
                'Phase info'         : AttData[self.mapper_dict["LT cable"]["Phase info"]],
                'Cable size phase'   : AttData[self.mapper_dict["LT cable"]["Cable size phase"]],
                'Cable type phase'   : AttData[self.mapper_dict["LT cable"]["Cable type phase"]],
                }
            self.NXgraph.add_edge('{}_{}_LT'.format(X1,Y1), '{}_{}_LT'.format(X2,Y2), **Attributes)
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['x'] = X1
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['y'] = Y1
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['Type'] = 'LTnode'
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['x'] = X2
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['y'] = Y2
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['Type'] = 'LTnode'
        return

    def __plot_colored_network(self):
        output_file('Bokeh_plots/'+self.feedername+'_Feeder.html')

        p = figure(plot_width = 1200, plot_height = 800)

        colors = ["#c9d9d3", "#718dbf", "#e84d60","#008000"]

        for node1, node2 in self.NXgraph.edges():
            N1 = self.NXgraph.node[node1]
            X1 = N1['x']
            Y1 = N1['y']
            N2 = self.NXgraph.node[node2]
            X2 = N2['x']
            Y2 = N2['y']
            type = self.NXgraph[node1][node2]['Type']
            if type in ['HT line', 'LT line', 'HT cable', 'LT cable','Service line']:
                if self.NXgraph[node1][node2]['Phase_con'] == 'RYB':
                    p.line([X1, X2], [Y1, Y2],color='#008000')
                elif self.NXgraph[node1][node2]['Phase_con'] == 'R':
                    p.line([X1, X2], [Y1, Y2],color='#FF0000')
                elif self.NXgraph[node1][node2]['Phase_con'] == 'Y':
                    p.line([X1, X2], [Y1, Y2],color='#FFFF00')
                elif self.NXgraph[node1][node2]['Phase_con'] == 'B':
                    p.line([X1, X2], [Y1, Y2],color='#0000ff')
            if type == 'DTs':
                p.line([X1, X2], [Y1, Y2],color='#000000',line_width = 20.0)
        show(p)
    
    def __add_distribution_transformers_node_to_network(self):

        print("Adding distribution transformers")
 
        for type, typeData in self.Node_data.items():
            
            if type == 'DTs':
                
                D = len(typeData)
            
            
                for i in range(D):
                    transData = typeData.loc[i]
                    ElmDict  = transData.to_dict()
                    ElmDict['Type'] =  type
                    
                    X0 = transData['x']
                    Y0 = transData['y']
                    
                    dist_from_ht_node = 99999999
                    dist_from_lt_node = 99999999
                    nearest_ht_node = None
                    nearest_lt_node = None
                    
                    
                    for Node in self.NXgraph.nodes():
                        X1 = self.NXgraph.node[Node]['x']
                        Y1 = self.NXgraph.node[Node]['y']
                        
                        if self.NXgraph.node[Node]['Type'] == 'HTnode':
                            if np.sqrt((X1-X0)**2+(Y1-Y0)**2) < dist_from_ht_node:
                                dist_from_ht_node = np.sqrt((X1-X0)**2+(Y1-Y0)**2)
                                nearest_ht_node = Node
                        
                        elif self.NXgraph.node[Node]['Type'] == 'LTnode':
                            if np.sqrt((X1-X0)**2+(Y1-Y0)**2) < dist_from_lt_node:
                                dist_from_lt_node = np.sqrt((X1-X0)**2+(Y1-Y0)**2)
                                nearest_lt_node = Node
                            
                        
                    self.NXgraph.add_edge(nearest_ht_node, nearest_lt_node, **ElmDict)
        return
    
    

    def __count_single_phase_customers_connected_to_single_phase_LT_line(self):
        R_cust = 0
        for node1, node2 in self.NXgraph.edges():
            if self.NXgraph[node1][node2]['Type'] == 'LT line' and self.NXgraph[node1][node2]['num_of_cond']==2:
                #phase_list = ['R', 'Y', 'B']
                temp_network =copy.deepcopy(self.NXgraph)
                temp_network.remove_edge(node1,node2)
                Islands = list(nx.connected_component_subgraphs(temp_network))    
                number_of_nodes = 9999999
                for i in range(len(Islands)):
                    if len(Islands[i].nodes) < number_of_nodes:
                        number_of_nodes = len(Islands[i].nodes)
                        island_index = i
                for node1, node2 in Islands[island_index].edges():
                    if self.NXgraph[node1][node2]['Type'] == 'Service line':
                        R_cust +=1
        print('R customers inevitable: ', R_cust)
                    

    
    def __add_LT_loads_random_phase_allocation(self):

        # Adding low tension costumers load nodes , all are connected to service line
        D = len(self.Node_data['Consumer_LT'])
        con_LT = self.Node_data["Consumer_LT"].rename(columns=self.mapper_dict["consumer_LT_converter"])
        for i in range(D):

            X0 = con_LT.X0[i]
            Y0 = con_LT.Y0[i]

            dist_from_consumer_lt = 9999999
            node_of_interest = None
            for Node in self.NXgraph.nodes():
                if self.NXgraph.node[Node]['Type'] == 'LTnode':
                    X1 = self.NXgraph.node[Node]['x']
                    Y1 = self.NXgraph.node[Node]['y']

                    if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < dist_from_consumer_lt:
                        dist_from_consumer_lt =  np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                        node_of_interest = Node
            

            neighbor_of_LT_node = [n for n in self.NXgraph.neighbors(node_of_interest)]
            
            flag = 0
            for Node in neighbor_of_LT_node:
                if 'Phase_con' in self.NXgraph[Node][node_of_interest] and self.NXgraph[Node][node_of_interest]['Phase_con'] == 'RYB':
                    flag = 1

            if flag == 0:
                phasecon = self.NXgraph[neighbor_of_LT_node[0]][node_of_interest]['Phase_con']
                phaseinfo = self.mapper_dict["correct_single_phase_name"]
            else:
                if self.Node_data['Consumer_LT'].LTC_PHASE[i] == self.mapper_dict["three_phase_con"]:
                    phasecon = self.mapper_dict["three_phase_con"]
                    phaseinfo = self.mapper_dict["correct_three_phase_name"]               
                else:
                    phasecon = random.choice(self.mapper_dict["single_phase_con_list"])
                    phaseinfo = self.mapper_dict["correct_single_phase_name"]

            Attributes = {
                'Type'               : 'Service line', 
                'KV'                 : con_LT.KV[i],
                'Phase_con'          : phasecon,
                'Length'             : dist_from_consumer_lt,
                'Enabled'            : con_LT.Enabled[i],
                'Cable ID'           : con_LT.CID[i],
                'Phase info'         : phaseinfo,
                'Cable size phase'   : self.mapper_dict["service_cond_size"],
                'Cable type phase'   : self.mapper_dict["service_cond_type"],
                }
            self.NXgraph.add_edge('{}_{}_LT'.format(X0,Y0),node_of_interest, **Attributes)
            self.NXgraph.node['{}_{}_LT'.format(X0,Y0)]['x'] = X0
            self.NXgraph.node['{}_{}_LT'.format(X0,Y0)]['y'] = Y0
            self.NXgraph.node['{}_{}_LT'.format(X0,Y0)]['Type'] = 'STnode'

            

            NodeData = self.NXgraph.node['{}_{}_LT'.format(X0,Y0)]
            customerID = con_LT.customerID[i]
            kW_load = con_LT.kW_load[i]
            pf = con_LT.pf[i]
            phase = phasecon
            TEC = con_LT.TEC[i]
            cons_type = con_LT.Costumer[i]

            if 'loads' not in NodeData:
                NodeData['loads']  ={}
            NodeData['loads'][customerID]= {
                'load'  : kW_load,
                'pf'    : 0.9 if math.isnan(pf) else pf,
                'phase' : phase,
                'voltage' : 0.44 if phase == 'RYB' else 0.254,
                'TEC' : TEC,
                'con_type': cons_type
            }
        print('LT costumers sucessfully added by randomly allocating phases!!!')
        
    def __add_HT_loads(self):

        # Adding low tension costumers load nodes , all are connected to service line
        D = len(self.Node_data['Consumer_HT'])
        con_HT = self.Node_data["Consumer_HT"].rename(columns=self.mapper_dict["consumer_HT_converter"])
        for i in range(D):

            X0 = con_HT.X0[i]
            Y0 = con_HT.Y0[i]

            dist_from_consumer_ht = 9999999
            node_of_interest = None
            for Node in self.NXgraph.nodes():
                if self.NXgraph.node[Node]['Type'] == 'HTnode':
                    X1 = self.NXgraph.node[Node]['x']
                    Y1 = self.NXgraph.node[Node]['y']

                    if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < dist_from_consumer_ht:
                        dist_from_consumer_ht =  np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                        node_of_interest = Node
            

            Attributes = {
                'Type'               : 'HT line', 
                'KV'                 : con_HT.KV[i],
                'Phase_con'          : con_HT.phase[i],
                'Length'             : dist_from_consumer_ht,
                'Enabled'            : con_HT.Enabled[i],
                'Cable ID'           : con_HT.CID[i],
                'Phase info'         : self.mapper_dict["correct_three_phase_name"] if con_HT.phase[i] == self.mapper_dict["three_phase_con"] else self.mapper_dict["correct_single_phase_name"],
                'Cable size phase'   : self.mapper_dict["HT_cond_size"],
                'Cable type phase'   : self.mapper_dict["HT_cond_type"],
                }
            self.NXgraph.add_edge('{}_{}_HT'.format(X0,Y0),node_of_interest, **Attributes)
            self.NXgraph.node['{}_{}_HT'.format(X0,Y0)]['x'] = X0
            self.NXgraph.node['{}_{}_HT'.format(X0,Y0)]['y'] = Y0
            self.NXgraph.node['{}_{}_HT'.format(X0,Y0)]['Type'] = 'HTnode'



            NodeData = self.NXgraph.node['{}_{}_HT'.format(X0,Y0)]
            customerID = con_HT.customerID[i]
            kW_load = con_HT.kW_load[i]
            pf = con_HT.pf[i]
            phase = con_HT.phase[i]
            volt = con_HT.KV[i]
            cons_type = con_HT.Costumer[i]

            if 'loads' not in NodeData:
                NodeData['loads']  ={}
            NodeData['loads'][customerID]= {
                'load'  : kW_load,
                'pf'    : 0.9 if math.isnan(pf) else pf,
                'phase' : phase,
                'voltage' : volt,
                'con_type': cons_type
            }
        print('HT costumers sucessfully added !!!')
    
    def __plot_load_distribution(self):
        
        output_file('Bokeh_plots/'+self.feedername+ 'load_distribution_plot.html')

        Phases = ["R", "Y", "B", "RYB"]
        R_Data = []
        Y_Data = []
        B_Data = []
        RYB_Data = []
        TR_ID = []
        num_of_trans = 0
        counts = []
        R_Count = []
        Y_Count = []
        B_Count = []
        RYB_Count = []

        for node1, node2 in self.NXgraph.edges():

            if self.NXgraph[node1][node2]['Type'] == 'DTs':
                R_load = 0
                Y_load = 0
                B_load = 0
                RYB_load = 0
                R_sum = 0
                Y_sum = 0
                B_sum = 0
                RYB_sum = 0
                counts.append(self.NXgraph[node1][node2]['DT_CC_KVA'])
                temp_network =copy.deepcopy(self.NXgraph)
                temp_network.remove_edge(node1,node2)
                Islands = list(nx.connected_component_subgraphs(temp_network))    
                number_of_nodes = 9999999
                for i in range(len(Islands)):
                    if len(Islands[i].nodes) < number_of_nodes:
                        number_of_nodes = len(Islands[i].nodes)
                        island_index = i
                for N1 in Islands[island_index].nodes():
                    NodeData = temp_network.node[N1]
                    if 'loads' in NodeData:
                        for keys, values in NodeData['loads'].items():
                            if values['phase'] == 'R':
                                R_load = R_load + values['load']
                                R_sum +=1
                            elif values['phase'] == 'Y':
                                Y_load = Y_load + values['load']
                                Y_sum +=1
                            elif values['phase'] == 'B':
                                B_load = B_load + values['load']
                                B_sum +=1
                            elif values['phase'] == 'RYB':
                                RYB_load = RYB_load + values['load']
                                RYB_sum +=1
                
                R_Data.append(R_load)
                Y_Data.append(Y_load)
                B_Data.append(B_load)
                RYB_Data.append(RYB_load)
                R_Count.append(R_sum)
                Y_Count.append(Y_sum)
                B_Count.append(B_sum)
                RYB_Count.append(RYB_sum)
                TR_ID.append('T'+str(num_of_trans))
                num_of_trans +=1
        Transformers = TR_ID

        data = {'Transformers' : Transformers,
        'R'   : R_Data,
        'Y'   : Y_Data,
        'B'   : B_Data,
        'RYB' : RYB_Data}

        data1 = {'Transformers' : Transformers,
        'R'   : R_Count,
        'Y'   : Y_Count,
        'B'   : B_Count,
        'RYB' : RYB_Count}

        p = figure(x_range=Transformers,plot_width=1200, plot_height=200, title="Distribution by phase (kW)",
           toolbar_location=None, tools="")
        
        colors = ["#c9d9d3", "#718dbf", "#e84d60","#008000"]

        p.vbar_stack(Phases, x='Transformers', width=0.9, color=colors, source=data,
             legend=[value(x) for x in Phases])

        p.y_range.start = -0.5
        #p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"

        p1 = figure(x_range=Transformers, plot_width=1200, plot_height=200, title="Transformer capacity (KVA)",
           toolbar_location=None, tools="")

        p1.vbar(x=Transformers, top=counts, width=0.9)

        p1.xgrid.grid_line_color = None
        p1.y_range.start = -0.5

        p2 = figure(x_range=Transformers, plot_width=1200, plot_height=200, title="Distribution by phase (consumer counts)",
           toolbar_location=None, tools="")

        p2.vbar_stack(Phases, x='Transformers', width=0.9, color=colors, source=data1,
             legend=[value(x) for x in Phases])
        print(data1)
        p2.y_range.start = -0.5
        #p2.x_range.range_padding = 0.1
        p2.xgrid.grid_line_color = None
        p2.axis.minor_tick_line_color = None
        p2.outline_line_color = None
        p2.legend.location = "top_left"
        p2.legend.orientation = "horizontal"


        print('Total load on R phase: ', sum(R_Data))
        print('Total load on Y phase: ', sum(Y_Data))
        print('Total load on B phase: ', sum(B_Data))
        print('Total load on RYB phase: ', sum(RYB_Data))
        print('Total R customers: ', sum(R_Count))
        print('Total Y customers: ', sum(Y_Count))
        print('Total B customers: ', sum(B_Count))
        print('Total RYB customers: ', sum(RYB_Count))
        print('Total load: ',sum(R_Data)+ sum(Y_Data)+ sum(B_Data)+ sum(RYB_Data))
        print('Total single phase customers: ', sum(R_Count)+ sum(Y_Count)+ sum(B_Count))

        show(column(p,p1,p2))
    
    def __add_power_transformers(self):
        
        print("Adding power transformers")
 
        for type, typeData in self.Node_data.items():
            
            if type == 'PTs':
                
                D = len(typeData)
            
                for i in range(D):

                    transData = typeData.loc[i]
                    ElmDict  = transData.to_dict()
                    ElmDict['Type'] =  type

                    if ElmDict[self.mapper_dict["PT_volt"]] == self.mapper_dict["HT_voltage"]:
                        X0 = self.Node_data['PTs'].x[i]
                        Y0 = self.Node_data['PTs'].y[i]
                        dist_from_ht = 9999999
                        node_of_interest = None
                        for Node in self.NXgraph.nodes():
                            if self.NXgraph.node[Node]['Type'] == 'HTnode':
                                X1 = self.NXgraph.node[Node]['x']
                                Y1 = self.NXgraph.node[Node]['y']

                                if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < dist_from_ht:
                                    dist_from_consumer_ht =  np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                                    node_of_interest = Node
                                    X2 = X1
                                    Y2 = Y1
                        self.NXgraph.add_edge('{}_{}_EHT'.format(X0,Y0),node_of_interest, **ElmDict)
                        self.NXgraph.node['{}_{}_EHT'.format(X0,Y0)]['x'] = X0
                        self.NXgraph.node['{}_{}_EHT'.format(X0,Y0)]['y'] = Y0
                        self.NXgraph.node['{}_{}_EHT'.format(X0,Y0)]['Type'] = 'EHTnode'
                

                for i in range(D):

                    transData = typeData.loc[i]
                    ElmDict  = transData.to_dict()
                    ElmDict['Type'] =  type

                    if ElmDict[self.mapper_dict["PT_volt"]] == self.mapper_dict["XHT_voltage"]:
                        X0 = self.Node_data['PTs'].x[i]
                        Y0 = self.Node_data['PTs'].y[i]
                        dist_from_ht = 9999999
                        node_of_interest = None
                        for Node in self.NXgraph.nodes():
                            if self.NXgraph.node[Node]['Type'] == 'EHTnode':
                                X1 = self.NXgraph.node[Node]['x']
                                Y1 = self.NXgraph.node[Node]['y']

                                if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < dist_from_ht:
                                    dist_from_consumer_ht =  np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                                    node_of_interest = Node

                        self.NXgraph.add_edge('{}_{}_XHT'.format(X0,Y0),node_of_interest, **ElmDict)
                        self.NXgraph.node['{}_{}_XHT'.format(X0,Y0)]['x'] = X0
                        self.NXgraph.node['{}_{}_XHT'.format(X0,Y0)]['y'] = Y0
                        self.NXgraph.node['{}_{}_XHT'.format(X0,Y0)]['Type'] = 'XHTnode' 
                    
                        AttData = {
                            'Type' : 'EHT line',
                            'Phase info' : self.mapper_dict["correct_three_phase_name"],
                            'Cable size phase'   : self.mapper_dict["EHT_cond_size"],
                            'Cable type phase'   : self.mapper_dict["EHT_cond_type"],
                            'Length'             : self.mapper_dict["EHT_cond_length"],
                        }
                        self.NXgraph.add_edge('{}_{}_XHT'.format(X2-5/1000,Y2+5/1000),'{}_{}_XHT'.format(X0,Y0),**AttData)
                        self.NXgraph.node['{}_{}_XHT'.format(X2-5/1000,Y2+5/1000)]['x'] = X2-5/1000
                        self.NXgraph.node['{}_{}_XHT'.format(X2-5/1000,Y2+5/1000)]['y'] = Y2+5/1000
                        self.NXgraph.node['{}_{}_XHT'.format(X2-5/1000,Y2+5/1000)]['Type'] = 'XHTnode'
                self.SS_node = '{}_{}_XHT'.format(X2-5/1000,Y2+5/1000)
    
    def  __Add_line_edge_property(self):
        for node1, node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] in ['HT line', 'HT cable', 'LT line','LT cable' ,'Service line', 'EHT line']:
                if edgeData['Phase info'] in self.mapper_dict["list_of_three_phase_four_wire"]:
                    edgeData['num_of_cond'] = 4
                elif edgeData['Phase info'] in self.mapper_dict["list_of_three_phase_three_wire"]:
                    edgeData['num_of_cond'] = 3
                elif edgeData['Phase info'] in self.mapper_dict["list_of_single_phase_two_wire"]:
                    edgeData['num_of_cond'] = 2
    
    def __force_all_LT_line_tobe3phase(self):
        for node1,node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] in ['LT line','LT cable']:
                edgeData['Phase info'] = self.mapper_dict["correct_three_phase_name"]
                edgeData['Phase_con'] = self.mapper_dict["three_phase_con"]



    def __fix_phase_issue_in_LT_line(self):
        for node1, node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] == 'LT line' and edgeData['Phase_con'] != self.mapper_dict["three_phase_con"]:
                temp_network =copy.deepcopy(self.NXgraph)
                temp_network.remove_edge(node1,node2)
                Islands = list(nx.connected_component_subgraphs(temp_network))
                number_of_nodes = 9999999
                for i in range(len(Islands)):
                    if len(Islands[i].nodes) < number_of_nodes:
                        number_of_nodes = len(Islands[i].nodes)
                        island_index = i
                for N1,N2 in Islands[island_index].edges():
                    Data = self.NXgraph[N1][N2]
                    if Data['Type'] == 'LT line':
                        if Data['Phase_con'] == self.mapper_dict["three_phase_con"]:
                            Data['Phase_con'] = edgeData['Phase_con']
                            Data['Phase info'] = self.mapper_dict["correct_single_phase_name"]

    

    def __count_number_of_downstream_customers(self):

        down_cust_dict = {k.replace('.','-'):[] for k in list(self.NXgraph.nodes())}
        hey = 1
        for node in self.NXgraph.nodes():
            print(hey)
            hey +=1
            count = 0
            temp_network = copy.deepcopy(self.NXgraph)
            temp_network.remove_node(node)
            Islands = list(nx.connected_component_subgraphs(temp_network))

            for i in range(len(Islands)):
                if Islands[i].has_node(self.SS_node) != True:
                    for N2 in Islands[i].nodes():
                        if 'loads' in Islands[i].node[N2]:
                            count+=1
            
            down_cust_dict[node.replace('.','-')]  = count
        
        df = pd.DataFrame.from_dict(down_cust_dict,orient='index')
        name =self.feedername + '.csv'
        name = name.replace(' ','-')
        df.to_csv(name)




                




  