import networkx as nx
from itertools import islice
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer


"""
Check that the phases on the low and high side of at transformer match. 
Also check that on the path from a transformer to the source (or load to the source if there are no transformers) that the number of phases increases
(There are some instances such as split nodes that rejoin, where this doesn't hold but it's still a useful check to perform)

"""

def is_matched_phases(model, needs_transformers=False):
    all_sources = []
    all_transformers = set()
    all_loads = set()
    load_source_map = {}

    for i in model.models:
        if isinstance(i,PowerSource) and i.connecting_element is not None:
            all_sources.append(i)
        elif isinstance(i,PowerSource):
            print('Warning - a PowerSource element has a None connecting element')
        if isinstance(i,PowerTransformer):
            all_transformers.add(i)
        if isinstance(i,Load):
            load_source_map[i.name] = []
            all_loads.add(i)


    if len(all_sources) > 1:
        print('Warning - using first source to orient the network')
    if len(all_sources) == 0:
        print('Model does not contain any power source')
        return False

    ### Check phases around the transformer ###
    result = True
    for transformer in all_transformers:
        # Either a three phase transformer or a single phase transformer
        if len(transformer.windings) == 2:
            high_phases = []
            low_phases = []
            for phase_windings in transformer.windings[0].phase_windings:
                high_phases.append(phase_windings.phase)
            for phase_windings in transformer.windings[1].phase_windings:
                low_phases.append(phase_windings.phase)

            ok = False
            if set(high_phases) == set(low_phases):
                ok = True
            elif set(low_phases) in set(high_phases):
                ok = True
            else:
                print('Something is wrong with Transformer '+transformer.name)
                result = False


        # i.e. A center-tap transformer
        elif len(transformer.windings) == 3:
            high_phases = []
            low_phases = []
            low_phases2 = []
            for phase_windings in transformer.windings[0]:
                high_phases.add(phase_windings.phase)
            for phase_windings in transformer.windings[1]:
                low_phases.add(phase_windings.phase)
            for phase_windings in transformer.windings[2]:
                low_phases2.add(phase_windings.phase)

            if low_phases2 != low_phases:
                print('Center tap winding phases mismatch for transformer '+transformer.name)
                result = False

            if len(low_phases2) != 2:
                print('Center tap low winding misrepresented for '+transformer.name)
                result = False

            if len(high_phases) > 2:
                print('Center tap transformer connected to three-phase winding for transformer '+transformer.name)
                result = False


        else:
            result = False
            print('Transformer '+transformer.name+' has incorrect number of windings')


    ### check there is a unique path from each load to the source
    ### check that each load has a path to the substation
    ### check that only zero or one transformers are on the path from load to source (exclude regulators)
    ### If there is a transformer, check that the phases on the low side are consistent with the transformer settign
    ### If there is a transformer, check that there phases on the high side are consistent with the transformer setting, and increase until the substation
    ### If there is no transformer, check that there phases increase until the substation

    load_transformer_map = {}
    load_source_map = {}
    for load in all_loads:
        load_transformer_map[load.name] = []
        load_source_map[load.name] = []
    for source in all_sources:
        ditto_graph = Network()
        ditto_graph.build(model,source.connecting_element)
        ditto_graph.set_attributes(model)
        ditto_graph.remove_open_switches(model) # This deletes the switches inside the networkx graph only
        source_name = source.connecting_element
        all_paths = nx.single_source_shortest_path(ditto_graph.graph,source_name)
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
                    break_load = True
                    break


            min_dist = float('inf')
            load_connection = load.connecting_element
            if load_connection in all_paths:

                ### check that each load has a path to the substation
                load_source_map[load.name].append(source.name)
                path = all_paths[load_connection]
#                print(load_connection,path)
                num_transformers = 0
                transformer_names = []

                ### check that only zero or one transformers are on the path from load to source (exclude regulators)

                for i in range(len(path)-1,0,-1):
                    element = ditto_graph.graph[path[i]][path[i-1]]
                    if element['equipment'] == 'PowerTransformer' and not element['is_substation']:
                        transformer_names.append(element['name'])
                        num_transformers+=1
                if num_transformers ==1:
                    load_transformer_map[load.name] = element['name']
                elif num_transformers == 0 and needs_transformers:
                    print('Load '+load.name+' has no transformers connected.')
                    result = False
                elif num_transformers > 2:
                    result = False
                    print('Load '+load.name+' has the following transformers connected: ')
                    for trans in transformer_names:
                        print(trans)

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
                            if not set(high_phases) in set(line_phases): #MV phase line phase must be able to support transformer phase
                                print('Load '+load.name+ ' has incorrect phases on high side of transformer for line '+element['name'])
                                result = False
                                break
                            if len(line_phases) > len(prev_line_phases):
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
                                print('Number of phases increases along line '+element['name'] +' from '+str(len(prev_line_phases))+' to '+str(len(line_phases)))
                                result = False
                                break
                            prev_line_phases = line_phases
                        elif element['equipment'] != 'Regulator' and element['equipment'] != 'PowerTransformer':
                            print('Warning: element of type '+element['equipment'] +' found on path to load '+load.name)


    for load in load_source_map:
        if len(load_source_map[load]) == 0:
            print('Load '+load+ ' not connected to any source')
            reult = False




    print(result)

    return result
