# -*- coding: utf-8 -*-

"""
test_opendss_reader
----------------------------------

Tests for OpenDSS reader
"""

import os
import ditto.models.base as bs
from ditto.readers.opendss.read import Reader
from ditto.store import Store

current_directory = os.path.realpath(os.path.dirname(__file__))
model = 'ieee_4node'
data_path = os.path.join(current_directory, 'standard_tests/{model}/'.format(model='ieee_4node'))
m = Store()
r = Reader(
    master_file=os.path.join(current_directory, 'data/small_cases/opendss/{model}/master.dss'.format(model=model)),
    buscoordinates_file=os.path.join(current_directory,
                                     'data/small_cases/opendss/{model}/buscoord.dss'.format(model=model))
)
r.parse(m)
m.set_names()


def get_non_empty_columns(df):
    all_columns = df.columns
    columns = []
    for c in all_columns:
        if isinstance((df[c].sum()), str):
            if len(df[c].sum()) > 0:
                columns.append(c)
        else:
            if (df[c].sum() > 0) or (df[c].dtypes == bool):
                columns.append(c)

    return set(columns)


def verify_component(component_dict, model_obj, component, to_append):
    if component == 'loads':
        loads_in_csv = component_dict[component].__len__()
        loads_in_model = 0
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Load':
                loads_in_model += 1
        assert loads_in_csv == loads_in_model
    elif component == 'phase_loads':
        obj_names = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Load':
                obj_names.append(m.model_names[model].name)

        for name in obj_names:
            model_set_len = len(model_obj.model_names[name].phase_loads)
            csv_phase_load_count = component_dict[component].__len__()
            assert csv_phase_load_count == model_set_len
    elif (component == 'windings') or (component == 'phase_windings'):
        obj_names = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                obj_names.append(m.model_names[model].name)
        if component == 'windings':
            for name in obj_names:
                model_set_len = len(model_obj.model_names[name].windings)
                csv_winding_count = component_dict[component].__len__()
                assert csv_winding_count == model_set_len
        else:
            sub_obj = len(model_obj.model_names[obj_names[0]].windings)
            for name in obj_names:
                for s in range(sub_obj):
                    model_set_len = len(model_obj.model_names[name].windings[s].phase_windings)
                    csv_phase_winding_count = component_dict[component].__len__()
                    assert csv_phase_winding_count == model_set_len
    elif component == 'wires':
        obj_names = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Line':
                obj_names.append(m.model_names[model].name)
        for name in obj_names:
            model_set_len = len(model_obj.model_names[name].wires)
            csv_wire_count = component_dict[component].__len__()
            assert csv_wire_count == model_set_len
    elif component == 'nodes':
        nodes_in_csv = component_dict[component].__len__()
        nodes_in_model = 0
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Node':
                nodes_in_model += 1
        assert nodes_in_csv == nodes_in_model
    elif component == 'transformers':
        in_csv = component_dict[component].__len__()
        in_model = 0
        for model in m.model_names:
            if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                in_model += 1
        assert in_csv == in_model
    elif component == 'lines':
        in_csv = component_dict[component].__len__()
        in_model = 0
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Line':
                in_model += 1
        assert in_csv == in_model


def verify_properties(component_dict, model_obj, component, to_append):
    names = list(component_dict[component][to_append + 'name'])
    csv_set = get_non_empty_columns(component_dict[component])

    if component == 'phase_loads':
        # phase_load object lies inside load objects
        loads = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Load':
                loads.append(m.model_names[model].name)
        csv_set.remove(to_append + 'name')
        phase_load_count = component_dict['phase_loads'].__len__()
        for load in loads:
            phase_loads = model_obj.model_names[load].phase_loads
            for w_count in range(phase_load_count):
                model_set = phase_loads[w_count].trait_names()
                model_set = [to_append + t for t in model_set]
                for t in csv_set:
                    assert t in model_set
    elif component == 'windings' or component == 'phase_windings':
        csv_set.remove(to_append + 'name')
        transformers = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                transformers.append(m.model_names[model].name)
        winding_count = component_dict['windings'].__len__()
        for transformer in transformers:
            windings = model_obj.model_names[transformer].windings
            for w_count in range(winding_count):
                if component == 'windings':
                    model_set = windings[w_count].trait_names()
                    model_set = [to_append + t for t in model_set]
                    for t in csv_set:
                        assert t in model_set
                else:
                    phase_winding_count = component_dict['phase_windings'].__len__()
                    phase_windings = windings[w_count].phase_windings
                    for p in range(phase_winding_count):
                        model_set = phase_windings[w_count].trait_names()
                        model_set = [to_append + t for t in model_set]
                        for t in csv_set:
                            assert t in model_set
    elif component == 'wires':
        csv_set.remove(to_append + 'name')
        lines = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Node':
                lines.append(m.model_names[model].name)
        lines = component_dict['lines']['Line.name']
        wire_count = component_dict['wires'].__len__()
        for line in lines:
            wires = model_obj.model_names[line].wires
            for w_count in range(wire_count):
                if component == 'windings':
                    model_set = wires[w_count].trait_names()
                    model_set = [to_append + t for t in model_set]
                    for t in csv_set:
                        assert t in model_set
    else:
        if component == 'loads':
            names = ['load_' + name for name in names]
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[-6:-2] == 'Load':
                    obj_names.append(m.model_names[model].name)
        elif component == 'nodes':
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[-6:-2] == 'Node':
                    obj_names.append(m.model_names[model].name)
        elif component == 'lines':
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[-6:-2] == 'Node':
                    obj_names.append(m.model_names[model].name)
        elif component == 'transformers':
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                    obj_names.append(m.model_names[model].name)
        for i, name in enumerate(names):
            model_set = model_obj.model_names[obj_names[i]].trait_names()
            model_set = set([to_append + t for t in model_set])
            phase_count = 0
            for t in csv_set:
                if 'phase' in t:
                    if component == 'loads':
                        assert t in model_set
                    else:
                        phase_count += 1
                else:
                    assert t in model_set
            if phase_count > 0:
                if component == 'loads':
                    pass
                else:
                    assert phase_count == len(model_obj.model_names[obj_names[0]].phases)


def verify_component_values(component_dict, model_obj, component, to_append):
    names = list(component_dict[component][to_append + 'name'])
    csv_set = get_non_empty_columns(component_dict[component])
    if (component == 'loads') or (component == 'phase_loads'):
        names = list(component_dict['loads']['Load.name'])
        obj_names = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Load':
                obj_names.append(m.model_names[model].name)
    elif component == 'nodes':
        obj_names = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Node':
                obj_names.append(m.model_names[model].name)
    elif component == 'transformers':
        obj_names = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                obj_names.append(m.model_names[model].name)
    else:
        obj_names = names
    df = component_dict[component]
    if component == 'phase_loads':
        # phase_load object lies inside load objects
        csv_set.remove(to_append + 'name')
        loads = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Load':
                loads.append(m.model_names[model].name)
        for load in loads:
            phase_loads = model_obj.model_names[load].phase_loads
            for p_count, name in enumerate(names):
                for t in csv_set:
                    in_model = getattr(phase_loads[p_count], t[len(to_append):])
                    in_csv = df[df[to_append + 'name'] == name[0:4] + '_' + name[4:] + '_' + str(p_count + 1)][t]
                    if t == 'PhaseLoad.q':
                        in_csv = in_csv.round(3)
                    if isinstance(in_model, str):
                        if len(list(in_csv)) > 0:
                            ind = in_csv.index[0]
                            assert in_csv[ind] == in_model
                            assert str(in_csv[0]) == in_model
                    elif isinstance(in_csv, bool):
                        assert float(bool(in_csv[0])) == in_model
                    elif isinstance(in_model, float):
                        in_model = round(in_model, 4)
                        assert float(in_csv) == in_model
    if component == 'wires':
        # phase_load object lies inside load objects
        csv_set.remove(to_append + 'name')
        lines = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Line':
                lines.append(m.model_names[model].name)
        for line in lines:
            wires = model_obj.model_names[line].wires
            for w_count, name in enumerate(names):
                for t in csv_set:
                    in_model = getattr(wires[w_count], t[len(to_append):])
                    in_csv = df[df[to_append + 'name'] == name][t]

                    if isinstance(in_model, str):
                        if len(list(in_csv)) > 0:
                            ind = in_csv.index[0]
                            assert in_csv[ind] == in_model
                            assert str(in_csv[0]) == in_model
                    elif isinstance(in_csv, bool):
                        assert float(bool(in_csv[0])) == in_model
                    elif isinstance(in_model, float):
                        in_model = round(in_model, 4)
                        assert float(in_csv) == in_model
                    '''elif isinstance(in_model, np.float64):
                        in_model = in_model.round(4)
                        if len(list(in_csv)>0):
                            assert float(list(in_csv)[0]) == in_model'''

    elif (component == 'windings') or (component == 'phase_windings'):
        names = list(component_dict['windings']['Winding.name'])
        # windings object lies inside transformer objects
        csv_set.remove(to_append + 'name')
        transformers = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                transformers.append(m.model_names[model].name)
        for transformer in transformers:
            windings = model_obj.model_names[transformer].windings
            for p_count, name in enumerate(names):
                if component == 'windings':
                    for t in csv_set:
                        in_model = getattr(windings[p_count], t[len(to_append):])
                        df[t] = df[t].astype(str)
                        in_csv = df[df[to_append + 'name'] == name][t]

                        if isinstance(in_model, str):
                            if len(list(in_csv)) > 0:
                                ind = in_csv.index[0]
                                assert in_csv[ind] == in_model
                        elif isinstance(in_csv, bool):
                            assert float(bool(in_csv[0])) == in_model
                        elif isinstance(in_model, float):
                            in_model = round(in_model, 4)
                            assert float(in_csv) == in_model
                else:
                    pw_names = list(component_dict[component][to_append + 'name'])
                    phase_windings = getattr(model_obj.model_names[transformer].windings[p_count], component)
                    for p, pw_name in enumerate(pw_names):
                        for t in csv_set:
                            in_model = getattr(phase_windings[p], t[len(to_append):])
                            in_csv = df[df[to_append + 'name'] == pw_name][t]

                            if isinstance(in_model, str):
                                if len(list(in_csv)) > 0:
                                    ind = in_csv.index[0]
                                    assert in_csv[ind] == in_model
                            elif isinstance(in_csv, bool):
                                assert float(bool(in_csv[0])) == in_model
                            elif isinstance(in_model, float):
                                in_model = round(in_model, 4)
                                assert float(in_csv) == in_model
    else:
        csv_set.remove(to_append + 'name')
        for name, obj_name in zip(names, obj_names):
            phase_count = 0
            for t in csv_set:
                if 'phase' in t:
                    if component == 'loads':
                        pass
                    else:
                        phase_count += 1
                else:
                    in_csv = df[df[to_append + 'name'] == name][t][0]
                    in_model = getattr(model_obj.model_names[obj_name], t[len(to_append):])

                    # handling for the list in reactance for transformers
                    if component == 'transformers':
                        if t == 'Transformer.reactances':
                            in_csv = [float(in_csv.replace('[', '').replace(']', ''))]

                    try:
                        if isinstance(in_csv, str):
                            if isinstance(in_model, list):
                                if isinstance(in_model[0], float):
                                    assert in_csv == in_model
                            else:
                                assert in_csv == in_model
                        elif isinstance(in_csv, bool):
                            assert float(in_csv) == in_model
                        else:
                            assert in_csv == in_model
                    except AssertionError as e:
                        if str(e) == 'assert 12.47 == 7200.0' or 'assert 4.16 == 2400.0':
                            raise
                            """msg = "Ignore broken Last.fm API: " + str(e)
                            print(msg)
                            pytest.skip(msg)
                        else:
                            raise (e)"""

            if phase_count > 0:
                for p_count in range(phase_count):
                    csv_phase_value = list(
                        df[df[to_append + 'name'] == name][to_append + 'phases[' + str(p_count) + ']'])
                    model_phase_value = model_obj.model_names[obj_name].phases[p_count].default_value
                    assert csv_phase_value[0] == model_phase_value



def get_unverified_properties(component_dict, model_obj, component, to_append):
    names = list(component_dict[component][to_append + 'name'])
    csv_set = get_non_empty_columns(component_dict[component])

    if component == 'phase_loads':
        # phase_load object lies inside load objects
        loads = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Load':
                loads.append(m.model_names[model].name)
        csv_set.remove(to_append + 'name')
        phase_load_count = component_dict['phase_loads'].__len__()
        for load in loads:
            phase_loads = model_obj.model_names[load].phase_loads
            for w_count in range(phase_load_count):
                model_set = phase_loads[w_count].trait_names()
                model_set = [to_append + t for t in model_set]
                mset = [attrib for attrib in model_set if attrib not in csv_set]
                assert [] == mset
                # assert (csv_set) == model_set
    elif component == 'windings' or component == 'phase_windings':
        csv_set.remove(to_append + 'name')
        transformers = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                transformers.append(m.model_names[model].name)
        winding_count = component_dict['windings'].__len__()
        for transformer in transformers:
            windings = model_obj.model_names[transformer].windings
            for w_count in range(winding_count):
                if component == 'windings':
                    model_set = windings[w_count].trait_names()
                    model_set = [to_append + t for t in model_set]
                    mset = [attrib for attrib in model_set if attrib not in csv_set]
                    assert [] == mset
                else:
                    phase_winding_count = component_dict['phase_windings'].__len__()
                    phase_windings = windings[w_count].phase_windings
                    for p in range(phase_winding_count):
                        model_set = phase_windings[w_count].trait_names()
                        model_set = [to_append + t for t in model_set]
                        mset = [attrib for attrib in model_set if attrib not in csv_set]
                        assert [] == mset
    elif component == 'wires':
        csv_set.remove(to_append + 'name')
        lines = []
        for model in m.model_names:
            if str(type(m.model_names[model]))[-6:-2] == 'Line':
                lines.append(m.model_names[model].name)
        # lines = component_dict['lines']['Line.name']
        wire_count = component_dict['wires'].__len__()
        for line in lines:
            wires = model_obj.model_names[line].wires
            for w_count in range(wire_count):
                model_set = wires[w_count].trait_names()
                model_set = [to_append + t for t in model_set]
                mset = [attrib for attrib in model_set if attrib not in csv_set]
                assert [] == mset
                # assert (csv_set) == model_set

    else:
        if component == 'loads':
            names = ['load_' + name for name in names]
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[-6:-2] == 'Load':
                    obj_names.append(m.model_names[model].name)
        elif component == 'nodes':
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[-6:-2] == 'Node':
                    obj_names.append(m.model_names[model].name)
        elif component == 'lines':
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[-6:-2] == 'Node':
                    obj_names.append(m.model_names[model].name)

        elif component == 'transformers':
            obj_names = []
            for model in m.model_names:
                if str(type(m.model_names[model]))[43:-2] == 'Transformer':
                    obj_names.append(m.model_names[model].name)
        for i in range(len(names)):  # , name in enumerate(names):
            model_set = model_obj.model_names[obj_names[i]].trait_names()
            model_set = set([to_append + t for t in model_set])
            mset = [attrib for attrib in model_set if attrib not in csv_set]
            assert [] == mset
            # assert (csv_set) == model_set
            '''phase_count = 0
            for prop in model_set:
                if 'phases' in prop:
                    if component =='nodes':
                        phase_count += 1
                        assert str(prop)+'['+str(phase_count)+']' in csv_set
                else:
                    assert prop in csv_set'''
            """phase_count = 0
            for t in csv_set:
                if 'phase' in t:
                    if component == 'loads':
                        assert t in model_set
                    else:
                        phase_count += 1
                else:
                    assert t in model_set
            if phase_count > 0:
                if component == 'loads':
                    pass
                else:
                    assert phase_count == len(model_obj.model_names[obj_names[0]].phases)
            """


files = os.listdir(data_path)
comp_dict = {}  # data dictionary
for i, file in enumerate(files):
    comp_dict[files[i][:-4]] = bs.get_csv_as_DF(data_path, file)


############################################################

# Tests for nodes:
# 1- Verify number of nodes
# 2- Verify the properties(columns) in csv
# 3- Verify node component values
# 4- Get unverified properties

############################################################


def test_verify_node():
    verify_component(comp_dict, m, 'nodes', 'Node.')


def test_verify_node_properties():
    verify_properties(comp_dict, m, 'nodes', 'Node.')


def test_comp_node_values():
    verify_component_values(comp_dict, m, 'nodes', 'Node.')


def test_unverified_node_properties():
    get_unverified_properties(comp_dict, m, 'nodes', 'Node.')


############################################################


# Tests for lines:
# 1- Verify number of lines
# 2- Verify the properties(columns) in csv
# 3- Verify line component values
# 4- Get unverified properties

############################################################

def test_verify_lines():
    verify_component(comp_dict, m, 'lines', 'Line.')


def test_verify_line_properties():
    verify_properties(comp_dict, m, 'lines', 'Line.')


def test_comp_line_values():
    verify_component_values(comp_dict, m, 'lines', 'Line.')


def test_unverified_line_properties():
    get_unverified_properties(comp_dict, m, 'lines', 'Line.')


############################################################

# Tests for loads:
# 1- Verify number of loads
# 2- Verify the properties(columns) in csv
# 3- Verify load component values
# 4- Get unverified properties

############################################################

def test_verify_loads():
    verify_component(comp_dict, m, 'loads', 'Load.')


def test_verify_load_properties():
    verify_properties(comp_dict, m, 'loads', 'Load.')


def test_comp_load_values():
    verify_component_values(comp_dict, m, 'loads', 'Load.')


def test_unverified_load_properties():
    get_unverified_properties(comp_dict, m, 'loads', 'Load.')


############################################################

# Tests for transformers:
# 1- Verify number of transformers
# 2- Verify the properties(columns) in csv
# 3- Verify transformer component values
# 4- Get unverified properties

############################################################

def test_verify_transformers():
    verify_component(comp_dict, m, 'transformers', 'Transformer.')


def test_verify_transformer_properties():
    verify_properties(comp_dict, m, 'transformers', 'Transformer.')


def test_comp_transformer_values():
    verify_component_values(comp_dict, m, 'transformers', 'Transformer.')


def test_unverified_transformer_properties():
    get_unverified_properties(comp_dict, m, 'transformers', 'Transformer.')


############################################################

# Tests for phase_loads:
# 1- Verify number of phase_loads
# 2- Verify the properties(columns) in csv
# 3- Verify phase_load component values
# 4- Get unverified properties

#############################################################

def test_verify_phase_load():
    verify_component(comp_dict, m, 'phase_loads', 'PhaseLoad.')


def test_verify_phase_load_properties():
    verify_properties(comp_dict, m, 'phase_loads', 'PhaseLoad.')


def test_comp_phase_load_values():
    verify_component_values(comp_dict, m, 'phase_loads', 'PhaseLoad.')


def test_unverified_phase_load_properties():
    get_unverified_properties(comp_dict, m, 'phase_loads', 'PhaseLoad.')


############################################################

# Tests for winding:
# 1- Verify number of winding
# 2- Verify the properties(columns) in csv
# 3- Verify winding component values
# 4- Get unverified properties

#############################################################

def test_verify_winding():
    verify_component(comp_dict, m, 'windings', 'Winding.')


def test_verify_winding_properties():
    verify_properties(comp_dict, m, 'windings', 'Winding.')


def test_comp_winding_values():
    verify_component_values(comp_dict, m, 'windings', 'Winding.')


def test_unverified_winding_properties():
    get_unverified_properties(comp_dict, m, 'windings', 'Winding.')


############################################################

# Tests for phase winding:
# 1- Verify number of phase winding
# 2- Verify the properties(columns) in csv
# 3- Verify phase winding component values
# 4- Get unverified properties

#############################################################

def test_verify_phase_winding():
    verify_component(comp_dict, m, 'phase_windings', 'PhaseWinding.')


def test_verify_phase_winding_properties():
    verify_properties(comp_dict, m, 'phase_windings', 'PhaseWinding.')


def test_comp_phase_winding_values():
    verify_component_values(comp_dict, m, 'phase_windings', 'PhaseWinding.')


def test_unverified_phase_winding_properties():
    get_unverified_properties(comp_dict, m, 'phase_windings', 'PhaseWinding.')


############################################################

# Tests for wires:
# 1- Verify number of wires
# 2- Verify the properties(columns) in csv
# 3- Verify winding component values
# 4- Get unverified properties

#############################################################

def test_verify_wire():
    verify_component(comp_dict, m, 'wires', 'Wire.')


def test_verify_wire_properties():
    verify_properties(comp_dict, m, 'wires', 'Wire.')


def test_comp_wire_values():
    verify_component_values(comp_dict, m, 'wires', 'Wire.')


def test_unverified_wire_properties():
    get_unverified_properties(comp_dict, m, 'wires', 'Wire.')
