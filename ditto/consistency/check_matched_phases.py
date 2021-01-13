import networkx as nx
from itertools import islice
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer


"""
Check that the phases on the low and high side of at transformer match. 

Parameters: 
    model: ditto.store.Store
        The DiTTo storage object with the full network representation
    verbose: boolean
        Whether to print information about which nodes caused problems

"""

def check_matched_phases(model, verbose=True):
    all_transformers = set()
    all_loads = set()
    load_source_map = {}

    for i in model.models:
        if isinstance(i,PowerTransformer):
            all_transformers.add(i)
        if isinstance(i,Load):
            load_source_map[i.name] = []
            all_loads.add(i)


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
                if verbose:
                    print('Something is wrong with Transformer '+transformer.name)
                result = False


        # i.e. A center-tap transformer
        elif len(transformer.windings) == 3:
            high_phases = []
            low_phases = []
            low_phases2 = []
            for phase_windings in transformer.windings[0].phase_windings:
                high_phases.append(phase_windings.phase)
            for phase_windings in transformer.windings[1].phase_windings:
                low_phases.append(phase_windings.phase)
            for phase_windings in transformer.windings[2].phase_windings:
                low_phases2.append(phase_windings.phase)

            if low_phases2 != low_phases:
                if verbose:
                    print('Center tap winding phases mismatch for transformer '+transformer.name)
                result = False

            if len(low_phases2) != 2:
                if verbose:
                    print('Center tap low winding misrepresented for '+transformer.name)
                result = False

            if len(high_phases) > 2:
                if verbose:
                    print('Center tap transformer connected to three-phase winding for transformer '+transformer.name)
                result = False


        else:
            result = False
            if verbose:
                print('Transformer '+transformer.name+' has incorrect number of windings')

    return result
