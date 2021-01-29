import networkx as nx
from itertools import islice
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer

"""
Check that every load has at least one transformer between it and the source node if needs_transformers is True
Check that every load has at most one transformer between it and the source node
Check that the phases on the low side of the transformer to the load are all the same
Check that the low side of the transformer is connected to a line that leads to a load
Check that the number of phases from the high side of the transformer (or from the load if there's no transformer) increase

Parameters: 
    model: ditto.store.Store
        The DiTTo storage object with the full network representation
    needs_transformers: boolean
        Whether there must be a transformer between every load and the substation
    verbose: boolean
        Whether to print information about which nodes caused problems


"""
def check_transformer_phase_path(model,needs_transformers=False,verbose=True):
    all_sources = []
    all_transformers = set()
    all_loads = set()
    load_transformer_map = {} # Not used but provides a mapping from load to transformer
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
#                print(load_connection,path)
                num_transformers = 0
                transformer_names = []

                ### check that only zero or one transformers are on the path from load to source (exclude regulators)
                transformer_low_side = None
                for i in range(len(path)-1,0,-1):
                    element = ditto_graph.graph[path[i]][path[i-1]]
                    if element['equipment'] == 'PowerTransformer' and not element['is_substation']: #TODO: check if the transformer is part of a regulator. Shouldn't be a problem but could be depending on how regulator defined 
                        transformer_names.append(element['name'])
                        num_transformers+=1
                    if num_transformers == 0 and not element['equipment'] == 'PowerTransformer':
                        transformer_low_side = path[i-1]

                ### Check that the low side of the transformer is connected to a line that leads to a load
                if num_transformers ==1:
                    load_transformer_map[load.name] = element['name']
                    if model[transformer_names[0]].to_element != transformer_low_side:
                        if verbose:
                            print('Load '+load.name+' has connected transformer of '+transformer_names[0]+' incorrectly connected (likely backwards)')
                        result = False
                elif num_transformers == 0 and needs_transformers:
                    if verbose:
                        print('Load '+load.name+' has no transformers connected.')
                    result = False
                elif num_transformers > 2:
                    result = False
                    if verbose:
                        print('Load '+load.name+' has the following transformers connected: ')
                        for trans in transformer_names:
                            print(trans)

                if num_transformers == 1 and not needs_transformers:
                    print('Warning - transformer found for system where no transformers required between load and customer')

                if num_transformers == 1:
                    low_phases = [phase_winding.phase for phase_winding in model[transformer_names[0]].windings[1].phase_windings]
                    high_phases = [phase_winding.phase for phase_winding in model[transformer_names[0]].windings[0].phase_windings]
                    prev_line_phases = ['A','B','C'] # Assume 3 phase power at substation

                    ### If there is a transformer, check that the phases on the low side are consistent with the transformer settign
                    for i in range(len(path)-1,0,-1):
                        element = ditto_graph.graph[path[i]][path[i-1]]
                        if element['equipment'] == 'PowerTransformer' and not element['is_substation']:
                            break
                        if element['equipment'] == 'Line':
                            line_phases = [wire.phase for wire in element['wires'] if wire.phase != 'N'] #Neutral phases not included in the transformer
                            if not set(line_phases) == set(low_phases): #Low phase lines must match transformer exactly
                                if verbose:
                                    print('Load '+load.name+ ' has incorrect phases on low side of transformer for line '+element['name'])
                                result = False
                                break
                        elif element['equipment'] != 'Regulator':
                            print('Warning: element of type '+element['equipment'] +' found on path to load '+load.name)

                    ### If there is a transformer, check that there phases on the high side are consistent with the transformer setting, and increase until the substation
                    for i in range(len(path)-1):
                        element = ditto_graph.graph[path[i]][path[i+1]]
                        if element['equipment'] == 'PowerTransformer' and not element['is_substation']:
                            break
                        if element['equipment'] == 'Line':
                            line_phases = [wire.phase for wire in element['wires'] if wire.phase != 'N'] #Neutral phases not included in the transformer
                            if not set(high_phases).issubset(set(line_phases)): #MV phase line phase must be able to support transformer phase
                                if verbose:
                                    print('Load '+load.name+ ' has incorrect phases on high side of transformer for line '+element['name'])
                                result = False
                                break
                            if len(line_phases) > len(prev_line_phases):
                                if verbose:
                                    print('Number of phases increases along line '+element['name'] +' from '+str(len(prev_line_phases))+' to '+str(len(line_phases)))
                                result = False
                                break
                            prev_line_phases = line_phases
                        elif element['equipment'] != 'Regulator':
                            print('Warning: element of type '+element['equipment'] +' found on path to load '+load.name)

                if num_transformers == 0:
                    prev_line_phases = ['A','B','C'] # Assume 3 phase power at substation

                    ### If there is no transformer, check that there phases increase until the substation
                    for i in range(len(path)-1):
                        element = ditto_graph.graph[path[i]][path[i+1]]
                        if element['equipment'] == 'Line':
                            line_phases = [wire.phase for wire in element['wires'] if wire.phase != 'N'] #Neutral phases not included in the transformer
                            if len(line_phases) > len(prev_line_phases):
                                if verbose:
                                    print('Number of phases increases along line '+element['name'] +' from '+str(len(prev_line_phases))+' to '+str(len(line_phases)))
                                result = False
                                break
                            prev_line_phases = line_phases
                        elif element['equipment'] != 'Regulator' and element['equipment'] != 'PowerTransformer':
                            print('Warning: element of type '+element['equipment'] +' found on path to load '+load.name)
    return result


