from ditto.readers.opendss.read import Reader
from ditto.models.powertransformer import PowerTransformer
from ditto.store import Store
import os

from check_loops import check_loops
from check_loads_connected import check_loads_connected
from check_unique_path import check_unique_path
from check_matched_phases import check_matched_phases
from check_transformer_phase_path import check_transformer_phase_path

test_system_master = os.path.join('..','..','tests','data','small_cases','opendss','ieee_13node','master.dss')
test_system_coords = os.path.join('..','..','tests','data','small_cases','opendss','ieee_13node','buscoords.dss')

"""
Tests:
    + Check if the system has any loops (once open switches are removed)
    + Check if there is a path from each load to the head node
    + Check that the phases on the high and low side of the transformer match
    + Check if there's a unique path from load to the source

    (transformer_phase_path does all of these):
    + Check that only zero or one transformers are on the path to the head node (excluding regulators)
    + Check that the number of phases increases from the transformer to the substation
    + Check that the number of phases increases from a three phase load to the substation
    + Check that the number of phases is the same from the load to the transformer

"""
model  = Store()
r = Reader(master_file = test_system_master,buscoords_file = test_system_coords)
r.parse(model)

for i in model.models:
    if isinstance(i,PowerTransformer):
        i.is_substation = True #Only for 13 node system. Need to fix in readers

print('Pass loops check:',flush=True)
loops_res = check_loops(model,verbose=True)
print(loops_res)
print()

print('Pass loads connected check:',flush=True)
loads_connected_res = check_loads_connected(model,verbose=True)
print(loads_connected_res)
print()

print('Pass unique path check:',flush=True)
unique_path_res = check_unique_path(model,show_all=True,verbose=True)
print(unique_path_res)
print()

print('Pass matched phases check:',flush=True)
matched_phases_res = check_matched_phases(model,verbose=True)
print(matched_phases_res)
print()

print('Pass transformer phase path check:',flush=True)
transformer_phase_res = check_transformer_phase_path(model,needs_transformers=False, verbose=True)
print(transformer_phase_res)
print()
