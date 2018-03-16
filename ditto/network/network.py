'''This class defines the network structure of DiTTo using the Store classes'''

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import random
import networkx as nx
import traceback
from ditto.models.base import DiTToHasTraits


class Network:
    def __init__(self):
        self.graph = None
        self.digraph = None #Doesn't contain attributes, just topology
        self.class_map = {} # Map the networkx names to the object type (not included in attributes)
        self.is_built = False #Flag that indicates whether the Network has been built or not.
        self.attributes_set = False #Flag that indicates whether the attributes have been set or not.

    def provide_graphs(self,graph,digraph):
        '''
            This functions sets the graph and digraph of the Network class with direct user inputs.
            This can be useful if the user has the graphs stored and does not want to re-compute them.
            It can also be useful when work has to be done to get connected networks. It might be easier to
            perform the work beforehand, and create a Network instance for each connected component.

            .. warning: The method does not do any safety check yet...
        '''
        self.graph=graph
        self.digraph=digraph
        self.is_built=True

    # Only builds connected nodes
    #
    #Nicolas modification: Added source in the args for bfs
    def build(self, model, source='sourcebus'):
        self.graph = nx.Graph()
        graph_edges = set()
        graph_nodes = set()
        for i in model.models:

            #Nicolas modification: I need the type of object that connects the nodes to postprocess the center tap loads
            #
            if hasattr(i, 'name') and i.name is not None:
                object_type = type(i).__name__

            if hasattr(i, 'from_element') and i.from_element is not None and hasattr(i, 'to_element') and i.to_element is not None:

                if hasattr(i, 'length') and i.length is not None:
                    length = i.length
                else:
                    length = 0 #Default if we do not have a valid length.

                #The following ugly code that repeats itself multiple times in build()
                #was a desperate attempt to speed up the network build method.
                #Does not make much difference though...
                #
                #TODO: Improve the performance of this function if possible. Otherwise, revert to pretty code
                #
                a = len(graph_nodes)
                graph_nodes.add(i.to_element)
                b = len(graph_nodes)
                if b == a + 1:
                    #if not i.to_element in graph_nodes:
                    self.graph.add_node(i.to_element)
                    #graph_nodes.add(i.to_element)
                a = len(graph_nodes)
                graph_nodes.add(i.from_element)
                b = len(graph_nodes)
                if b == a + 1:
                    #if not i.from_element in graph_nodes:
                    self.graph.add_node(i.from_element)
                    #graph_nodes.add(i.from_element)

                self.graph.add_edge(i.from_element, i.to_element, equipment=object_type, equipment_name=i.name, length=length)
                graph_edges.add((i.from_element, i.to_element))

            if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                a = len(graph_nodes)
                graph_nodes.add(i.connecting_element)
                b = len(graph_nodes)
                if b == a + 1:
                    #if not i.connecting_element in graph_nodes:
                    self.graph.add_node(i.connecting_element)
                    #graph_nodes.add(i.connecting_element)
                a = len(graph_nodes)
                graph_nodes.add(i.name)
                b = len(graph_nodes)
                if b == a + 1:
                    #if not i.name in graph_nodes:
                    self.graph.add_node(i.name)
                    #graph_nodes.add(i.name)
                a = len(graph_edges)
                graph_edges.add((i.connecting_element, i.name))
                b = len(graph_edges)
                if b == a + 1:
                    #if not (i.connecting_element,i.name) in graph_edges:
                    self.graph.add_edge(*(i.connecting_element, i.name))
                    #graph_edges.add((i.connecting_element,i.name))

        #Nicolas modification: Calling to_directed() on NetworkX undirected graph gives a directed graph with edges in both direction
        #a-b gives a->b and a<-b, which is not what we want
        #
        #self.digraph = self.graph.to_directed()
        #
        #Using the bfs_order method:
        self.digraph = nx.DiGraph()
        self.digraph.add_edges_from(list(self.bfs_order(source=source)))

        edge_equipment = nx.get_edge_attributes(self.graph, 'equipment')
        edge_equipment_name = nx.get_edge_attributes(self.graph, 'equipment_name')
        for edge in edge_equipment:
            if self.digraph.has_edge(*edge):
                self.digraph[edge[0]][edge[1]]['equipment'] = edge_equipment[edge]
            elif self.digraph.has_edge(*edge[::-1]):
                self.digraph[edge[1]][edge[0]]['equipment'] = edge_equipment[edge]

        for edge in edge_equipment_name:
            if self.digraph.has_edge(*edge):
                self.digraph[edge[0]][edge[1]]['equipment_name'] = edge_equipment_name[edge]
            elif self.digraph.has_edge(*edge[::-1]):
                self.digraph[edge[1]][edge[0]]['equipment_name'] = edge_equipment_name[edge]

        self.is_built = True

    def set_attributes(self, model):
        graph_nodes = set(self.graph.nodes())
        graph_edges = set(self.digraph.edges()) #Use the ordering provided from the BFS order
        for i in model.models:
            if hasattr(i, 'name') and i.name is not None:
                object_type = type(i).__name__
                self.class_map[i.name] = object_type

                if i.name in graph_nodes:
                    for attr in tuple(set(dir(i)) - set(dir(DiTToHasTraits))): #only set attributes from the subclass, not the base class
                        if attr[0] != '_':
                            self.graph.node[i.name][attr] = getattr(i, attr)
                            self.digraph.node[i.name][attr] = getattr(i, attr)

                if hasattr(i, 'from_element') and i.from_element is not None and hasattr(i, 'to_element') and i.to_element is not None:
                    if (i.from_element, i.to_element) in graph_edges:
                        for attr in tuple(set(dir(i)) - set(dir(DiTToHasTraits))): #only set attributes from the subclass, not the base class
                            if attr[0] != '_':
                                self.graph[i.from_element][i.to_element][attr] = getattr(i, attr)
                                self.digraph[i.from_element][i.to_element][attr] = getattr(i, attr)

                    if (i.to_element, i.from_element) in graph_edges:
                        for attr in tuple(set(dir(i)) - set(dir(DiTToHasTraits))): #only set attributes from the subclass, not the base class
                            if attr[0] != '_':
                                self.graph[i.to_element][i.from_element][attr] = getattr(i, attr)
                                self.digraph[i.to_element][i.from_element][attr] = getattr(i, attr)

                if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                    if (i.connecting_element, i.name) in graph_edges:
                        for attr in tuple(set(dir(i)) - set(dir(DiTToHasTraits))): #only set attributes from the subclass, not the base class
                            if attr[0] != '_':
                                self.graph[i.connecting_element][i.name][attr] = getattr(i, attr)
                                self.digraph[i.connecting_element][i.name][attr] = getattr(i, attr)

        self.attributes_set = True

    def get_upstream_transformer(self, model, node):

        curr_node = node
        curr = self.digraph.predecessors(node)
        edge_equipment = nx.get_edge_attributes(self.digraph, 'equipment')
        edge_equipment_name = nx.get_edge_attributes(self.digraph, 'equipment_name')
        #import pdb; pdb.set_trace()
        while (curr != []):
            edge_type = edge_equipment[(curr[0], curr_node)]
            if edge_type == 'PowerTransformer':
                return edge_equipment_name[(curr[0], curr_node)]
            curr_node = curr[0] # assuming that the network is a DAG
            curr = self.digraph.predecessors(curr_node)
        return None

    def get_all_elements_downstream(self, model, source):
        '''Returns all the DiTTo objects which location is downstream of a given node.
This might be handy when trying to find all the objects below a substation such that the network can be properly seperated in different feeders for analysis.

'''
        _elts = set()
        model.set_names()

        #Checking that the network is already built
        #TODO: Log instead of printing...
        if not self.is_built:
            print('Warning. Trying to use Network model without building the network.')
            print('Calling build() with source={}'.format(source))
            self.build(model, source=source)

        #Checking that the attributes have been set
        #TODO: Log instead of printing...
        if not self.attributes_set:
            print('Warning. Trying to use Network model without setting the attributes first.')
            print('Setting the attributes...')
            self.set_attributes(model)

        #Run the dfs or die trying...
        try:
            childrens = nx.dfs_successors(self.digraph, source)
        except:
            traceback.print_exc()
            raise ValueError('dfs failed with source={}'.format(source))

        #Following two lines extract the data stored in the edges
        #More precisely, the type of equipment and the name of the equipment
        #that makes the connection (usually a line or a transformer)
        #
        edge_equipment = nx.get_edge_attributes(self.graph, 'equipment')
        edge_equipment_name = nx.get_edge_attributes(self.graph, 'equipment_name')

        #Build the list of equipment names downstream
        for source, destinations in childrens.items():
            _elts.add(source)
            for destination in destinations:
                _elts.add(destination)
                if (source, destination) in edge_equipment_name:
                    _elts.add(edge_equipment_name[(source, destination)])
                elif (destination, source) in edge_equipment_name:
                    _elts.add(edge_equipment_name[(destination, source)])

        #Get the corresponding DiTTo objects
        #Warning: This will fail if set_names() has not been called before.
        _obj = []
        for x in _elts:
            try:
                _obj.append(model[x])
            except:
                raise ValueError('Unable to get DiTTo object with name {}'.format(x))

        return _obj

    def get_nodes(self):
        return self.graph.nodes()

    def print_nodes(self):
        for i in self.graph.nodes():
            try:
                sp = nx.shortest_path(self.graph, 'sourcebus', i)
                print(i, sp)
            except:
                print('No path to ' + i)

    def print_edges(self):
        for i in self.graph.edges():
            print(i)

    def print_attrs(self):
        print(self.graph.nodes(data=True))

    def bfs_order(self, source='sourcebus'):
        start_node = self.graph[source]
        return (set(nx.bfs_edges(self.graph, source)))

    '''Find all edges that have both edges in the set of provided nodes'''

    def find_internal_edges(self, nodeset):
        internal_edges = set()
        all_edges = set()
        names = nx.get_edge_attributes(self.graph, 'name')
        for node in nodeset:
            linked_edges = self.graph.edges([node])
            for edge in linked_edges:
                all_edges.add(edge)

        for edge in all_edges:
            if edge[0] in nodeset and edge[1] in nodeset:
                if (edge[0], edge[1]) in names:
                    internal_edges.add(names[(edge[0], edge[1])])
                elif (edge[1], edge[0]) in names:
                    internal_edges.add(names[(edge[1], edge[0])])

        return (internal_edges)

    def find_cycles(self):
        duplicate_cycles = list(nx.simple_cycles(self.digraph))
        all_cycles = set()
        final_cycles = []
        for i in duplicate_cycles:
            sorted = []
            for node in i:
                sorted.append(node)
            sorted.sort()
            sorted = tuple(sorted)
            if not (sorted in all_cycles):
                all_cycles.add(sorted)
                final_cycles.append(i)
        return (final_cycles)

    def order_by_phase(self, edge):
        deg_1 = len(self.graph.node[edge[0]]['phases'])
        deg_2 = len(self.graph.node[edge[1]]['phases'])
        if deg_2 > deg_1:
            return ([edge[1], edge[0]])
        return ([edge[0], edge[1]])

    def middle_single_phase(self, nodes):
        at_1p_section = False
        cnt = 0
        max_cnt = 0
        pos_max_cnt = -1
        min_phase = 1000
        for i in range(len(nodes)):
            #print('phaselen:')
            #print(len(self.graph.node[nodes[i]]['phases']))
            if (not 'phases' in self.graph.node[nodes[i]]) or self.graph.node[nodes[i]]['phases'] == None:
                pos = rand.randint(0, len(nodes) - 2)
                order1 = tuple([nodes[pos], nodes[pos + 1]])
                order2 = tuple([nodes[pos + 1], nodes[pos]])
                if order1 in self.graph.edges():
                    return (self.graph[order1[0]][order1[1]]['name'])
                else:
                    return (self.graph[order2[0]][order2[1]]['name'])
            if len(self.graph.node[nodes[i]]['phases']) < min_phase:
                min_phase = len(self.graph.node[nodes[i]]['phases'])
        #print(min_phase)
        for i in range(len(nodes)):
            node = nodes[i]
            if at_1p_section and len(self.graph.node[node]['phases']) > min_phase:
                if cnt > max_cnt:
                    max_cnt = cnt
                    pos_max_cnt = i - 1
                cnt = 0
                at_1p_section = False
            if len(self.graph.node[node]['phases']) == min_phase:
                cnt = cnt + 1
                at_1p_section = True
        if cnt > 0 and cnt > max_cnt:
            pos_max_cnt = len(nodes) - 2 #Shift by 1 to avoid any index out of bounds issues.
            cnt = max_cnt = cnt

        if pos_max_cnt > -1:
            order1 = tuple([nodes[pos_max_cnt - max_cnt / 2], nodes[pos_max_cnt - max_cnt / 2 + 1]])
            order2 = tuple([nodes[pos_max_cnt - max_cnt / 2 + 1], nodes[pos_max_cnt - max_cnt / 2]])
            if order1 in self.graph.edges():
                print(order1)
                return (self.graph[order1[0]][order1[1]]['name'])
            else:
                print(order2)
                return (self.graph[order2[0]][order2[1]]['name'])
        else:
            return ()
