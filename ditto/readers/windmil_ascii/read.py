# -*- coding: utf-8 -*-
import numpy as np
import logging

from ditto.readers.abstract_reader import AbstractReader

from ditto.models.regulator import Regulator
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.wire import Wire
from ditto.models.load import Load
from ditto.models.capacitor import Capacitor
from ditto.models.phase_load import PhaseLoad
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.position import Position
from ditto.readers.windmil_ascii.wm_reader import wm2graph
from ditto.models.power_source import PowerSource

logger = logging.getLogger(__name__)

from traitlets import Unicode


class Reader(AbstractReader):
    """
        Author: Aadil Latif
        TODO: Add reader details here
    """

    register_names = ["windmil", "Windmil", "WM", "wm"]

    def __init__(self, **kwargs):
        """
            Windmil-->class constructor
        """
        super(Reader, self).__init__(**kwargs)
        self.windmil_folder = (
            r"C:\Users\alatif\Desktop\DiTTo\ditto\readers\windmil_ascii\Network"
        )

        if "network_folder" in kwargs:
            self.windmil_folder = kwargs["network_folder"]

    def filter_edges_by_class(self, class_name):
        relevant_edges = (
            (u, v)
            for u, v, d in self.nxGraph.edges(data=True)
            if d["class"] == class_name
        )
        return relevant_edges

    def get_file_content(self):
        """
            Windmil generates multiple xml(Multispeak format) files for a single project. The code below
            reads all the xml files in a given folder and merges them to form 1 dictionary
        """
        try:
            wm_data = wm2graph(self.windmil_folder)
            self.nxGraph = wm_data.nxGraph
        except:
            raise ValueError(
                "Unable to open project from {name}".format(name=self.windmil_folder)
            )
        return

    def parse(self, model, **kwargs):
        """
            Parse the xml file and get topological elements
        """

        if "verbose" in kwargs and isinstance(kwargs["verbose"], bool):
            self.verbose = kwargs["verbose"]
        else:
            self.verbose = False

        # Call parse method of abtract reader
        super(Reader, self).parse(model, **kwargs)

    def fixStr(self, String):
        BannedChrs = [" ", "."]
        for Chr in BannedChrs:
            String = String.replace(Chr, "_")
        return String.lower()

    def parse_nodes(self, model):
        self.get_file_content()
        for node_name in self.nxGraph.nodes():
            node = Node(model)
            node.name = node_name
            if "x" in self.nxGraph.node[node_name]:
                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node_name]["x"])
                node_pos.lat = float(self.nxGraph.node[node_name]["y"])
                node.positions.append(node_pos)

    def parse_lines(self, model):
        self.phase_2_index = {
            "A": [0],
            "B": [1],
            "C": [2],
            "AB": [0, 1],
            "AC": [0, 2],
            "BC": [1, 2],
            "ABC": [0, 1, 2],
        }

        OHcables = self.nxGraph.graph["Overhead Conductor"]
        UGcables = self.nxGraph.graph["Underground Conductor"]
        Devices = self.nxGraph.graph["Device"]
        # Fuse = self.nxGraph.graph['Overcurrent Device']
        Layout = self.nxGraph.graph["Construction Code"]
        for node1, node2 in self.nxGraph.edges():
            if self.nxGraph[node1][node2]["class"] == "line":
                self.create_line(model, node1, node2, OHcables, UGcables)
            elif self.nxGraph[node1][node2]["class"] == "switch":
                self.create_switch(model, node1, node2)
            elif self.nxGraph[node1][node2]["class"] == "device":
                self.create_device(model, node1, node2, Devices)
        self.parse_feeder_metadata(model)
        return

    def create_device(self, model, node1, node2, Devices):
        device = Line(model)
        device.name = node2.replace("node_", "")
        device.from_element = node1
        device.to_element = node2
        device.is_fuse = True
        device.is_switch = False
        device.is_banked = False
        device.is_breaker = False
        device.is_recloser = False
        device.is_substation = False
        device.is_sectionalizer = False
        device.length = 1  #

        device.feeder_name = (
            ""
            if not isinstance(self.nxGraph[node1][node2]["feeder"], str)
            else self.nxGraph[node1][node2]["feeder"]
        )
        device.substation_name = (
            ""
            if not isinstance(self.nxGraph[node1][node2]["substation"], str)
            else self.nxGraph[node1][node2]["substation"]
        )
        phases = self.nxGraph[node1][node2]["phases"]
        phase_list = self.phase_2_index[phases]

        for phase, phase_index in zip(phases, phase_list):
            device_type = self.nxGraph[node1][node2]["equipment"][phase_index]
            device_data = Devices[Devices["Equipment Identifier"] == device_type]
            phase_device = Wire(model)
            phase_device.nameclass = device_type.replace(" ", "_")
            phase_device.phase = phase
            phase_device.is_open = bool(
                self.nxGraph[node1][node2]["isClosed"][phase_index]
            )
            # TODO: Fix enabled property for device
            phase_device.is_switch = True
            phase_device.is_fuse = False
            phase_device.is_recloser = False
            phase_device.is_breaker = False
            phase_device.ampacity = float(device_data["Current Rating"].iloc[0])
            phase_device.fuse_limit = float(
                device_data["Max Asymmetrical Fault"].iloc[0]
            )
            device.wires.append(phase_device)

        for node_name in [node1, node2]:
            if "x" in self.nxGraph.node[node_name]:
                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node_name]["x"])
                node_pos.lat = float(self.nxGraph.node[node_name]["y"])
                device.positions.append(node_pos)

    def create_switch(self, model, node1, node2):
        switch = Line(model)
        switch.name = node2.replace("node_", "")
        switch.from_element = node1
        switch.to_element = node2
        switch.is_fuse = False
        switch.is_switch = True
        switch.is_banked = False
        switch.is_breaker = False
        switch.is_recloser = False
        switch.is_substation = False
        switch.is_sectionalizer = False
        switch.length = 1  #
        switch.feeder_name = (
            ""
            if isinstance(self.nxGraph[node1][node2]["feeder"], float)
            else self.nxGraph[node1][node2]["feeder"]
        )
        switch.substation_name = (
            ""
            if isinstance(self.nxGraph[node1][node2]["substation"], float)
            else self.nxGraph[node1][node2]["substation"]
        )
        phases = self.nxGraph[node1][node2]["phases"]
        phase_list = self.phase_2_index[phases]

        for phase, phase_index in zip(phases, phase_list):
            phase_sw = Wire(model)
            phase_sw.phase = phase
            phase_sw.is_open = (
                True if self.nxGraph[node1][node2]["state"] == "O" else False
            )
            # TODO: Fix enabled property for switch
            phase_sw.is_switch = True
            phase_sw.is_fuse = False
            phase_sw.is_recloser = False
            phase_sw.is_breaker = False

            switch.wires.append(phase_sw)

        for node_name in [node1, node2]:
            if "x" in self.nxGraph.node[node_name]:
                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node_name]["x"])
                node_pos.lat = float(self.nxGraph.node[node_name]["y"])
                switch.positions.append(node_pos)

    def create_line(self, model, node1, node2, OHcables, UGcables):
        line = Line(model)
        line.name = node2.replace("node_", "")
        line.from_element = node1
        line.to_element = node2
        line.is_breaker = False
        line.is_recloser = False
        line.is_banked = False
        line.is_fuse = False
        line.is_sectionalizer = False
        line.is_switch = False
        line.length = self.convert_to_meters(
            float(self.nxGraph[node1][node2]["length"]), "ft"
        )
        # line.nominal_voltage = float(self.nxGraph[node1][node2]['kv'])    #TODO: line nominal KV
        line.line_type = self.nxGraph[node1][node2]["type"]
        line.feeder_name = (
            ""
            if isinstance(self.nxGraph[node1][node2]["feeder"], float)
            else self.nxGraph[node1][node2]["feeder"]
        )
        line.substation_name = (
            ""
            if isinstance(self.nxGraph[node1][node2]["substation"], float)
            else self.nxGraph[node1][node2]["substation"]
        )

        for node_name in [node1, node2]:
            if "x" in self.nxGraph.node[node_name]:
                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node_name]["x"])
                node_pos.lat = float(self.nxGraph.node[node_name]["y"])
                line.positions.append(node_pos)

        phases = self.nxGraph[node1][node2]["phases"]
        phase_list = self.phase_2_index[phases]
        nNeutrals = int(self.nxGraph[node1][node2]["nNeutrals"])
        nertral_list = np.add(range(nNeutrals), 3)
        neutral_phases = "N" * nNeutrals
        if nNeutrals:
            phases += neutral_phases
            phase_list.extend(nertral_list)
        for phase, phase_index in zip(phases, phase_list):
            conductor_name = self.nxGraph[node1][node2]["conductors"][phase_index]
            conductor_name = (
                "default_ph_cond"
                if (phase_index < 3) and (isinstance(conductor_name, float))
                else "default_nt_cond"
                if (phase_index > 2) and (isinstance(conductor_name, float))
                else conductor_name
            )
            phase_wire = Wire(model)
            phase_wire.nameclass = conductor_name.replace(" ", "_").replace(".", "_")
            phase_wire.phase = phase
            phase_wire.is_switch = False
            phase_wire.is_fuse = False
            phase_wire.is_recloser = False
            phase_wire.is_breaker = False
            phase_wire.is_open = False
            phase_wire.X = (
                -1 if phase is "A" else 1 if phase is "C" else 0
            )  # TODO: Fix conductor layout later
            phase_wire.Y = 10 if phase is not "N" else 8
            if self.nxGraph[node1][node2]["type"] == "overhead":
                cond_data = OHcables[OHcables["Equipment Identifier"] == conductor_name]
                if len(cond_data):
                    phase_wire.gmr = self.convert_to_meters(
                        float(cond_data["Geometric Mean Radius"].iloc[0]), "ft"
                    )
                    phase_wire.diameter = self.convert_to_meters(
                        float(cond_data["Diameter"].iloc[0]), "in"
                    )
                    phase_wire.ampacity = float(cond_data["Carrying Capacity"].iloc[0])
                    phase_wire.resistance = self.convert_from_meters(
                        float(cond_data["Resistance @ 50"].iloc[0]), "mi"
                    )
            if self.nxGraph[node1][node2]["type"] == "underground":
                cond_data = UGcables[UGcables["Equipment Identifier"] == conductor_name]
                if len(cond_data):
                    phase_wire.gmr = self.convert_to_meters(
                        float(cond_data["Geometric Mean Radius In Feet"].iloc[0]), "ft"
                    )
                    phase_wire.concentric_neutral_gmr = self.convert_to_meters(
                        float(cond_data["GMR (Neutral) In Feed"].iloc[0]), "ft"
                    )
                    phase_wire.diameter = self.convert_to_meters(
                        float(cond_data["Diameter of Conductor In Feet"].iloc[0]), "ft"
                    )
                    phase_wire.insulation_thickness = self.convert_to_meters(
                        float(cond_data["OD of Cable Insulation In Feet"].iloc[0]), "ft"
                    )
                    phase_wire.concentric_neutral_diameter = self.convert_to_meters(
                        float(
                            cond_data["OD of Cable Including Neutral In Fee"].iloc[0]
                        ),
                        "ft",
                    )
                    phase_wire.ampacity = float(
                        cond_data["Carrying Capacity In Amps"].iloc[0]
                    )
                    phase_wire.resistance = self.convert_from_meters(
                        float(
                            cond_data["Phase Conductor Resistance Ohms/Mile"].iloc[0]
                        ),
                        "mi",
                    )
                    phase_wire.concentric_neutral_resistance = self.convert_from_meters(
                        float(cond_data["Concentric Neutral Resist Ohms/Mile"].iloc[0]),
                        "ft",
                    )
            #
            if phase_wire.resistance == None:
                phase_wire.resistance = 0
            if phase_wire.gmr == None or phase_wire.gmr == 0:
                phase_wire.gmr = 1.0

            line.wires.append(phase_wire)

            Dmatrix = np.zeros((len(line.wires), len(line.wires)))
            Phases = []
            GMRs = []
            Rs = []
            for i, wire1 in enumerate(line.wires):
                Phases.append(wire1.phase)
                GMRs.append(wire1.gmr)
                Rs.append(wire1.resistance)
                for j, wire2 in enumerate(line.wires):
                    distance = self.distance([wire1.X, wire1.Y], [wire2.X, wire2.Y])
                    Dmatrix[i, j] = distance
            if line.wires:
                Z = self.get_primitive_impedance_matrix(Dmatrix, GMRs, Rs)
                if nNeutrals:
                    Z = self.kron_reduction(Z)
                line.impedance_matrix = Z.tolist()

    def parse_loads(self, model):
        loadmixes = self.nxGraph.graph["Load Mix"]
        for node in self.nxGraph.nodes():
            if "loads" in self.nxGraph.node[node] and len(
                list(self.nxGraph.edges([node]))
            ):
                node1, node2 = list(self.nxGraph.edges([node]))[0]
                for load_name, load_properties in self.nxGraph.node[node][
                    "loads"
                ].items():
                    if bool(load_properties["enabled"]):
                        loadmix = load_properties["load mix"]
                        if loadmix.upper().replace(" ", "") != "NONE":
                            lm = loadmixes[loadmixes["Equipment Identifier"] == loadmix]
                            Z = float(lm["Constant IMP"].iloc[0])
                            I = float(lm["Constant Current"].iloc[0])
                            P = float(lm["Constant kVA"].iloc[0])
                            useZIP = 1
                            conn = "Y" if lm["Connection Code"].iloc[0] == "W" else "D"
                        else:
                            Z = 0
                            I = 0
                            P = 1
                            useZIP = 0
                            conn = "Y"
                        load = Load(model)
                        load.name = load_properties["name"].replace("node", "load")
                        # load.nominal_voltage = TODO: nominal voltage needs to be added
                        load.connection_type = conn
                        load.connecting_element = node
                        # TODO: Add loadshape attribute to the load object
                        load.feeder_name = (
                            ""
                            if not isinstance(self.nxGraph[node1][node2]["feeder"], str)
                            else self.nxGraph[node1][node2]["feeder"]
                        )
                        load.substation_name = (
                            ""
                            if not isinstance(
                                self.nxGraph[node1][node2]["substation"], str
                            )
                            else self.nxGraph[node1][node2]["substation"]
                        )

                        phases = load_properties["phases"]
                        phase_list = self.phase_2_index[phases]
                        for phase, phase_index in zip(phases, phase_list):
                            load_phase = PhaseLoad(model)
                            load_phase.phase = phase
                            load_phase.p = float(load_properties["kw"][phase_index])
                            load_phase.q = float(load_properties["kvar"][phase_index])
                            load_phase.use_zip = useZIP
                            load_phase.ppercentpower = P * 100
                            load_phase.qpercentpower = P * 100
                            load_phase.ppercentcurrent = I * 100
                            load_phase.qpercentcurrent = I * 100
                            load_phase.ppercentimpedance = Z * 100
                            load_phase.qpercentimpedance = Z * 100
                            load_phase.model = 1 if not useZIP else 8
                            load.phase_loads.append(load_phase)

                        if "x" in self.nxGraph.node[node]:
                            node_pos = Position(model)
                            node_pos.long = float(self.nxGraph.node[node]["x"])
                            node_pos.lat = float(self.nxGraph.node[node]["y"])
                            load.positions.append(node_pos)

    def parse_capacitors(self, model):
        for node in self.nxGraph.nodes():
            if "capacitors" in self.nxGraph.node[node] and len(
                list(self.nxGraph.edges([node]))
            ):
                node1, node2 = list(self.nxGraph.edges([node]))[0]
                for cap_name, cap_properties in self.nxGraph.node[node][
                    "loads"
                ].items():
                    if cap_properties["state"] != "Disconnected":
                        capacitor = Capacitor(model)
                        capacitor.name = cap_properties["name"].replace("node", "cap")
                        capacitor.connection_type = cap_properties["conn"]
                        capacitor.connecting_element = node
                        capacitor.nominal_voltage = cap_properties["kvRated"]
                        capacitor.mode = cap_properties["reg mode"]
                        capacitor.high = cap_properties["Off Setting"]
                        capacitor.low = cap_properties["On Setting"]
                        # capacitor.delay = cap_properties['']
                        capacitor.pt_phase = cap_properties["control phase"]
                        capacitor.measuring_element = cap_properties["Ctrl Element"]
                        capacitor.feeder_name = (
                            ""
                            if not isinstance(self.nxGraph[node1][node2]["feeder"], str)
                            else self.nxGraph[node1][node2]["feeder"]
                        )
                        capacitor.substation_name = (
                            ""
                            if not isinstance(
                                self.nxGraph[node1][node2]["substation"], str
                            )
                            else self.nxGraph[node1][node2]["substation"]
                        )

                        phases = cap_properties["phases"]
                        phase_list = self.phase_2_index[phases]
                        for phase, phase_index in zip(phases, phase_list):
                            cap_phase = PhaseCapacitor(model)
                            cap_phase.phase = phase
                            cap_phase.var = float(["kvar"][phase_index])
                            cap_phase.switch = (
                                0 if cap_properties["state"] == "Off" else 1
                            )
                            # cap_phase.sections = useZIP
                            # cap_phase.normalsections = P * 100

                        if "x" in self.nxGraph.node[node]:
                            node_pos = Position(model)
                            node_pos.long = float(self.nxGraph.node[node]["x"])
                            node_pos.lat = float(self.nxGraph.node[node]["y"])
                            capacitor.positions.append(node_pos)

    def parse_transformers(self, model):
        xfmrs = self.filter_edges_by_class("transformer")
        xfmr_types = self.nxGraph.graph["Transformer"]
        for xfmr in xfmrs:
            node1, node2 = xfmr
            # Get the transformer type
            tr_types = set(self.nxGraph[node1][node2]["equipment"])
            tr_types.discard("NONE")
            if tr_types:
                # tr data from library
                tr_type = list(tr_types)[0]
                winding_data = xfmr_types[xfmr_types["Equipment Identifier"] == tr_type]
                # create transformer

                phases = self.nxGraph[node1][node2]["phases"]
                nPhases = len(phases)
                nwdgs = 2 if np.isnan(self.nxGraph[node1][node2]["hasTertiary"]) else 3

                X_R_ratio = float(winding_data["X/R Ratio- Phase A"].iloc[0])
                Zpercentage = float(winding_data["Percent Impedance- Zps"].iloc[0])
                r_percent = np.sqrt(Zpercentage ** 2 / (X_R_ratio ** 2 + 1))
                x_percent = np.sqrt(Zpercentage ** 2 - r_percent ** 2)

                tr = PowerTransformer(model)
                tr.name = node2.replace("node_", "tr_")
                tr.substation_name = (
                    ""
                    if not isinstance(self.nxGraph[node1][node2]["substation"], str)
                    else self.nxGraph[node1][node2]["substation"]
                )
                tr.feeder_name = (
                    ""
                    if not isinstance(self.nxGraph[node1][node2]["feeder"], str)
                    else self.nxGraph[node1][node2]["feeder"]
                )
                tr.from_element = node1
                tr.to_element = node2
                tr.normhkva = sum(
                    [
                        float(winding_data["Single Phase Base kVA- Zps"].iloc[0]),
                        float(winding_data["Single Phase Base kVA- Zpt"].iloc[0]),
                        float(winding_data["Single Phase Base kVA- Zst"].iloc[0]),
                    ]
                )
                tr.noload_loss = float(
                    winding_data["No-Load Loss- Zps"].iloc[0]
                ) / float(winding_data["Single Phase Base kVA- Zps"].iloc[0])
                tr.install_type = (
                    "PADMOUNT"
                    if bool(winding_data["Is Pad Mounted Transformer"].iloc[0])
                    else "POLEMOUNT"
                )
                tr.reactances.append(float(x_percent))
                tr.phase_shift = 0
                tr.is_center_tap = int(self.nxGraph[node1][node2]["is center tapped"])
                # Set transformer position
                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node2]["x"])
                node_pos.lat = float(self.nxGraph.node[node2]["y"])
                tr.positions.append(node_pos)

                for i in range(nwdgs):

                    wdg = Winding(model)
                    wdg.resistance = r_percent / nwdgs
                    kV = float(self.nxGraph[node1][node2]["kv"][i]) * 1000
                    wdg.nominal_voltage = kV if nPhases == 1 else 1.732 * kV
                    wdg.connection_type = self.nxGraph[node1][node2]["conn"][i]
                    wdg.rated_power = (
                        float(winding_data["Single Phase Rated kVA- Zps"]) * 1000
                    )
                    wdg.voltage_type = 0 if i == 0 else 2
                    for j, phase in enumerate(phases):

                        phswdg = PhaseWinding(model)
                        ix = self.phase_2_index[phase][0]
                        phswdg.phase = phase
                        phswdg.tap_position = 1.0  # self.nxGraph[node1][node2]['kv'][i]
                        phswdg.compensator_r = 0
                        phswdg.compensator_x = 0
                        wdg.phase_windings.append(phswdg)

                    tr.windings.append(wdg)

    def parse_regulators(self, model):
        regulators = self.filter_edges_by_class("regulator")
        rg_types = self.nxGraph.graph["Regulator"]
        for reg in regulators:
            node1, node2 = reg

            print(self.nxGraph[node1][node2]["kv"])
            reg_data = self.nxGraph[node1][node2]

            regulator_types = set(self.nxGraph[node1][node2]["equipment"])
            regulator_types.discard("NONE")
            if regulator_types:
                reg_type = list(regulator_types)[0]
                reg_type_data = rg_types[rg_types["Equipment Identifier"] == reg_type]
                # print(reg_type_data)
                Regu = Regulator(model)
                Regu.name = reg_data["name"]
                Regu.from_element = node1
                Regu.to_element = node2
                Regu.bandwidth = float(reg_type_data.iloc[-1]["Bandwidth"])
                Regu.ltc = 1

                XFMRname = self.CreateRegXfmr(
                    model, node1, node2, reg_data, reg_type_data
                )

                Regu.connected_transformer = XFMRname
                Regu.feeder_name = reg_data["feeder"]
                Regu.substation_name = reg_data["substation"]

                node_pos = Position(model)
                node_pos.long = float(self.nxGraph.node[node2]["x"])
                node_pos.lat = float(self.nxGraph.node[node2]["y"])
                Regu.positions.append(node_pos)
        return

    def parse_feeder_metadata(self, model):
        PowerSources = self.filter_edges_by_class("substation")

        for node1, node2 in PowerSources:
            print(self.nxGraph[node1][node2])
            Source = PowerSource(model)
            Source.name = self.nxGraph[node1][node2]["name"]
            Source.connecting_element = node1
            Source.nominal_voltage = (
                1.732 * float(self.nxGraph[node1][node2]["kv"]) * 1000
            )
            Source.operating_voltage = float(self.nxGraph[node1][node2]["Vpu"])
            Source.substation = True
            Source.transformer = False
            Source.is_sourcebus = True
            Source.connection_type = (
                "Y" if self.nxGraph[node1][node2]["conn"] == "W" else "D"
            )
            # Source.phases = [Unicode(default_value=x) for x in self.nxGraph[node1][node2]['phases']]

        print("Feeder")

    def CreateRegXfmr(self, model, node1, node2, reg_data, reg_type_data):
        print(reg_type_data)
        tr = PowerTransformer(model)
        tr.name = "xfmr_" + reg_data["name"]
        tr.substation_name = (
            ""
            if not isinstance(reg_data["substation"], str)
            else reg_data["substation"]
        )
        tr.feeder_name = (
            "" if not isinstance(reg_data["feeder"], str) else reg_data["feeder"]
        )
        tr.from_element = node1
        tr.to_element = node2
        tr.normhkva = (
            float(reg_data["kv"][0]) * float(reg_type_data.iloc[-1]["Ampacity"]) * 3
        )
        tr.loadloss = float(1)
        tr.noload_loss = float(0.1)  # TODO fix the noload losses here
        tr.install_type = "PADMOUNT"
        tr.reactances.append([10.0])
        tr.phase_shift = 0
        tr.is_center_tap = False
        # Set transformer position
        node_pos = Position(model)
        node_pos.long = float(self.nxGraph.node[node2]["x"])
        node_pos.lat = float(self.nxGraph.node[node2]["y"])
        tr.positions.append(node_pos)
        for i in range(2):
            nPhases = len(reg_data["phases"])
            wdg = Winding(model)
            kV = float(self.nxGraph[node1][node2]["kv"][0]) * 1000
            wdg.resistance = 0.5
            wdg.nominal_voltage = kV if nPhases == 1 else 1.732 * kV
            wdg.connection_type = self.nxGraph[node1][node2]["conn"][i]
            wdg.rated_power = (
                float(reg_data["kv"][0])
                * float(reg_type_data.iloc[-1]["Ampacity"])
                * 1000
            )
            wdg.voltage_type = 0 if i == 0 else 2
            phases = reg_data["phases"]
            LDCr = reg_data["LDCr"]
            LDCx = reg_data["LDCx"]
            Vset = reg_data["Vpu"]
            Vub = reg_data["fhhp"]
            Vlb = reg_data["fhlp"]
            for j, ZippedData in enumerate(zip(phases, LDCr, LDCx, Vlb, Vub, Vset)):
                phase, r, x, vu, vl, vs = ZippedData
                nSteps = 33
                vPerStep = (float(vu) - float(vl)) / nSteps
                Tap = int((float(vs) - 1) / vPerStep)
                print("Tap: ", Tap)

                phswdg = PhaseWinding(model)
                ix = self.phase_2_index[phase][0]
                phswdg.phase = phase
                phswdg.tap_position = float(Tap)
                phswdg.compensator_r = float(r)
                phswdg.compensator_x = float(x)
                wdg.phase_windings.append(phswdg)
            tr.windings.append(wdg)
        return tr.name
