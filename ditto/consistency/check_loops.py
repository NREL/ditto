import networkx as nx
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load

"""
This function sets all the switch states in networkx model and then sees if there are any loops in the resulting network
"""

def has_loops(model):
    all_sources = []
    for i in model.models:
        if isinstance(i,PowerSource) and i.connecting_element is not None:
            all_sources.append(i)
        elif isinstance(i,PowerSource):
            print('Warning - a PowerSource element has a None connecting element')

    if len(all_sources) > 1:
        print('Warning - using first source to orient the network')

    # TODO: Address issue in network.py where a single source is used to determine bfs order
    if len(all_sources) == 0:
        raise('Model does not contain any power source. Required to build networkx graph')

    for source in all_sources:
        print('Checking loops for source '+source.name)
        ditto_graph = Network()
        ditto_graph.build(model,source.connecting_element)
        ditto_graph.set_attributes(model)
        ditto_graph.remove_open_switches(model) # This deletes the switches inside the networkx graph only
    
        loops = nx.cycle_basis(ditto_graph.graph)
        number_of_loops = len(loops)
        if number_of_loops > 0:
            print('Loops found:')
            print(loops)
        if number_of_loops == 0:
            return False
    return True


