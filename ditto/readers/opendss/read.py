# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

# Python import
import math
import sys
import os
import json

import numpy as np

import logging
import time
from six import string_types
from functools import reduce

# OpenDSSdirect import
import opendssdirect as dss

# Ditto imports
from ditto.readers.abstract_reader import AbstractReader
from ditto.store import Store
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.power_source import PowerSource
from ditto.models.position import Position
from ditto.models.storage import Storage
from ditto.models.phase_storage import PhaseStorage


from ditto.models.feeder_metadata import Feeder_metadata

from ditto.models.base import Unicode

logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        logger.debug("%r (%r, %r) %2.2f sec" % (method.__name__, args, kw, te - ts))
        return result

    return timed


class Reader(AbstractReader):
    """OpenDSS--->DiTTo reader class.
    Use to read and parse an OpenDSS circuit model to DiTTo.

    :param log_file: Name/path of the log file. Optional. Default='./OpenDSS_reader.log'
    :type log_file: str

    **Constructor:**

    >>> my_reader=Reader(log_file='./logs/my_log.log')

    .. warning::

    The reader uses OpenDSSDirect heavily. <https://github.com/NREL/OpenDSSDirect.py>
    For more information on this package contact Dheepak Krishnamurthy.
    """

    register_names = ["dss", "opendss", "OpenDSS", "DSS"]

    def __init__(self, **kwargs):
        """Constructor for the OpenDSS reader."""

        # Call super
        super(Reader, self).__init__(**kwargs)

        self.DSS_file_names = {}

        if "master_file" in kwargs:
            self.DSS_file_names["master"] = kwargs["master_file"]
        else:
            self.DSS_file_names["master"] = "./master.dss"

        if "buscoordinates_file" in kwargs:
            self.DSS_file_names["Nodes"] = kwargs["buscoordinates_file"]
        else:
            self.DSS_file_names["Nodes"] = "./buscoord.dss"

        # Get the delimiter
        if "coordinates_delimiter" in kwargs and isinstance(
            kwargs["coordinates_delimiter"], string_types
        ):
            self.coordinates_delimiter = kwargs["coordinates_delimiter"]
        else:
            self.coordinates_delimiter = ","

        if kwargs.get("default_values_file", None) is not None:
            self.DSS_file_names["default_values_file"] = kwargs["default_values_file"]
        else:
            self.DSS_file_names["default_values_file"] = None
        #        ] = "/C/Users/bkavuri/Downloads/ditto/ditto/default_values/opendss_default_values.json"

        if kwargs.get("remove_opendss_default_values_flag", None) is True:
            self.DSS_file_names["remove_opendss_default_values_flag"] = True
        else:
            self.DSS_file_names["remove_opendss_default_values_flag"] = False

        # self.DSS_file_names={'Nodes': 'buscoords.dss',
        #                     'master': 'master.dss'}

        self.is_opendssdirect_built = False
        self.all_object_names = []
        logger.info("OpenDSS--->DiTTo reader instanciated")

    def set_dss_file_names(self, new_names):
        """Specify the path to some required DSS files.
        Because the reader is relying on OpenDSSdirect, we only need the path to the master file and the path to the bus coordinates file.

        :param new_names: dictionary with file names: {'Nodes': path_to_file, 'master': path_to_file}
        :type new_names: dict
        :returns: 1 for sucess, -1 for failure.
        :rtype: int
        """
        if not isinstance(new_names, dict):
            logger.error("set_dss_file_names() expects a dictionary")
            return -1
        for key, value in new_names.items():
            if key not in ["Nodes", "master"]:
                return -1
            self.DSS_file_names[key] = value
        return 1

    def function(self, string):
        """Execture the OpenDSS command passed as a string.
        Log an error if the commanf cannot be runned.

        :param string: String of the OpenDSS command to execute (ex: 'New Transformer.T1 ...')
        :type string: str
        """
        try:
            return dss.run_command(string)
        except:
            logger.error("Unable to execute the following command: \n" + string)

    def phase_mapping(self, dss_phase):
        """Map the phases of OpenDSS (1, 2, or 3) into DiTTo phases ('A', 'B', or 'C').

        **Phase mapping:**

        +---------------+-------------+
        | OpenDSS phase | DiTTo phase |
        +===============+=============+
        |    1 or '1'   |     'A'     |
        +---------------+-------------+
        |    2 or '2'   |     'B'     |
        +---------------+-------------+
        |    3 or '3'   |     'C'     |
        +---------------+-------------+

        :param dss_phase: Phase number in OpenDSS format
        :type dss_phase: int or str
        :returns: Phase in DiTTo format
        :rtype: str

        .. note:: The function accepts both integers and strings as input (1 or '1' for example).
        """
        # Also make sure that if a phase is already in DiTTo format it does not return a None instead...
        if dss_phase == 1 or dss_phase == "1" or dss_phase == "A":
            return "A"
        if dss_phase == 2 or dss_phase == "2" or dss_phase == "B":
            return "B"
        if dss_phase == 3 or dss_phase == "3" or dss_phase == "C":
            return "C"
        return None

    @timeit
    def build_opendssdirect(self, master_dss_file):
        """Uses OpenDSSDirect to run the master DSS file.

        :param master_dss_file: Path to DSS file responsible for creating the circuit and loading all the OpenDSS objects. (Usually, it looks like a serie of redirect commands).
        :type master_dss_file: str
        :returns: 1 for success, -1 for failure.
        :rtype: int

        ..note:: After running this function, all circuit elements can be accessed through the openDSSDirect api.

        .. warning:: Calling this function before parsing is required.
        """
        logger.info("Reading DSS file {name}...".format(name=master_dss_file))

        try:
            self.function("redirect {master_file}".format(master_file=master_dss_file))
        except:
            logger.error(
                "Unable to redirect master file: {filename}".format(
                    filename=master_dss_file
                )
            )
            return -1

        self.is_opendssdirect_built = True

        logger.info("build_opendssdirect succesful")

        return 1

    def parse(self, model, **kwargs):
        """General parse function.
        Responsible for calling the sub-parsers and logging progress.

        :param model: DiTTo model
        :type model: DiTTo model
        :param verbose: Set verbose mode. Optional. Default=False
        :type verbose: bool
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        start = time.time()
        self.source_name = "Sourcebus"
        # In order to parse, we need that opendssdirect was previously run
        if not self.is_opendssdirect_built:
            self.build_opendssdirect(self.DSS_file_names["master"])
            # logger.error('Trying to parse before building opendssdirect.')
            # return -1
        end = time.time()
        logger.debug("Build OpenDSSdirect= {}".format(end - start))

        if "feeder_file" in kwargs:
            self.feeder_file = kwargs["feeder_file"]
            self.parse_feeder_metadata(model)

        read_power_source = True
        if "read_power_source" in kwargs:
            read_power_source = kwargs["read_power_source"]
        if read_power_source:
            self.parse_power_source(
                model
            )  # TODO: push this to abstract reader once power source parsing is stable...

        # Call parse from abstract reader class
        super(Reader, self).parse(model, **kwargs)

        self.parse_storage(model)

        self.set_nominal_voltages(model)

        return 1

    def set_nominal_voltages(self, model):
        """Loop over the buses and set the kv base.
        Then loop over the objects and set the kv base using the connecting element.
        .. warning: This has to be called last in parse.
        """
        model.set_names()
        AllBusNames = dss.Circuit.AllBusNames()
        for bus_name in AllBusNames:
            # Set the active bus
            dss.Circuit.SetActiveBus(bus_name)
            # Set the nominal voltage of the corresponding node in the DiTTo Model
            try:
                model[bus_name.lower()].nominal_voltage = (
                    dss.Bus.kVBase() * math.sqrt(3) * 10 ** 3
                )  # DiTTo in volts
            except:
                print("Could not set nominal voltage for bus {b}".format(b=bus_name))
                pass

        for obj in model.models:
            if hasattr(obj, "nominal_voltage") and obj.nominal_voltage is None:
                # If the object has a connecting_element attribute
                if hasattr(obj, "connecting_element"):
                    try:
                        obj.nominal_voltage = model[
                            obj.connecting_element
                        ].nominal_voltage
                    except:
                        pass
                elif hasattr(obj, "from_element"):
                    try:
                        obj.nominal_voltage = model[obj.from_element].nominal_voltage
                    except:
                        pass
            elif isinstance(obj, PowerTransformer) or isinstance(obj, Regulator):
                # Get the from_element
                _from = obj.from_element
                # Get the to_element
                _to = obj.to_element
                mapp = {0: _from, 1: _to, 2: _to}
                for x in range(3):
                    if (
                        len(obj.windings) > x
                        and obj.windings[x].nominal_voltage is None
                    ):
                        try:
                            obj.windings[x].nominal_voltage = model[
                                mapp[x]
                            ].nominal_voltage
                        except:
                            pass

    def parse_feeder_metadata(self, model):
        with open(self.feeder_file, "r") as f:
            lines = f.readlines()
        feeders = {}
        substations = {}
        substation_transformers = {}
        for line in lines[1:]:
            node, sub, feed, sub_trans = list(map(lambda x: x.strip(), line.split(" ")))
            if not feed in feeders:
                feeders[feed] = [node.lower().replace(".", "")]
            else:
                feeders[feed].append(node.lower().replace(".", ""))
            if not feed in substations:
                substations[feed] = sub.lower().replace(".", "")
            if not feed in substation_transformers:
                substation_transformers[feed] = sub.lower().replace(".", "")

        for f_name, f_data in feeders.items():
            api_feeder_metadata = Feeder_metadata(model)
            api_feeder_metadata.name = f_name
            if f_name in substation_transformers:
                api_feeder_metadata.transformer = substation_transformers[f_name]
            if f_name in substations:
                api_feeder_metadata.substation = substations[f_name]

    @timeit
    def parse_power_source(self, model, **kwargs):
        """Power source parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        sources = _dss_class_to_dict("Vsource")

        for source_name, source_data in sources.items():

            # Skip PowerSource object if disabled
            if not source_data["enabled"]:
                continue

            # Instanciate DiTTo PowerSource object
            try:
                api_power_source = PowerSource(model)
            except:
                continue

            # Set the name of the source
            try:
                api_power_source.name = source_name
            except:
                pass

            # Set the nominal voltage of the source
            try:
                api_power_source.nominal_voltage = (
                    float(source_data["basekv"]) * 10 ** 3
                )  # DiTTo in volts
            except:
                pass

            # Set the per unit value of the source
            try:
                api_power_source.per_unit = float(source_data["pu"])
            except:
                pass

            # Set the source_bus flag to True
            try:
                # We have an external power source here
                api_power_source.is_sourcebus = True
            except:
                pass

            # Set the rated power of the source
            try:
                api_power_source.rated_power = float(source_data["baseMVA"]) * 10 ** 6
            except:
                pass

            # Set the emergency power of the source
            try:
                api_power_source.emergency_power = (
                    float(source_data["MVAsc3"]) * 10 ** 6
                )
            except:
                pass

            # Zero sequence impedance
            if "Z0" in source_data and isinstance(source_data["Z0"], list):
                if len(source_data["Z0"]) == 2:
                    try:
                        api_power_source.zero_sequence_impedance = complex(
                            float(source_data["Z0"][0]), float(source_data["Z0"][1])
                        )
                    except:
                        pass
            elif (
                "R0" in source_data
                and source_data["R0"] != ""
                and "X0" in source_data
                and source_data["X0"] != ""
            ):
                try:
                    api_power_source.zero_sequence_impedance = complex(
                        float(source_data["R0"]), float(source_data["X0"])
                    )
                except:
                    pass

            # Positive sequence impedance
            if "Z1" in source_data and isinstance(source_data["Z1"], list):
                if len(source_data["Z1"]) == 2:
                    try:
                        api_power_source.positive_sequence_impedance = complex(
                            float(source_data["Z1"][0]), float(source_data["Z1"][1])
                        )
                    except:
                        pass
            elif (
                "R1" in source_data
                and source_data["R1"] != ""
                and "X1" in source_data
                and source_data["X1"] != ""
            ):
                try:
                    api_power_source.positive_sequence_impedance = complex(
                        float(source_data["R1"]), float(source_data["X1"])
                    )
                except:
                    pass

            # Phase angle
            try:
                api_power_source.phase_angle = float(source_data["angle"])
            except:
                pass

            api_power_source.phases = list(
                map(lambda x: Unicode(self.phase_mapping(x)), [1, 2, 3])
            )

            # Get the coordinate file
            self.bus_coord_file = self.DSS_file_names["Nodes"]
            skip_coordinate_parsing = False

            try:
                with open(self.bus_coord_file, "r") as g:
                    coordinates = g.readlines()
            except IOError:
                skip_coordinate_parsing = True

            X, Y = None, None
            if not skip_coordinate_parsing:
                for line in coordinates:
                    if line.strip() == "":
                        continue

                    try:
                        name, X, Y = list(
                            map(
                                lambda x: x.strip(),
                                line.split(self.coordinates_delimiter),
                            )
                        )
                        name = name.lower()
                    except:
                        logger.warning("Could not parse: " + str(line))
                        name = None
                        X = None
                        Y = None
                        pass

                    try:
                        X = float(X)
                        Y = float(Y)
                    except:
                        logger.warning(
                            "Could not cast coordinates {X}, {Y} for bus {name}".format(
                                X=X, Y=Y, name=name
                            )
                        )
                        pass

            powersource_pos = Position(model)
            powersource_pos.long = X
            powersource_pos.lat = Y
            api_power_source.positions.append(powersource_pos)

            try:
                if "." in source_data["bus1"]:
                    api_power_source.connecting_element = source_data["bus1"].split(
                        "."
                    )[0]
                else:
                    api_power_source.connecting_element = source_data["bus1"]
                self.source_name = api_power_source.connecting_element + "_src"
                api_feeder_metadata = Feeder_metadata(model)
                api_feeder_metadata.name = self.source_name
                api_feeder_metadata.headnode = api_power_source.connecting_element
                api_feeder_metadata.substation = api_power_source.connecting_element
                api_feeder_metadata.nominal_voltage = api_power_source.nominal_voltage
            except:
                pass

        return 1

    @timeit
    def parse_nodes(self, model, **kwargs):
        """Node parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :param coordinates_delimiter: The character that delimites the fieds in the coordinates file. Optional. Default=','
        :type coordinates_delimiter: str
        :returns: 1 for success, -1 for failure
        :rtype: int

        .. note:: This function is a bit different from the other parsers. To get the bus coordinates, it has to read and parse the coordinates file.

        .. note:: There is currently no easy way to get the bus data in OpenDSSdirect yet. To get the phase numbers, we loop over the lines and extract the phases from the two end buses.
        """
        # Get the coordinate file
        self.bus_coord_file = self.DSS_file_names["Nodes"]
        skip_coordinate_parsing = False

        try:
            with open(self.bus_coord_file, "r") as g:
                coordinates = g.readlines()
        except IOError:
            skip_coordinate_parsing = True

        buses = {}
        if not skip_coordinate_parsing:
            for line in coordinates:
                if line.strip() == "":
                    continue

                try:
                    name, X, Y = list(
                        map(lambda x: x.strip(), line.split(self.coordinates_delimiter))
                    )
                    name = name.lower()
                except:
                    logger.warning("Could not parse line : " + str(line))
                    name = None
                    X = None
                    Y = None
                    pass

                try:
                    X = float(X)
                    Y = float(Y)
                except:
                    logger.warning(
                        "Could not cast coordinates {X}, {Y} for bus {name}".format(
                            X=X, Y=Y, name=name
                        )
                    )
                    pass

                if not name in buses:
                    buses[name] = {}
                    buses[name]["positions"] = [X, Y]
                    if name not in self.all_object_names:
                        self.all_object_names.append(name)
                    else:
                        logger.warning("Duplicate object Node {name}".format(name=name))
                else:
                    buses[name]["positions"] = [X, Y]

        # Extract the line data
        lines = _dss_class_to_dict("line")

        # Loop over the lines to get the phases
        for name, data in lines.items():

            # Parse bus1 data
            if "." in data["bus1"]:
                temp = data["bus1"].split(".")
                b1_name = temp[0].strip()
                b1_phases = list(map(lambda x: int(x), temp[1:]))
            elif data["phases"] == "3":
                b1_name = data["bus1"].strip()
                b1_phases = [1, 2, 3]
            else:
                raise ValueError(
                    "Phases not specified for {b1}.".format(b1=data["bus1"])
                )

            for each in b1_phases:
                if not each in [1, 2, 3]:
                    raise ValueError(
                        "Phase {name} is not supported for bus {b1}.".format(
                            name=each, b1=data["bus1"]
                        )
                    )

            # Parse bus2 data
            if "." in data["bus2"]:
                temp = data["bus2"].split(".")
                b2_name = temp[0].strip()
                b2_phases = list(map(lambda x: int(x), temp[1:]))
            elif data["phases"] == "3":
                b2_name = data["bus2"].strip()
                b2_phases = [1, 2, 3]
            else:
                raise ValueError(
                    "Phases not specified for {b2}.".format(b2=data["bus2"])
                )

            for each in b2_phases:
                if not each in [1, 2, 3]:
                    raise ValueError(
                        "Phase {name} is not supported for bus {b2}.".format(
                            name=each, b2=data["bus2"]
                        )
                    )

            # Update the buses dictionary
            if b1_name is not None and not b1_name in buses:
                if b1_name not in self.all_object_names:
                    self.all_object_names.append(b1_name)
                else:
                    logger.warning("Duplicate object Node {name}".format(name=b1_name))
                buses[b1_name] = {}
                buses[b1_name]["positions"] = None
                buses[b1_name]["phases"] = b1_phases
            elif not "phases" in buses[b1_name]:
                buses[b1_name]["phases"] = b1_phases
            else:
                buses[b1_name]["phases"] += b1_phases
                buses[b1_name]["phases"] = np.unique(buses[b1_name]["phases"]).tolist()

            # Update the buses dictionary
            if b2_name is not None and not b2_name in buses:
                if b2_name not in self.all_object_names:
                    self.all_object_names.append(b2_name)
                else:
                    logger.warning("Duplicate object Node {name}".format(name=b2_name))
                buses[b2_name] = {}
                buses[b2_name]["positions"] = None
                buses[b2_name]["phases"] = b2_phases
            elif not "phases" in buses[b2_name]:
                buses[b2_name]["phases"] = b2_phases
            else:
                buses[b2_name]["phases"] += b2_phases
                buses[b2_name]["phases"] = np.unique(buses[b2_name]["phases"]).tolist()

        # Extract the transformer data
        transformers = _dss_class_to_dict("transformer")
        # Loop over the transformers to get the phases
        for name, data in transformers.items():

            # Parse bus1 data
            for bus in data["buses"]:
                if "." in bus:
                    temp = bus.split(".")
                    b_name = temp[0].strip()
                    b_phases = list(map(lambda x: int(x), temp[1:]))
                elif data["phases"] == "3":
                    b_name = bus.strip()
                    b_phases = [1, 2, 3]
                else:
                    b_name = None
                    b_phases = None

                # Update the buses dictionary
                if b_name is not None and not b_name in buses:
                    if b_name not in self.all_object_names:
                        self.all_object_names.append(b_name)
                    else:
                        logger.warning(
                            "Duplicate object Node {name}".format(name=b_name)
                        )
                    buses[b_name] = {}
                    buses[b_name]["positions"] = None
                    buses[b_name]["phases"] = b_phases
                elif not "phases" in buses[b_name]:
                    buses[b_name]["phases"] = b_phases
                else:
                    buses[b_name]["phases"] += b_phases
                    buses[b_name]["phases"] = np.unique(
                        buses[b_name]["phases"]
                    ).tolist()

        # Extract the load data
        loads = _dss_class_to_dict("load")
        # Loop over the loads to get the phases
        for name, data in loads.items():
            # Parse bus1 data
            if "." in data["bus1"]:
                temp = data["bus1"].split(".")
                b1_name = temp[0].strip()
                b1_phases = list(map(lambda x: int(x), temp[1:]))
            elif data["phases"] == "3":
                b1_name = data["bus1"].strip()
                b1_phases = [1, 2, 3]
            else:
                b1_name = None
                b1_phases = None
            # Update the buses dictionary
            if b1_name is not None and not b1_name in buses:
                if b1_name not in self.all_object_names:
                    self.all_object_names.append(b1_name)
                else:
                    logger.warning("Duplicate object Node {name}".format(name=b1_name))
                buses[b1_name] = {}
                buses[b1_name]["positions"] = None
                buses[b1_name]["phases"] = b1_phases
            elif not "phases" in buses[b1_name]:
                buses[b1_name]["phases"] = b1_phases
            else:
                buses[b1_name]["phases"] += b1_phases
                buses[b1_name]["phases"] = np.unique(buses[b1_name]["phases"]).tolist()

        self._nodes = []

        # Loop over the dictionary of nodes and create the DiTTo Node objects
        for name, data in buses.items():

            api_node = Node(model)

            try:
                api_node.name = name
            except:
                pass

            try:
                node_pos = Position(model)
                node_pos.long = data["positions"][0]
                node_pos.lat = data["positions"][1]
                api_node.positions.append(node_pos)
            except:
                pass

            api_node.feeder_name = self.source_name

            try:
                api_node.phases = list(
                    map(lambda x: Unicode(self.phase_mapping(x)), data["phases"])
                )
            except:
                pass

            self._nodes.append(api_node)

        return 1

    # @timeit
    def parse_lines(self, model):
        """Line parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        # In order to parse, we need that opendssdirect was previously run
        if not self.is_opendssdirect_built:
            self.build_opendssdirect(self.DSS_file_names["master"])

        # In OpenDSS, fuses are attached to line objects
        # Here, we get all the line names which have a fuse
        # Even if a fuse is disabled we identify it as a fuse.
        # If the line is disabled we ignore it unless it's a switch
        fuses = _dss_class_to_dict("Fuse")
        fuses_names = [
            d["MonitoredObj"].lower().split(".")[1] for name, d in fuses.items()
        ]

        # In the same way, reclosers are also attached to line objects
        reclosers = _dss_class_to_dict("recloser")
        reclosers_names = [
            d["MonitoredObj"].lower().split(".")[1] for name, d in reclosers.items()
        ]

        start = time.time()
        lines = _dss_class_to_dict("Line")

        middle = time.time()
        logger.debug("Line class to dataframe= {}".format(middle - start))

        N_lines = len(lines)
        self._lines = []

        for name, data in lines.items():

            # Skip Line object if disabled and not a switch
            # (Otherwise it could mean that the switch is open)
            if not data["Switch"] and not data["enabled"]:
                continue

            api_line = Line(model)
            api_line.feeder_name = self.source_name

            # Name
            try:
                line_name = name.split("ine.")[1].lower()
                if line_name not in self.all_object_names:
                    self.all_object_names.append(line_name)
                else:
                    logger.warning(
                        "Duplicate object Line {name}".format(name=line_name)
                    )
                api_line.name = line_name
            except:
                pass

            # Get the linecode if provided
            try:
                linecode = data["linecode"]
            except:
                linecode = None

            api_line.nameclass = linecode

            # If we have a valid linecode, try to get the data
            if linecode is not None:
                linecodes = _dss_class_to_dict("linecode")
                if "linecode." + linecode.lower() in linecodes:
                    linecode_data = linecodes["linecode." + linecode.lower()]
                else:
                    linecode_data = None
            else:
                linecode_data = None

            # Get the distance unit if provided
            try:
                line_unit = data["units"]
            except:
                try:
                    line_unit = linecode_data["units"]
                except:
                    logger.warning(
                        "Could not find the distance unit for line {name}. Using kilometers instead...".format(
                            name=name
                        )
                    )
                    line_unit = u"km"
                    pass
                pass

            if line_unit.lower() not in ["ft", "mi", "m", "km", "kft", "cm", "in"]:
                line_unit = u"km"

            # length
            try:
                length = float(data["length"])
                api_line.length = self.convert_to_meters(length, line_unit)
            except:
                pass

            phases_bus1 = []
            # from_element
            try:
                if "." in data["bus1"]:
                    temp = data["bus1"].split(".")
                    api_line.from_element = temp[0]
                    phases_bus1 = list(map(int, temp[1:]))
                else:
                    api_line.from_element = data["bus1"].strip()
                    phases_bus1 = [1, 2, 3]
            except:
                pass

            phases_bus2 = []
            # to_element
            try:
                if "." in data["bus2"]:
                    temp = data["bus2"].split(".")
                    api_line.to_element = temp[0]
                    phases_bus2 = list(map(int, temp[1:]))
                else:
                    api_line.to_element = data["bus2"].strip()
                    phases_bus2 = [1, 2, 3]
            except:
                pass

            if phases_bus1 != phases_bus2:
                logger.warning(
                    "Phases do not match for line {name}. Bus1={b1}. Bus2={b2}".format(
                        name=name, b1=data["bus1"], b2=data["bus2"]
                    )
                )

            # is_switch
            # try:
            #    api_line.is_switch=int(data['Switch'])
            # except:
            #    pass

            # is_fuse
            # if line_name.replace("(", "").replace(")", "") in fuses_names:
            if line_name in fuses_names:
                api_line.is_fuse = True
                api_line.nameclass = line_name.split("(")[0]
            # is_recloser
            elif line_name in reclosers_names or "recloser" in line_name:
                api_line.is_recloser = True
                api_line.nameclass = line_name.split("(")[0]
            elif "breaker" in line_name:
                api_line.is_breaker = True
                api_line.nameclass = line_name.split("(")[0]
            elif "Switch" in data and data["Switch"]:
                api_line.is_switch = True
                api_line.nameclass = line_name.split("(")[0]

            # faultrate
            if "faultrate" in data:
                try:
                    api_line.faultrate = float(data["faultrate"])
                except:
                    pass
            elif linecode_data is not None and "faultrate" in linecode_data:
                try:
                    api_line.faultrate = float(linecode_data["faultrate"])
                except:
                    pass

            # impedance_matrix
            # We have the Rmatrix and Xmatrix
            if "rmatrix" in data and "xmatrix" in data:
                Rmatrix = data["rmatrix"]
                Xmatrix = data["xmatrix"]
            elif "rmatrix" in linecode_data and "xmatrix" in linecode_data:
                Rmatrix = linecode_data["rmatrix"]
                Xmatrix = linecode_data["xmatrix"]
            else:
                Rmatrix = None
                Xmatrix = None

            # Matrices are in Ohms per some unit distance which is the unit defined in the line
            if line_unit is not None and Rmatrix is not None and Xmatrix is not None:
                try:
                    if (
                        isinstance(Rmatrix, list)
                        and len(Rmatrix) == 1
                        and "|" in Rmatrix[0]
                    ):
                        rowsR = Rmatrix[0].split("|")
                        rowsR = list(map(lambda x: x.strip(), rowsR))
                        new_Rmatrix = []
                        for rowR in rowsR:
                            new_Rmatrix.append([])
                            new_Rmatrix[-1] += list(
                                map(
                                    lambda x: self.convert_to_meters(
                                        float(x.strip()), line_unit, inverse=True
                                    ),
                                    rowR.split(" "),
                                )
                            )
                        new_Rmatrix = self.symmetrize(new_Rmatrix)
                    else:
                        new_Rmatrix = list(
                            map(
                                lambda x: self.convert_to_meters(
                                    float(x), line_unit, inverse=True
                                ),
                                Rmatrix,
                            )
                        )

                    if (
                        isinstance(Xmatrix, list)
                        and len(Xmatrix) == 1
                        and "|" in Xmatrix[0]
                    ):
                        rowsX = Xmatrix[0].split("|")
                        rowsX = list(map(lambda x: x.strip(), rowsX))
                        new_Xmatrix = []
                        for rowX in rowsX:
                            new_Xmatrix.append([])
                            new_Xmatrix[-1] += list(
                                map(
                                    lambda x: self.convert_to_meters(
                                        float(x.strip()), line_unit, inverse=True
                                    ),
                                    rowX.split(" "),
                                )
                            )
                        new_Xmatrix = self.symmetrize(new_Xmatrix)
                    else:
                        new_Xmatrix = list(
                            map(
                                lambda x: self.convert_to_meters(
                                    float(x), line_unit, inverse=True
                                ),
                                Xmatrix,
                            )
                        )
                    new_Rmatrix = np.array(new_Rmatrix)
                    new_Xmatrix = np.array(new_Xmatrix)
                    Z = new_Rmatrix + 1j * new_Xmatrix
                    if Z.ndim == 1:
                        Z = [Z.tolist()]
                    else:
                        Z = Z.tolist()
                    api_line.impedance_matrix = Z
                except:
                    pass

            if "cmatrix" in data:
                Cmatrix = data["cmatrix"]
            elif "cmatrix" in linecode_data:
                Cmatrix = linecode_data["cmatrix"]
            else:
                Cmatrix = None
            if Cmatrix is not None:
                # capacitance matrix
                try:
                    if (
                        isinstance(Cmatrix, list)
                        and len(Cmatrix) == 1
                        and "|" in Cmatrix[0]
                    ):
                        rowsC = Cmatrix[0].split("|")
                        rowsC = list(map(lambda x: x.strip(), rowsC))
                        new_Cmatrix = []
                        for rowC in rowsC:
                            new_Cmatrix.append([])
                            new_Cmatrix[-1] += list(
                                map(
                                    lambda x: self.convert_to_meters(
                                        float(x.strip()), line_unit, inverse=True
                                    ),
                                    rowC.split(" "),
                                )
                            )
                        new_Cmatrix = self.symmetrize(new_Cmatrix)
                    else:
                        new_Cmatrix = list(
                            map(
                                lambda x: self.convert_to_meters(
                                    float(x), line_unit, inverse=True
                                ),
                                Cmatrix,
                            )
                        )
                    new_Cmatrix = np.array(new_Cmatrix)
                    if new_Cmatrix.ndim == 1:
                        new_Cmatrix = [new_Cmatrix.tolist()]
                    else:
                        new_Cmatrix = new_Cmatrix.tolist()
                    api_line.capacitance_matrix = new_Cmatrix
                except:
                    pass

            # Number of phases
            try:
                N_phases = int(data["phases"])
            except:
                N_phases = 3
                pass

            # Try to get the geometry code if it exists
            try:
                line_geometry_code = data["geometry"].lower()
            except:
                line_geometry_code = None
                pass

            # If it is an empty string, convert it to None
            if line_geometry_code == "":
                line_geometry_code = None

            # If we have a geometry code, try to get the corresponding data
            if line_geometry_code is not None:
                try:
                    line_geometries = _dss_class_to_dict("linegeometry")
                    this_line_geometry = line_geometries[
                        "linegeometry.{}".format(line_geometry_code)
                    ]
                except:
                    logger.warning(
                        "Could not get the geometry {line_geom} data of line {line_name}".format(
                            line_geom=line_geometry_code, line_name=name
                        )
                    )
                    this_line_geometry = None
                    pass
            else:
                this_line_geometry = None

            # wires
            # Try to get the number of conductors from the geometry if we have one:
            if this_line_geometry is not None and "nconds" in this_line_geometry:
                number_of_conductors = int(this_line_geometry["nconds"])
            # Otherwise, use the number of phases
            else:
                number_of_conductors = N_phases

            # Initialize empty list to store the wires
            wires = []

            # Loop over the wires and create the Wire DiTTo objects one by one.
            for p in range(number_of_conductors):

                wires.append(Wire(model))

                # Initialize the wire nameclass with the linecode name
                # This is just a best effort to get some information
                # when no wiredata is provided...
                wires[p].nameclass = ""

                if name in fuses_names:
                    wires[p].is_fuse = True
                else:
                    wires[p].is_fuse = False

                if api_line.is_switch is True:
                    wires[p].is_switch = True
                    if data["enabled"] is True:
                        wires[p].is_open = False
                    else:
                        wires[p].is_open = True
                else:
                    wires[p].is_switch = False

                if api_line.is_breaker is True:
                    wires[p].is_breaker = True
                else:
                    wires[p].is_breaker = False

                if api_line.is_recloser is True:
                    wires[p].is_recloser = True
                else:
                    wires[p].is_recloser = False

                # phase
                try:
                    wires[p].phase = self.phase_mapping(phases_bus1[p])
                except:
                    # Handles the neutral
                    if p >= len(phases_bus1):
                        wires[p].phase = "N"
                    pass

                # normamps
                try:
                    wires[p].ampacity = float(data["normamps"])
                except:
                    pass

                # emergamps
                try:
                    wires[p].emergency_ampacity = float(data["emergamps"])
                except:
                    pass

                # If we have linegeometry data, we can do something
                if this_line_geometry is not None:

                    # nameclass
                    try:
                        wires[p].nameclass = this_line_geometry["wires"][0].split(" ")[
                            p
                        ]
                    except:
                        pass

                    # Get the unit for the distances
                    # NOTE: It is possible to specify different units for the different wires
                    # Get the units from the list.
                    if isinstance(this_line_geometry["units"], list):
                        line_geometry_unit = this_line_geometry["units"][p]
                    elif isinstance(this_line_geometry["units"], str):
                        line_geometry_unit = this_line_geometry["units"]
                    else:
                        logger(
                            "Could not find the lineGeometry distance unit for line {name}.".format(
                                name=name
                            )
                        )
                        if unit is not None:
                            logger.info(
                                "Using the line unit instead: {unit}".format(unit=unit)
                            )
                            line_geometry_unit = unit
                        # If we do not have units for the line either, then w'd rather set everything to None...
                        else:
                            line_geometry_unit = None

                    # X
                    # If we have a valid distance unit
                    if line_geometry_unit is not None:
                        if "x" in this_line_geometry:
                            if isinstance(this_line_geometry["x"], list):
                                try:
                                    geom_x = float(this_line_geometry["x"][p])
                                except:
                                    geom_x = None
                                    pass
                            elif isinstance(this_line_geometry["x"], (str, int, float)):
                                geom_x = float(this_line_geometry["x"])
                            else:
                                geom_x = None

                            try:
                                wires[p].X = self.convert_to_meters(
                                    geom_x, line_geometry_unit
                                )
                            except:
                                pass

                    # Y
                    # If we have a valid distance unit
                    if line_geometry_unit is not None:
                        if "h" in this_line_geometry:
                            if isinstance(this_line_geometry["h"], list):
                                try:
                                    geom_y = float(this_line_geometry["h"][p])
                                except:
                                    geom_y = None
                                    pass
                            elif isinstance(this_line_geometry["h"], (str, int, float)):
                                geom_y = float(this_line_geometry["h"])
                            else:
                                geom_y = None
                            try:
                                wires[p].Y = self.convert_to_meters(
                                    geom_y, line_geometry_unit
                                )
                            except:
                                pass

                    # Check if we have wireData that we can use
                    if "wires" in this_line_geometry:
                        if isinstance(this_line_geometry["wires"], list):
                            if (
                                len(this_line_geometry["wires"]) == 1
                                and " " in this_line_geometry["wires"][0]
                            ):
                                this_line_wireData_code = (
                                    this_line_geometry["wires"][0].split(" ")[p].lower()
                                )
                            else:
                                try:
                                    this_line_wireData_code = this_line_geometry[
                                        "wires"
                                    ][p].lower()
                                except:
                                    this_line_wireData_code = None
                                    pass
                        elif isinstance(this_line_geometry["wires"], str):
                            this_line_wireData_code = this_line_geometry["wires"]
                        else:
                            this_line_wireData_code = None
                        if (
                            this_line_wireData_code is None
                            and "wire" in this_line_geometry
                            and isinstance(this_line_geometry["wire"], str)
                        ):
                            this_line_wireData_code = this_line_geometry["wire"]

                    # If empty, convert it to None
                    if this_line_wireData_code == "":
                        this_line_wireData_code = None

                    # Try to get the Wire data for this lineGeometry
                    is_cable = False
                    if this_line_wireData_code is not None:
                        try:
                            all_wire_data = _dss_class_to_dict("wiredata")
                            CNData = _dss_class_to_dict("CNData")
                            for cnname, cnvalues in CNData.items():
                                if this_line_wireData_code == cnname.split(".")[1]:
                                    is_cable = True
                                    this_line_wireData = CNData[
                                        "CNData.{}".format(cnname.split(".")[1])
                                    ]
                                    api_line.line_type = "underground"
                            if is_cable is False:
                                this_line_wireData = all_wire_data[
                                    "wiredata.{}".format(this_line_wireData_code)
                                ]
                                api_line.line_type = "overhead"
                        except:
                            logger.warning(
                                "Could not get the wireData {wiredata} of lineGeometry {line_geom}".format(
                                    wiredata=this_line_wireData_code,
                                    line_geom=this_line_geometry,
                                )
                            )
                            pass
                    else:
                        this_line_wireData = None

                    # If we have valid WireData
                    if this_line_wireData is not None:

                        # Get the unit for the radius distance
                        try:
                            wire_radius_unit = this_line_wireData["radunits"]
                        # If not present, assume the same unit as the lineGeometry
                        except:
                            logger(
                                "Could not find the wireData radius distance unit for Wiredata {name}.".format(
                                    name=this_line_wireData_code
                                )
                            )
                            if line_geometry_unit is not None:
                                logger.info(
                                    "Using the lineGeometry unit instead: {unit}".format(
                                        unit=line_geometry_unit
                                    )
                                )
                                wire_radius_unit = line_geometry_unit
                            # If we do not have units for the line either, then w'd rather set everything to None...
                            else:
                                wire_radius_unit = None
                            pass

                        # diameter
                        # If we have valid wiredata radius distance unit
                        if wire_radius_unit is not None:
                            try:
                                wires[p].diameter = self.convert_to_meters(
                                    float(this_line_wireData["diam"]), wire_radius_unit
                                )
                            except:
                                pass

                        # Get the unit for the GMR
                        try:
                            wire_gmr_unit = this_line_wireData["GMRunits"]
                        # If not present, assume the same unit as the lineGeometry
                        except:
                            logger(
                                "Could not find the wireData GMR distance unit for Wiredata {name}.".format(
                                    name=this_line_wireData_code
                                )
                            )
                            if line_geometry_unit is not None:
                                logger.info(
                                    "Using the lineGeometry unit instead: {unit}".format(
                                        unit=line_geometry_unit
                                    )
                                )
                                wire_gmr_unit = line_geometry_unit
                            # If we do not have units for the line either, then w'd rather set everything to None...
                            else:
                                wire_gmr_unit = None
                            pass

                        # gmr
                        # If we have valid wiredata GMR distance unit
                        if wire_gmr_unit is not None:
                            try:
                                wires[p].gmr = self.convert_to_meters(
                                    float(this_line_wireData["GMRac"]), wire_gmr_unit
                                )
                            except:
                                pass

                        # ampacity
                        try:
                            wires[p].ampacity = float(this_line_wireData["normamps"])
                        except:
                            pass

                        if wires[p].ampacity == -1 or wires[p].ampacity == 0:
                            wires[p].ampacity = None

                        # ampacity emergency
                        try:
                            wires[p].emergency_ampacity = float(
                                this_line_wireData["emergamps"]
                            )
                        except:
                            pass

                        if (
                            wires[p].emergency_ampacity == -1
                            or wires[p].emergency_ampacity == 0
                        ):
                            wires[p].emergency_ampacity = None

                        # resistance
                        # Should be Rac*length_of_line
                        # Rac is in ohms per Runits
                        # We have to make sure that the line length is in the same unit
                        #
                        # First, check if we have a valid line length, otherwise there is no point...
                        if api_line.length is not None:
                            # Try to get the per unit resistance
                            try:
                                Rac = float(this_line_wireData["Rac"])
                            except:
                                Rac = None
                                pass
                            # If we succeed...
                            if Rac is not None:
                                # Try to get the distance unit for the resistance
                                try:
                                    Runits = this_line_wireData["Runits"]
                                # If not present, assume it is the same as the line unit
                                # But log this, because it might not be the case. Assume the user is responsible here....
                                except:
                                    logger.warning(
                                        "Could not find the resistance unit for wire {wire}".format(
                                            wire=this_line_wireData_code
                                        )
                                    )
                                    if unit is not None:
                                        logger.info(
                                            "Using line length unit instead: {unit}".format(
                                                unit=unit
                                            )
                                        )
                                        Runits = unit
                                    else:
                                        Runits = None
                                    pass
                                # If we have a valid unit for the resistance
                                if Runits is not None:
                                    wires[p].resistance = (
                                        self.convert_to_meters(
                                            Rac, Runits, inverse=True
                                        )
                                        * api_line.length
                                    )
                    if wires[p].ampacity is None and "normamps" in data:
                        try:
                            wires[p].ampacity = float(data["normamps"])
                        except:
                            pass

                    if wires[p].ampacity == -1 or wires[p].ampacity == 0:
                        wires[p].ampacity = None

                    if wires[p].emergency_ampacity is None and "emergamps" in data:
                        try:
                            wires[p].emergency_ampacity = float(data["emergamps"])
                        except:
                            pass

                    if (
                        wires[p].emergency_ampacity == -1
                        or wires[p].emergency_ampacity == 0
                    ):
                        wires[p].emergency_ampacity = None

                    # is_switch
                    wires[p].is_switch = api_line.is_switch

                    # Concentric Neutral
                    if is_cable == True:
                        cndata = _dss_class_to_dict("CNData")
                        if cndata is not None:
                            for name, data in cndata.items():
                                try:
                                    gmr_unit = data["GMRunits"]
                                except:
                                    logger(
                                        "Could not find the GMRunits for {name}.".format(
                                            name=name
                                        )
                                    )
                                if gmr_unit is not None:
                                    try:
                                        wires[
                                            p
                                        ].concentric_neutral_gmr = self.convert_to_meters(
                                            float(data["GmrStrand"]), gmr_unit
                                        )
                                    except:
                                        logger("Could not convert to GMRunits")

                                try:
                                    r_unit = data["Runits"]
                                except:
                                    logger(
                                        "Could not find the Runits for {name}.".format(
                                            name=name
                                        )
                                    )
                                if r_unit is not None:
                                    try:
                                        wires[
                                            p
                                        ].concentric_neutral_resistance = self.convert_to_meters(
                                            float(data["Rstrand"]), r_unit
                                        )
                                    except:
                                        logger("Could not convert to  Runits")

                                try:
                                    rad_unit = data["radunits"]
                                except:
                                    logger(
                                        "Could not find the Radunits for {name}.".format(
                                            name=name
                                        )
                                    )
                                if rad_unit is not None:
                                    try:
                                        wires[
                                            p
                                        ].concentric_neutral_diameter = self.convert_to_meters(
                                            float(data["DiaStrand"]), data["radunits"]
                                        )
                                        wires[
                                            p
                                        ].concentric_neutral_outside_diameter = self.convert_to_meters(
                                            float(data["DiaCable"]), data["radunits"]
                                        )
                                        wires[
                                            p
                                        ].insulation_thickness = self.convert_to_meters(
                                            float(data["InsLayer"]), data["radunits"]
                                        )
                                    except:
                                        logger("Could not convert to radunits")
                                wires[p].concentric_neutral_nstrand = int(data["k"])

            api_line.wires = wires
            self._lines.append(api_line)

        end = time.time()
        logger.debug("rest= {}".format(end - middle))
        return 1

    @timeit
    def parse_transformers(self, model):
        """Transformer parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """

        transformers = _dss_class_to_dict("transformer")
        self._transformers = []

        for name, data in transformers.items():

            # Skip Transformer object if disabled
            if not data["enabled"]:
                continue

            api_transformer = PowerTransformer(model)
            api_transformer.feeder_name = self.source_name

            # Name
            try:
                trans_name = name.split("ransformer.")[1].lower()
                if trans_name not in self.all_object_names:
                    self.all_object_names.append(trans_name)
                else:
                    logger.warning(
                        "Duplicate object Transformer {name}".format(
                            name=transformer_name
                        )
                    )
                api_transformer.name = trans_name
            except:
                pass

            # Loadloss
            try:
                api_transformer.loadloss = float(
                    data["%loadloss"]
                )  # DiTTo in volt ampere
            except:
                pass

            if "sub" in data and data["sub"] == "Yes":
                api_transformer.is_substation = True

            # normhkva
            try:
                # DiTTo in volt ampere
                api_transformer.normhkva = float(data["normhkVA"])
            except:
                pass

            # noload_loss
            try:
                api_transformer.noload_loss = float(data["%noloadloss"])
            except:
                pass

            # from_element and to_element
            try:
                bus_data = data["buses"]
                if len(bus_data) == 2:
                    b1, b2 = bus_data
                    if "." in b1:
                        temp = b1.split(".")
                        b1_name = temp[0]
                        b1_phases = temp[1:]
                    else:
                        b1_name = b1
                        b1_phases = [1, 2, 3]
                    if "." in b2:
                        temp = b2.split(".")
                        b2_name = temp[0]
                        b2_phases = temp[1:]
                    else:
                        b2_name = b2
                        b2_phases = [1, 2, 3]
                if len(bus_data) == 3:
                    b1, b2, b3 = bus_data
                    if "." in b1:
                        temp = b1.split(".")
                        b1_name = temp[0]
                        b1_phases = temp[1:]
                    else:
                        b1_name = b1
                        b1_phases = [1, 2, 3]
                    if "." in b2:
                        temp = b2.split(".")
                        b2_name = temp[0]
                        b2_phases = temp[1:]
                    else:
                        b2_name = b2
                        b2_phases = [1, 2, 3]
                    if "." in b3:
                        temp = b3.split(".")
                        b3_name = temp[0]
                        b3_phases = temp[1:]
                    else:
                        b3_name = b3
                        b3_phases = [1, 2, 3]
                api_transformer.from_element = b1_name
                api_transformer.to_element = b2_name
            except:
                pass

            # windings
            windings = []
            try:
                N_windings = int(data["windings"])
            except:
                N_windings = 2
                pass

            # reactances
            if "Xscarray" in data:
                try:
                    eph = list(map(lambda x: float(x), data["Xscarray"]))
                    for x in eph:
                        api_transformer.reactances.append(x)
                except:
                    pass

            elif N_windings == 1 and "XHL" in data:
                api_transformer.reactances = [float(data["XHL"])]
            elif N_windings == 2:
                api_transformer.reactances = []
                if "XHL" in data:
                    api_transformer.reactances.append(float(data["XHL"]))
                if "XLT" in data:
                    api_transformer.reactances.append(float(data["XLT"]))
                if "XHT" in data:
                    api_transformer.reactances.append(float(data["XHT"]))
            # Number of phases
            try:
                N_phases = int(data["phases"])
            except:
                N_phases = 3
                pass

            # If we have a one phase 3 winding transformer in OpenDSS, it should represent a 2 winding center tap transformer
            if N_windings == 3 and N_phases == 1:
                api_transformer.is_center_tap = True

            if not 1 <= N_phases <= 3:
                logger.warning(
                    "Number of phases should be between 1 and 3, got {N} for transformer {name}".format(
                        N=N_phases, name=name
                    )
                )

            if (
                N_windings >= 2
                and data["conns"][0].lower() == "wye"
                and data["conns"][1].lower() == "wye"
            ):
                api_transformer.phase_shift = 0

            if (
                N_windings >= 2
                and data["conns"][0].lower() == "delta"
                and data["conns"][1].lower() == "delta"
            ):
                api_transformer.phase_shift = 0

            if (
                N_windings >= 2
                and data["conns"][0].lower() == "wye"
                and data["conns"][1].lower() == "delta"
            ):
                api_transformer.phase_shift = -30

            if (
                N_windings >= 2
                and data["conns"][0].lower() == "delta"
                and data["conns"][1].lower() == "wye"
            ):
                api_transformer.phase_shift = -30

            for w in range(N_windings):

                windings.append(Winding(model))

                # connection type
                try:
                    if data["conns"][w].lower() == "wye":
                        windings[w].connection_type = "Y"
                    elif data["conns"][w].lower() == "delta":
                        windings[w].connection_type = "D"
                except:
                    pass

                # rated power
                # rated_power removed from powerTransformer and added to Winding by Nicolas
                try:
                    windings[w].rated_power = (
                        float(data["kVAs"][w]) * 10 ** 3
                    )  # DiTTo in volt ampere
                except:
                    windings[w].rated_power = None
                    pass

                # emergency_power
                # emergency_power removed from powerTransformer and added to Winding by Tarek
                try:
                    windings[w].emergency_power = (
                        float(data["emerghkVA"]) * 10 ** 3
                    )  # DiTTo in volt ampere
                except:
                    windings[w].emergency_power = None
                    pass

                # nominal_voltage
                try:
                    windings[w].nominal_voltage = (
                        float(data["kVs"][w]) * 10 ** 3
                    )  # DiTTo in Volts
                except:
                    pass

                # resistance
                try:
                    windings[w].resistance = float(data["%Rs"][w])
                except:
                    pass

                if ".0" in data["buses"][w] and N_windings == 2:
                    windings[w].is_grounded = True
                else:
                    windings[w].is_grounded = False

                phase_windings = []
                # need to use info from the bus since N_phases may not match number of connections
                for p in range(len(b1_phases)):

                    phase_windings.append(PhaseWinding(model))

                    # tap position
                    if "taps" in data:
                        try:
                            phase_windings[p].tap_position = float(data["taps"][w])
                        except:
                            pass
                    elif "tap" in data:
                        try:
                            phase_windings[p].tap_position = float(data["tap"])
                        except:
                            pass

                    # phase
                    try:
                        phase_windings[p].phase = self.phase_mapping(b1_phases[p])
                    except:
                        pass

                    regulators = _dss_class_to_dict("RegControl")
                    for reg_name, reg_data in regulators.items():

                        if (
                            "transformer" in reg_data
                            and reg_data["transformer"].lower()
                            == api_transformer.name.lower()
                        ):
                            if "R" in reg_data:
                                phase_windings[p].compensator_r = float(reg_data["R"])
                            if "X" in reg_data:
                                phase_windings[p].compensator_x = float(reg_data["X"])

                # Store the phase winding objects in the winding objects
                for pw in phase_windings:
                    windings[w].phase_windings.append(pw)

            # Voltage Type
            if N_windings == 2:
                if float(data["kVs"][0]) >= float(data["kVs"][1]):
                    windings[0].voltage_type = 0
                    windings[1].voltage_type = 2
                else:
                    windings[0].voltage_type = 2
                    windings[1].voltage_type = 0
            elif N_windings == 3:
                if float(data["kVs"][0]) == max(list(map(float, data["kVs"]))):
                    windings[0].voltage_type = 0
                    windings[1].voltage_type = 2
                    windings[2].voltage_type = 2
                elif float(data["kVs"][1]) == max(list(map(float, data["kVs"]))):
                    windings[0].voltage_type = 2
                    windings[1].voltage_type = 0
                    windings[2].voltage_type = 2
                else:
                    windings[0].voltage_type = 2
                    windings[1].voltage_type = 2
                    windings[2].voltage_type = 0

            # Store the winding objects in the transformer object
            for ww in windings:
                api_transformer.windings.append(ww)
            self._transformers.append(api_transformer)
        return 1

    @timeit
    def parse_regulators(self, model):
        """Regulator parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        regulators = _dss_class_to_dict("RegControl")
        transformers = _dss_class_to_dict("Transformer")
        self._regulators = []

        for name, data in regulators.items():

            # Skip Regulator object if disabled
            if not data["enabled"]:
                continue

            api_regulator = Regulator(model)

            api_regulator.feeder_name = self.source_name

            # Name
            try:
                reg_name = "regulator_" + name.split(".")[1].lower()
                if reg_name not in self.all_object_names:
                    self.all_object_names.append(reg_name)
                else:
                    logger.warning(
                        "Duplicate object Regulator {name}".format(name=reg_name)
                    )
                api_regulator.name = reg_name
            except:
                pass

            # winding(number of the winding of the transformer element that the RegControl is monitoring)
            try:
                winding = int(data["winding"])
                api_regulator.winding = winding
            except:
                pass

            # windings (The actual Windings Ditto objects)
            #
            # We need the transformer data first
            if (
                "transformer" in data
                and "Transformer.{}".format(data["transformer"].lower()) in transformers
            ):
                trans = transformers[
                    "Transformer.{}".format(data["transformer"].lower())
                ]

                # Total number of windings
                N_windings = int(trans["windings"])
                if (
                    N_windings >= 2
                    and trans["conns"][0].lower() == "wye"
                    and trans["conns"][1].lower() == "wye"
                ):
                    api_regulator.phase_shift = 0

                if (
                    N_windings >= 2
                    and trans["conns"][0].lower() == "delta"
                    and trans["conns"][1].lower() == "delta"
                ):
                    api_regulator.phase_shift = 0

                if (
                    N_windings >= 2
                    and trans["conns"][0].lower() == "wye"
                    and trans["conns"][1].lower() == "delta"
                ):
                    api_regulator.phase_shift = -30

                if (
                    N_windings >= 2
                    and trans["conns"][0].lower() == "delta"
                    and trans["conns"][1].lower() == "wye"
                ):
                    api_regulator.phase_shift = -30

                # Initialize the list of Windings
                api_regulator.windings = [Winding(model) for _ in range(N_windings)]

                # Connection type
                for w in range(N_windings):
                    if "conns" in trans:
                        try:
                            api_regulator.windings[w].connection_type = trans["conns"][
                                w
                            ]
                        except:
                            pass

                    try:
                        if trans["conns"][w].lower() == "wye":
                            api_regulator.windings[w].connection_type = "Y"
                        elif trans["conns"][w].lower() == "delta":
                            api_regulator.windings[w].connection_type = "D"
                    except:
                        pass

                # nominal_voltage
                for w in range(N_windings):
                    if "kVs" in trans:
                        try:
                            api_regulator.windings[w].nominal_voltage = (
                                float(trans["kVs"][w]) * 10 ** 3
                            )  # DiTTo in Volts
                        except:
                            pass

                # resistance
                for w in range(N_windings):
                    if "%Rs" in trans:
                        try:
                            api_regulator.windings[w].resistance = float(
                                trans["%Rs"][w]
                            )
                        except:
                            pass

                # rated_power
                for w in range(N_windings):
                    if "kVAs" in trans:
                        try:
                            api_regulator.windings[w].rated_power = (
                                float(trans["kVAs"][w]) * 10 ** 3
                            )  # DiTTo in volt ampere
                        except:
                            pass

                # emergency_power
                for w in range(N_windings):
                    if "emerghkVA" in trans:
                        try:
                            api_regulator.windings[w].emergency_power = (
                                float(trans["emerghkVA"]) * 10 ** 3
                            )  # DiTTo in volt ampere
                        except:
                            pass

                # phase_windings
                for w in range(N_windings):
                    # Get the phase
                    if "buses" in trans:
                        try:
                            bus = trans["buses"][w]
                        except:
                            pass
                        if "." in bus:
                            temp = bus.split(".")
                            bus_name, phases = temp[0], temp[1:]
                        else:
                            phases = ["1", "2", "3"]
                    else:
                        phases = ["1", "2", "3"]

                    api_regulator.windings[w].phase_windings = [
                        PhaseWinding(model) for _ in phases
                    ]

                    for p, phase in enumerate(phases):
                        # phase
                        api_regulator.windings[w].phase_windings[
                            p
                        ].phase = self.phase_mapping(phase)

                        # tap_position
                        if "taps" in trans:
                            api_regulator.windings[w].phase_windings[
                                p
                            ].tap_position = float(trans["taps"][w])

                        elif "TapNum" in data:
                            api_regulator.windings[w].phase_windings[
                                p
                            ].tap_position = float(data["TapNum"])

                        # compensator_r
                        if "R" in data:
                            try:
                                api_regulator.windings[w].phase_windings[
                                    p
                                ].compensator_r = float(data["R"])
                            except:
                                pass

                        # compensator_x
                        if "X" in data:
                            try:
                                api_regulator.windings[w].phase_windings[
                                    p
                                ].compensator_x = float(data["X"])
                            except:
                                pass

            else:
                logger.warning(
                    "Could not find the transformer data for regulator {name}".format(
                        name=name
                    )
                )

            # Voltage Type
            if N_windings == 2:
                if float(trans["kVs"][0]) >= float(trans["kVs"][1]):
                    api_regulator.windings[0].voltage_type = 0
                    api_regulator.windings[1].voltage_type = 2
                else:
                    api_regulator.windings[0].voltage_type = 2
                    api_regulator.windings[1].voltage_type = 0
            elif N_windings == 3:
                if float(trans["kVs"][0]) == max(list(map(float, trans["kVs"]))):
                    api_regulator.windings[0].voltage_type = 0
                    api_regulator.windings[1].voltage_type = 2
                    api_regulator.windings[2].voltage_type = 2
                elif float(trans["kVs"][1]) == max(list(map(float, trans["kVs"]))):
                    api_regulator.windings[0].voltage_type = 2
                    api_regulator.windings[1].voltage_type = 0
                    api_regulator.windings[2].voltage_type = 2
                else:
                    api_regulator.windings[0].voltage_type = 2
                    api_regulator.windings[1].voltage_type = 2
                    api_regulator.windings[2].voltage_type = 0

            # CTprim
            try:
                api_regulator.ct_prim = float(data["CTprim"])
            except:
                pass

            # noload_loss
            try:
                api_regulator.noload_loss = float(data["%noloadloss"])
            except:
                pass

            # delay
            try:
                api_regulator.delay = float(data["delay"])
            except:
                pass

            # highstep
            try:
                api_regulator.highstep = int(data["maxtapchange"])
            except:
                pass

            # lowstep
            try:
                api_regulator.lowstep = api_regulator.highstep
            except:
                pass

            # setpoint
            try:
                api_regulator.setpoint = int(data["vreg"])
            except:
                pass

            # pt_ratio
            try:
                api_regulator.pt_ratio = float(data["ptratio"])
            except:
                pass

            # bandwidth
            try:
                api_regulator.bandwidth = float(data["band"])
            except:
                pass

            # bandcenter
            try:
                api_regulator.bandcenter = float(data["vreg"])
            except:
                pass

            # voltage_limit
            try:
                api_regulator.voltage_limit = float(data["vlimit"])
            except:
                pass

            # connected_transformer
            try:
                api_regulator.connected_transformer = data["transformer"].lower()
            except:
                pass

            # Some data needed in ditto can only be accessed through the connected transformer.
            # Therefore, transformers need to be parsed first.
            # Searching for the transformer object:
            if api_regulator.connected_transformer is not None:
                for trans in self._transformers:
                    if trans.name == api_regulator.connected_transformer:
                        # from_element
                        api_regulator.from_element = trans.from_element

                        # to_element
                        api_regulator.to_element = trans.to_element

                        # reactances
                        api_regulator.reactances = trans.reactances

                        break

            # pt_phase
            try:
                api_regulator.pt_phase = self.phase_mapping(
                    phases[int(data["PTphase"]) - 1]
                )
            except:
                pass

            self._regulators.append(api_regulator)

        return 1

    @timeit
    def parse_capacitors(self, model):
        """Capacitor parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        capacitors = _dss_class_to_dict("capacitor")
        cap_control = _dss_class_to_dict("CapControl")
        self._capacitors = []

        for name, data in capacitors.items():
            # Skip Capacitor object if disabled
            if not data["enabled"]:
                continue

            api_capacitor = Capacitor(model)

            api_capacitor.feeder_name = self.source_name

            # Name
            try:
                cap_name = name.split("apacitor.")[1].lower()
                if cap_name not in self.all_object_names:
                    self.all_object_names.append(cap_name)
                else:
                    logger.warning(
                        "Duplicate object Capacitor {name}".format(name=cap_name)
                    )
                api_capacitor.name = cap_name
            except:
                pass

            # Nominal voltage
            try:
                api_capacitor.nominal_voltage = (
                    float(data["kv"]) * 10 ** 3
                )  # DiTTo in volts
            except:
                pass

            # connection_type
            try:
                if data["conn"].lower() == "wye":
                    api_capacitor.connection_type = "Y"
                elif data["conn"].lower() == "delta":
                    api_capacitor.connection_type = "D"
            except:
                pass

            control_id = None
            # Find the capControl that corresponds to the capacitor if any
            for capc_name, capc_data in cap_control.items():
                if capc_data["capacitor"].lower() == api_capacitor.name:
                    control_id = capc_name
                    break

            # delay
            try:
                api_capacitor.delay = float(cap_control[control_id]["Delay"])
            except:
                pass

            # Measuring element
            try:
                api_capacitor.measuring_element = cap_control[control_id]["element"]
            except:
                pass

            # mode
            try:
                if cap_control[control_id]["type"] == "volt":
                    api_capacitor.mode = "voltage"
                elif cap_control[control_id]["type"] == "current":
                    api_capacitor.mode = "currentFlow"
                elif cap_control[control_id]["type"] == "kvar":
                    api_capacitor.mode = "reactivePower"
                elif cap_control[control_id]["type"] == "PF":
                    api_capacitor.mode = None
                elif cap_control[control_id]["type"] == "time":
                    api_capacitor.mode = "timeScheduled"
            except:
                pass

            # low
            if control_id is not None:
                try:
                    api_capacitor.low = float(cap_control[control_id]["Vmin"])
                except:
                    pass

            # High
            if control_id is not None:
                try:
                    api_capacitor.high = float(cap_control[control_id]["Vmax"])
                except:
                    pass

            # resistance
            try:
                api_capacitor.resistance = sum(map(lambda x: float(x), data["R"]))
            except:
                pass

            # reactance
            try:
                api_capacitor.reactance = sum(map(lambda x: float(x), data["XL"]))
            except:
                pass

            # PT ratio
            if control_id is not None:
                try:
                    api_capacitor.pt_ratio = float(cap_control[control_id]["PTratio"])
                except:
                    pass

            # CT ratio
            if control_id is not None:
                try:
                    api_capacitor.ct_ratio = float(cap_control[control_id]["CTratio"])
                except:
                    pass

            # PT phase
            if control_id is not None:
                try:
                    api_capacitor.pt_phase = self.phase_mapping(
                        int(cap_control[control_id]["PTPhase"])
                    )
                except:
                    pass

            # connecting element
            try:
                if "." in data["bus1"]:
                    temp = data["bus1"].split(".")
                    b_name = temp[0]
                    phases = temp[1:]
                else:
                    b_name = data["bus1"]
                    phases = [1, 2, 3]
                api_capacitor.connecting_element = b_name
            except:
                b_name = None
                phases = None
                pass

            # N_phases
            try:
                N_phases = int(data["phases"])
            except:
                N_phases = None
                pass

            if phases is None and N_phases == 3:
                phases = [1, 2, 3]

            if N_phases is None and api_capacitor.pt_phase is not None:
                N_phases = 1

            if phases is not None and N_phases is not None:

                # Phase capacitors
                phase_capacitors = []
                for p, pha in enumerate(phases):
                    phase_capacitors.append(PhaseCapacitor(model))

                    # phase
                    if (
                        api_capacitor.pt_phase is not None
                        and api_capacitor.pt_phase == self.phase_mapping(pha)
                    ):
                        phase_capacitors[p].phase = api_capacitor.pt_phase
                    else:
                        phase_capacitors[p].phase = self.phase_mapping(pha)

                    # var
                    list_data = data["kvar"]
                    if isinstance(list_data, list) and len(list_data) == len(phases):
                        try:
                            phase_capacitors[p].var = (
                                float(list_data[p]) * 10 ** 3
                            )  # DiTTo in var
                        except:
                            pass
                    elif isinstance(list_data, list):
                        try:
                            phase_capacitors[p].var = (
                                float(list_data[0]) / float(N_phases) * 10 ** 3
                            )  # DiTTo in var
                        except:
                            pass
                    else:
                        try:
                            phase_capacitors[p].var = (
                                float(list_data) / float(N_phases) * 10 ** 3
                            )  # DiTTo in var
                        except:
                            pass

                api_capacitor.phase_capacitors = phase_capacitors

            self._capacitors.append(api_capacitor)

        return 1

    @timeit
    def parse_loads(self, model):
        """Load parser.

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        loads = _dss_class_to_dict("Load")
        self._loads = []

        for name, data in loads.items():

            # Skip Load object if disabled
            if not data["enabled"]:
                continue

            api_load = Load(model)
            api_load.feeder_name = self.source_name

            # Name
            try:
                # load_name=name.split('oad.')[1].lower()
                load_name = "load_" + name.split("oad.")[1].lower()
                if load_name not in self.all_object_names:
                    self.all_object_names.append(load_name)
                else:
                    logger.warning(
                        "Duplicate object Load {name}".format(name=load_name)
                    )
                api_load.name = load_name
            except:
                pass

            # Connecting_element
            try:
                api_load.connecting_element = data["bus1"]
            except:
                pass

            # nominal voltage
            try:
                api_load.nominal_voltage = float(data["kV"]) * 10 ** 3  # DiTTo in volts
            except:
                pass

            try:
                api_load.num_users = float(data["NumCust"])
            except:
                pass

            # connection_type
            try:
                conn = data["conn"]
                if conn.lower() == "wye":
                    api_load.connection_type = "Y"
                elif conn.lower() == "delta":
                    api_load.connection_type = "D"
            except:
                pass

            # vmin
            try:
                api_load.vmin = float(data["Vminpu"])
            except:
                pass

            # vmax
            try:
                api_load.vmax = float(data["Vmaxpu"])
            except:
                pass

            # Get the number of phases
            try:
                N_phases = int(data["phases"])
            except:
                N_phases = 1
                pass

            # Get the actual phase numbers (in the connection data)
            try:
                if "." in data["bus1"]:
                    temp = data["bus1"].split(".")
                    bus = temp[0]
                    phases = list(map(lambda x: int(x), temp[1:]))
                else:
                    bus = data["bus1"]
                    phases = ["A", "B", "C"]
                api_load.connecting_element = bus
            except:
                bus = None
                phases = []
                pass

            # Now, we can have N_phases different from len(phases) for 3 reasons:
            #    - There is an error (in this case, raise an error...)
            #    - One of them is None because not given by the model
            #      There are 3 subcases:
            #            - N_phases=None AND phases=None ==> raise an error...
            #            - N_phases=None ==> just reset N_phases=len(phases)
            #            - phases=None   ==> if N_phases==3, then phases=[A,B,C], otherwise
            #                                raise an error because we cannot just guess the correct phases...
            #    - The connection is Delta
            #        In this case, we should create the correct number of phase loads and make sure
            #        the connection information will be handled correctly

            if N_phases != len(phases):
                if N_phases is None and phases is None:
                    logger.warning(
                        "No Phase information for load {name}".format(name=name)
                    )
                elif N_phases is None and phases is not None:
                    N_phases = len(phases)
                elif phases is None and N_phases == 3:
                    phases = ["A", "B", "C"]
                elif phases is None and N_phases != 3:
                    logger.warning(
                        "No Phase information for load {name}".format(name=name)
                    )
                elif api_load.connection_type == "D":
                    phases = phases[:N_phases]
                else:
                    logger.warning(
                        "Phases do not match for load {name}".format(name=name)
                    )

            # Get the kW if present
            try:
                kW = float(data["kW"])
            except:
                kW = None
                pass

            # Get the kva if present
            try:
                kva = float(data["kVA"])
            except:
                kva = None
                pass

            # Get the power factor if present
            try:
                pf = float(data["pf"])
            except:
                pf = None
                pass

            try:
                load_model = int(data["model"])
            except:
                load_model = None
                pass

            # Phase Loads
            kW /= float(len(phases))  # Load assumed balanced
            kva /= float(len(phases))  # Load assumed balanced

            _phase_loads = []

            for i, p in enumerate(phases):

                _phase_loads.append(PhaseLoad(model))
                _phase_loads[i].phase = self.phase_mapping(p)

                # Case one: KW and pf
                if kW is not None and pf is not None:
                    _phase_loads[i].p = kW * 10 ** 3  # DiTT0 in watts
                    _phase_loads[i].q = (
                        kW * 10 ** 3 * np.sqrt(1 - pf ** 2)
                    ) / pf  # DiTT0 in var

                # Case two: kvar and pf
                elif kva is not None and pf is not None:
                    # Handle the special case where pf=1
                    if pf == 1:
                        # in this case, pure reactive power
                        _phase_loads[i].p = 0.0
                    else:
                        _phase_loads[i].p = (pf * kvar * 10 ** 3) / np.sqrt(
                            1 - pf ** 2
                        )  # DiTT0 in watts
                    _phase_loads[i].q = kva * 10 ** 3  # DiTT0 in var

                # Case three kW and kvar
                elif kW is not None and kva is not None:
                    _phase_loads[i].p = kW * 10 ** 3  # DiTT0 in Watts
                    _phase_loads[i].q = kvar * 10 ** 3  # DiTT0 in var

                # Try to get the model
                try:
                    _model = int(data["model"])
                except:
                    _model = None
                    pass

                if load_model is not None:
                    _phase_loads[i].model = load_model

                # ZIPV model (model==8)
                if _model == 8:
                    # Try to get the ZIPV coefficients
                    try:
                        ZIPV = list(map(lambda x: float(x), data["ZIPV"].split()))
                    except:
                        ZIPV = None
                        pass

                    # If we have valid coefficients
                    if ZIPV is not None:
                        _phase_loads[i].use_zip = True

                        if not np.allclose(sum(ZIPV[:3]), 1.0) or not np.allclose(
                            sum(ZIPV[3:-1]), 1.0
                        ):
                            logger.warning(
                                "ZIPV coefficients for load {name} do not sum properly".format(
                                    name=name
                                )
                            )

                        _phase_loads[i].ppercentcurrent = ZIPV[1] * 100
                        _phase_loads[i].qpercentcurrent = ZIPV[4] * 100
                        _phase_loads[i].ppercentpower = ZIPV[2] * 100
                        _phase_loads[i].qpercentpower = ZIPV[5] * 100
                        _phase_loads[i].ppercentimpedance = ZIPV[0] * 100
                        _phase_loads[i].qpercentimpedance = ZIPV[3] * 100
                else:
                    _phase_loads[i].use_zip = False

            api_load.phase_loads = _phase_loads
            self._loads.append(api_load)

        return 1

    def parse_storage(self, model):
        """Parse the storages."""
        storages = _dss_class_to_dict("storage")

        for name, data in storages.items():

            # Skip Storage object if disabled
            if not data["enabled"]:
                continue

            api_storage = Storage(model)
            api_storage.feeder_name = self.source_name

            # Name
            try:
                api_storage.name = name
            except:
                pass

            # connecting_element
            try:
                api_storage.connecting_element = data["bus1"]
            except:
                pass

            # nominal_voltage
            try:
                api_storage.nominal_voltage = (
                    float(data["kv"]) * 10 ** 3
                )  # DiTTo in volts
            except:
                pass

            # rated_power
            try:
                api_storage.rated_power = (
                    float(data["kWrated"]) * 10 ** 3
                )  # DiTTo in watts
            except:
                pass

            # rated_kWh
            try:
                api_storage.rated_kWh = float(data["kWhrated"])
            except:
                pass

            # stored_kWh
            try:
                api_storage.stored_kWh = float(data["kWhstored"])
            except:
                pass

            # reserve
            try:
                api_storage.reserve = float(data["%reserve"])
            except:
                pass

            # state
            try:
                api_storage.state = data["State"]
            except:
                pass

            # discharge_rate
            try:
                api_storage.discharge_rate = float(data["%Discharge"])
            except:
                pass

            # charge_rate
            try:
                api_storage.charge_rate = float(data["%Charge"])
            except:
                pass

            # charging_efficiency
            try:
                api_storage.charging_efficiency = float(data["%EffCharge"])
            except:
                pass

            # discharging_efficiency
            try:
                api_storage.discharging_efficiency = float(data["%EffDischarge"])
            except:
                pass

            # resistance
            try:
                api_storage.resistance = float(data["%R"])
            except:
                pass

            # reactance
            try:
                api_storage.reactance = float(data["%X"])
            except:
                pass

            # model_
            try:
                api_storage.model_ = int(data["model"])
            except:
                pass

            # yearly
            try:
                api_storage.yearly = data["yearly"]
            except:
                pass

            # daily
            try:
                api_storage.daily = data["daily"]
            except:
                pass

            # duty
            try:
                api_storage.duty = data["duty"]
            except:
                pass

            # discharge_trigger
            try:
                api_storage.discharge_trigger = float(data["DischargeTrigger"])
            except:
                pass

            # charge_trigger
            try:
                api_storage.charge_trigger = float(data["ChargeTrigger"])
            except:
                pass

            N_phases = int(data["phases"])

            for phase in range(N_phases):
                try:
                    api_phase_storage = PhaseStorage(model)
                except:
                    pass

                try:
                    api_phase_storage.p = float(data["kW"]) / float(N_phases)
                except:
                    pass

                try:
                    api_phase_storage.q = float(data["kvar"]) / float(N_phases)
                except:
                    pass

                api_storage.phase_storages.append(api_phase_storage)


def _dss_class_to_dict(class_name):
    return dss.utils.class_to_dataframe(class_name).to_dict(orient="index")
