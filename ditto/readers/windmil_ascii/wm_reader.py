__author__ = "Aadil Latif"
__version__ = "1.0.0"
__maintainer__ = "Aadil Latif"
__email__ = "aadil.latif@nrel.gov"

from bokeh.models import  BoxSelectTool, BoxZoomTool, PanTool, WheelZoomTool, ResetTool, SaveTool, HoverTool
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc, show

from ditto.readers.windmil_ascii.wm_lookup_tables import *
import networkx as nx
import pandas as pd
import numpy as np
import logging
import os

class wm2graph:

    def __init__(self, project_folder=None):
        self.files = {}
        self.tables = {}
        try:
            file_list = os.listdir(project_folder)
            #print(file_list)
            for file in file_list:
                if file.lower().endswith('.asm'):
                    self.files['Assemblies'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.cld'):
                    self.files['Archieved Load'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.lcp'):
                    self.files['Load Control Points'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.sld'):
                    self.files['Billing Load Data'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.csv'):
                    self.files['External Tables'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.seq'):
                    self.files['Equipment Data'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.std'):
                    self.files['Circuit Elements'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.rsl'):
                    self.files['Results'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.gps'):
                    self.files['Structure Locations'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.mpt'):
                    self.files['Map Points'] = os.path.join(project_folder, file)
            if len(self.files) == 0:
                raise ValueError('Folder path "{}" does not contain project files'.format(project_folder))
        except:
            raise ValueError('Folder path "{}" does not exist '.format(project_folder))

        no_header = ['Map Points', 'Archieved Load', 'Billing Load Data', 'Equipment Data', 'Circuit Elements']
        skip_line = ['Circuit Elements', 'Equipment Data']
        for table_name, table_path in self.files.items():
            logging.info('Reading table: .{}'.format(table_path))
            if table_name in skip_line:
                skiplines = 1
            else:
                skiplines = 0
            if table_name in no_header:
                table_header = None
            else:
                table_header = 0
            try:
                self.tables[table_name] = pd.read_csv(table_path, skiprows=skiplines, header=table_header, low_memory=False)
            except:
                logging.warning('File at ".{}" was not read correctly.'.format(table_path))
        self.tables['Equipment Data Headings'] = pd.DataFrame(std_file_headings)
        self.tables['Equipment Lib Headings'] = pd.DataFrame(seq_file_headings)
        self.create_graph()

    def create_graph(self):
        self.library = {}
        class_id_lookup = {
            1  : 'Overhead Line',
            2  : 'Capacitor',
            3  : 'Underground Line',
            4  : 'Regulator',
            5  : 'Transformer',
            6  : 'Switch',
            8  : 'Node',
            9  : 'Source',
            10 : 'Overcurrent Device',
            11 : 'Motor',
            12 : 'Generator',
            13 : 'Consumer',
        }

        if 'Circuit Elements' in self.tables:
            Sections = self.tables['Circuit Elements']
            for id, class_name in class_id_lookup.items():
                self.library[class_name] = Sections.loc[Sections[1] == id]
            self.nxGraph = nx.DiGraph()
            self.create_element_libraries()
            self.create_devices()
            self.create_lines()
            self.create_switches()
            self.create_transformers()
            self.create_regulators()
            self.create_substation()
            self.create_nodes()
            self.create_loads()
            self.create_capacitors()
            #self.create_generators()
            #self.create_motors()
            self.get_base_kv()
            self.get_graph_metrics()
            self.create_plot(True)
        else:
            raise ValueError('Circuit elements file not found')

    def get_base_kv(self):
        for node1, node2 in self.nxGraph.edges():
            if 'kv' not in self.nxGraph[node1][node2]:
                self.get_edge_attribute(node1, node2, 'kv')

    def get_edge_attribute(self,Node1, Node2, Ppty):
        self.EdgePath = []
        Value = self.iterate_nodes(Node1, Node2, Ppty)
        for Edge in self.EdgePath:
            self.nxGraph[Edge[0]][Edge[1]][Ppty] = Value
        return

    def iterate_nodes(self, Node1, Node2, Ppty):
        self.EdgePath.append([Node1, Node2])
        if Ppty not in self.nxGraph[Node1][Node2]:
            inEdge = self.nxGraph.in_edges([Node1])
            if inEdge:
                inEdgeNodes = list(inEdge[0])
                return self.iterate_nodes(inEdgeNodes[0], inEdgeNodes[1], Ppty)
        else:
            return self.nxGraph[Node1][Node2][Ppty]

    def create_element_libraries(self):
        class_id_lookup = {
            1  : 'Overhead Conductor',
            2  : 'Underground Conductor',
            3  : 'Zsm Conductor',
            4  : 'Zabc Conductor',
            5  : 'Transformer',
            6  : 'Regulator',
            7  : 'Load Mix',
            8  : 'Construction Code',
            9  : 'Load Zone',
            10 : 'Device',
            11 : 'Protected Device',
            12 : 'Assemblies',
            13 : 'Switchgear',
        }
        element_type_library = {}
        if 'Equipment Data' in self.tables:
            element_type_data = self.tables['Equipment Data']
            for id, class_name in class_id_lookup.items():
                Headings = self.tables['Equipment Lib Headings'][class_name]
                element_type_library[class_name] = element_type_data.loc[element_type_data[1] == id]
                element_type_library[class_name].columns = Headings.tolist()
            self.nxGraph.graph = element_type_library
        else:
            raise ValueError('Circuit element types file not found')
        return element_type_library

    def get_class_type_locations(self, class_name):
        relevant_edges = ((u, v) for u, v, d in self.nxGraph.edges(data=True) if d['class'] == class_name)
        Xs=[]
        Ys=[]
        for edge in relevant_edges:
            node1, node2 = edge
            x = self.nxGraph.node[node2]['x']
            y = self.nxGraph.node[node2]['y']
            if None not in [x, y]:
                Xs.append(x)
                Ys.append(y)
        return Xs, Ys

    def create_plot(self, updateCoordinates):
        load_x = []
        load_y = []
        load_lines_xs = []
        load_lines_ys = []
        if updateCoordinates:
            edges = [list(x) for x in self.nxGraph.edges()]

            self.plotdata = {
                'Xs': [],
                'Ys': [],
            }
            for edge in edges:
                node1, node2 = edge
                if 'x' in self.nxGraph.node[node1] and 'x' in self.nxGraph.node[node2]:
                    x1 = self.nxGraph.node[node1]['x']
                    y1 = self.nxGraph.node[node1]['y']
                    x2 = self.nxGraph.node[node2]['x']
                    y2 = self.nxGraph.node[node2]['y']
                    if None not in [x1, x2, y1, y2]:
                        self.plotdata['Xs'].append([x1, x2])
                        self.plotdata['Ys'].append([y1, y2])

                for node in [node1, node2]:
                    if 'loads' in self.nxGraph.node[node]:
                        for load_name, load_properties in self.nxGraph.node[node]['loads'].items():
                            if 'x' in self.nxGraph.node[node] and self.nxGraph.node[node]:
                                x1 = self.nxGraph.node[node]['x']
                                y1 = self.nxGraph.node[node]['y']
                                x2 = load_properties['x']
                                y2 = load_properties['y']
                                dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                                if 0 not in [x1, x2, y1, y2] and dist < 500:
                                    load_x.append(x2)
                                    load_y.append(y2)
                                    load_lines_xs.append([x1, x2])
                                    load_lines_ys.append([y1, y2])

        Linesource = ColumnDataSource(self.plotdata)
        plot = figure(title=None, plot_width=900, plot_height=900,
                      tools=[ResetTool(), BoxSelectTool(), SaveTool(), BoxZoomTool(), WheelZoomTool(),
                             PanTool()])

        # plot edges (lines, fuses, switches, transformers, regulators)
        plot.multi_line(xs="Xs", ys="Ys", source=Linesource, line_width=2, legend='Edges', line_color='#00008B') # , line_color=ColorBy
        # plot loads
        plot.triangle(x=load_x, y=load_y, legend='Loads', color='orange')
        # plot substation
        Xs, Ys = self.get_class_type_locations('substation')
        plot.circle_x(x=Xs, y=Ys, size=14, legend='Substation', fill_color='red', line_color='black')
        Xs, Ys = self.get_class_type_locations('regulator')
        plot.hex(x=Xs, y=Ys, size=14, legend='Regulators', fill_color='lightgreen', line_color='black')
        plot.multi_line(xs=load_lines_xs, ys=load_lines_ys, line_width=2, legend='Drop lines', line_color='black')

        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        curdoc().add_root(plot)

        show(plot)
        return

    def get_graph_metrics(self):
        nxGraph = self.nxGraph.to_undirected()
        islands = list(nx.connected_component_subgraphs(nxGraph))
        print('Number of islands: ', len(islands))
        loops = nx.cycle_basis(nxGraph)
        print('Number of loops: ', len(loops))
        print('')
        for i, eachCycle in enumerate(loops):
            print('Loop ' + str(i) + ' : starts with node "' + eachCycle[0] + '"')

    def create_generators(self):
        Headings = self.tables['Equipment Data Headings']['Generator']
        generators = self.library['Generator']
        generators.index = range(len(generators))
        generators.columns = list(Headings)
        for r, generator in generators.iterrows():
            from_node = 'node_' + self.fix_string(generator['Parent Element Name'])
            #to_node = 'node_' + self.fix_string(load['Element Name'])
            if from_node in self.nxGraph.nodes():
                if 'capacitors' not in self.nxGraph.node[from_node]:
                    self.nxGraph.node[from_node]['capacitors'] = {}
                self.nxGraph.node[from_node]['capacitors'][self.fix_string(generator['Element Name'])] = {
                    'name'          : self.fix_string(generator['Element Name']),
                    'x'             : generator['X Coordinate'],
                    'y'             : generator['Y Coordinate'],

                    'model'         : generator_model[int(generator['Model'])],
                    'Vfix'          : generator['Voltage to Hold'],
                    'kvRated'            : generator['Rated Voltage'],
                    'load location' : generator['Load Location'],
                    'load mix'      : generator['Load Mix Description'],
                    'load zone'     : generator['Load Zone Description'],
                    'load growth'   : generator['Load Growth'],
                    'kw'            : [generator['Allocated kW (Ph A)'],
                                       generator['Allocated kW (Ph B)'],
                                       generator['Allocated kW (Ph C)']],
                    'kvar'          : [generator['Allocated kvar (Ph A)'],
                                       generator['Allocated kvar (Ph B)'],
                                       generator['Allocated kvar (Ph C)']],
                    'consumers'     : [generator['Allocated Consumers (Ph A)'],
                                       generator['Allocated Consumers (Ph B)'],
                                       generator['Allocated Consumers (Ph C)']],
                    'kwOut'         : generator['kW Out'],
                    'kwOut max'     : generator['Maximum kW Out'],
                    'kvar max lead' : generator['Maximum kvar Lead Output'],
                    'kvar max lag'  : generator['Maximum kvar Lagg Output'],
                    'conn'          : generator_conn[int(generator['Wye or Delta Connection'])],
                    'failure rate'  : generator['Failure Rate'],
                    'repair Time'   : generator['Repair Time'],
                }
        return

    def create_capacitors(self):
        Headings = self.tables['Equipment Data Headings']['Capacitor']
        capacitors = self.library['Capacitor']
        capacitors.index = range(len(capacitors))
        capacitors.columns = list(Headings)
        for r, capacitor in capacitors.iterrows():
            print(capacitor)
            from_node = 'node_' + self.fix_string(capacitor['Parent Element Name'])
            #to_node = 'node_' + self.fix_string(load['Element Name'])
            if from_node in self.nxGraph.nodes():
                if 'capacitors' not in self.nxGraph.node[from_node]:
                    self.nxGraph.node[from_node]['capacitors'] = {}
                self.nxGraph.node[from_node]['capacitors'][self.fix_string(capacitor['Element Name'])] = {
                    'name'          : self.fix_string(capacitor['Element Name']),
                    'phases'        :capacitor['Phase Configuration'],
                    'x'             : capacitor['X Coordinate'],
                    'y'             : capacitor['Y Coordinate'],
                    'On Setting'    : capacitor['Switch On Setting'],
                    'Off Setting'   : capacitor['Switch Off Setting'],
                    'state'         : capacitor_state[int(capacitor['Switch Status Code'])],
                    'reg mode'      : capacitor_control_type[int(capacitor['Switch Type Code'])],
                    'kvRated'       : capacitor['Voltage Rating'],
                    'kvar'          : [capacitor['kvar, Phase A'],
                                       capacitor['kvar, Phase B'],
                                       capacitor['kvar, Phase C']],
                    'Ctrl Element'  : capacitor['Control Element'],
                    'conn'          : capacitor_conn[capacitor['Connection']],
                    'kvarRated'     : capacitor['Unit Size kvar'],
                    'control phase' : capacitor['Control Phase'],
                    'failure rate'  : capacitor['Failure Rate'],
                    'repair Time'   : capacitor['Repair Time'],
                    'bypass Time'   : capacitor['Bypass Time'],
                }
        return

    def create_loads(self):
        Headings = self.tables['Equipment Data Headings']['Consumer']
        service_locations = self.library['Consumer']
        service_locations.index = range(len(service_locations))
        service_locations.columns = list(Headings)
        for r, load in service_locations.iterrows():
            from_node = 'node_' + self.fix_string(load['Parent Element Name'])
            to_node = 'node_' + self.fix_string(load['Element Name'])
            if from_node in self.nxGraph.nodes():
                if 'loads' not in self.nxGraph.node[from_node]:
                    self.nxGraph.node[from_node]['loads'] = {}
                self.nxGraph.node[from_node]['loads'][self.fix_string(load['Element Name'])] = {
                    'name'          : self.fix_string(load['Element Name']),
                    'type'          : customer_types[load['Consumer Type']],
                    'phases'        : load['Phase Configuration'],
                    'x'             : load['X Coordinate'],
                    'y'             : load['Y Coordinate'],
                    'load mix'      : load['Load Mix Description'],
                    'load zone'     : load['Load Zone Description'],
                    'load growth'   : load['Load Growth'],
                    'billing code'  : load['Billing Code'],
                    'kw'            : [load['Allocated kW (Ph A)'],
                                       load['Allocated kW (Ph B)'],
                                       load['Allocated kW (Ph C)']],
                    'kvar'          : [load['Allocated kvar (Ph A)'],
                                       load['Allocated kvar (Ph B)'],
                                       load['Allocated kvar (Ph C)']],
                    'consumers'     : [load['Allocated Consumers (Ph A)'],
                                       load['Allocated Consumers (Ph B)'],
                                       load['Allocated Consumers (Ph C)']],
                    'isInteruptable': load['Load Interruptible Type'],
                    'enabled'       : load['Is Consumer Active 0=Inactive, 1=Active'],
                    'meter number'  : load['Meter Number']

                }
        return

    def create_nodes(self):
        Headings = self.tables['Equipment Data Headings']['Node']
        nodes = self.library['Node']
        nodes.index = range(len(nodes))
        nodes.columns = list(Headings)
        for r, node in nodes.iterrows():
            from_node = 'node_' + self.fix_string(node['Parent Element Name'])
            to_node = 'node_' + self.fix_string(node['Element Name'])
            reg_dict = {
                'name'         : self.fix_string(node['Element Name']),
                'class'        : 'node',
                'phases'       : node['Phase Configuration'],
                'Load zone'    : node['Load Zone Description'],
                'Load ctrl pt' : node['Load Allocation Control Point'],
                'Load mix'     : node['Load Mix Description'],
                'Load loc'     : node['Load Zone Description'],
                'Load growth'  : node['Load Growth'],
                'Billing ref'  : node['Billing Reference'],
                'kw'           : [node['Allocated kW, Phase A'],
                                  node['Allocated kW, Phase B'],
                                  node['Allocated kW, Phase C']],
                'kvar'         : [node['Allocated kvar, Phase A'],
                                  node['Allocated kvar, Phase B'],
                                  node['Allocated kvar, Phase C']],
                'consumers'    : [node['Allocated Consumers, Ph A'],
                                  node['Allocated Consumers, Ph B'],
                                  node['Allocated Consumers, Ph C']],
                'parents'      : [node['A Phase Parent'],
                                  node['B Phase Parent'],
                                  node['C Phase Parent']],
                'isMandatory'  :  node['Node Is Mandatory'],
                'enabled'      : [node['Phase A Energized'],
                                  node['Phase B Energized'],
                                  node['Phase C Energized']],
                'GID'          : node['GUID'],
                'substation'   : node['Substation Name'],
                'feeder'       : node['Feeder Name'],
                'mGID'         : node['mGUID'],
            }
            self.nxGraph.add_edge(from_node, to_node, reg_dict)
            self.nxGraph.node[to_node] = {
                'x': node['X Coordinate'],
                'y': node['Y Coordinate'],
            }

    def create_substation(self):
        Headings = self.tables['Equipment Data Headings']['Source']
        substations = self.library['Source']
        substations.index = range(len(substations))
        substations.columns = list(Headings)
        for r, substation in substations.iterrows():
            from_node = 'node_' + self.fix_string(substation['Parent Element Name'])
            to_node = 'node_' + self.fix_string(substation['Element Name'])
            reg_dict = {
                'name'         : self.fix_string(substation['Element Name']),
                'class'        : 'substation',
                'phases'       : substation['Phase Configuration'],
                'conn'         : substation['Wye or Delta Connection Code'],
                'Vpu'          : substation['Bus Voltage'],
                'kv'           : substation['Nominal Voltage'],
                'ohGndZ'       : substation['OH Ground Ohms for Min Fault'],
                'ugGndZ'       : substation['UG Ground Ohms for Min Fault'],
                'Zsm min'      : substation['Zsm Impedance Desc Minimum'],
                'Zsm max'      : substation['Zsm Impedance Desc Minimum'],
                'reg code'     : substation['Regulation Code'],
                'load alloc pt': substation['Load Allocation Control Point'],
                'enabled'      : [substation['Phase A Energized'],
                                  substation['Phase B Energized'],
                                  substation['Phase C Energized']],
                'GID'          : substation['GUID'],
                'substation'   : substation['Substation Name'],
                'feeder'       : substation['Feeder Name'],
                'mGID'         : substation['mGUID'],
            }
            self.nxGraph.graph['kvBase'] = reg_dict['kv']
            self.nxGraph.add_edge(from_node, to_node, reg_dict)
            self.nxGraph.node[to_node] = {
                'x': substation['X Coordinate'],
                'y': substation['Y Coordinate'],
            }

        return

    def create_regulators(self):
        Headings = self.tables['Equipment Data Headings']['Regulator']
        regs = self.library['Regulator']
        regs.index = range(len(regs))
        regs.columns = list(Headings)
        for r, reg in regs.iterrows():
            from_node = 'node_' + self.fix_string(reg['Parent Element Name'])
            to_node = 'node_' + self.fix_string(reg['Element Name'])
            reg_dict = {
                'name'        : self.fix_string(reg['Element Name']),
                'class'       : 'regulator',
                'phases'      : reg['Phase Configuration'],
                'reg type'    : reg['Regulator Type'],
                'conn'        : xfmr_conn[int(reg['Regulator Winding Connection'])],
                'contrl ph'   : reg['Controlling Phase'],
                'equipment'   : [reg['Regulator Description, Phase A'],
                                 reg['Regulator Description, Phase B'],
                                 reg['Regulator Description, Phase C']],
                'Vpu'         : [reg['Output Voltage, Phase A'],
                                 reg['Output Voltage, Phase B'],
                                 reg['Output Voltage, Phase C']],
                'LDCr'        : [reg['LDC R Setting, Phase A'],
                                 reg['LDC R Setting, Phase B'],
                                 reg['LDC R Setting, Phase C']],
                'LDCx'        : [reg['LDC X Setting, Phase A'],
                                 reg['LDC X Setting, Phase B'],
                                 reg['LDC X Setting, Phase C']],
                'fhhp'        : [reg['House High Protector, Ph A'],
                                 reg['1st House High Protector, Ph B'],
                                 reg['1st House High Protector, Ph C']],
                'fhlp'        : [reg['1st House Low Protector, Ph A'],
                                 reg['1st House Low Protector, Ph A'],
                                 reg['1st House Low Protector, Ph A']],
                'enabled'     : [reg['Phase A Energized'],
                                 reg['Phase B Energized'],
                                 reg['Phase C Energized']],
                'failure rate' : reg['Failure Rate'],
                'repair Time'  : reg['Repair Time'],
                'bypass Time'  : reg['Bypass Time'],
                'GID'          : reg['GUID'],
                'substation'   : reg['Substation Name'],
                'feeder'       : reg['Feeder Name'],
                'mGID'         : reg['mGUID'],
            }

            self.nxGraph.add_edge(from_node, to_node, reg_dict)
            self.nxGraph.node[to_node] = {
                'x': reg['X Coordinate'],
                'y': reg['Y Coordinate'],
            }

    def create_transformers(self):
        Headings = self.tables['Equipment Data Headings']['Transformer']
        xfmrs = self.library['Transformer']
        xfmrs.index = range(len(xfmrs))
        xfmrs.columns = list(Headings)
        for r, xfmr in xfmrs.iterrows():
            from_node = 'node_' + self.fix_string(xfmr['Parent Element Name'])
            to_node = 'node_' + self.fix_string(xfmr['Element Name'])
            fuse_dict = {
                'name'             : self.fix_string(xfmr['Element Name']),
                'class'            : 'transformer',
                'phases'           : xfmr['Phase Configuration'],
                'conn'             : xfmr_conn[int(xfmr['Transformer Winding Connection'])],
                'kv'               : [xfmr['Rated Input Voltage (Src Side)'],
                                      xfmr['Rated Output Voltage (Load Side)'],
                                      xfmr['Rated Tertiary Output Voltage']],
                'kvIn'             : xfmr['Rated Input Voltage (Src Side)'],
                'kvOut'            : xfmr['Rated Output Voltage (Load Side)'],
                'kvTer'            : xfmr['Rated Tertiary Output Voltage'],
                'mounting'         : xfmr_mounting[int(xfmr['Transformer Mounting'])],
                'hasTertiary'      : xfmr['Tertiary Child Identifier'],
                'unom'             : xfmr['Nominal Output Voltage In kV.'],
                'kva'              : [xfmr['Tran kVA A'],
                                      xfmr['Tran kVA B'],
                                      xfmr['Tran kVA C']],
                'regulators'       : [xfmr['Xfmr Cond Desc. Ph A'],
                                      xfmr['Xfmr Cond Desc. Ph B'],
                                      xfmr['Xfmr Cond Desc. Ph C']],

                'equipment'        : [xfmr['Xfmr Cond Desc. Ph A'],
                                      xfmr['Xfmr Cond Desc. Ph B'],
                                      xfmr['Xfmr Cond Desc. Ph C']],
                'is center tapped' : xfmr['Is Center Tap'],
                'GID'              : xfmr['GUID'],
                'substation'       : xfmr['Substation Name'],
                'feeder'           : xfmr['Feeder Name'],
                'mGID'             : xfmr['mGUID'],
            }
            self.nxGraph.add_edge(from_node, to_node, fuse_dict)

            self.nxGraph.node[to_node] = {
                'x': xfmr['X Coordinate'],
                'y': xfmr['Y Coordinate'],
            }

    def create_devices(self):
        Headings = self.tables['Equipment Data Headings']['Overcurrent Device']
        fuses = self.library['Overcurrent Device']
        fuses.index = range(len(fuses))
        fuses.columns = list(Headings)
        for r, fuse in fuses.iterrows():
            from_node = 'node_' + self.fix_string(fuse['Parent Element Name'])
            to_node = 'node_' + self.fix_string(fuse['Element Name'])
            fuse_dict = {
                'name'         : self.fix_string(fuse['Element Name']),
                'class'        : 'device',
                'phases'       : fuse['Phase Configuration'],
                'Control point': fuse['Load Allocation Control Point'],
                'equipment'    : [fuse['Description, Ph A'],
                                  fuse['Description, Ph B'],
                                  fuse['Description, Ph C']],
                'isClosed'     : [fuse['Is Closed, Phase A'],
                                  fuse['Is Closed, Phase B'],
                                  fuse['Is Closed, Phase C']],
                'isFeederBay'  : fuse['Is Feeder Bay'],
                'failure rate' : fuse['Failure Rate'],
                'repair Time'  : fuse['Repair Time'],
                'bypass Time'  : fuse['Bypass Time'],
                'close Time'   : fuse['Close Time'],
                'open Time'    : fuse['Open Time'],
                'Operation'    : fault_coord_type[int(fuse['Fuse Coordination Method'])],
                'enabled'      : [fuse['Phase A Energized'],
                                  fuse['Phase B Energized'],
                                  fuse['Phase C Energized']],
                'GID'          : fuse['GUID'],
                'substation'   : fuse['Substation Name'],
                'feeder'       : fuse['Feeder Name'],
                'mGID'         : fuse['mGUID'],
            }
            self.nxGraph.add_edge(from_node, to_node, fuse_dict)
            self.nxGraph.node[to_node] = {
                'x': fuse['X Coordinate'],
                'y': fuse['Y Coordinate'],
            }

    def create_switches(self):
        Headings = self.tables['Equipment Data Headings']['Switch']
        switches = self.library['Switch']
        switches.index = range(len(switches))
        switches.columns = list(Headings)
        for r, switch in switches.iterrows():
            from_node = 'node_' + self.fix_string(switch['Parent Element Name'])
            to_node = 'node_' + self.fix_string(switch['Element Name'])
            switch_dict = {
                'name'         : self.fix_string(switch['Element Name']),
                'class'        : 'switch',
                'phases'       : switch['Phase Configuration'],
                'failure rate' : switch['Failure Rate'],
                'repair Time'  : switch['Repair Time'],
                'bypass Time'  : switch['Bypass Time In Hours'],
                'close Time'   : switch['Close Time In Hours'],
                'open Time'    : switch['Open Time In Hours'],
                'state'        : switch['Switch Status'],
                'partner'      : switch['ptnrGUID'],
                'enabled'      : [switch['Phase A Energized'],
                                  switch['Phase B Energized'],
                                  switch['Phase C Energized']],
                'GID'          : switch['GUID'],
                'substation'   : switch['Substation Name'],
                'feeder'       : switch['Feeder Name'],
                'mGID'         : switch['mGUID'],
            }
            self.nxGraph.add_edge(from_node, to_node, switch_dict)
            self.nxGraph.node[to_node] = {
                'x': switch['X Coordinate'],
                'y': switch['Y Coordinate'],
            }

    def create_lines(self):
        Headings = self.tables['Equipment Data Headings']['Line']
        line_tables = [self.library['Overhead Line'], self.library['Underground Line']]
        for line_id, line_database in enumerate(line_tables):
            line_database.index = range(len(line_database))
            line_database.columns = list(Headings)
            if line_id == 0:
                line_type = 'overhead'
            else:
                line_type = 'underground'
            for r, line in line_database.iterrows():
                from_node = 'node_' + self.fix_string(line['Parent Element Name'])
                to_node   = 'node_' + self.fix_string(line['Element Name'])
                line_properties = {
                    'type'        : line_type,
                    'name'        : self.fix_string(line['Element Name']),
                    'class'       : 'line',
                    'phases'      : line['Phase Configuration'],
                    'conductors'  : [line['Conductor Phase A'],
                                     line['Conductor Phase B'],
                                     line['Conductor Phase C'],
                                     line['Conductor neutral']],
                    'enabled'     : [line['Phase A Energized'],
                                     line['Phase B Energized'],
                                     line['Phase C Energized']],
                    'nNeutrals'   : line['Number of Neutrals'],
                    'imp length'  : line['Impedance Length'],
                    'length'      : line['Conductor Graphical Length'],
                    'GID'         : line['GUID'],
                    'substation'  : line['Substation Name'],
                    'feeder'      : line['Feeder Name'],
                    'mGID'        : line['mGUID'],

                }

                self.nxGraph.add_edge(from_node, to_node, line_properties)
                self.nxGraph.node[to_node] = {
                    'x': line['X Coordinate'],
                    'y': line['Y Coordinate'],
                }

    def fix_string(self, String):
        BannedChrs = [' ', '.', '{', '}']
        for Chr in BannedChrs:
            String = String.replace(Chr, '_')
        return String.lower()