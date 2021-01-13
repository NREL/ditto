import networkx as nx
from itertools import islice
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer

"""
Checks if there is a unique path from the load to the source. If there are zero paths or multiple paths it returns false
Parameters: 
    model: ditto.store.Store
        The DiTTo storage object with the full network representation
    needs_transformers: boolean
        Whether or not the model includes transformers. Some models have the loads connected directly to the primary
    show_all: boolean
        Flag for whether to show all the loads that have problems, or just the first one that's found. Used in conjunction with verbose
    verbose: boolean
        Whether to print information about which nodes caused problems

"""
def check_unique_path(model, needs_transformers=False, show_all=False, verbose =True):
    all_sources = []
    all_transformers = set()
    all_loads = set()
    result = True

    for i in model.models:
        if isinstance(i,PowerSource) and i.connecting_element is not None:
            all_sources.append(i)
        elif isinstance(i,PowerSource):
            print('Warning - a PowerSource element has a None connecting element')
        if isinstance(i,PowerTransformer):
            all_transformers.add(i)
        if isinstance(i,Load):
            all_loads.add(i)

    if len(all_sources) > 1:
        print('Warning - using first source to orient the network')
    if len(all_sources) == 0:
        print('Model does not contain any power source')
        return False

    load_transformer_map = {}
    all_bad_loads = []

    for load in all_loads:
        load_transformer_map[load.name] = []
    for source in all_sources:
        ditto_graph = Network()
        ditto_graph.build(model,source.connecting_element)
        ditto_graph.set_attributes(model)
        ditto_graph.remove_open_switches(model) # This deletes the switches inside the networkx graph only
        source_name = source.connecting_element
        break_load = False
        for load in all_loads:
            
            ### check there is a unique path from each load to the source
            two_paths = nx.all_simple_paths(ditto_graph.graph, source_name, load.name) # Warning - this can take a very long time if the graph is has large numbers of loops (shouldn't hold for distribution systems)
            num_paths = 0
            if break_load:
                break
            for candidate in two_paths:
                num_paths +=1
                if num_paths > 1:
                    print('Multiple paths from load '+load.name+' to '+source_name)
                    result = False
                    if not show_all:
                        break_load = True
                    all_bad_loads.append((">1",load.name))
                    break
            if num_paths == 0:
                print('No path from load '+load.name+' to ' + source_name)
                if not show_all:
                    break_load = True
                all_bad_loads.append(("0",load.name))
                result = False
                break
    if verbose:
        if show_all and len(all_bad_loads) >0:
            print('All bad loads:')
        elif len(all_bad_loads)>0:
            print('First bad load:')
        for load in all_bad_loads:
            print(load[0],'connections for load',load[1])
        all_bad_loads = []

    return result



