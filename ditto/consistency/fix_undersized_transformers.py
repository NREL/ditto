import networkx as nx
from itertools import islice
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer

"""
DO: Increase size of transformers to support the maximum loads downstream of it
Requires a valid path from each load to the source

Parameters: 
    model: ditto.store.Store
        The DiTTo storage object with the full network representation
    verbose: boolean
        Whether to print information about which nodes caused problems
"""

def fix_undersized_transformers(model,verbose=True):
    all_sources = []
    all_transformers = set()
    all_loads = set()
    transformer_load_map = {} # provides a mapping of all the loads connected to a transformer if there's a path from the load to a source
    result = True
    transformer_sizes = [15,25,50,75,100,300,500,1000,2000,3000,5000] # upgrade sizes in kva
    model.set_names()

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
        return

    for source in all_sources:
        ditto_graph = Network()
        ditto_graph.build(model,source.connecting_element)
        ditto_graph.set_attributes(model)
        ditto_graph.remove_open_switches(model) # This deletes the switches inside the networkx graph only
        source_name = source.connecting_element
        all_paths = nx.single_source_shortest_path(ditto_graph.graph,source_name)
        break_load = False
        for load in all_loads:
            load_connection = load.connecting_element
            if load_connection in all_paths:

                ### check that each load has a path to the substation
                path = all_paths[load_connection]
                num_transformers = 0
                transformer_names = []

                for i in range(len(path)-1,0,-1):
                    element = ditto_graph.graph[path[i]][path[i-1]]
                    if element['equipment'] == 'PowerTransformer' and not element['is_substation']: #TODO: check if the transformer is part of a regulator. Shouldn't be a problem but could be depending on how regulator defined 
                        transformer_names.append(element['name'])
                        num_transformers+=1

                ### If the transformer is connected correctly with the load underneath it, update the transformer-load mapping dictionary
                if num_transformers ==1:
                    if not transformer_names[0] in transformer_load_map:
                        transformer_load_map[transformer_names[0]] = []
                    transformer_load_map[transformer_names[0]].append(load.name)

        for transformer in transformer_load_map:
            transformer_size = model[transformer].windings[0].rated_power/1000
            total_load_kw = 0 
            for load in transformer_load_map[transformer]:
                load_kw = 0
                for phase_load in model[load].phase_loads:
                    total_load_kw += phase_load.p/1000
                    load_kw += phase_load.p/1000
            if transformer_size <total_load_kw:
                new_transformer_size = None
                for sz in transformer_sizes:
                    if sz > total_load_kw:
                        new_transformer_size = sz
                        break
                if new_transformer_size is not None:
                    print(f'Tranformer {transformer} with size {transformer_size} kVA serves {total_load_kw} kW. Upgrading to {new_transformer_size} kVA')
                    for winding in model[transformer].windings:
                        winding.rated_power = new_transformer_size*1000
                else:
                    print(f'Tranformer {transformer} with size {transformer_size} kVA serves {total_load_kw} kW. No upgrade size found (max is 5000 kVA)')

    


