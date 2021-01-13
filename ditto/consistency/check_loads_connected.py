
import networkx as nx
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load

"""
This uses the DiTTo Network functionality to check that there is a path from a load to the source node. Considers switch states. Transformer consistency checked elsewhere
Parameters: 
    model: ditto.store.Store
        The DiTTo storage object with the full network representation
    verbose: boolean
        Whether to print information about which nodes caused problems

"""
def check_loads_connected(model,verbose=True):
    all_sources = []
    all_loads = set()
    load_source_map = {}
    result = True

    for i in model.models:
        if isinstance(i,PowerSource) and i.connecting_element is not None:
            all_sources.append(i)
        elif isinstance(i,PowerSource):
            print('Warning - a PowerSource element has a None connecting element')
        if isinstance(i,Load):
            all_loads.add(i)
            load_source_map[i.name] = []

    if len(all_sources) == 0:
        print('Model does not contain any power source')
        return False
    
    for source in all_sources:
        ditto_graph = Network()
        ditto_graph.build(model,source.connecting_element)
        ditto_graph.set_attributes(model)
        ditto_graph.remove_open_switches(model) # This deletes the switches inside the networkx graph only
        source_name = source.connecting_element
        all_paths = nx.single_source_shortest_path(ditto_graph.graph,source_name)
        
        for load in all_loads:
            min_dist = float('inf')
            load_connection = load.connecting_element
            if load_connection in all_paths:
                load_source_map[load.name].append(source_name)


    result = True
    sourceless_loads = []
    multi_source_loads = {}
    for load in load_source_map:
        if len(load_source_map[load]) == 0:
            result = False 
            sourceless_loads.append(load)
        if len(load_source_map[load]) >1:
            result = False 
            multi_source_loads[load.name] = load_source_map[load]

    if verbose:
        if len(sourceless_loads) > 0:
            print('Loads missing sources:')
            for load in sourceless_loads:
                print(load)

        if len(multi_source_loads)> 0:
            print('Loads with multiple sources:')
            for load in multi_source_loads:
                print(load+ ': ' +multi_source_loads[load])

    return result

