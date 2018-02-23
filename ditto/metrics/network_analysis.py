# coding: utf8

import networkx as nx
import numpy as np
import math
import time

from ditto.network.network import Network
from ditto.models.regulator import Regulator
from ditto.models.line import Line
from ditto.models.capacitor import Capacitor
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer
from ditto.models.node import Node


class network_analyzer():
    '''This class is used to compute validation metrics from the DiTTo representation itself.


**Initialization:**

>>> analyst=network_analyzer(model, source)

Where model is the DiTTo model under consideration, and source is the source node.


**Usage:**

There are different ways to use this class:

    - Compute metrics for the whole network.

        - Compute a specific metric:

            >>> n_regulator=analyst.number_of_regulators()

            This will compute the number of regulators in the whole network.

        - Compute all metrics:

            >>> results=analyst.compute_all_metrics()

            This will compute all the available metrics in the whole network.

            .. warning:: Some metrics have N^2 complexity...

    - Compute metrics for individual feeders.

        - Compute a specific metric:

            >>> n_regulator=analyst.number_of_regulators(feeder_1)

            This will compute the number of regulators for a feeder named 'feeder_1'.

            .. warning:: Currently not implemented.

        - Compute all metrics for all feeders:

            >>> results=analyst.compute_all_metrics_per_feeder()

            This will compute all available metrics for all feeders.

            .. warning:: This requires having done the feeder split of the network. (See section 'feeder split')


**Feeder split:**

To compute the metrics at the feeder level, you have to provide the following:

    - feeder_names: A list of the feeder names.
    - feeder_nodes: A list of lists which contains the nodes in each feeder. (indexing should be consistent with feeder_names)

Give this information to the network_analyzer is straightforward:

    >>> analyst.add_feeder_information(feeder_names, feeder_nodes)

The actual feeder split is done through:

    >>> analyst.split_network_into_feeders()


.. note::

    - Using compute_all_metrics or compute_all_metrics_per_feeder only loops over the objects once in order to improve performance.
      It is NOT a wrapper that calls the metric functions one by one.
      Therefore, it is strongly recommanded to use one of these two methods when more than a few metrics are needed.
    - The class constructor is building the network (using the DiTTo Network module) which can take some time...

Author: Nicolas Gensollen. December 2017

'''

    def __init__(self, model, source):
        '''Class CONSTRUCTOR.

'''
        #Store the model as attribute
        self.model=model

        #Store the source name as attribute
        self.source=source

        #Build the Network
        #
        #WARNING: Time consuming...
        #
        self.G=Network()
        self.G.build(self.model, source=self.source)

		#Set the attributes in the graph
        self.G.set_attributes(self.model)

		#Equipment types and names on the edges
        self.edge_equipment     =nx.get_edge_attributes(self.G.graph,'equipment')
        self.edge_equipment_name=nx.get_edge_attributes(self.G.graph,'equipment_name')

        #IMPORTANT: the following two parameters define what is LV and what is MV.
        #- Object is LV if object.nominal_voltage<=LV_threshold
        #- Object is MV if MV_threshold>=object.nominal_voltage>LV_threshold
        #Metrics are obviously extremely sensitive to these two parameters...
        #
        self.LV_threshold=1000 #In volts. Default=1kV
        self.MV_threshold=69000#In volts. Default=69kV

        self.feeder_names=None
        self.feeder_nodes=None

        self.feeder_networks={}
        self.node_feeder_mapping={}

        self.__substations=[obj for obj in self.model.models if isinstance(obj,PowerTransformer) and obj.is_substation==1]



    def add_feeder_information(self, feeder_names, feeder_nodes, substations, feeder_types):
        '''Use this function to add the feeder information if available.

:param feeder_names: List of the feeder names
:type feeder_names: List(str)
:param feeder_nodes: List of lists containing feeder nodes
:type feeder_nodes: List of Lists of strings
:param feeder_types: List of feeder types.
:type feeder_types: List or string if all feeders have the same type

'''
        if len(feeder_names)!=len(feeder_nodes):
            raise ValueError('Number of feeder names {a} does not match number of feeder lists of nodes {b}'.format(a=len(feeder_names), b=len(feeder_nodes)))
        if isinstance(feeder_types,str):
            self.feeder_types={k:feeder_types for k in feeder_names}
        elif isinstance(feeder_types, list):
            if len(feeder_names)!=len(feeder_types):
                raise ValueError('Number of feeder names {a} does not match number of feeder types of nodes {b}'.format(a=len(feeder_names), b=len(feeder_types)))
            else:
                self.feeder_types={k:v for k,v in zip(feeder_names,feeder_types)}
        self.feeder_names=feeder_names
        self.feeder_nodes=feeder_nodes
        self.substations=substations



    def split_network_into_feeders(self):
        '''This function splits the network into subnetworks corresponding to the feeders.

.. note:: add_feeder_information should be called first

'''
        if self.feeder_names is None or self.feeder_nodes is None:
            raise ValueError('Cannot split the network into feeders because feeders are unknown. Call add_feeder_information first.')

        for cpt,feeder_name in enumerate(self.feeder_names):
            feeder_node_list =self.feeder_nodes[cpt]
            self.feeder_networks[feeder_name]=self.G.graph.subgraph(feeder_node_list)

            #If the feeder information is perfect, that is the end of the story.
            #But, most of the time, some nodes are missing from the feeder information.
            #This means that we get disconnected feeder networks which will cause some
            #issues later (when computing the diameter for example)
            #For this reason, the following code is trying to infer the missing nodes
            #and edges such that the feeder networks are all connected in the end.
            while not nx.is_connected(self.feeder_networks[feeder_name]):
                self.connect_disconnected_components(feeder_name)
                feeder_node_list =self.feeder_nodes[cpt]
                self.feeder_networks[feeder_name]=self.G.graph.subgraph(feeder_node_list)

            #Build the node_feeder_mapping
            #for node in self.feeder_nodes[cpt]:
            for node in self.feeder_networks[feeder_name].nodes():
                self.node_feeder_mapping[node]=feeder_name



    def export(self,*args):
        '''Export the metrics to excel report card.

:param export_path: Relative path to the output file
:type export_path: str

.. TODO:: Include all required metrics in here.

.. warning:: Not well tested...

'''
        #TODO: Add some safety checks here...
        if args:
            export_path=args[0]
        else:
            export_path='./output.xlsx'

        #TODO: More maintainable way for this...
        cols=['Feeder_name','substation_name','Feeder_type','Substation_Capacity_MVA', 'Substation_Type', 'distribution_transformer_total_capacity_MVA',
              'nb_of_distribution_transformers', 'number_of_customers', 'ratio_1phto3ph_Xfrm', 'lv_length_miles', 'mv_length_miles',
              'furtherest_node_miles', 'length_mv3ph_miles', 'length_OH_mv3ph_miles', 'length_mv2ph_miles', 'length_OH_mv2ph_miles', 'length_mv1ph_miles',
              'length_OH_mv1ph_miles', 'length_lv3ph_miles', 'length_OH_lv3ph_miles', 'length_lv1ph_miles', 'length_OH_lv1ph_miles', 'percentage_load_LV_kW_phA',
              'percentage_load_LV_kW_phB', 'percentage_load_LV_kW_phC', 'total_demand', 'total_kVar', 'nb_loads_LV_1ph', 'nb_loads_LV_3ph', 'nb_loads_MV_3ph',
              'avg_nb_load_per_transformer', 'nb_of_regulators', 'nb_of_capacitors', 'nb_of_boosters', 'nominal_voltage_HV_KV', 'nominal_voltage_MV_KV',
              'nominal_voltage_LV_KV', 'nb_of_fuses', 'nb_of_reclosers', 'nb_of_sectionalizers', 'nb_of_switches', 'nb_of_breakers', 'nb_of_interruptors', 'average_degree',
              'average_path_length', 'diameter']

        #Create empty DataFrame for output
        card=pd.DataFrame(columns=cols)

        n_row=0
        for key,data in self.results.iteritems():
            card.loc[n_row]=[key]+[data[x] if data.has_key(x) else None for x in cols[1:]]
            n_row+=1

        #Instanciate the writer
        xlsx_writer = pd.ExcelWriter(export_path)
        #Write to excel
        card.to_excel(xlsx_writer)
        #Save
        xlsx_writer.save()



    def tag_objects(self):
        '''TODO...

'''

        for obj in self.model.models:
            if hasattr(obj,'feeder_name'):
                if isinstance(obj,Node):
                    if self.node_feeder_mapping.has_key(obj.name):
                        obj.feeder_name=self.node_feeder_mapping[obj.name]
                        obj.substation_name=self.substations[obj.feeder_name]
                    else:
                        obj.feeder_name='subtransmission'
                        obj.substation_name=self.source
                        print('Node {name} was not found in feeder mapping'.format(name=obj.name))
                elif hasattr(obj,'connecting_element'):
                    if self.node_feeder_mapping.has_key(obj.connecting_element):
                        obj.feeder_name=self.node_feeder_mapping[obj.connecting_element]
                        obj.substation_name=self.substations[obj.feeder_name]
                    else:
                        obj.feeder_name='subtransmission'
                        obj.substation_name=self.source
                        print('Object {name} connecting element {namec} was not found in feeder mapping'.format(name=obj.name, namec=obj.connecting_element))
                elif hasattr(obj,'from_element'):
                    if self.node_feeder_mapping.has_key(obj.from_element):
                        obj.feeder_name=self.node_feeder_mapping[obj.from_element]
                        obj.substation_name=self.substations[obj.feeder_name]
                    else:
                        obj.feeder_name='subtransmission'
                        obj.substation_name=self.source
                        print('Object {name} from element {namec} was not found in feeder mapping'.format(name=obj.name, namec=obj.from_element))
                else:
                    print(obj.name,type(obj))



    def connect_disconnected_components(self, feeder_name):
        '''Helper function for split_network_into_feeders.
This function takes the first two disconnected components in the feeder network corresponding to feeder_name, and connects them with a shortest path.
The underlying assumption is that all nodes lying on the shortest path are actual members of this feeder.

'''
        #Get the index of feeder_name
        idx=self.feeder_names.index(feeder_name)

        #Get the feeder_node_list
        feeder_node_list =self.feeder_nodes[idx]

        #Build the subgraph from the complete network
        self.feeder_networks[feeder_name]=self.G.graph.subgraph(feeder_node_list)

        #Compute the connected components
        #Since we were called by split_network_into_feeders only if the graph was disconnected,
        #we know that we have at least 2 elements in cc
        cc=nx.connected_components(self.feeder_networks[feeder_name])

        #cc is a generator and calling list() on it is a bad idea...
        #We simply grab the first two components...
        first_component=cc.next()
        second_component=cc.next()

        #...and we grab one node at random from each component.
        n1=first_component.pop()
        n2=second_component.pop()

        #If there are the same, you have a serious problem.
        #Better kill it here than waiting for weird issues later...
        if n1==n2:
            raise ValueError('Feeder splitting error. Nodes from 2 different components are the same.')

        #Compute the shortest path
        path=nx.shortest_path(self.G.graph,n1,n2)

        #For each node in the shortest path...
        for node in path:
            #...if the node is not already in the feeder, then add it
            if node not in self.feeder_nodes[idx]:
                self.feeder_nodes[idx].append(node)



    def setup_results_data_structure(self,*args):
        '''This function creates the data structure which contains the result metrics for a SINGLE network.

**Usage:**

>>> data_struct=network_analyzer.setup_results_data_structure(network)

The network argument can be a networkx Graph or networkx DiGraph or a string representing the name of a known feeder.

>>> data_struct=network_analyzer.setup_results_data_structure()

This will create the data structure for the whole network.

'''
        #If arguments were provided
        if args:

            #Only accepts one argument
            if len(args)>1:
                raise ValueError('setup_results_data_structure error: Too many input arguments.')

            #Cache it
            network=args[0]

            #Case one: it is a string
            if isinstance(network, str):

                #Check that this is the name of a feeder
                if network in self.feeder_names:

                    if self.substations.has_key(network):
                        _src=self.substations[network]
                    else:
                        raise ValueError('Could not find the substation for feeder {}'.format(network))

                    #Check that we have split the network into feeders
                    if self.feeder_networks is not None:

                        #Check that the name is linked to a graph object
                        if self.feeder_networks.has_key(network):
                            _net=self.feeder_networks[network]

                        #Error raising...
                        else:
                            raise ValueError('{} is not a known feeder.'.format(network))

                    #Error raising...
                    else:
                        raise ValueError('Trying to call setup_results_data_structure on feeder {}, but feeders were not defined yet. Try calling split_network_into_feeders.'.format(network))

                #Error raising...
                else:
                    raise ValueError('{} is not a known feeder name. Try calling add_feeder_information')

            #Case two: it is a graph or a digrah (Only networkx is supported for this option...)
            elif isinstance(network, nx.classes.graph.Graph) or isinstance(network, nx.classes.digraph.DiGraph):
                #Cache the network
                _net=network
                for feeder_name,nett in self.feeder_networks.iteritems():
                    if nett==_net:
                        _src=feeder_name
                        network=feeder_name

            #Otherwise, the format of the input is not supported
            else:
                raise ValueError('Unsupported type of argument. Provide a graph, DiGraph, or string')

        #If not input, use the whole network...
        else:
            _net=self.G.graph
            _src=self.source

        sub_MVA=None
        for su in self.__substations:
            if _src in su.name.replace('.',''):
                sub_MVA=min([z.rated_power for z in su.windings])*10**-6

        #Create the results dictionary.
        #Note: All metrics relying on networkX calls are computed here.
        #
        results={'nb_of_regulators':0,                                   #Number of regulators
                 'Substation_Capacity_MVA':sub_MVA,
                 'nb_of_fuses':0,                                        #Number of fuses
                 'nb_of_switches':0,                                     #Number of switches
                 'nb_of_reclosers':0,                                    #Number of reclosers
                 'nb_of_breakers':0,
                 'nb_of_capacitors':0,                                   #Number of capacitors
                 'number_of_customers':0,
                 'nb_of_distribution_transformers':0,                    #Number of distribution transformers
                 'distribution_transformer_total_capacity_MVA':0,        #Total capacity of distribution transformers (in MVA)
                 'nb_1ph_Xfrm':0,                                        #Number of 1 phase distribution transformers
                 'nb_3ph_Xfrm':0,                                        #Number of 3 phase distribution transformers
                 'ratio_1phto3ph_Xfrm':0,                                #Ratio of 1 phase distribution transformers to three phase distribution transformers
                 'average_degree':self.average_degree(_net),             #Average degree
                 'diameter':self.diameter(_net),                         #Network diameter (in number of edges, NOT in distance)
                 'average_path_length':self.average_path_length(_net),   #Average path length (in number of edges, NOT in distance)
                 'furtherest_node_miles':self.furtherest_node_miles(_net,_src),
                 'lv_length_miles':0,                                    #Total length of LV lines (in miles)
                 'mv_length_miles':0,                                    #Total length of MV lines (in miles)
                 'length_mv1ph_miles':0,                                 #Total length of 1 phase MV lines (in miles)
                 'length_OH_mv1ph_miles':0,                              #Total length of overhead 1 phase MV lines (in miles)
                 'length_mv2ph_miles':0,                                 #Total length of 2 phase MV lines (in miles)
                 'length_OH_mv2ph_miles':0,                              #Total length of overhead 2 phase MV lines (in miles)
                 'length_mv3ph_miles':0,                                 #Total length of 3 phase MV lines (in miles)
                 'length_OH_mv3ph_miles':0,                              #Total length of overhead 3 phase MV lines (in miles)
                 'length_lv1ph_miles':0,                                 #Total length of 1 phase LV lines (in miles)
                 'length_OH_lv1ph_miles':0,                              #Total length of overhead 1 phase LV lines (in miles)
                 'length_lv2ph_miles':0,                                 #Total length of 2 phase LV lines (in miles)
                 'length_OH_lv2ph_miles':0,                              #Total length of overhead 2 phase LV lines (in miles)
                 'length_lv3ph_miles':0,                                 #Total length of 3 phase LV lines (in miles)
                 'length_OH_lv3ph_miles':0,                              #Total length of overhead 3 phase LV lines (in miles)
                 'total_demand':0,                                       #Total demand (active power)
                 'total_kVar':0,                                         #Total demand (reactive power)
                 'nb_loads_LV_1ph':0,                                    #Number of 1 phase LV loads
                 'nb_loads_LV_3ph':0,                                    #Number of 3 phase LV loads
                 'nb_loads_MV_3ph':0,                                    #Number of 3 phase MV loads
                 'percentage_load_LV_kW_phA':0,                          #Percentage of total LV demand that is phase A
                 'percentage_load_LV_kW_phB':0,                          #Percentage of total LV demand that is phase B
                 'percentage_load_LV_kW_phC':0,                          #Percentage of total LV demand that is phase C
                 'demand_LV_phase_A':0,                                  #Total LV demand on phase A
                 'demand_LV_phase_B':0,                                  #Total LV demand on phase B
                 'demand_LV_phase_C':0,                                  #Total LV demand on phase C
                 'nb_load_per_transformer':{},                           #Store the number of loads per distribution transformer
                 'avg_nb_load_per_transformer':0,                        #Average number of loads per distribution transformer
                 'substation_name':_src,
                 'Feeder_type':None,
                 }
        if 'feeder_types' in self.__dict__ and self.feeder_types.has_key(network):
            results['Feeder_type']=self.feeder_types[network]
        return results



    def analyze_object(self, obj, feeder_name):
        '''This function takes as input a DiTTo object and the name of the corresponding feeder, and analyze it.
All information needed for the metric extraction is updated here.

'''
        #If we get a line
        if isinstance(obj,Line):

            #Update the counts
            #
            #Fuses
            if obj.is_fuse==1:
                self.results[feeder_name]['nb_of_fuses']+=1

            #Switches
            if obj.is_switch==1:
                self.results[feeder_name]['nb_of_switches']+=1

            #Reclosers
            if obj.is_recloser==1:
                self.results[feeder_name]['nb_of_reclosers']+=1

            #Breakers
            if obj.is_breaker==1:
                self.results[feeder_name]['nb_of_breakers']+=1

            #Get the phases (needed later)
            if hasattr(obj, 'wires') and obj.wires is not None:
                phases=[wire.phase for wire in obj.wires if wire.phase in ['A','B','C'] and wire.drop!=1]

            #If we do not have phase information, raise an error...
            else:
                raise ValueError('No phase information for line {}'.format(obj.name))

            #If the line is low voltage
            if obj.nominal_voltage is not None and obj.nominal_voltage*math.sqrt(3)<=self.LV_threshold:

                #Update the counter for low voltage line length
                if hasattr(obj, 'length') and obj.length>=0:
                    self.results[feeder_name]['lv_length_miles']+=obj.length

                    #Update the counters for specific number of phases
                    if phases is not None:

                        #Single Phase low voltage line
                        if len(phases)==1:
                            self.results[feeder_name]['length_lv1ph_miles']+=obj.length

                            #Single Phase low voltage Overhead Line
                            if obj.line_type=='overhead':
                                self.results[feeder_name]['length_OH_lv1ph_miles']+=obj.length

                        #Two Phase low voltage Line
                        elif len(phases)==2:
                            self.results[feeder_name]['length_lv2ph_miles']+=obj.length

                            #Two Phase low voltage Overhead Line
                            if obj.line_type=='overhead':
                                self.results[feeder_name]['length_OH_lv2ph_miles']+=obj.length

                        #Three Phase low voltage Line
                        elif len(phases)==3:
                            self.results[feeder_name]['length_lv3ph_miles']+=obj.length

                            #Three Phase low voltage Overhead Line
                            if obj.line_type=='overhead':
                                self.results[feeder_name]['length_OH_lv3ph_miles']+=obj.length

            #If the line is medium voltage
            elif obj.nominal_voltage is not None and self.MV_threshold>obj.nominal_voltage*math.sqrt(3)>self.LV_threshold:

                #Update the counter for low voltage line length
                if hasattr(obj, 'length') and obj.length>=0:
                    self.results[feeder_name]['mv_length_miles']+=obj.length

                    #Update the counters for specific number of phases
                    if phases is not None:

                        #Single Phase medium voltage line
                        if len(phases)==1:
                            self.results[feeder_name]['length_mv1ph_miles']+=obj.length

                            #Single Phase medium voltage Overhead line
                            if obj.line_type=='overhead':
                                self.results[feeder_name]['length_OH_mv1ph_miles']+=obj.length

                        #Two Phase medium voltage line
                        elif len(phases)==2:
                            self.results[feeder_name]['length_mv2ph_miles']+=obj.length

                            #Two Phase medium voltage Overhead line
                            if obj.line_type=='overhead':
                                self.results[feeder_name]['length_OH_mv2ph_miles']+=obj.length

                        #Three Phase medium voltage line
                        elif len(phases)==3:
                            self.results[feeder_name]['length_mv3ph_miles']+=obj.length

                            #Three Phase medium voltage Overhead line
                            if obj.line_type=='overhead':
                                self.results[feeder_name]['length_OH_mv3ph_miles']+=obj.length

            return


        #If we get a load
        if isinstance(obj,Load):

            if hasattr(obj, 'num_users') and obj.num_users is not None:
                self.results[feeder_name]['number_of_customers']+=obj.num_users

            if hasattr(obj, 'upstream_transformer_name') and obj.upstream_transformer_name is not None:
                if self.results[feeder_name]['nb_load_per_transformer'].has_key(obj.upstream_transformer_name):
                    self.results[feeder_name]['nb_load_per_transformer'][obj.upstream_transformer_name]+=1
                else:
                    self.results[feeder_name]['nb_load_per_transformer'][obj.upstream_transformer_name]=1

            #If the load is low voltage
            if hasattr(obj,'nominal_voltage') and obj.nominal_voltage is not None:
                if obj.nominal_voltage*math.sqrt(3)<=self.LV_threshold:

                    #Update the counters
                    if hasattr(obj,'phase_loads') and obj.phase_loads is not None:

                        _phase_loads_=[p for p in obj.phase_loads if p.drop!=1]

                        #One phase low voltage load count
                        if len(_phase_loads_)==1:
                            self.results[feeder_name]['nb_loads_LV_1ph']+=1

                        #Three phase low voltage load count
                        elif len(_phase_loads_)==3:
                            self.results[feeder_name]['nb_loads_LV_3ph']+=1

                        #The following block keeps track of the total active power for each phase
                        for phase_load in _phase_loads_:
                            if hasattr(phase_load,'phase') and phase_load.phase in ['A','B','C']:
                                if hasattr(phase_load,'p') and phase_load.p is not None:

                                    #Phase A
                                    if phase_load.phase=='A':
                                        self.results[feeder_name]['demand_LV_phase_A']+=phase_load.p

                                    #Phase B
                                    elif phase_load.phase=='B':
                                        self.results[feeder_name]['demand_LV_phase_B']+=phase_load.p

                                    #Phase C
                                    elif phase_load.phase=='C':
                                        self.results[feeder_name]['demand_LV_phase_C']+=phase_load.p

                #If the load is medium voltage
                elif self.MV_threshold>obj.nominal_voltage*math.sqrt(3)>self.LV_threshold:
                    if hasattr(obj,'phase_loads') and obj.phase_loads is not None:

                        _phase_loads_=[p for p in obj.phase_loads if p.drop!=1]

                        #Update the count of three phase medium voltage loads
                        if len(_phase_loads_)==3:
                            self.results[feeder_name]['nb_loads_MV_3ph']+=1

            #Total demand and total KVAR updates
            if hasattr(obj,'phase_loads') and obj.phase_loads is not None:
                _phase_loads_=[p for p in obj.phase_loads if p.drop!=1]
                self.results[feeder_name]['total_demand']+=np.sum([pl.p for pl in _phase_loads_ if pl.p is not None])
                self.load_distribution.append(np.sum([pl.p for pl in _phase_loads_ if pl.p is not None]))
                self.results[feeder_name]['total_kVar']+=np.sum([pl.q for pl in _phase_loads_ if pl.q is not None])

            return


        #If we get a regulator
        if isinstance(obj, Regulator):

            #Update the count
            self.results[feeder_name]['nb_of_regulators']+=1

            return


        #If we get a capacitor
        if isinstance(obj, Capacitor):

            #Update the count
            self.results[feeder_name]['nb_of_capacitors']+=1

            return


        #If we get a Transformer
        if isinstance(obj, PowerTransformer):

            #Update the count
            #self.results[feeder_name]['nb_of_distribution_transformers']+=1

            if hasattr(obj, 'windings') and obj.windings is not None and len(obj.windings)>0:

                if (hasattr(obj.windings[0],'nominal_voltage') and
                    obj.windings[0].nominal_voltage is not None and
                    hasattr(obj.windings[1],'nominal_voltage') and
                    obj.windings[1].nominal_voltage is not None and
                    obj.windings[0].nominal_voltage!=obj.windings[1].nominal_voltage):
                    self.results[feeder_name]['nb_of_distribution_transformers']+=1

                    if hasattr(obj.windings[0], 'rated_power') and obj.windings[0].rated_power is not None:
                        self.results[feeder_name]['distribution_transformer_total_capacity_MVA']+=obj.windings[0].rated_power*10**-6 #DiTTo in va

                    if hasattr(obj.windings[0],'phase_windings') and obj.windings[0].phase_windings is not None:
                        if len(obj.windings[0].phase_windings)==1:
                            self.results[feeder_name]['nb_1ph_Xfrm']+=1
                        elif len(obj.windings[0].phase_windings)==3:
                            self.results[feeder_name]['nb_3ph_Xfrm']+=1

            return



    def get_feeder(self, obj):
        '''Returns the name of the feeder which contains the given object.
If no matching feeder is found, the function returns None.

'''
        if self.node_feeder_mapping.has_key(obj.name):
            return self.node_feeder_mapping[obj.name]
        elif hasattr(obj,'connecting_element') and self.node_feeder_mapping.has_key(obj.connecting_element):
            return self.node_feeder_mapping[obj.connecting_element]
        elif hasattr(obj, 'from_element') and self.node_feeder_mapping.has_key(obj.from_element):
            return self.node_feeder_mapping[obj.from_element]
        else:
            print('Could not find feeder for {}'.format(obj.name))
            return None



    def compute_all_metrics_per_feeder(self):
        '''Computes all the available metrics for each feeder.

'''
        self.load_distribution=[]
        #List of keys that will have to be converted to miles (DiTTo is in meter)
        keys_to_convert_to_miles=['lv_length_miles', 'mv_length_miles', 'length_mv1ph_miles', 'length_mv2ph_miles', 'length_mv3ph_miles',
                                  'length_lv1ph_miles', 'length_lv2ph_miles', 'length_lv3ph_miles', 'length_OH_mv1ph_miles', 'length_OH_mv2ph_miles',
                                  'length_OH_mv3ph_miles', 'length_OH_lv1ph_miles', 'length_OH_lv2ph_miles', 'length_OH_lv3ph_miles']

        #List of keys to divide by 10^3
        keys_to_divide_by_1000=['total_demand','total_kVar']

        #Setup the data structures for all feeders
        self.results={k:self.setup_results_data_structure(k) for k in self.feeder_names}

        #Loop over the objects in the model and analyze them
        for obj in self.model.models:
            #Get the feeder of this object if it exists
            if hasattr(obj,'name'):
                _feeder_ref=self.get_feeder(obj)
                #If we have a valid name, analyze the object
                if _feeder_ref is not None:
                    self.analyze_object(obj,_feeder_ref)

        #Do some post-processing of the results before returning them
        #
        #Compute the percentages of low voltage load kW for each phase
        for _feeder_ref in self.feeder_names:
            total_demand_LV=self.results[_feeder_ref]['demand_LV_phase_A']+self.results[_feeder_ref]['demand_LV_phase_B']+self.results[_feeder_ref]['demand_LV_phase_C']
            if total_demand_LV!=0:
                self.results[_feeder_ref]['percentage_load_LV_kW_phA']=float(self.results[_feeder_ref]['demand_LV_phase_A'])/float(total_demand_LV)*100
                self.results[_feeder_ref]['percentage_load_LV_kW_phB']=float(self.results[_feeder_ref]['demand_LV_phase_B'])/float(total_demand_LV)*100
                self.results[_feeder_ref]['percentage_load_LV_kW_phC']=float(self.results[_feeder_ref]['demand_LV_phase_C'])/float(total_demand_LV)*100
            else:
                self.results[_feeder_ref]['percentage_load_LV_kW_phA']=0
                self.results[_feeder_ref]['percentage_load_LV_kW_phB']=0
                self.results[_feeder_ref]['percentage_load_LV_kW_phC']=0

            #ratio_1phto3ph_Xfrm
            if self.results[_feeder_ref]['nb_3ph_Xfrm']!=0:
                self.results[_feeder_ref]['ratio_1phto3ph_Xfrm']=float(self.results[_feeder_ref]['nb_1ph_Xfrm'])/float(self.results[_feeder_ref]['nb_3ph_Xfrm'])
            else:
                self.results[_feeder_ref]['ratio_1phto3ph_Xfrm']=np.inf

            #avg_nb_load_per_transformer
            if len(self.results[_feeder_ref]['nb_load_per_transformer'])>0:
                self.results[_feeder_ref]['avg_nb_load_per_transformer']=np.mean(self.results[_feeder_ref]['nb_load_per_transformer'].values())

            #Convert to miles
            for k in keys_to_convert_to_miles:
                if self.results[_feeder_ref].has_key(k):
                    self.results[_feeder_ref][k]*=0.000621371

            #Divide by 10^3
            for k in keys_to_divide_by_1000:
                if self.results[_feeder_ref].has_key(k):
                    self.results[_feeder_ref][k]*=10**-3



    def compute_all_metrics(self):
        '''This function computes all the metrics for the whole network in a way that optimizes performance.
Instead of calling all the metrics one by one, we loop over the objects only once and update the metrics.

.. note:: If you only need a very few metrics, it is probably better to call the functions responsible for them.

'''
        self.results={'global':self.setup_results_data_structure()}
        self.load_distribution=[]

        #List of keys that will have to be converted to miles (DiTTo is in meter)
        keys_to_convert_to_miles=['lv_length_miles', 'mv_length_miles', 'length_mv1ph_miles', 'length_mv2ph_miles', 'length_mv3ph_miles',
                                  'length_lv1ph_miles', 'length_lv2ph_miles', 'length_lv3ph_miles', 'length_OH_mv1ph_miles', 'length_OH_mv2ph_miles',
                                  'length_OH_mv3ph_miles', 'length_OH_lv1ph_miles', 'length_OH_lv2ph_miles', 'length_OH_lv3ph_miles']

        #List of keys to divide by 10^3
        keys_to_divide_by_1000=['total_demand','total_kVar']

        #Main Loop that iterates over all the objects in the model
        for obj in self.model.models:
            self.analyze_object(obj,'global')

        #Do some post-processing of the results before returning them
        #
        #Compute the percentages of low voltage load kW for each phase
        for _feeder_ref in ['global']:
            total_demand_LV=self.results[_feeder_ref]['demand_LV_phase_A']+self.results[_feeder_ref]['demand_LV_phase_B']+self.results[_feeder_ref]['demand_LV_phase_C']
            if total_demand_LV==0:
                self.results[_feeder_ref]['percentage_load_LV_kW_phA']=0
                self.results[_feeder_ref]['percentage_load_LV_kW_phB']=0
                self.results[_feeder_ref]['percentage_load_LV_kW_phC']=0
            else:
                self.results[_feeder_ref]['percentage_load_LV_kW_phA']=float(self.results[_feeder_ref]['demand_LV_phase_A'])/float(total_demand_LV)*100
                self.results[_feeder_ref]['percentage_load_LV_kW_phB']=float(self.results[_feeder_ref]['demand_LV_phase_B'])/float(total_demand_LV)*100
                self.results[_feeder_ref]['percentage_load_LV_kW_phC']=float(self.results[_feeder_ref]['demand_LV_phase_C'])/float(total_demand_LV)*100

            #ratio_1phto3ph_Xfrm
            if self.results[_feeder_ref]['nb_3ph_Xfrm']!=0:
                self.results[_feeder_ref]['ratio_1phto3ph_Xfrm']=float(self.results[_feeder_ref]['nb_1ph_Xfrm'])/float(self.results[_feeder_ref]['nb_3ph_Xfrm'])
            else:
                self.results[_feeder_ref]['ratio_1phto3ph_Xfrm']=np.inf

            #avg_nb_load_per_transformer
            if len(self.results[_feeder_ref]['nb_load_per_transformer'])>0:
                self.results[_feeder_ref]['avg_nb_load_per_transformer']=np.mean(self.results[_feeder_ref]['nb_load_per_transformer'].values())

            #Convert to miles
            for k in keys_to_convert_to_miles:
                if self.results[_feeder_ref].has_key(k):
                    self.results[_feeder_ref][k]*=0.000621371

            #Divide by 10^3
            for k in keys_to_divide_by_1000:
                if self.results[_feeder_ref].has_key(k):
                    self.results[_feeder_ref][k]*=10**-3



    def number_of_regulators(self):
        '''Returns the number of regulators.

'''
        return sum([1 for obj in self.model.models if isinstance(obj, Regulator)])



    def number_of_fuses(self):
        '''Returns the number of fuses.

'''
        return sum([1 for obj in self.model.models if isinstance(obj, Line) and obj.is_fuse==1])



    def number_of_reclosers(self):
        '''Returns the number of reclosers.

'''
        return sum([1 for obj in self.model.models if isinstance(obj, Line) and obj.is_recloser==1])



    def number_of_switches(self):
        '''Returns the number of switches.

'''
        return sum([1 for obj in self.model.models if isinstance(obj, Line) and obj.is_switch==1])



    def number_of_capacitors(self):
        '''Returns the number of capacitors.

'''
        return sum([1 for obj in self.model.models if isinstance(obj, Capacitor)])



    def average_degree(self,*args):
        '''Returns the average degree of the network.

'''
        if args:
            return np.mean(nx.degree(args[0]).values())
        else:
            return np.mean(nx.degree(self.G.graph).values())



    def diameter(self,*args):
        '''Returns the diameter of the network.

'''
        if args:
            return nx.diameter(args[0])
        else:
            return nx.diameter(self.G.graph)



    def average_path_length(self,*args):
        '''Returns the average path length of the network.

'''
        if args:
            try:
                return nx.average_shortest_path_length(args[0])
            except ZeroDivisionError:
                return 0
        else:
            return nx.average_shortest_path_length(self.G.graph)



    def furtherest_node_miles(self,*args):
        '''Returns the maximum eccentricity from the source, in miles.

.. warning:: Not working....

'''
        if args:
            if len(args)==1:
                _net=args[0]
                _src=self.source
            elif len(args)==2:
                _net,_src=args
        else:
            _net=self.G.graph
            _src=self.source
        dist={}
        if not _net.has_node(_src):
            _sp=nx.shortest_path(self.G.graph,_src,_net.nodes()[0])
            for n1,n2 in zip(_sp[:-1],_sp[1:]):
                _net.add_edge(n1,n2,length=self.G.graph[n1][n2]['length'])
        for node in _net.nodes():
            dist[node]=nx.shortest_path_length(_net,_src,node,weight='length')
        return np.max(dist.values())*0.000621371 #Convert length to miles



    def furtherest_node_miles_clever(self):
        '''Returns the maximum eccentricity from the source, in miles.

Relies on the assumption that the furthrest node is a leaf, which is often True in distribution systems.

.. warning:: Not working....

'''
        dist={}
        for node in self.G.graph.nodes():
            if nx.degree(self.G.graph, node)==1:
                dist[node]=nx.shortest_path_length(self.G.graph,self.source,node,weight='length')
        return np.max(dist.values())*0.000621371 #Convert length to miles



    def lv_length_miles(self):
        '''Returns the sum of the low voltage line lengths in miles.

'''
        total_length=0
        for obj in self.model.models:
            if isinstance(obj,Line):
                if obj.nominal_voltage<=self.LV_threshold:
                    if hasattr(obj, 'length') and obj.length>=0:
                        total_length+=obj.length
        return total_length*0.000621371 #Convert length to miles



    def mv_length_miles(self):
        '''Returns the sum of the medium voltage line lengths in miles.

'''
        total_length=0
        for obj in self.model.models:
            if isinstance(obj,Line):
                if self.MV_threshold>=obj.nominal_voltage>self.LV_threshold:
                    if hasattr(obj, 'length') and obj.length>=0:
                        total_length+=obj.length
        return total_length*0.000621371 #Convert length to miles



    def length_mvXph_miles(self,X):
        '''Returns the sum of the medium voltage, X phase, line lengths in miles.

'''
        if not isinstance(X,int):
            raise ValueError('Number of phases should be an integer.')
        if not 1<=X<=3:
            raise ValueError('Number of phases should be 1, 2, or 3.')
        total_length=0
        for obj in self.model.models:
            if isinstance(obj,Line):
                if self.MV_threshold>=obj.nominal_voltage>self.LV_threshold:
                    if hasattr(obj, 'wires') and obj.wires is not None:
                        phases=[wire.phase for wire in obj.wires if wire.phase in ['A','B','C']]
                        if len(phases)==X and hasattr(obj, 'length') and obj.length>=0:
                            total_length+=obj.length
        return total_length*0.000621371 #Convert length to miles



    def length_lvXph_miles(self,X):
        '''Returns the sum of the low voltage, X phase, line lengths in miles.

'''
        if not isinstance(X,int):
            raise ValueError('Number of phases should be an integer.')
        if not 1<=X<=3:
            raise ValueError('Number of phases should be 1, 2, or 3.')
        total_length=0
        for obj in self.model.models:
            if isinstance(obj,Line):
                if obj.nominal_voltage<=self.LV_threshold:
                    if hasattr(obj, 'wires') and obj.wires is not None:
                        phases=[wire.phase for wire in obj.wires if wire.phase in ['A','B','C']]
                        if len(phases)==X and hasattr(obj, 'length') and obj.length>=0:
                            total_length+=obj.length
        return total_length*0.000621371 #Convert length to miles



    def total_demand(self):
        '''Returns the sum of all loads active power in kW.

'''
        tot_demand=0
        for obj in self.model.models:
            if isinstance(obj,Load):
                if hasattr(obj,'phase_loads') and obj.phase_loads is not None:
                    tot_demand+=np.sum([pl.p for pl in obj.phase_loads if pl.p is not None])
        return tot_demand*10**-3 #in kW



    def total_reactive_power(self):
        '''Returns the sum of all loads reactive power in kVar.

'''
        tot_kVar=0
        for obj in self.model.models:
            if isinstance(obj,Load):
                if hasattr(obj,'phase_loads') and obj.phase_loads is not None:
                    tot_kVar+=np.sum([pl.q for pl in obj.phase_loads if pl.q is not None])
        return tot_kVar*10**-3 #in kW



    def number_of_loads_LV_Xph(self,X):
        '''Returns the number of low voltage, X phase, loads.

'''
        if not isinstance(X,int):
            raise ValueError('Number of phases should be an integer.')
        if X not in [1,3]:
            raise ValueError('Number of phases should be 1, or 3.')
        nb=0
        for obj in self.model.models:
            if isinstance(obj,Load):
                if hasattr(obj,'nominal_voltage') and obj.nominal_voltage is not None:
                    if obj.nominal_voltage<=self.LV_threshold:
                        if hasattr(obj,'phase_loads') and obj.phase_loads is not None:
                            if len(obj.phase_loads)==X:
                                nb+=1
        return nb



    def number_of_loads_MV_3ph(self):
        '''Returns the number of medium voltage, 3 phase, loads.

'''
        nb=0
        for obj in self.model.models:
            if isinstance(obj,Load):
                if hasattr(obj,'nominal_voltage') and obj.nominal_voltage is not None:
                    if self.MV_threshold>=obj.nominal_voltage>self.LV_threshold:
                        if hasattr(obj,'phase_loads') and obj.phase_loads is not None:
                            if len(obj.phase_loads)==3:
                                nb+=1
        return nb



    def percentage_load_LV_kW_phX(self,X):
        '''Returns the percentage of low voltage phase X in kW:

res=(sum of active power for all phase_loads X)/(total_demand)*100

'''
        if not isinstance(X,str):
            raise ValueError('Phase should be a string.')
        if X not in ['A','B','C']:
            raise ValueError('Phase should be A, B, or C.')

        demand_phase_X=0
        tot_demand=0

        for obj in self.model.models:
            if isinstance(obj,Load):
                if hasattr(obj,'nominal_voltage') and obj.nominal_voltage is not None:
                    if obj.nominal_voltage<=self.LV_threshold:
                        if hasattr(obj,'phase_loads') and obj.phase_loads is not None:
                            for phase_load in obj.phase_loads:
                                if hasattr(phase_load,'phase') and phase_load.phase in ['A','B','C']:
                                    if hasattr(phase_load,'p') and phase_load.p is not None:
                                        if phase_load.phase==X:
                                            demand_phase_X+=phase_load.p
                                            tot_demand+=phase_load.p
                                        else:
                                            tot_demand+=phase_load.p
        return float(demand_phase_X)/float(tot_demand)*100
