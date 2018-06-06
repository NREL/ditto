__author__ = "Aadil Latif"
__version__ = "1.0.0"
__maintainer__ = "Aadil Latif"
__email__ = "aadil.latif@nrel.gov"

from bokeh.models import  BoxSelectTool, BoxZoomTool, PanTool, WheelZoomTool, ResetTool, SaveTool, HoverTool
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc, show
import networkx as nx
import pandas as pd
import numpy as np
import logging
import os

class WM_reader:

    def __init__(self, project_folder=None):
        self.files = {}
        self.tables = {}
        try:
            file_list = os.listdir(project_folder)
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
                elif file.lower().endswith('.stdlib'):
                    self.files['Equipment Data Headings'] = os.path.join(project_folder, file)
                elif file.lower().endswith('.seqlib'):
                    self.files['Equipment Lib Headings'] = os.path.join(project_folder, file)
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
        self.create_graph()

    def create_graph(self):
        self.library = {}
        class_id_lookup = {
            1 : 'OH lines',
            3 : 'UG lines',
            4 : 'Regulators',
            5 : 'Transformers',
            6 : 'Switches',
            8 : 'Fake Node Sections',
            9 : 'Substations',
            10: 'Fuse',
            13: 'Service Locations',
        }

        if 'Circuit Elements' in self.tables:
            Sections = self.tables['Circuit Elements']
            for id, class_name in class_id_lookup.items():
                self.library[class_name] = Sections.loc[Sections[1] == id]
            self.nxGraph = nx.DiGraph()
            self.create_element_libraries()
            self.create_fuses()
            self.create_lines()
            self.create_switches()
            self.create_transformers()
            self.create_regulators()
            self.create_substation()
            #self.create_fake_nodes()
            self.create_loads()
            self.get_base_kv()
            self.get_graph_metrics()
            self.create_plot(True)


        else:
            raise ValueError('Circuit elements file not found')

    def get_base_kv(self):
        for node1, node2 in self.nxGraph.edges():
            if 'kv' not in self.nxGraph[node1][node2]:
                self.get_edge_attribute(node1, node2, 'kv')
        for node1, node2 in self.nxGraph.edges():
            if 'kv' not in self.nxGraph[node1][node2]:
                self.nxGraph[node1][node2]['kv'] = self.nxGraph.graph['kvBase']
                self.nxGraph.node[node1]['kv'] = self.nxGraph.graph['kvBase']
                self.nxGraph.node[node2]['kv'] = self.nxGraph.graph['kvBase']


    def get_edge_attribute(self,Node1, Node2, Ppty):
        self.EdgePath = []
        Value = self.iterate_nodes(Node1, Node2, Ppty)
        #print(Node1, Node2, Value)
        if isinstance(Value, str):
            for Edge in self.EdgePath:
                self.nxGraph[Edge[0]][Edge[1]][Ppty] = Value
                self.nxGraph.node[Edge[0]]['kv'] = Value
                self.nxGraph.node[Edge[1]]['kv'] = Value
        elif isinstance(Value, list):
            for Edge in self.EdgePath:
                self.nxGraph[Edge[0]][Edge[1]][Ppty] = min(Value)
                self.nxGraph.node[Edge[0]]['kv'] = min(Value)
                self.nxGraph.node[Edge[1]]['kv'] = min(Value)
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
            1  : 'OH cables',
            2  : 'UG cables',
            5  : 'Transformer types',
            6  : 'Regulator types',
            7  : 'Load types',
            8  : 'Wire layouts',
            10 : 'Protection device types',
            11 : 'Protection extended',
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

    def create_loads(self):
        Headings = self.tables['Equipment Data Headings']['Service Locations']
        service_locations = self.library['Service Locations']
        service_locations.index = range(len(service_locations))
        service_locations.columns = list(Headings)
        #print(service_locations.T[10])

        load_data = self.tables['External Tables']
        loads = load_data[load_data['table'].isin(['Consumers', 'Light'])]
        for r, load in loads.iterrows():
            GID = load['id']
            data = service_locations[service_locations['oGID'] == GID]
            for r, ldData in data.iterrows():
                from_node = 'node_' + self.fix_string(ldData['parentID'])
                if from_node in self.nxGraph.nodes():
                    if 'loads' not in self.nxGraph.node[from_node]:
                        self.nxGraph.node[from_node]['loads'] = {}
                    self.nxGraph.node[from_node]['loads'][self.fix_string(GID)] = {
                        'type'          : load['table'],
                        'x'             : load['X'],
                        'y'             : load['Y'],
                        'Meter Number'  : load['Meter Number'],
                        'Meter Type'    : load['Meter Type'],
                        'Meter Misc'    : load['MeterMisc'],
                        'Serial Number' : load['Serial Number']
                    }
        return

    def create_fake_nodes(self):
        Headings = self.tables['Equipment Data Headings']['Fake Node Sections']
        fake_nodes = self.library['Fake Node Sections']
        fake_nodes.index = range(len(fake_nodes))
        fake_nodes.columns = list(Headings)
        for r, fake_node in fake_nodes.iterrows():
            from_node = 'node_' + self.fix_string(fake_node['parentID'])
            to_node = 'node_' + self.fix_string(fake_node['objectID'])
            reg_dict = {
                'name'        : self.fix_string(fake_node['objectID']),
                'class'       : 'fake_node',
                'phases'      : fake_node['phases'],
                'GID'         : fake_node['GID'],
                'substation'  : fake_node['substation'],
                'feeder'      : fake_node['feeder'],
                'mGID'        : fake_node['mGID'],
            }
            self.nxGraph.add_edge(from_node, to_node, reg_dict)
            self.nxGraph.node[to_node] = {
                'x' : fake_node['x1'],
                'y' : fake_node['y1'],
            }

    def create_substation(self):
        Headings = self.tables['Equipment Data Headings']['Substations']
        substations = self.library['Substations']
        substations.index = range(len(substations))
        substations.columns = list(Headings)
        for r, substation in substations.iterrows():
            from_node = 'node_' + self.fix_string(substation['parentID'])
            to_node = 'node_' + self.fix_string(substation['objectID'])
            reg_dict = {
                'name'        : self.fix_string(substation['objectID']),
                'class'       : 'substation',
                'phases'      : substation['phases'],
                'upu'         : substation['upu'],
                'kv'          : substation['kv'],
                'ohGndZ'      : substation['ohGndZ'],
                'ugGndZ'      : substation['ugGndZ'],
                'GID'         : substation['GID'],
                'substation'  : substation['substation'],
                'feeder'      : substation['feeder'],
                'mGID'        : substation['mGID'],
            }
            self.nxGraph.graph['kvBase'] = reg_dict['kv']
            self.nxGraph.add_edge(from_node, to_node, reg_dict)
            self.nxGraph.node[to_node] = {
                'x': substation['x1'],
                'y': substation['y1'],
            }

        return

    def create_regulators(self):
        Headings = self.tables['Equipment Data Headings']['Regulators']
        regs = self.library['Regulators']
        regs.index = range(len(regs))
        regs.columns = list(Headings)
        for r, reg in regs.iterrows():
            from_node = 'node_' + self.fix_string(reg['parentID'])
            to_node = 'node_' + self.fix_string(reg['objectID'])
            reg_dict = {
                'name'        : self.fix_string(reg['objectID']),
                'class'       : 'regulator',
                'phases'      : reg['phases'],
                'facility'    : reg['facility'],
                'u'           : [reg['uoutA'], reg['uoutB'], reg['uoutC']],
                'equipment'   : [reg['equipA'], reg['equipB'], reg['equipC']],
                'fhHi'        : [reg['fhHiA'], reg['fhHiB'], reg['fhHiC']],
                'GID'         : reg['GID'],
                'substation'  : reg['substation'],
                'feeder'      : reg['feeder'],
                'mGID'        : reg['mGID'],
            }

            self.nxGraph.add_edge(from_node, to_node, reg_dict)
            self.nxGraph.node[to_node] = {
                'x': reg['x1'],
                'y': reg['y1'],
            }

    def create_transformers(self):
        Headings = self.tables['Equipment Data Headings']['Transformers']
        xfmrs = self.library['Transformers']
        xfmrs.index = range(len(xfmrs))
        xfmrs.columns = list(Headings)
        for r, xfmr in xfmrs.iterrows():
            from_node = 'node_' + self.fix_string(xfmr['parentID'])
            to_node = 'node_' + self.fix_string(xfmr['objectID'])
            fuse_dict = {
                'name'        : self.fix_string(xfmr['objectID']),
                'class'       : 'transformer',
                'phases'      : xfmr['phases'],
                'kv'          : [xfmr['uh'],  xfmr['ul']],
                'sphases'     : xfmr['sphases'],
                'unom'        : xfmr['unom'],
                'kva'         : [xfmr['kvaA'],xfmr['kvaB'],xfmr['kvaC']],
                'equipment'   : [xfmr['equipA'], xfmr['equipB'], xfmr['equipC']],
                'data'        : [xfmr['A'],xfmr['B'],xfmr['C']],
                'GID'         : xfmr['GID'],
                'substation'  : xfmr['substation'],
                'feeder'      : xfmr['feeder'],
                'mGID'        : xfmr['mGID'],
            }
            self.nxGraph.add_edge(from_node, to_node, fuse_dict)
            self.nxGraph.node[to_node] = {
                'x': xfmr['x1'],
                'y': xfmr['y1'],
            }

    def create_fuses(self):
        Headings = self.tables['Equipment Data Headings']['Fuse']
        fuses = self.library['Fuse']
        fuses.index = range(len(fuses))
        fuses.columns = list(Headings)
        for r, fuse in fuses.iterrows():
            from_node = 'node_' + self.fix_string(fuse['parentID'])
            to_node = 'node_' + self.fix_string(fuse['objectID'])
            fuse_dict = {
                'name'        : self.fix_string(fuse['objectID']),
                'class'       : 'fuse',
                'phases'      : fuse['phases'],
                'unknown1'    : fuse['unknown1'],
                'unknown2'    : fuse['unknown2'],
                'equipment'   : [fuse['equipA'], fuse['equipB'], fuse['equipC']],
                'facility'    : fuse['facility'],
                'GID'         : fuse['GID'],
                'substation'  : fuse['substation'],
                'feeder'      : fuse['feeder'],
                'mGID'        : fuse['mGID'],
            }
            self.nxGraph.add_edge(from_node, to_node, fuse_dict)
            self.nxGraph.node[to_node] = {
                'x': fuse['x1'],
                'y': fuse['y1'],
            }

    def create_switches(self):
        Headings = self.tables['Equipment Data Headings']['Switches']
        switches = self.library['Switches']
        switches.index = range(len(switches))
        switches.columns = list(Headings)
        for r, switch in switches.iterrows():
            from_node = 'node_' + self.fix_string(switch['parentID'])
            to_node = 'node_' + self.fix_string(switch['objectID'])
            switch_dict = {
                'name'        : self.fix_string(switch['objectID']),
                'class'       : 'switch',
                'phases'      : switch['phases'],
                'state'       : switch['state'],
                'partner'     : switch['partnerID'],
                'GID'         : switch['GID'],
                'substation'  : switch['substation'],
                'feeder'      : switch['feeder'],
                'mGID'        : switch['mGID'],
            }
            self.nxGraph.add_edge(from_node, to_node, switch_dict)
            self.nxGraph.node[to_node] = {
                'x': switch['x1'],
                'y': switch['y1'],
            }

    def create_lines(self):
        Headings = self.tables['Equipment Data Headings']['Line']
        line_tables = [self.library['OH lines'], self.library['UG lines']]
        for line_id, line_database in enumerate(line_tables):
            line_database.index = range(len(line_database))
            line_database.columns = list(Headings)
            if line_id == 0:
                line_type = 'overhead'
            else:
                line_type = 'underground'
            for r, line in line_database.iterrows():
                from_node = 'node_' + self.fix_string(line['parentID'])
                to_node   = 'node_' + self.fix_string(line['objectID'])
                line_properties = {
                    'type'        : line_type,
                    'name'        : self.fix_string(line['objectID']),
                    'class'       : 'line',
                    'phases'      : line['phases'],
                    'grade'       : line['grade'],
                    'length'      : line['length'],
                    'GID'         : line['GID'],
                    'substation'  : line['substation'],
                    'feeder'      : line['feeder'],
                    'mGID'        : line['mGID'],
                }

                line_properties['wires'] = {}
                if 'A' in line_properties['phases']:
                    line_properties['wires']['A'] = line['condA']
                if 'B' in line_properties['phases']:
                    line_properties['wires']['B'] = line['condB']
                if 'C' in line_properties['phases']:
                    line_properties['wires']['C'] = line['condC']
                line_properties['wires']['N'] = '' if isinstance(line['condN'], float) else line['condN']
                self.nxGraph.add_edge(from_node, to_node, line_properties)
                self.nxGraph.node[to_node] = {
                    'x': line['x1'],
                    'y': line['y1'],
                }

    def fix_string(self, String):
        BannedChrs = [' ', '.', '{', '}']
        for Chr in BannedChrs:
            String = String.replace(Chr, '_')
        return String.lower()

#a = Reader(r'C:\Users\alatif\Desktop\Test Exports\Angel Fire')

