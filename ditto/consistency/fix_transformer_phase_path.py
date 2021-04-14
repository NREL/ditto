import networkx as nx
from itertools import islice
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer

"""
DON'T: Ensure every load has at least one transformer between it and the source node if needs_transformers is True
DON'T: that every load has at most one transformer between it and the source node
DO: Ensure that the phases on the low side of the transformer to the load are all the same
DO: Ensure that if the number of phases from the high side of the transformer matches the number of line phases but they're different e.g. A on transformer vs B on line, adjust the transformer phase.
TODO: Ensure that the low side of the transformer is connected to a line that leads to a load

Parameters: 
    model: ditto.store.Store
        The DiTTo storage object with the full network representation
    needs_transformers: boolean
        Whether there must be a transformer between every load and the substation
    verbose: boolean
        Whether to print information about which nodes caused problems


"""
def fix_transformer_phase_path(model,needs_transformers=False,verbose=True):
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

                ### Fix the low side of the transformer is connected to a line that leads to a load if possible
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
                        print('Load '+load.name+' has connected transformer of '+transformer_names[0]+' incorrectly connected (likely backwards). Trying to rotate...')
                        if model[transformer_names[0]].from_element == transformer_low_side:
                            from_element_orig = model[transformer_names[0]].from_element
                            to_element_orig = model[transformer_names[0]].to_element
                            model[transformer_names[0]].from_element = to_element_orig
                            model[transformer_names[0]].to_element = from_element_orig
                            print('Succeeded.')
                        else:
                            print('Failed.')



                ### If there is a transformer, check that there phases on the high side are consistent with the transformer setting, and increase until the substation
                if num_transformers == 1:
                    high_phases = [phase_winding.phase for phase_winding in model[transformer_names[0]].windings[0].phase_windings]
                    for i in range(len(path)-1):
                        element = ditto_graph.graph[path[i]][path[i+1]]
                        if element['equipment'] == 'PowerTransformer' and not element['is_substation']:
                            break
                        if element['equipment'] == 'Line':
                            line_phases = [wire.phase for wire in element['wires'] if wire.phase != 'N'] #Neutral phases not included in the transformer
                            if not set(high_phases).issubset(set(line_phases)): #MV phase line phase must be able to support transformer phase
                                if len(set(high_phases)) == 1 and len(set(line_phases)) == 1:
                                    print('Single phase transformer has incorrect phase of '+str(high_phases)+'. Setting to be '+str(line_phases))
                                    high_phases = [phase_winding.phase for phase_winding in model[transformer_names[0]].windings[0].phase_windings]
                                    model[transformer_names[0]].windings[0].phase_windings[0].phase = line_phases[0]
                        elif element['equipment'] != 'Regulator':
                            print('Warning: element of type '+element['equipment'] +' found on path to load '+load.name)


                #TODO: Add other checks as well
