# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 10:57:57 2019
@author: kduwadi
"""

import numpy as np
import pandas as pd
import os
import networkx as nx
import matplotlib.pyplot as plt
import math
import random

# Develop class object to read and build the network
class Reader:
    
    LineFiles = {
            'HT_line'   : {'Coordinates': 'ht_line_nodes.csv' , 'Attribute data': 'ht_line_attributes.csv'},
            'LT_line'   : {'Coordinates': 'lt_line_nodes.csv' , 'Attribute data': 'lt_line_attributes.csv'},
            'Service_line'   : {'Coordinates': 'service_line_nodes.csv' , 'Attribute data': 'service_line_attributes.csv'}
    }

    NodeFiles = {
            'Consumer_LT'   : 'consumer_lt.csv',
            'Consumer_HT'   : 'consumer_ht.csv',
            'DTs'           : 'distribution_transformer.csv',
            'HTpole'        : 'ht_pole.csv',
            'LTpole'        : 'lt_pole.csv'
    }
    
    
    def __init__(self,path,mapper_dict):
        self.path = path
        self.FeederNode = []
        self.mapper_dict = mapper_dict
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
        self.__Create_HT_Edges()
        self.__GetGraphMetrics()
        self.__FixIslands_HT_Network()
        self.__Create_LT_Edges()
        self.__GetGraphMetrics()
        self.__add_transformers_node_to_network()
        self.__Create_Servive_Edges()
        self.__Fix_final_islands()
        self.__GetGraphMetrics()
        self.__force_LT_lines_tobe_3phase()
        self.__choose_phaseof_serviceline_randomly()
        #self.__visualize_Islands()
        #self.__visualize_network()
        #self.__visualize_colored_network()
        self.__Edit_LT_property()
        self.__fix_incorrect_phase_con()
        self.__create_load_nodes()
        self.__Add_sub_station_transformer()
        self.__Add_line_edge_property()
        print('Success!!!')
        return


    def __force_LT_lines_tobe_3phase(self):
        for node1,node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] in ['LT line']:
                edgeData['Phase info'] = self.mapper_dict["correct_three_phase_name"]
                edgeData['Phase_con'] = self.mapper_dict["three_phase_con"]

    def __choose_phaseof_serviceline_randomly(self):
        for node1,node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] in ['Service line'] and edgeData['Phase_con'] != self.mapper_dict["three_phase_con"]:
                edgeData['Phase info'] = self.mapper_dict["correct_single_phase_name"]
                edgeData['Phase_con'] = random.choice(self.mapper_dict["single_phase_con_list"])



    def __Edit_LT_property(self):
        for node1, node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] == 'LT line':
                if edgeData['Phase info'] in self.mapper_dict["list_of_three_phase"]:
                    edgeData['Phase info'] = self.mapper_dict["correct_three_phase_name"]



    def __visualize_colored_network(self):
        from bokeh.plotting import figure, output_file, show
        output_file('colored_network.html')

        p = figure(plot_width = 1500, plot_height = 1000)

        colors = ["#c9d9d3", "#718dbf", "#e84d60","#008000"]

        for node1, node2 in self.NXgraph.edges():
            N1 = self.NXgraph.node[node1]
            X1 = N1['x']
            Y1 = N1['y']
            N2 = self.NXgraph.node[node2]
            X2 = N2['x']
            Y2 = N2['y']
            type = self.NXgraph[node1][node2]['Type']
            if type in ['HT line', 'LT line', 'Service line']:
                if self.NXgraph[node1][node2]['Phase_con'] == 'RYB':
                    p.line([X1, X2], [Y1, Y2],color='#008000')
                elif self.NXgraph[node1][node2]['Phase_con'] == 'R':
                    p.line([X1, X2], [Y1, Y2],color='#FF0000')
                elif self.NXgraph[node1][node2]['Phase_con'] == 'Y':
                    p.line([X1, X2], [Y1, Y2],color='#FFFF00')
                elif self.NXgraph[node1][node2]['Phase_con'] == 'B':
                    p.line([X1, X2], [Y1, Y2],color='#0000ff')
        show(p)

        

    def __Add_sub_station_transformer(self):
        x_coord_trans = 141465.98
        y_coord_trans = 1255355.61
        
        D = 9999999
        head_Node = 'ht'
        for Node in self.NXgraph.nodes():
            if self.NXgraph.node[Node]['Type'] == 'HTnode':
                x = self.NXgraph.node[Node]['x']
                y = self.NXgraph.node[Node]['y']

                if D > np.sqrt((x-x_coord_trans)**2+(y-y_coord_trans)**2):
                    D = np.sqrt((x-x_coord_trans)**2+(y-y_coord_trans)**2)
                    head_Node = Node
        
        SubTransAtt  = {
            'Type' : 'DTs',
        }
        self.NXgraph.add_edge('{}_{}_EHT'.format(x_coord_trans,y_coord_trans), head_Node, **SubTransAtt)
        self.FeederNode = '{}_{}_EHT'.format(x_coord_trans,y_coord_trans)
        self.NXgraph.node['{}_{}_EHT'.format(x_coord_trans,y_coord_trans)]['x'] = x_coord_trans
        self.NXgraph.node['{}_{}_EHT'.format(x_coord_trans,y_coord_trans)]['y'] = y_coord_trans
        self.NXgraph.node['{}_{}_EHT'.format(x_coord_trans,y_coord_trans)]['Type'] = 'EHTnode'

        print(self.FeederNode)



    def __Fix_final_islands(self):
        
        self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))

        for i in range(len(self.Islands)):
            if len(self.Islands[i].nodes) < 10:
                self.NXgraph.remove_nodes_from(list(self.Islands[i].nodes()))
        


    def __find_neighbor_HTnode_and_contract(self,i):
        D = 99999999
        for node1 in self.Islands[i].nodes():
            X0 = self.Islands[i].node[node1]['x']
            Y0 = self.Islands[i].node[node1]['y']
            for k in range(len(self.Islands)):
                if k != i:
                    for node2 in self.Islands[k].nodes():
                        X1 =  self.Islands[k].node[node2]['x']
                        Y1 =  self.Islands[k].node[node2]['y']
                        if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < D:
                            D = np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                            N1 = node1
                            N2 = node2
        return [N1,N2]


    def __FixIslands_HT_Network(self):
        Node1 = []
        Node2 = []
        for i in range(len(self.Islands)):
            print(len(self.Islands[i].nodes))
            if len(self.Islands[i].nodes) == 68:
                nodes = self.__find_neighbor_HTnode_and_contract(i)
                Node1.append(nodes[0])
                Node2.append(nodes[1])
            elif len(self.Islands[i].nodes) == 4:
                nodes = self.__find_neighbor_HTnode_and_contract(i)
                Node1.append(nodes[0])
                Node2.append(nodes[1])
            elif len(self.Islands[i].nodes) == 40:
                nodes = self.__find_neighbor_HTnode_and_contract(i)
                Node1.append(nodes[0])
                Node2.append(nodes[1])
            elif len(self.Islands[i].nodes) == 132:
                nodes = self.__find_neighbor_HTnode_and_contract(i)
                Node1.append(nodes[0])
                Node2.append(nodes[1])
        print(Node1)
        print(Node2)
        for i in range(len(Node1)):
            self.NXgraph = nx.contracted_nodes(self.NXgraph, Node1[i],Node2[i])
                    
        self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))
        nodes = self.__find_neighbor_HTnode_and_contract(0)
        self.NXgraph = nx.contracted_nodes(self.NXgraph, nodes[0],nodes[1])



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
                'Enabled'     : AttData[self.mapper_dict["HT line"]["Enabled"]],
                'Cable ID'   : AttData[self.mapper_dict["HT line"]["Cable ID"]],
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
                'Conductor_type'     : AttData[self.mapper_dict["LT line"]["Conductor_type"]],
                'Length'             : AttData[self.mapper_dict["LT line"]["Length"]],
                'Height'             : AttData[self.mapper_dict["LT line"]["Height"]],
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
    
    def __Create_Servive_Edges(self):
        
        cData = self.Line_data['Service_line']['CD']
        aData = self.Line_data['Service_line']['ATD']

        print('Creating Service_edges')

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
                'Type'               : 'Service line',      
                'Length'             : AttData[self.mapper_dict["ST line"]["Length"]],
                'Enabled'            : AttData[self.mapper_dict["ST line"]["Enabled"]],
                'Cable ID'           : AttData[self.mapper_dict["ST line"]["Cable ID"]],
                'Phase_con'          : AttData[self.mapper_dict["ST line"]["Phase_con"]],
                'Phase info'         : AttData[self.mapper_dict["ST line"]["Phase info"]],
                'Cable size phase'   : AttData[self.mapper_dict["ST line"]["Cable size phase"]],
                'Cable type phase'   : AttData[self.mapper_dict["ST line"]["Cable type phase"]],
                }
            self.NXgraph.add_edge('{}_{}_LT'.format(X1,Y1), '{}_{}_LT'.format(X2,Y2), **Attributes)
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['x'] = X1
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['y'] = Y1
            self.NXgraph.node['{}_{}_LT'.format(X1,Y1)]['Type'] = 'STnode'
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['x'] = X2
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['y'] = Y2
            self.NXgraph.node['{}_{}_LT'.format(X2,Y2)]['Type'] = 'STnode'
        return
    
    def __GetGraphMetrics(self):

        print('Number of nodes: ' + str(len(self.NXgraph.nodes())))
        self.Islands = list(nx.connected_component_subgraphs(self.NXgraph))
        self.NumIslands = len(self.Islands)
        print('Number of islands: ' + str(len(self.Islands)))
        self.Loops = nx.cycle_basis(self.NXgraph)
        print('Number of loops: ' + str(len(self.Loops)))
        return
    
    def __visualize_network(self): 
        
        Fig = plt.figure(figsize=(20,10))
        for node1, node2 in self.NXgraph.edges():
            N1 = self.NXgraph.node[node1]
            X1 = N1['x']
            Y1 = N1['y']
            N2 = self.NXgraph.node[node2]
            X2 = N2['x']
            Y2 = N2['y']
            type = self.NXgraph[node1][node2]['Type']
            if type == 'HT line':
                plt.plot([X1, X2], [Y1, Y2],LineWidth = 3,color  ='r')
            elif type == 'LT line':
                plt.plot([X1, X2], [Y1, Y2],LineWidth = 2,color  ='b')
            elif type == 'Service line':
                plt.plot([X1, X2], [Y1, Y2],LineWidth = 1,color  ='g')
            elif type == 'DTs':
                plt.plot([X1, X2], [Y1, Y2],LineWidth = 6 ,color  ='k')
        plt.xlabel("x - coordinate")
        plt.ylabel("y - coordinate")
        plt.show()
        return
    
    # Adding transformer node by connecting nearest HT pole and LT pole 
  
    def __add_transformers_node_to_network(self):
 
        for type, typeData in self.Node_data.items():
            
            if type == 'DTs':
                
                D = len(typeData)
            
            
                for i in range(D):
                    transData = typeData.loc[i]
                    ElmDict  = transData.to_dict()
                    ElmDict['Type'] =  type
                    
                    X0 = transData['x']
                    Y0 = transData['y']
                    #tNodeName = '{}_{}'.format(X0,Y0)
                    
                    dist_from_ht_pole = 99999999
                    dist_from_lt_pole = 99999999
                    nearest_ht_pole = []
                    nearest_lt_pole = []
                    
                    
                    # Find nearest HT pole
                    
                    for pole in range(len(self.Node_data['HTpole'])):
                        X1 = self.Node_data['HTpole'].xcoord[pole]
                        Y1 = self.Node_data['HTpole'].ycoord[pole]
                        
                        if np.sqrt((X1-X0)**2+(Y1-Y0)**2) < dist_from_ht_pole:
                            dist_from_ht_pole = np.sqrt((X1-X0)**2+(Y1-Y0)**2)
                            nearest_ht_pole = (X1,Y1)
                            
                    # Find nearest LT pole
                    
                    for pole in range(len(self.Node_data['LTpole'])):
                        X1 = self.Node_data['LTpole'].xcoord[pole]
                        Y1 = self.Node_data['LTpole'].ycoord[pole]
                        
                        if np.sqrt((X1-X0)**2+(Y1-Y0)**2) < dist_from_lt_pole:
                            dist_from_lt_pole = np.sqrt((X1-X0)**2+(Y1-Y0)**2)
                            nearest_lt_pole = (X1,Y1)    
                    
                    # Finding the node in NXgraph which is close to nearest HT pole and LT pole
                    
                    dist_from_ht_node = 99999999
                    dist_from_lt_node = 99999999
                    nearest_ht_node = None
                    nearest_lt_node = None
                    
                    
                    for Node in self.NXgraph.nodes():
                        X1 = self.NXgraph.node[Node]['x']
                        Y1 = self.NXgraph.node[Node]['y']
                        
                        
                        if np.sqrt((X1-nearest_ht_pole[0])**2+(Y1-nearest_ht_pole[1])**2) < dist_from_ht_node:
                            dist_from_ht_node = np.sqrt((X1-nearest_ht_pole[0])**2+(Y1-nearest_ht_pole[1])**2)
                            nearest_ht_node = Node
                        
                        
                        if np.sqrt((X1-nearest_lt_pole[0])**2+(Y1-nearest_lt_pole[1])**2) < dist_from_lt_node:
                            dist_from_lt_node = np.sqrt((X1-nearest_lt_pole[0])**2+(Y1-nearest_lt_pole[1])**2)
                            nearest_lt_node = Node
                            
                        
                    self.NXgraph.add_edge(nearest_ht_node, nearest_lt_node, **ElmDict)
        return
        
    def __visualize_Islands(self):
         import matplotlib.colors as colors 
         colors_list = list(colors._colors_full_map.values())

         Fig = plt.figure(figsize=(20,10))
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
                 plt.plot([X1, X2], [Y1, Y2], color = colors_list[color_index])
         plt.show()
                 
    def __create_load_nodes(self):

        # Adding low tension costumers load nodes , all are connected to service line

        D = len(self.Node_data['Consumer_LT'])
        con_LT = self.Node_data["Consumer_LT"].rename(columns=self.mapper_dict["consumer_LT_converter"])
        for i in range(D):

            X0 = con_LT.X0[i]
            Y0 = con_LT.Y0[i]

            dist_from_consumer_lt = 9999999
            node_of_interest = None
            for Node in self.NXgraph.nodes():
                if self.NXgraph.node[Node]['Type'] == 'STnode':
                    X1 = self.NXgraph.node[Node]['x']
                    Y1 = self.NXgraph.node[Node]['y']

                    if np.sqrt((X0-X1)**2+(Y0-Y1)**2) < dist_from_consumer_lt:
                        dist_from_consumer_lt =  np.sqrt((X0-X1)**2+(Y0-Y1)**2)
                        node_of_interest = Node
            
            NodeData = self.NXgraph.node[node_of_interest]
            
            customerID = con_LT.customerID[i]
            kW_load = con_LT.kW_load[i]
            pf = con_LT.pf[i]
            phase = con_LT.phase[i]
            TEC = con_LT.TEC[i]

            neighbor = [n for n in self.NXgraph.neighbors(node_of_interest)]
            if self.NXgraph[node_of_interest][neighbor[0]]['Phase_con'] != phase:
                phase = self.NXgraph[node_of_interest][neighbor[0]]['Phase_con']
            
            volt = 0.44 if phase == 'RYB' else 0.254

            if 'loads' not in NodeData:
                NodeData['loads']  ={}
            NodeData['loads'][customerID]= {
                'load'  : kW_load,
                'pf'    : 0.9 if math.isnan(pf) else pf,
                'phase' : phase,
                'voltage' : volt,
                'TEC'   : TEC
            }
            if  i ==1:
                print(NodeData)
        print('LT costumers sucessfully added !!!')
        
        # Adding HT tension costumers load nodes , all are connected to service line

        D = len(self.Node_data['Consumer_HT'])
        con_HT = self.Node_data['Consumer_HT'].rename(columns=self.mapper_dict["consumer_HT_converter"])

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
            
            NodeData = self.NXgraph.node[node_of_interest]
            customerID = con_HT.customerID[i]
            kW_load = con_HT.kW_load[i]
            pf = con_HT.pf[i]
            phase = con_HT.phase[i]

            if 'loads' not in NodeData:
                NodeData['loads']  ={}
            NodeData['loads'][customerID] = {
                'load'  : kW_load,
                'pf'    : 0.9 if math.isnan(pf) else pf,
                'phase' : phase,
                'voltage' : self.mapper_dict["HT_voltage"]
            }
            print(NodeData)
        return
    
    
    def __fix_incorrect_phase_con(self):
        for node1, node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] in ['HT line', 'LT line', 'Service line']:
                if edgeData['Phase_con'] == self.mapper_dict["three_phase_con"]:
                        edgeData['Phase info'] = self.mapper_dict["correct_three_phase_name"]

    
    def  __Add_line_edge_property(self):
        for node1, node2 in self.NXgraph.edges():
            edgeData = self.NXgraph[node1][node2]
            if edgeData['Type'] in ['HT line', 'LT line', 'Service line']:
                if edgeData['Phase info'] in self.mapper_dict["list_of_three_phase_four_wire"]:
                    edgeData['num_of_cond'] = 4
                elif edgeData['Phase info'] in self.mapper_dict["list_of_three_phase_three_wire"]:
                    edgeData['num_of_cond'] = 3
                elif edgeData['Phase info'] in self.mapper_dict["list_of_single_phase_two_wire"]:
                    edgeData['num_of_cond'] = 2





