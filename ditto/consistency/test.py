from ditto.readers.opendss.read import Reader
from ditto.models.powertransformer import PowerTransformer
from ditto.store import Store
import phases_match
import check_loops
import os

test_system_master = os.path.join('..','..','tests','data','small_cases','opendss','ieee_13node','master.dss')
test_system_coords = os.path.join('..','..','tests','data','small_cases','opendss','ieee_13node','buscoords.dss')

model  = Store()
r = Reader(master_file = test_system_master,buscoords_file = test_system_coords)
r.parse(model)

for i in model.models:
    if isinstance(i,PowerTransformer):
        i.is_substation = True #Only for 13 node system. Need to fix in readers

check_loops.has_loops(model)
phases_match.is_matched_phases(model)

