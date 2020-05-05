# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import os
import math
import logging
import decimal

import numpy as np
import pandas as pd

from functools import reduce

# DiTTo imports
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.timeseries import Timeseries
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.storage import Storage
from ditto.models.phase_storage import PhaseStorage
from ditto.models.power_source import PowerSource
from ditto.models.photovoltaic import Photovoltaic

from ditto.writers.abstract_writer import AbstractWriter

logger = logging.getLogger(__name__)


class Writer(AbstractWriter):
    """
    DiTTo--->OpenDSS writer class.
    Use to write a DiTTo model to OpenDSS format.

    :param log_file: Name/path of the log file. Optional. Default='./OpenDSS_writer.log'
    :type log_file: str
    :param output_path: Path to write the OpenDSS files. Optional. Default='./'
    :type output_path: str

    **Constructor:**

    >>> my_writer=Writer(log_file='./logs/my_log.log', output_path='./feeder_output/')

    **Output file names:**

    +-----------------+--------------------+
    |     Object      |    File name       |
    +=================+====================+
    |      buses      |   Buscoords.dss    |
    +-----------------+--------------------+
    |  transformers   |   Transformers.dss |
    +-----------------+--------------------+
    |      loads      |      Loads.dss     |
    +-----------------+--------------------+
    |   regulators    |   Regulators.dss   |
    +-----------------+--------------------+
    |   capacitors    |   Capacitors.dss   |
    +-----------------+--------------------+
    |     lines       |      Lines.dss     |
    +-----------------+--------------------+
    |    wiredata     |    WireData.dss    |
    +-----------------+--------------------+
    |   linegeometry  |  LineGeometry.dss  |
    +-----------------+--------------------+
    |     linecodes   |    LineCodes.dss   |
    +-----------------+--------------------+
    |     loadshapes  |    LoadShapes.dss  |
    +-----------------+--------------------+
    |     storages    |     Storages.dss   |
    +-----------------+--------------------+
    |    PVSystems    |     PVSystems.dss  |
    +-----------------+--------------------+
    |      master     |      Master.dss    |
    +-----------------+--------------------+

    author: Nicolas Gensollen. October 2017.
    """

    register_names = ["dss", "opendss", "OpenDSS", "DSS"]

    def __init__(self, **kwargs):
        """Constructor for the OpenDSS writer."""
        self.timeseries_datasets = {}
        self.timeseries_format = {}
        self.all_linecodes = {}
        self.all_wires = {}
        self.all_geometries = {}
        self.compensator = {}
        self.all_cables = {}

        self.files_to_redirect = []
        self.substations_redirect = {}
        self.feeders_redirect = {}

        self.write_taps = False
        self.separate_feeders = False
        self.separate_substations = False
        self.verbose = False

        self.output_filenames = {
            "buses": "Buscoords.dss",
            "transformers": "Transformers.dss",
            "loads": "Loads.dss",
            "regulators": "Regulators.dss",
            "capacitors": "Capacitors.dss",
            "capcontrols": "CapControls.dss",
            "lines": "Lines.dss",
            "linecodes": "LineCodes.dss",
            "linegeometry": "LineGeometry.dss",
            "wiredata": "WireData.dss",
            "loadshapes": "LoadShapes.dss",
            "storage": "Storage.dss",
            "PVSystems": "PVSystems.dss",
            "master": "Master.dss",
            "CNDATA": "CNData.dss",
        }

        # Call super
        super(Writer, self).__init__(**kwargs)

        self._baseKV_ = set()
        self._baseKV_feeders_ = {}

        logger.info("DiTTo--->OpenDSS writer successfuly instanciated.")

    def float_to_str(self, f):
        """ Used to create floats without being in scientific notation"""
        ctx = decimal.Context()
        d1 = ctx.create_decimal(repr(f))
        return format(d1, "f")

    def write(self, model, **kwargs):
        """General writing function responsible for calling the sub-functions.

        :param model: DiTTo model
        :type model: DiTTo model
        :param verbose: Set verbose mode. Optional. Default=False
        :type verbose: bool
        :param write_taps: Write the transformer taps if they are provided. (This can cause some problems). Optional. Default=False
        :type write_taps: bool
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        # Verbose print the progress
        if "verbose" in kwargs and isinstance(kwargs["verbose"], bool):
            self.verbose = kwargs["verbose"]
        else:
            self.verbose = False

        if "write_taps" in kwargs:
            self.write_taps = kwargs["write_taps"]
        else:
            self.write_taps = False

        if "separate_feeders" in kwargs:
            self.separate_feeders = kwargs["separate_feeders"]
        else:
            self.separate_feeders = False

        if "separate_substations" in kwargs:
            self.separate_substations = kwargs["separate_substations"]
        else:
            self.separate_substations = False

        # Write the bus coordinates
        logger.info("Writing the bus coordinates...")
        if self.verbose:
            logger.debug("Writing the bus coordinates...")
        s = self.write_bus_coordinates(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the transformers
        logger.info("Writing the transformers...")
        if self.verbose:
            logger.debug("Writing the transformers...")
        s = self.write_transformers(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the regulators
        logger.info("Writing the regulators...")
        if self.verbose:
            logger.debug("Writing the regulators...")
        s = self.write_regulators(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # write the timeseries
        logger.info("Writing the timeseries...")
        if self.verbose:
            logger.debug("Writing the timeseries...")
        s = self.write_timeseries(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # write the loads
        logger.info("Writing the loads...")
        if self.verbose:
            logger.debug("Writing the loads...")
        s = self.write_loads(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the lines
        logger.info("Writting the lines...")
        if self.verbose:
            logger.debug("Writting the lines...")
        s = self.write_lines(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the capacitors
        self.logger.info("Writing the capacitors...")
        if self.verbose:
            logger.debug("Writing the capacitors...")
        s = self.write_capacitors(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the storage elements
        logger.info("Writting the storage devices...")
        if self.verbose:
            logger.debug("Writting the storage devices...")
        s = self.write_storages(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the PV
        logger.info("Writting the PVs...")
        if self.verbose:
            logger.debug("Writting the PVs...")
        s = self.write_PVs(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        # Write the Master file
        logger.info("Writting the master file...")
        if self.verbose:
            logger.debug("Writting the master file...")
        s = self.write_master_file(model)
        if self.verbose and s != -1:
            logger.debug("Succesful!")

        logger.info("Done.")
        if self.verbose:
            logger.debug("Writting done.")

        return 1

    def phase_mapping(self, phase):
        """Maps the Ditto phases ('A','B','C') into OpenDSS phases (1,2,3).

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

        :param phase: Phase in DiTTo format
        :type phase: unicode
        :returns: Phase in OpenDSS format
        :rtype: int

        .. note:: Returns None if phase is not in ['A','B','C']
        """
        if phase == u"A":
            return 1
        elif phase == u"B":
            return 2
        elif phase == u"C":
            return 3
        else:
            return None

    def mode_mapping(self, mode):
        """TODO"""
        if mode.lower() == "currentflow":
            return "current"
        elif mode.lower() == "voltage":
            return "voltage"
        elif mode.lower() == "activepower":
            return "PF"
        elif mode.lower() == "reactivepower":
            return "kvar"
        elif mode.lower() == "admittance":
            return None
        elif mode.lower() == "timescheduled":
            return "time"
        else:
            return None

    def write_bus_coordinates(self, model):
        """Write the bus coordinates to a CSV file ('buscoords.csv' by default), with the following format:

        >>> bus_name,coordinate_X,coordinate_Y

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        feeder_text_map = {}
        substation_text_map = {}
        self.all_buses = []
        # Loop over the DiTTo objects
        for i in model.models:
            # If we find a node
            if isinstance(i, Node):

                # Extract the name and the coordinates
                if (hasattr(i, "name") and i.name is not None) and (
                    hasattr(i, "positions")
                    and i.positions is not None
                    and len(i.positions) > 0
                ):
                    if (
                        self.separate_feeders
                        and hasattr(i, "feeder_name")
                        and i.feeder_name is not None
                    ):
                        feeder_name = i.feeder_name
                    else:
                        feeder_name = "DEFAULT"
                    if (
                        self.separate_substations
                        and hasattr(i, "substation_name")
                        and i.substation_name is not None
                    ):
                        substation_name = i.substation_name
                    else:
                        substation_name = "DEFAULT"

                    if not substation_name in substation_text_map:
                        substation_text_map[substation_name] = set([feeder_name])
                    else:
                        substation_text_map[substation_name].add(feeder_name)
                    txt = ""
                    if substation_name + "_" + feeder_name in feeder_text_map:
                        txt = feeder_text_map[substation_name + "_" + feeder_name]

                    txt += "{name} {X} {Y}\n".format(
                        name=i.name.lower(), X=i.positions[0].long, Y=i.positions[0].lat
                    )
                    feeder_text_map[substation_name + "_" + feeder_name] = txt

        for substation_name in substation_text_map:
            all_substation_buses = []
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    all_substation_buses.append(txt)
                    self.all_buses.append(txt)
                    if feeder_name != "":  # Substation elements are written separately
                        with open(
                            os.path.join(output_folder, self.output_filenames["buses"]),
                            "w",
                        ) as fp:
                            fp.write(txt)
                        # Not currently redirecting buscoords to each subfolder - just use the aggregate in the root directory
                        # self.files_to_redirect.append(os.path.join(output_redirect,self.output_filenames['buses']))
            output_folder = os.path.join(self.output_path, substation_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            with open(
                os.path.join(output_folder, self.output_filenames["buses"]), "w"
            ) as fp:
                fp.write("\n".join(all_substation_buses))
        if len(self.all_buses) > 0:
            with open(
                os.path.join(self.output_path, self.output_filenames["buses"]), "w"
            ) as fp:  # Writes all the buscoords to the base folder as well
                fp.write("".join(txt for txt in self.all_buses))
            self.files_to_redirect.append(self.output_filenames["buses"])

        return 1

    def write_transformers(self, model):
        """Write the transformers to an OpenDSS file (Transformers.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int

        .. note::

            - Assume that within the transformer API everything is stored in windings.
            - Currently not modelling open winding connections (e.g. open-delta open-wye)
        """
        # Create and open the transformer DSS file
        substation_text_map = {}
        feeder_text_map = {}

        # Loop over the DiTTo objects
        for i in model.models:
            # If we get a transformer object...
            if isinstance(i, PowerTransformer):
                # Write the data in the file
                # Name
                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]

                if hasattr(i, "name") and i.name is not None:
                    txt += "New Transformer." + i.name
                else:
                    # If we do not have a valid name, do not even try
                    # to write anything for this transformer....
                    continue

                # Number of phases and windings
                if hasattr(i, "windings") and i.windings is not None:
                    N_phases = []
                    for winding in i.windings:
                        if (
                            hasattr(winding, "phase_windings")
                            and winding.phase_windings is not None
                        ):
                            N_phases.append(len(winding.phase_windings))
                    if len(np.unique(N_phases)) != 1:
                        logger.error(
                            "Did not find the same number of phases accross windings of transformer {name}".format(
                                name=i.name
                            )
                        )

                    try:
                        # phase-phase connection defined with phase=1 even though it's two phase.
                        if (
                            len(i.windings) == 3
                            and i.windings[0].connection_type is not None
                            and i.windings[0].connection_type == "D"
                        ):
                            txt += " phases={Np}".format(Np=N_phases[0] - 1)
                        else:
                            txt += " phases={Np}".format(Np=N_phases[0])
                        txt += " windings={N}".format(N=len(i.windings))
                    except:
                        logger.error(
                            "Could not write the number of phases for transformer {name}".format(
                                name=i.name
                            )
                        )

                # Connection
                if hasattr(i, "from_element") and i.from_element is not None:
                    bus1 = i.from_element
                else:
                    bus1 = None
                if hasattr(i, "to_element") and i.to_element is not None:
                    bus2 = i.to_element
                else:
                    bus2 = None

                if bus1 is not None and bus2 is not None:
                    buses = [bus1, bus2]
                else:
                    buses = None

                # Rated power
                # if hasattr(i, 'rated_power') and i.rated_power is not None:
                #    fp.write(' kva='+str(i.rated_power*10**-3)) #OpenDSS in kWatts

                # Emergency power
                # Emergency_power removed from powerTransformers and added to windings by Tarek
                # if hasattr(i, 'emergency_power') and i.emergency_power is not None:
                #    fp.write(' EmergHKVA='+str(i.emergency_power*10**-3)) #OpenDSS in kWatts

                # Loadloss
                if hasattr(i, "loadloss") and i.loadloss is not None:
                    txt += " %loadloss=" + str(i.loadloss)  # OpenDSS in kWatts

                # install type (Not mapped)

                # noload_loss
                if hasattr(i, "noload_loss") and i.noload_loss is not None:
                    txt += " %Noloadloss=" + str(i.noload_loss)

                # noload_loss
                if hasattr(i, "normhkva") and i.normhkva is not None:
                    txt += " normhkva=" + str(i.normhkva)

                # phase shift (Not mapped)

                # Assume that we only have two or three windings. Three are used for center-tap transformers. Other single or three phase transformers use 2 windings
                # For banked 3-phase transformers, separate single phase transformers are used
                if hasattr(i, "windings") and i.windings is not None:

                    for cnt, winding in enumerate(i.windings):
                        if (
                            hasattr(winding, "phase_windings")
                            and winding.phase_windings is not None
                        ):

                            for phase_winding in winding.phase_windings:
                                if (
                                    hasattr(phase_winding, "compensator_r")
                                    and phase_winding.compensator_r is not None
                                ):
                                    if not i.name in self.compensator:
                                        self.compensator[i.name] = {}
                                        self.compensator[i.name]["R"] = set(
                                            [phase_winding.compensator_r]
                                        )
                                    elif "R" in self.compensator[i.name]:
                                        self.compensator[i.name]["R"].add(
                                            phase_winding.compensator_r
                                        )
                                    else:
                                        self.compensator[i.name]["R"] = set(
                                            [phase_winding.compensator_r]
                                        )

                                if (
                                    hasattr(phase_winding, "compensator_x")
                                    and phase_winding.compensator_x is not None
                                ):
                                    if not i.name in self.compensator:
                                        self.compensator[i.name] = {}
                                        self.compensator[i.name]["X"] = set(
                                            [phase_winding.compensator_x]
                                        )
                                    elif "X" in self.compensator[i.name]:
                                        self.compensator[i.name]["X"].add(
                                            phase_winding.compensator_x
                                        )
                                    else:
                                        self.compensator[i.name]["X"] = set(
                                            [phase_winding.compensator_x]
                                        )

                    if len(i.windings) == 2:

                        for cnt, winding in enumerate(i.windings):

                            txt += " wdg={N}".format(N=cnt + 1)

                            # Connection type
                            if (
                                hasattr(winding, "connection_type")
                                and winding.connection_type is not None
                            ):
                                if winding.connection_type == "Y":
                                    txt += " conn=wye"
                                elif winding.connection_type == "D":
                                    txt += " conn=delta"
                                else:
                                    logger.error(
                                        "Unsupported type of connection {conn} for transformer {name}".format(
                                            conn=winding.connection_type, name=i.name
                                        )
                                    )

                            # Voltage type (Not mapped)

                            # Nominal voltage
                            if (
                                hasattr(winding, "nominal_voltage")
                                and winding.nominal_voltage is not None
                            ):
                                txt += " Kv={kv}".format(
                                    kv=winding.nominal_voltage * 10 ** -3
                                )  # OpenDSS in kvolts
                                if (
                                    not substation_name + "_" + feeder_name
                                    in self._baseKV_feeders_
                                ):
                                    self._baseKV_feeders_[
                                        substation_name + "_" + feeder_name
                                    ] = set()

                                if (
                                    winding.nominal_voltage < 300
                                ):  # Line-Neutral voltage for 120 V
                                    self._baseKV_.add(
                                        winding.nominal_voltage
                                        * math.sqrt(3)
                                        * 10 ** -3
                                    )
                                    self._baseKV_feeders_[
                                        substation_name + "_" + feeder_name
                                    ].add(
                                        winding.nominal_voltage
                                        * math.sqrt(3)
                                        * 10 ** -3
                                    )
                                else:
                                    self._baseKV_.add(
                                        winding.nominal_voltage * 10 ** -3
                                    )
                                    self._baseKV_feeders_[
                                        substation_name + "_" + feeder_name
                                    ].add(winding.nominal_voltage * 10 ** -3)

                            # rated power
                            if (
                                hasattr(winding, "rated_power")
                                and winding.rated_power is not None
                            ):
                                txt += " kva={kva}".format(
                                    kva=winding.rated_power * 10 ** -3
                                )

                            # emergency_power
                            # Was added to windings by Tarek
                            if (
                                hasattr(winding, "emergency_power")
                                and winding.emergency_power is not None
                            ):
                                txt += " EmergHKVA={}".format(
                                    winding.emergency_power * 10 ** -3
                                )  # OpenDSS in kWatts

                            # resistance
                            if (
                                hasattr(winding, "resistance")
                                and winding.resistance is not None
                            ):
                                txt += " %R={R}".format(R=winding.resistance)

                            # Voltage limit (Not mapped)

                            # Reverse resistance (Not mapped)

                            # Check if winding is grounded
                            # this check is done here so that it happens only for 2 windings

                            # Phase windings
                            if (
                                hasattr(winding, "phase_windings")
                                and winding.phase_windings is not None
                            ):

                                if buses is not None:
                                    bus = buses[cnt]
                                    txt += " bus={bus}".format(bus=str(bus))

                                if len(winding.phase_windings) != 3:

                                    for j, phase_winding in enumerate(
                                        winding.phase_windings
                                    ):

                                        # Connection
                                        if (
                                            hasattr(phase_winding, "phase")
                                            and phase_winding.phase is not None
                                        ):
                                            txt += "." + str(
                                                self.phase_mapping(phase_winding.phase)
                                            )

                                    if (
                                        winding.connection_type == "D"
                                        and len(winding.phase_windings) == 1
                                    ):
                                        print(
                                            "Warning - only one phase specified for a delta system - adding another connection"
                                        )
                                        if self.phase_mapping(phase_winding.phase) == 1:
                                            txt += ".2"
                                        if self.phase_mapping(phase_winding.phase) == 2:
                                            txt += ".3"
                                        if self.phase_mapping(phase_winding.phase) == 3:
                                            txt += ".1"

                            if winding.is_grounded:
                                txt += ".0"

                            if (
                                hasattr(winding, "phase_windings")
                                and winding.phase_windings is not None
                            ):
                                # Tap position
                                # THIS CAN CAUSE PROBLEMS
                                # Use write_taps boolean to write this information or not
                                if (
                                    self.write_taps
                                    and hasattr(
                                        winding.phase_windings[0], "tap_position"
                                    )
                                    and winding.phase_windings[0].tap_position
                                    is not None
                                ):
                                    txt += " Tap={tap}".format(
                                        tap=winding.phase_windings[0].tap_position
                                    )

                        if hasattr(i, "reactances") and i.reactances is not None:
                            # Since we are in the case of 2 windings, we should only have one reactance
                            if isinstance(i.reactances, list):
                                if len(i.reactances) != 1:
                                    logger.error(
                                        "Number of reactances incorrect for transformer {name}. Expected 1, got {N}".format(
                                            name=i.name, N=len(i.reactances)
                                        )
                                    )
                                else:
                                    txt += " XHL={reac}".format(reac=i.reactances[0])
                            # If it is not a list, maybe it was entered as a scalar, but should not be that way....
                            elif isinstance(i.reactances, (int, float)):
                                txt += " XHL={reac}".format(reac=i.reactances)
                            else:
                                logger.error(
                                    "Reactances not understood for transformer {name}.".format(
                                        name=i.name
                                    )
                                )

                    # This is used to represent center-tap transformers
                    # As described in the documentation, if the R and X values are not known, the values described by default_r and default_x should be used
                    if len(i.windings) == 3:
                        default_r = [0.6, 1.2, 1.2]
                        default_x = [2.04, 2.04, 1.36]

                        for cnt, winding in enumerate(i.windings):

                            txt += " wdg={N}".format(N=cnt + 1)

                            if (
                                hasattr(winding, "connection_type")
                                and winding.connection_type is not None
                            ):
                                if winding.connection_type == "Y":
                                    txt += " conn=wye"
                                elif winding.connection_type == "D":
                                    txt += " conn=delta"
                                else:
                                    logger.error(
                                        "Unsupported type of connection {conn} for transformer {name}".format(
                                            conn=winding.connection_type, name=i.name
                                        )
                                    )

                            # Connection
                            if buses is not None:

                                if cnt == 0 or cnt == 1:
                                    txt += " bus={b}".format(b=buses[cnt])
                                elif cnt == 2:
                                    txt += " bus={b}".format(b=buses[cnt - 1])

                                # These are the configurations for center tap transformers
                                if cnt == 0:
                                    txt += ".{}".format(
                                        self.phase_mapping(
                                            winding.phase_windings[
                                                0
                                            ].phase  # Should beOnly one phase if it's a Wye transformer
                                        )
                                    )
                                    if (
                                        len(winding.phase_windings) > 1
                                        and winding.connection_type == "Y"
                                    ):
                                        print(
                                            "Warning - Wye center-tap transformer with more than one phase connection. Only using first one"
                                        )
                                    if (
                                        winding.connection_type == "D"
                                        and len(winding.phase_windings) >= 2
                                    ):
                                        txt += ".{}".format(
                                            self.phase_mapping(
                                                winding.phase_windings[1].phase
                                            )
                                        )
                                        if len(winding.phase_windings) > 2:
                                            print(
                                                "Warning - Delta center-tap transformer with more than two phase connection. Only using first two"
                                            )
                                    if (
                                        winding.connection_type == "D"
                                        and len(winding.phase_windings) == 1
                                    ):
                                        print(
                                            "Warning - only one phase specified for a delta system - adding another connection"
                                        )
                                        if self.phase_mapping(phase_winding.phase) == 1:
                                            txt += ".2"
                                        if self.phase_mapping(phase_winding.phase) == 2:
                                            txt += ".3"
                                        if self.phase_mapping(phase_winding.phase) == 3:
                                            txt += ".1"

                                if cnt == 1:
                                    txt += ".1.0"
                                if cnt == 2:
                                    txt += ".0.2"

                            # Voltage type (Not mapped)

                            # Nominal voltage
                            if (
                                hasattr(winding, "nominal_voltage")
                                and winding.nominal_voltage is not None
                            ):
                                txt += " Kv={kv}".format(
                                    kv=winding.nominal_voltage * 10 ** -3
                                )  # OpenDSS in kvolts
                                if (
                                    not substation_name + "_" + feeder_name
                                    in self._baseKV_feeders_
                                ):
                                    self._baseKV_feeders_[
                                        substation_name + "_" + feeder_name
                                    ] = set()
                                if (
                                    winding.nominal_voltage < 300
                                ):  # Line-Neutral voltage for 120 V
                                    self._baseKV_.add(
                                        winding.nominal_voltage
                                        * math.sqrt(3)
                                        * 10 ** -3
                                    )
                                    self._baseKV_feeders_[
                                        substation_name + "_" + feeder_name
                                    ].add(
                                        winding.nominal_voltage
                                        * math.sqrt(3)
                                        * 10 ** -3
                                    )
                                else:
                                    self._baseKV_.add(
                                        winding.nominal_voltage * 10 ** -3
                                    )
                                    self._baseKV_feeders_[
                                        substation_name + "_" + feeder_name
                                    ].add(winding.nominal_voltage * 10 ** -3)

                            # rated power
                            if (
                                hasattr(winding, "rated_power")
                                and winding.rated_power is not None
                            ):
                                txt += " kva={kva}".format(
                                    kva=winding.rated_power * 10 ** -3
                                )

                            # emergency_power
                            # Was added to windings by Tarek
                            if (
                                hasattr(winding, "emergency_power")
                                and winding.emergency_power is not None
                            ):
                                txt += " EmergHKVA={}".format(
                                    winding.emergency_power * 10 ** -3
                                )  # OpenDSS in kWatts

                            # Tap position
                            if (
                                self.write_taps
                                and hasattr(winding, "phase_windings")
                                and winding.phase_windings is not None
                                and hasattr(winding.phase_windings[0], "tap_position")
                                and winding.phase_windings[0].tap_position is not None
                            ):
                                txt += " Tap={tap}".format(
                                    tap=winding.phase_windings[0].tap_position
                                )

                            # Voltage limit (Not mapped)

                            # resistance
                            # if hasattr(winding, 'resistance') and winding.resistance is not None:
                            #    fp.write(' %R={R}'.format(R=winding.resistance))

                            # Reverse resistance (Not mapped)

                            if (
                                hasattr(winding, "resistance")
                                and winding.resistance is not None
                            ):
                                txt += " %r={R}".format(R=winding.resistance)
                            else:
                                txt += " %r={R}".format(R=default_r[cnt - 1])

                        if hasattr(i, "reactances") and i.reactances is not None:
                            # Here, we should have 3 reactances
                            if (
                                isinstance(i.reactances, list)
                                and len(i.reactances) == 3
                            ):
                                txt += " XHL={XHL} XLT={XLT} XHT={XHT}".format(
                                    XHL=i.reactances[0],
                                    XLT=i.reactances[1],
                                    XHT=i.reactances[2],
                                )
                            else:
                                logger.error(
                                    "Wrong number of reactances for transformer {name}".format(
                                        name=i.name
                                    )
                                )
                        else:
                            txt += " XHL=%f XHT=%f XLT=%f" % (
                                default_x[0],
                                default_x[1],
                                default_x[2],
                            )

                txt += "\n\n"
                feeder_text_map[substation_name + "_" + feeder_name] = txt

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(
                            output_folder, self.output_filenames["transformers"]
                        ),
                        "w",
                    ) as fp:
                        fp.write(txt)
                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(
                                feeder_name, self.output_filenames["transformers"]
                            )
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["transformers"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["transformers"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(
                            output_redirect, self.output_filenames["transformers"]
                        )
                    )

        return 1

    def write_storages(self, model):
        """Write the storage devices stored in the model.

        .. note:: Pretty straightforward for now since the DiTTo storage model class was built from the OpenDSS documentation.
                  The core representation is succeptible to change when mapping with other formats.

        .. todo:: Develop the docstring a little bit more...
        """

        substation_text_map = {}
        feeder_text_map = {}
        for i in model.models:
            if isinstance(i, Storage):
                # import pdb;pdb.set_trace()
                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]

                # Name
                if hasattr(i, "name") and i.name is not None:
                    txt += "New Storage.{name}".format(name=i.name)

                # Phases
                if hasattr(i, "phase_storages") and i.phase_storages is not None:
                    txt += " phases={N_phases}".format(N_phases=len(i.phase_storages))

                    # kW (Need to sum over the phase_storage elements)
                    if sum([1 for phs in i.phase_storages if phs.p is None]) == 0:
                        p_tot = sum([phs.p for phs in i.phase_storages])
                        txt += " kW={kW}".format(kW=p_tot * 10 ** -3)  # DiTTo in watts

                        # Power factor
                        if sum([1 for phs in i.phase_storages if phs.q is None]) == 0:
                            q_tot = sum([phs.q for phs in i.phase_storages])
                            if q_tot != 0 and p_tot != 0:
                                pf = float(p_tot) / math.sqrt(p_tot ** 2 + q_tot ** 2)
                                txt += " pf={pf}".format(pf=pf)

                # connecting_element
                if (
                    hasattr(i, "connecting_element")
                    and i.connecting_element is not None
                ):
                    txt += " Bus1={elt}".format(elt=i.connecting_element)
                    if (
                        hasattr(i, "phase_storages")
                        and i.phase_storages is not None
                        and len(i.phase_storages) > 0
                    ):
                        for phase_storage in i.phase_storages:
                            txt += "." + str(self.phase_mapping(phase_storage.phase))

                # nominal_voltage
                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    txt += " kV={volt}".format(
                        volt=i.nominal_voltage * 10 ** -3
                    )  # DiTTo in volts
                    if not substation_name + "_" + feeder_name in self._baseKV_feeders_:
                        self._baseKV_feeders_[
                            substation_name + "_" + feeder_name
                        ] = set()
                    if i.nominal_voltage < 300:  # Line-Neutral voltage for 120 V
                        self._baseKV_.add(i.nominal_voltage * math.sqrt(3) * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * math.sqrt(3) * 10 ** -3
                        )
                    else:
                        self._baseKV_.add(i.nominal_voltage * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * 10 ** -3
                        )
                    if hasattr(i, "active_rating") and i.active_rating is not None:
                        pf_local = 1.0
                        if i.power_factor is not None:
                            pf_local = abs(i.power_factor)
                        txt += " kVA={kva}".format(
                            kva=i.active_rating / pf_local * 10 ** -3
                        )  # DiTTo in watts

                # rated_power
                if hasattr(i, "rated_power") and i.rated_power is not None:
                    txt += " kWRated={kW}".format(
                        kW=i.rated_power * 10 ** -3
                    )  # DiTTo in watts

                # rated_kWh
                if hasattr(i, "rated_kWh") and i.rated_kWh is not None:
                    txt += " kWhRated={kWh}".format(kWh=i.rated_kWh * 10 ** -3)

                # stored_kWh
                if hasattr(i, "stored_kWh") and i.stored_kWh is not None:
                    txt += " kWhStored={stored}".format(stored=i.stored_kWh * 10 ** -3)

                # state
                if hasattr(i, "state") and i.state is not None:
                    txt += " State={state}".format(state=i.state)
                else:
                    txt += " State=IDLING"  # Default value in OpenDSS

                # reserve
                if hasattr(i, "reserve") and i.reserve is not None:
                    txt += " %reserve={reserve}".format(reserve=i.reserve * 10 ** -3)

                # discharge_rate
                if hasattr(i, "discharge_rate") and i.discharge_rate is not None:
                    txt += " %Discharge={discharge_rate}".format(
                        discharge_rate=i.discharge_rate
                    )

                # charge_rate
                if hasattr(i, "charge_rate") and i.charge_rate is not None:
                    txt += " %Charge={charge_rate}".format(charge_rate=i.charge_rate)

                # charging_efficiency
                if (
                    hasattr(i, "charging_efficiency")
                    and i.charging_efficiency is not None
                ):
                    txt += " %EffCharge={charge_eff}".format(
                        charge_eff=i.charging_efficiency
                    )

                # discharging_efficiency
                if (
                    hasattr(i, "discharging_efficiency")
                    and i.discharging_efficiency is not None
                ):
                    txt += " %EffDischarge={discharge_eff}".format(
                        discharge_eff=i.discharging_efficiency
                    )

                # resistance
                if hasattr(i, "resistance") and i.resistance is not None:
                    txt += " %R={resistance}".format(resistance=i.resistance)

                # reactance
                if hasattr(i, "reactance") and i.reactance is not None:
                    txt += " %X={reactance}".format(reactance=i.reactance)

                # model
                if hasattr(i, "model_") and i.model_ is not None:
                    txt += " model={model}".format(model=i.model_)

                # Yearly/Daily/Duty/Charge trigger/Discharge trigger
                #
                # TODO: See with Tarek and Elaine how we can support that

                txt += "\n"
                feeder_text_map[substation_name + "_" + feeder_name] = txt

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(output_folder, self.output_filenames["storage"]),
                        "w",
                    ) as fp:
                        fp.write(txt)
                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(feeder_name, self.output_filenames["storage"])
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["storage"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["storage"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(output_redirect, self.output_filenames["storage"])
                    )

        return 1

    def write_PVs(self, model):
        """Write the PVs."""
        feeder_text_map = {}
        feeder_voltvar_map = {}
        feeder_voltwatt_map = {}
        substation_text_map = {}
        for i in model.models:
            if isinstance(i, Photovoltaic):
                # If is_sourcebus is set to 1, then the object represents a source and not a PV system
                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                voltvar_nodes = set()
                voltwatt_nodes = set()
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]

                if substation_name + "_" + feeder_name in feeder_voltvar_map:
                    voltvar_nodes = feeder_voltvar_map[
                        substation_name + "_" + feeder_name
                    ]

                if substation_name + "_" + feeder_name in feeder_voltwatt_map:
                    voltwatt_nodes = feeder_voltwatt_map[
                        substation_name + "_" + feeder_name
                    ]

                # Name
                if hasattr(i, "name") and i.name is not None:
                    txt += "New PVSystem.{name}".format(name=i.name)

                # connecting element
                if (
                    hasattr(i, "connecting_element")
                    and i.connecting_element is not None
                ):
                    txt += " bus1={connecting_elt}".format(
                        connecting_elt=i.connecting_element
                    )
                    if hasattr(i, "phases") and i.phases is not None:
                        for phase in i.phases:
                            txt += "." + str(self.phase_mapping(phase))

                # Phases
                if hasattr(i, "phases") and i.phases is not None:
                    txt += " phases={n_phases}".format(n_phases=len(i.phases))

                # nominal voltage
                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    if i.nominal_voltage < 300:
                        txt += " kV={kV}".format(
                            kV=i.nominal_voltage * math.sqrt(3) * 10 ** -3
                        )  # DiTTo in volts
                    else:
                        txt += " kV={kV}".format(
                            kV=i.nominal_voltage * 10 ** -3
                        )  # DiTTo in volts
                    if not substation_name + "_" + feeder_name in self._baseKV_feeders_:
                        self._baseKV_feeders_[
                            substation_name + "_" + feeder_name
                        ] = set()
                    if (
                        i.nominal_voltage < 300
                    ):  # Line-Neutral voltage for 120 V (i.e. 240V)
                        self._baseKV_.add(i.nominal_voltage * math.sqrt(3) * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * 2 * 10 ** -3
                        )
                    else:
                        self._baseKV_.add(i.nominal_voltage * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * 10 ** -3
                        )
                else:
                    parent = model[i.connecting_element]
                    if (
                        hasattr(parent, "nominal_voltage")
                        and parent.nominal_voltage is not None
                    ):
                        if parent.nominal_voltage < 300:
                            txt += " kV={kV}".format(
                                kV=parent.nominal_voltage * math.sqrt(3) * 10 ** -3
                            )  # DiTTo in volts
                        else:
                            txt += " kV={kV}".format(
                                kV=parent.nominal_voltage * 10 ** -3
                            )  # DiTTo in volts
                        if (
                            not substation_name + "_" + feeder_name
                            in self._baseKV_feeders_
                        ):
                            self._baseKV_feeders_[
                                substation_name + "_" + feeder_name
                            ] = set()
                        if (
                            parent.nominal_voltage < 300
                        ):  # Line-Line voltage for 120 V (i.e. 240V)
                            self._baseKV_.add(
                                parent.nominal_voltage * math.sqrt(3) * 10 ** -3
                            )
                            self._baseKV_feeders_[
                                substation_name + "_" + feeder_name
                            ].add(parent.nominal_voltage * 2 * 10 ** -3)
                        else:
                            self._baseKV_.add(parent.nominal_voltage * 10 ** -3)
                            self._baseKV_feeders_[
                                substation_name + "_" + feeder_name
                            ].add(parent.nominal_voltage * 10 ** -3)

                if hasattr(i, "active_rating") and i.active_rating is not None:
                    pf_local = 1.0
                    if i.power_factor is not None:
                        pf_local = abs(i.power_factor)
                    txt += " kVA={kva}".format(
                        kva=i.active_rating / pf_local * 10 ** -3
                    )  # DiTTo in watts

                    if not (hasattr(i, "rated_power") and i.rated_power is not None):
                        txt += " Pmpp={kw}".format(
                            kw=i.active_rating
                            * pf_local
                            * 1.1
                            * 10
                            ** -3  # Set the inverter to be oversized by 10% if active rating not specified
                        )  # DiTTo in watts

                if hasattr(i, "rated_power") and i.rated_power is not None:
                    txt += " Pmpp={kw}".format(
                        kw=i.rated_power
                        * 10
                        ** -3  # Set the inverter to be oversized by 10% if active rating not specified
                    )  # DiTTo in watts

                if hasattr(i, "reactive_rating") and i.reactive_rating is not None:
                    txt += " kvarlimit={kvar}".format(
                        kvar=i.reactive_rating
                        * 10
                        ** -3  # Set the inverter to be oversized by 10% if active rating not specified
                    )  # DiTTo in watts

                # connection type
                if hasattr(i, "connection_type") and i.connection_type is not None:
                    mapps = {"D": "delta", "Y": "wye"}
                    if i.connection_type in mapps:
                        txt += " conn={conn}".format(conn=mapps[i.connection_type])
                    else:
                        raise NotImplementedError(
                            "Connection {conn} for PV systems is currently not supported.".format(
                                conn=i.connection_type
                            )
                        )

                # cutout_percent
                if hasattr(i, "cutout_percent") and i.cutout_percent is not None:
                    txt += " %Cutout={cutout}".format(cutout=i.cutout_percent)

                # cutin_percent
                if hasattr(i, "cutin_percent") and i.cutin_percent is not None:
                    txt += " %Cutin={cutin}".format(cutin=i.cutin_percent)

                # resistance
                if hasattr(i, "resistance") and i.resistance is not None:
                    txt += " %R={resistance}".format(resistance=i.resistance)

                # reactance
                if hasattr(i, "reactance") and i.reactance is not None:
                    txt += " %X={reactance}".format(reactance=i.reactance)

                # v_max_pu
                if hasattr(i, "v_max_pu") and i.v_max_pu is not None:
                    txt += " Vmaxpu={v_max_pu}".format(v_max_pu=i.v_max_pu)

                # v_min_pu
                if hasattr(i, "v_min_pu") and i.v_min_pu is not None:
                    txt += " Vminpu={v_min_pu}".format(v_min_pu=i.v_min_pu)

                # power_factor
                if hasattr(i, "control_type") and (
                    i.control_type is None or i.control_type == "powerfactor"
                ):  # use powerfactor as default mode
                    if hasattr(i, "power_factor") and i.power_factor is not None:
                        txt += " Model=1 pf={power_factor}".format(
                            power_factor=i.power_factor
                        )

                if (
                    hasattr(i, "control_type")
                    and i.control_type is not None
                    and i.control_type == "voltwatt"
                ):
                    txt += " Model=1 kvar=0"
                    voltwatt_nodes.add(i.name)

                if (
                    hasattr(i, "control_type")
                    and i.control_type is not None
                    and i.control_type == "voltvar"
                ):
                    txt += " Model=1 kvar=0"
                    voltvar_nodes.add(i.name)

                if (
                    hasattr(i, "timeseries")
                    and i.timeseries is not None
                    and len(i.timeseries) > 0
                ):
                    txt += " irradiance=1"
                    for ts in i.timeseries:
                        if (
                            hasattr(ts, "data_location")
                            and ts.data_location is not None
                            and os.path.isfile(ts.data_location)
                        ):
                            filename = self.timeseries_datasets[
                                substation_name + "_" + feeder_name
                            ][ts.data_location]
                            txt += " {ts_format}={filename}".format(
                                ts_format=self.timeseries_format[filename],
                                filename=filename,
                            )
                        else:
                            pass
                            # TODO: manage the data correctly when it is only in memory

                txt += "\n"
                feeder_text_map[substation_name + "_" + feeder_name] = txt
                feeder_voltvar_map[substation_name + "_" + feeder_name] = voltvar_nodes
                feeder_voltwatt_map[
                    substation_name + "_" + feeder_name
                ] = voltwatt_nodes

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                voltvar_nodes = feeder_voltvar_map[substation_name + "_" + feeder_name]
                voltwatt_nodes = feeder_voltwatt_map[
                    substation_name + "_" + feeder_name
                ]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                inv_txt = ""
                if len(voltvar_nodes) > 0:
                    inv_txt += "New XYCurve.VoltVarCurve_{loc} npts=6 Yarray=(1.0,1.0,0.0,0.0,-1.0,-1.0) Xarray=(0.5,0.93,0.97,1.03,1.06,1.5)\n\n".format(
                        loc=substation_name + "_" + feeder_name
                    )  # Default voltvar curve used
                    inv_txt += "New InvControl.InvPVCtrVV_{loc} mode=VOLTVAR voltage_curvex_ref=rated vvc_curve1=VoltVarCurve_{loc} VV_RefReactivePower=VARMAX_VARS DeltaQ_factor=0.5 PVSystemlist=[".format(
                        loc=substation_name + "_" + feeder_name
                    )
                    for node in voltvar_nodes:
                        inv_txt += node + ","
                    inv_txt = inv_txt.strip(",")
                    inv_txt += "]\n\n"

                if len(voltwatt_nodes) > 0:
                    inv_txt += "New XYCurve.VoltWattCurve_{loc} npts=4  Yarray=(1.0,1.0,0.0,0.0) XArray=(0.5,1.06,1.1,1.5)\n\n".format(
                        loc=substation_name + "_" + feeder_name
                    )  # Default volt-watt curve used
                    inv_txt += "New InvControl.InvPVCtrVW_{loc} mode=VOLTWATT voltage_curvex_ref=rated VoltwattYAxis=PAVAILABLEPU voltwatt_curve=VoltWattCurve_{loc} eventlog=yes DeltaP_factor=0.25 PVSystemlist=[".format(
                        loc=substation_name + "_" + feeder_name
                    )
                    for node in voltwatt_nodes:
                        inv_txt += node + ","
                    inv_txt = inv_txt.strip(",")
                    inv_txt += "]"

                if txt != "":
                    txt += "\n" + inv_txt
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(output_folder, self.output_filenames["PVSystems"]),
                        "w",
                    ) as fp:
                        fp.write(txt)

                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(
                                feeder_name, self.output_filenames["PVSystems"]
                            )
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["PVSystems"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["PVSystems"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(
                            output_redirect, self.output_filenames["PVSystems"]
                        )
                    )

    def write_timeseries(self, model):
        """Write all the unique timeseries objects to csv files if they are in memory.
        If the data is already on disk, no new data is created.
        Then create the Loadshapes.dss file containing the links to the loadshapes.
        Currently all loadshapes are assumed to be yearly
        TODO: Add daily profiles as well
        """

        substation_text_map = {}
        feeder_text_map = {}
        all_data = set()
        for i in model.models:
            if isinstance(i, Timeseries):
                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]
                if substation_name + "_" + feeder_name not in self.timeseries_datasets:
                    self.timeseries_datasets[substation_name + "_" + feeder_name] = {}

                if (
                    hasattr(i, "data_location")
                    and i.data_location is not None
                    and i.data_label is not None
                    and (i.scale_factor is None or i.scale_factor == 1)
                ):
                    filename = i.data_label
                    location = i.data_location
                    if (
                        i.data_location
                        in self.timeseries_datasets[substation_name + "_" + feeder_name]
                        and substation_name + "_" + feeder_name in feeder_text_map
                    ):  # Need to make sure the loadshape exits in each subfolder
                        continue
                    npoints = len(
                        pd.read_csv(os.path.join(self.output_path, i.data_location))
                    )
                    if (
                        npoints == 24 or npoints == 24 * 60 or npoints == 24 * 60 * 60
                    ):  # The cases of hourly, minute or second resolution data for exactly one day TODO: make this more precise
                        self.timeseries_format[filename] = "daily"
                    else:
                        self.timeseries_format[filename] = "yearly"

                    interval = 1
                    if i.interval is not None:
                        interval = i.interval
                    txt += "New Loadshape.{filename} npts= {npoints} interval={interv} mult = (file={data_location})\n\n".format(
                        filename=filename,
                        npoints=npoints,
                        # data_location=i.data_location.split("/")[-1],
                        data_location=location,
                        interv=interval,
                    )
                    self.timeseries_datasets[substation_name + "_" + feeder_name][
                        i.data_location
                    ] = filename

                elif (
                    hasattr(i, "data_location")
                    and i.data_location is not None
                    and i.data_label is not None
                    and i.scale_factor is not None
                    and i.scale_factor != 1
                ):
                    filename = i.data_label + "_scaled"
                    scaled_data_location = (
                        i.data_location[:-4]
                        + "__scaled%s" % (str(int((i.scale_factor) * 100)).zfill(3))
                        + i.data_location[-4:]
                    )
                    if (
                        i.data_location
                        in self.timeseries_datasets[substation_name + "_" + feeder_name]
                        and substation_name + "_" + feeder_name in feeder_text_map
                    ):  # Need to make sure the loadshape exits in each subfolder
                        continue
                    timeseries = pd.read_csv(
                        os.path.join(self.output_path, i.data_location)
                    )
                    npoints = len(timeseries)
                    timeseries.iloc[:, [0]] = timeseries.iloc[:, [0]] * i.scale_factor
                    timeseries.to_csv(scaled_data_location, index=False)
                    if (
                        npoints == 24 or npoints == 24 * 60 or npoints == 24 * 60 * 60
                    ):  # The cases of hourly, minute or second resolution data for exactly one day TODO: make this more precise
                        self.timeseries_format[filename] = "daily"
                    else:
                        self.timeseries_format[filename] = "yearly"
                    txt += "New Loadshape.{filename} npts= {npoints} interval=1 mult = (file={data_location})\n\n".format(
                        filename=filename,
                        npoints=npoints,
                        data_location=scaled_data_location,
                    )
                # elif: In memory
                #     pass
                else:
                    import pdb

                    pdb.set_trace()
                    pass  # problem

                self.timeseries_datasets[substation_name + "_" + feeder_name][
                    i.data_location
                ] = filename
                feeder_text_map[substation_name + "_" + feeder_name] = txt

                # pass #TODO: write the timeseries data if it's in memory

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(
                            output_folder, self.output_filenames["loadshapes"]
                        ),
                        "w",
                    ) as fp:
                        fp.write(txt)
                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(
                                feeder_name, self.output_filenames["loadshapes"]
                            )
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["loadshapes"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["loadshapes"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(
                            output_redirect, self.output_filenames["loadshapes"]
                        )
                    )

    def write_loads(self, model):
        """Write the loads to an OpenDSS file (Loads.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """

        substation_text_map = {}
        feeder_text_map = {}
        for i in model.models:
            if isinstance(i, Load):
                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]

                # Name
                if hasattr(i, "name") and i.name is not None:
                    txt += "New Load." + i.name
                else:
                    continue

                # Connection type
                if hasattr(i, "connection_type") and i.connection_type is not None:
                    if i.connection_type == "Y":
                        txt += " conn=wye"
                    elif i.connection_type == "D":
                        txt += " conn=delta"

                # Connecting element
                if (
                    hasattr(i, "connecting_element")
                    and i.connecting_element is not None
                ):
                    txt += " bus1={bus}".format(bus=i.connecting_element)
                    if hasattr(i, "phase_loads") and i.phase_loads is not None:
                        for phase_load in i.phase_loads:
                            if (
                                hasattr(phase_load, "phase")
                                and phase_load.phase is not None
                            ):
                                txt += ".{p}".format(
                                    p=self.phase_mapping(phase_load.phase)
                                )

                        if i.connection_type == "D" and len(i.phase_loads) == 1:
                            if self.phase_mapping(i.phase_loads[0].phase) == 1:
                                txt += ".2"
                            if self.phase_mapping(i.phase_loads[0].phase) == 2:
                                txt += ".3"
                            if self.phase_mapping(i.phase_loads[0].phase) == 3:
                                txt += ".1"

                # nominal voltage
                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    if i.nominal_voltage < 300:
                        txt += " kV={volt}".format(
                            volt=i.nominal_voltage * math.sqrt(3) * 10 ** -3
                        )
                    else:
                        txt += " kV={volt}".format(volt=i.nominal_voltage * 10 ** -3)
                    if not substation_name + "_" + feeder_name in self._baseKV_feeders_:
                        self._baseKV_feeders_[
                            substation_name + "_" + feeder_name
                        ] = set()
                    if i.nominal_voltage < 300:  # Line-Neutral voltage for 120 V
                        self._baseKV_.add(i.nominal_voltage * math.sqrt(3) * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * math.sqrt(3) * 10 ** -3
                        )
                    else:
                        self._baseKV_.add(i.nominal_voltage * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * 10 ** -3
                        )

                # Vmin
                if hasattr(i, "vmin") and i.vmin is not None:
                    txt += " Vminpu={vmin}".format(vmin=i.vmin)

                # Vmax
                if hasattr(i, "vmax") and i.vmax is not None:
                    txt += " Vmaxpu={vmax}".format(vmax=i.vmax)

                # positions (Not mapped)

                # KW
                total_P = 0
                if hasattr(i, "phase_loads") and i.phase_loads:
                    txt += " model={N}".format(N=i.phase_loads[0].model)

                    for phase_load in i.phase_loads:
                        if hasattr(phase_load, "p") and phase_load.p is not None:
                            total_P += phase_load.p
                    txt += " kW={P}".format(P=total_P * 10 ** -3)

                # Kva
                total_Q = 0
                if hasattr(i, "phase_loads") and i.phase_loads:
                    for phase_load in i.phase_loads:
                        if hasattr(phase_load, "q") and phase_load.q is not None:
                            total_Q += phase_load.q
                    txt += " kvar={Q}".format(Q=total_Q * 10 ** -3)

                # phase_loads
                if hasattr(i, "phase_loads") and i.phase_loads:

                    # if i.connection_type=='Y':
                    txt += " Phases={N}".format(N=len(i.phase_loads))
                    # elif i.connection_type=='D' and len(i.phase_loads)==3:
                    #    fp.write(' Phases=3')
                    # elif i.connection_type=='D' and len(i.phase_loads)==2:
                    #    fp.write(' Phases=1')

                    for phase_load in i.phase_loads:

                        # P
                        # if hasattr(phase_load, 'p') and phase_load.p is not None:
                        #    fp.write(' kW={P}'.format(P=phase_load.p*10**-3))

                        # Q
                        # if hasattr(phase_load, 'q') and phase_load.q is not None:
                        #    fp.write(' kva={Q}'.format(Q=phase_load.q*10**-3))

                        # ZIP load model
                        if (
                            hasattr(phase_load, "use_zip")
                            and phase_load.use_zip is not None
                        ):
                            if phase_load.use_zip:

                                # Get the coefficients
                                if (
                                    (
                                        hasattr(i, "ppercentimpedance")
                                        and i.ppercentimpedance is not None
                                    )
                                    and (
                                        hasattr(i, "qpercentimpedance")
                                        and i.qpercentimpedance is not None
                                    )
                                    and (
                                        hasattr(i, "ppercentcurrent")
                                        and i.ppercentcurrent is not None
                                    )
                                    and (
                                        hasattr(i, "qpercentcurrent")
                                        and i.qpercentcurrent is not None
                                    )
                                    and (
                                        hasattr(i, "ppercentpower")
                                        and i.ppercentpower is not None
                                    )
                                    and (
                                        hasattr(i, "qpercentpower")
                                        and i.qpercentpower is not None
                                    )
                                ):

                                    txt += (
                                        " model=8 ZIPV=[%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f]"
                                        % (
                                            i.ppercentimpedance,
                                            i.ppercentcurrent,
                                            i.ppercentpower,
                                            i.qpercentimpedance,
                                            i.qpercentcurrent,
                                            i.qpercentpower,
                                        )
                                    )

                # fp.write(' model=1')

                # timeseries object
                if hasattr(i, "timeseries") and i.timeseries is not None:
                    for ts in i.timeseries:
                        substation = "DEFAULT"
                        feeder = "DEFAULT"
                        if ts.feeder_name is not None:
                            feeder = ts.feeder_name
                        if ts.substation_name is not None:
                            substation = ts.substation_name
                        if (
                            hasattr(ts, "data_location")
                            and ts.data_label is not None
                            and ts.data_location is not None
                        ):
                            filename = self.timeseries_datasets[
                                substation + "_" + feeder
                            ][ts.data_location]
                            txt += " {ts_format}={filename}".format(
                                ts_format=self.timeseries_format[filename],
                                filename=filename,
                            )
                        else:
                            pass
                            # TODO: manage the data correctly when it is only in memory

                txt += "\n\n"
                feeder_text_map[substation_name + "_" + feeder_name] = txt
        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(output_folder, self.output_filenames["loads"]), "w"
                    ) as fp:
                        fp.write(txt)
                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(feeder_name, self.output_filenames["loads"])
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["loads"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["loads"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(output_redirect, self.output_filenames["loads"])
                    )

        return 1

    def write_regulators(self, model):
        """Write the regulators to an OpenDSS file (Regulators.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """

        substation_text_map = {}
        feeder_text_map = {}
        # It might be the case that we have to create new transformers from the regulators.
        # In this case, we build the strings and store them in a list.
        # At the end, we simply loop over the list to write all strings to transformers.dss
        transfo_creation_string_map = {}

        for i in model.models:
            if isinstance(i, Regulator):

                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                transfo_creation_string = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]
                    transfo_creation_string = transfo_creation_string_map[
                        substation_name + "_" + feeder_name
                    ]

                if hasattr(i, "name") and i.name is not None:
                    txt += "New RegControl.{name}".format(name=i.name)
                else:
                    continue

                # Connected transformer
                if hasattr(i, "connected_transformer"):

                    # If we have a valid connected_transformer then job's easy...
                    if i.connected_transformer is not None:
                        txt += " transformer={trans}".format(
                            trans=i.connected_transformer
                        )

                    # Otherwise, we have to create a new transformer and write it to the transformers file
                    else:

                        # Initialize the string:
                        transfo_creation_string += "New Transformer."

                        # Name:
                        transfo_name = "trans_{}".format(
                            i.name
                        )  # Maybe not the best naming convention....
                        transfo_creation_string += transfo_name

                        # Number of Phases
                        if hasattr(i, "windings") and i.windings is not None:
                            if (
                                hasattr(i.windings[0], "phase_windings")
                                and i.windings[0].phase_windings is not None
                            ):
                                try:
                                    transfo_creation_string += " phases={}".format(
                                        len(i.windings[0].phase_windings)
                                    )
                                except:
                                    pass
                                phases = [
                                    self.phase_mapping(x.phase)
                                    for x in i.windings[0].phase_windings
                                ]
                                phase_string = reduce(
                                    lambda x, y: str(x) + "." + str(y), phases
                                )

                        # Number of windings
                        if hasattr(i, "windings") and i.windings is not None:
                            try:
                                transfo_creation_string += " windings={}".format(
                                    len(i.windings)
                                )
                            except:
                                pass

                        # buses:
                        if (
                            hasattr(i, "from_element")
                            and i.from_element is not None
                            and hasattr(i, "to_element")
                            and i.to_element is not None
                        ):
                            transfo_creation_string += " buses=({b1}.{p},{b2}.{p})".format(
                                b1=i.from_element, b2=i.to_element, p=phase_string
                            )

                        # Conns
                        if hasattr(i, "windings") and i.windings is not None:
                            conns = " conns=("
                            for w, winding in enumerate(i.windings):
                                if hasattr(
                                    i.windings[w], "connection_type"
                                ) and i.windings[w].connection_type in ["Y", "D", "Z"]:
                                    mapp = {"Y": "Wye", "D": "Delta", "Z": "Zigzag"}
                                    conns += mapp[i.windings[w].connection_type] + ", "
                            conns = conns[:-2]
                            conns += ")"
                            if conns == " conns)":
                                conns = ""
                            transfo_creation_string += conns

                        # kvs
                        if hasattr(i, "windings") and i.windings is not None:
                            kvs = " kvs=("
                            for w, winding in enumerate(i.windings):
                                if hasattr(i.windings[w], "nominal_voltage"):
                                    kvs += (
                                        str(i.windings[w].nominal_voltage * 10 ** -3)
                                        + ", "
                                    )
                                    if (
                                        not substation_name + "_" + feeder_name
                                        in self._baseKV_feeders_
                                    ):
                                        self._baseKV_feeders_[
                                            substation_name + "_" + feeder_name
                                        ] = set()
                                    if (
                                        i.windings[w].nominal_voltage < 300
                                    ):  # Line-Neutral voltage for 120 V
                                        self._baseKV_.add(
                                            i.windings[w].nominal_voltage
                                            * math.sqrt(3)
                                            * 10 ** -3
                                        )
                                        self._baseKV_feeders_[
                                            substation_name + "_" + feeder_name
                                        ].add(
                                            winding.nominal_voltage
                                            * math.sqrt(3)
                                            * 10 ** -3
                                        )
                                    else:
                                        self._baseKV_.add(
                                            i.windings[w].nominal_voltage * 10 ** -3
                                        )
                                        self._baseKV_feeders_[
                                            substation_name + "_" + feeder_name
                                        ].add(winding.nominal_voltage * 10 ** -3)

                            kvs = kvs[:-2]
                            kvs += ")"
                            transfo_creation_string += kvs

                        # kvas
                        if hasattr(i, "windings") and i.windings is not None:
                            kvas = " kvas=("
                            for w, winding in enumerate(i.windings):
                                if (
                                    hasattr(i.windings[w], "rated_power")
                                    and i.windings[w].rated_power is not None
                                ):
                                    kvas += (
                                        str(i.windings[w].rated_power * 10 ** -3) + ", "
                                    )
                            kvas = kvas[:-2]
                            kvas += ")"
                            transfo_creation_string += kvas

                        # emergency_power
                        if hasattr(i, "windings") and i.windings is not None:
                            if (
                                hasattr(i.windings[0], "emergency_power")
                                and i.windings[0].emergency_power is not None
                            ):
                                transfo_creation_string += " EmerghKVA={}".format(
                                    i.windings[0].emergency_power
                                )

                        # reactances:
                        if hasattr(i, "reactances") and i.reactances is not None:
                            # XHL:
                            try:
                                if isinstance(i.reactances[0], (int, float)):
                                    transfo_creation_string += " XHL={}".format(
                                        i.reactances[0]
                                    )
                            except:
                                logger.warning(
                                    "Could not extract XHL from regulator {name}".format(
                                        name=i.name
                                    )
                                )
                                pass
                            # XLT:
                            try:
                                if isinstance(i.reactances[1], (int, float)):
                                    transfo_creation_string += " XLT={}".format(
                                        i.reactances[1]
                                    )
                            except:
                                logger.warning(
                                    "Could not extract XLT from regulator {name}".format(
                                        name=i.name
                                    )
                                )
                                pass
                            # XHT:
                            try:
                                if isinstance(i.reactances[2], (int, float)):
                                    transfo_creation_string += " XHT={}".format(
                                        i.reactances[2]
                                    )
                            except:
                                logger.warning(
                                    "Could not extract XHT from regulator {name}".format(
                                        name=i.name
                                    )
                                )
                                pass

                        txt += " transformer={trans}".format(trans=transfo_name)

                # Winding
                if hasattr(i, "winding") and i.winding is not None:
                    txt += " winding={w}".format(w=i.winding)
                else:
                    txt += " winding=2"

                # CTprim
                if hasattr(i, "ct_prim") and i.ct_prim is not None:
                    txt += " CTprim={CT}".format(CT=i.ct_prim)

                # noload_loss
                if hasattr(i, "noload_loss") and i.noload_loss is not None:
                    txt += " %noLoadLoss={nL}".format(NL=i.noload_loss)

                # Delay
                if hasattr(i, "delay") and i.delay is not None:
                    txt += " delay={d}".format(d=i.delay)

                # highstep
                # if hasattr(i, "highstep") and i.highstep is not None:
                #     txt += " maxtapchange={high}".format(high=i.highstep)

                # lowstep (Not mapped)

                # pt ratio
                if hasattr(i, "pt_ratio") and i.pt_ratio is not None:
                    txt += " ptratio={PT}".format(PT=i.pt_ratio)

                # ct ratio  (Not mapped)

                # phase shift (Not mapped)

                # ltc (Not mapped)

                # bandwidth
                if hasattr(i, "bandwidth") and i.bandwidth is not None:
                    txt += " band={b}".format(
                        b=i.bandwidth * 1.2
                    )  # The bandwidth is operated at 120 V

                # band center
                if hasattr(i, "bandcenter") and i.bandcenter is not None:
                    txt += " vreg={vreg}".format(vreg=i.bandcenter)

                # Pt phase
                if hasattr(i, "pt_phase") and i.pt_phase is not None:
                    txt += " Ptphase={PT}".format(PT=self.phase_mapping(i.pt_phase))

                # Voltage limit
                if hasattr(i, "voltage_limit") and i.voltage_limit is not None:
                    txt += " vlimit={vlim}".format(vlim=i.voltage_limit)

                if hasattr(i, "setpoint") and i.setpoint is not None:
                    txt += " vreg = {setp}".format(setp=i.setpoint / 100.0 * 120)

                # X (Store in the Phase Windings of the transformer)
                if i.name in self.compensator:
                    if "X" in self.compensator[i.name]:
                        if len(self.compensator[i.name]["X"]) == 1:
                            txt += " X={x}".format(
                                x=list(self.compensator[i.name]["X"])[0]
                            )
                        else:
                            logger.warning(
                                """Compensator_x not the same for all windings of transformer {name}.
                                                   Using the first value for regControl {name2}.""".format(
                                    name=i.connected_transformer, name2=i.name
                                )
                            )
                            txt += " X={x}".format(
                                x=list(self.compensator[i.name]["X"])[0]
                            )

                # R (Store in the Phase Windings of the transformer)
                if i.name in self.compensator:
                    if "R" in self.compensator[i.name]:
                        if len(self.compensator[i.name]["R"]) == 1:
                            txt += " R={r}".format(
                                r=list(self.compensator[i.name]["R"])[0]
                            )
                        else:
                            logger.warning(
                                """Compensator_r not the same for all windings of transformer {name}.
                                                   Using the first value for regControl {name2}.""".format(
                                    name=i.connected_transformer, name2=i.name
                                )
                            )
                            txt += " R={r}".format(
                                r=list(self.compensator[i.name]["R"])[0]
                            )

                txt += "\n\n"
                if len(transfo_creation_string) > 0:
                    transfo_creation_string += "\n\n"
                feeder_text_map[substation_name + "_" + feeder_name] = txt
                transfo_creation_string_map[
                    substation_name + "_" + feeder_name
                ] = transfo_creation_string

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                if substation_name + "_" + feeder_name in transfo_creation_string_map:
                    transfo_creation_string = transfo_creation_string_map[
                        substation_name + "_" + feeder_name
                    ]
                else:
                    transfo_creation_string = ""
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(
                            output_folder, self.output_filenames["regulators"]
                        ),
                        "w",
                    ) as fp:
                        fp.write(txt)
                    if len(transfo_creation_string) > 0:
                        with open(
                            os.path.join(
                                output_folder, self.output_filenames["transformers"]
                            ),
                            "a",
                        ) as f:
                            f.write(transfo_creation_string)

                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(
                                feeder_name, self.output_filenames["regulators"]
                            )
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["regulators"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["regulators"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(
                            output_redirect, self.output_filenames["regulators"]
                        )
                    )

        return 1

    def write_capacitors(self, model):
        """Write the capacitors to an OpenDSS file (Capacitors.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """

        substation_text_map = {}
        feeder_text_map = {}
        for i in model.models:

            if isinstance(i, Capacitor):

                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]

                # Name
                if hasattr(i, "name") and i.name is not None:
                    txt += "New Capacitor.{name}".format(name=i.name)
                else:
                    continue

                # Connecting element
                if i.connecting_element is not None:
                    txt += " Bus1=" + i.connecting_element

                    # For a 3-phase capbank we don't add any suffixes to the output.
                    if (
                        hasattr(i, "phase_capacitors")
                        and i.phase_capacitors is not None
                        and len(i.phase_capacitors) != 3
                    ):
                        for phase_capacitor in i.phase_capacitors:

                            if (
                                hasattr(phase_capacitor, "phase")
                                and phase_capacitor.phase is not None
                            ):
                                if phase_capacitor.phase == "A":
                                    txt += ".1"
                                if phase_capacitor.phase == "B":
                                    txt += ".2"
                                if phase_capacitor.phase == "C":
                                    txt += ".3"

                # Phases
                if hasattr(i, "phase_capacitors") and i.phase_capacitors is not None:
                    txt += " phases={N}".format(N=len(i.phase_capacitors))

                # nominal_voltage
                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    txt += " Kv={volt}".format(
                        volt=i.nominal_voltage * 10 ** -3
                    )  # OpenDSS in Kvolts
                    if not substation_name + "_" + feeder_name in self._baseKV_feeders_:
                        self._baseKV_feeders_[
                            substation_name + "_" + feeder_name
                        ] = set()
                    if i.nominal_voltage < 300:  # Line-Neutral voltage for 120 V
                        self._baseKV_.add(i.nominal_voltage * math.sqrt(3) * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * math.sqrt(3) * 10 ** -3
                        )
                    else:
                        self._baseKV_.add(i.nominal_voltage * 10 ** -3)
                        self._baseKV_feeders_[substation_name + "_" + feeder_name].add(
                            i.nominal_voltage * 10 ** -3
                        )

                # connection type
                if hasattr(i, "connection_type") and i.connection_type is not None:
                    if i.connection_type == "Y":
                        txt += " conn=Wye"
                    elif i.connection_type == "D":
                        txt += " conn=delta"
                    else:
                        logger.error(
                            "Unknown connection type in capacitor {name}".format(
                                name=i.name
                            )
                        )

                # Rated kvar
                # In DiTTo, this is splitted accross phase_capacitors
                # We thus have to sum them up
                total_var = 0
                if hasattr(i, "phase_capacitors") and i.phase_capacitors is not None:
                    for phase_capacitor in i.phase_capacitors:
                        if (
                            hasattr(phase_capacitor, "var")
                            and phase_capacitor.var is not None
                        ):
                            try:
                                total_var += phase_capacitor.var
                            except:
                                logger.error(
                                    "Cannot compute Var of capacitor {name}".format(
                                        name=name
                                    )
                                )
                                pass
                    total_var *= 10 ** -3  # OpenDSS in Kvar
                    txt += " Kvar={kvar}".format(kvar=total_var)

                # We create a CapControl if we have valid input
                # values that indicate that we should
                create_capcontrol = False
                if (hasattr(i, "name") and i.name is not None) and (
                    (hasattr(i, "delay") and i.delay is not None)
                    or (hasattr(i, "mode") and i.mode is not None)
                    or (hasattr(i, "low") and i.low is not None)
                    or (hasattr(i, "high") and i.high is not None)
                    or (hasattr(i, "pt_ratio") and i.pt_ratio is not None)
                    or (hasattr(i, "ct_ratio") and i.ct_ratio is not None)
                    or (hasattr(i, "pt_phase") and i.pt_phase is not None)
                ):
                    create_capcontrol = True

                # Create CapControl
                if create_capcontrol:
                    txt += "\n\nNew CapControl.{name} Capacitor={name}".format(
                        name=i.name
                    )

                    # Element (CONTROL)
                    if (
                        hasattr(i, "measuring_element")
                        and i.measuring_element is not None
                    ):
                        txt += " Element=Line.{elt} Terminal=1".format(
                            elt=i.measuring_element
                        )

                    # Delay (CONTROL)
                    if hasattr(i, "delay") and i.delay is not None:
                        txt += " delay={d}".format(d=i.delay)

                    # mode (CONTROL)
                    if hasattr(i, "mode") and i.mode is not None:
                        txt += " Type={m}".format(m=self.mode_mapping(i.mode))

                    # Low (CONTROL)
                    if hasattr(i, "low") and i.low is not None:
                        txt += " Vmin={vmin}".format(vmin=i.low)

                    # high (CONTROL)
                    if hasattr(i, "high") and i.high is not None:
                        txt += " Vmax={vmax}".format(vmax=i.high)

                    # Pt ratio (CONTROL)
                    if hasattr(i, "pt_ratio") and i.pt_ratio is not None:
                        txt += " Ptratio={PT}".format(PT=i.pt_ratio)

                    # Ct ratio (CONTROL)
                    if hasattr(i, "ct_ratio") and i.ct_ratio is not None:
                        txt += " Ctratio={CT}".format(CT=i.ct_ratio)

                    # Pt phase (CONTROL)
                    if hasattr(i, "pt_phase") and i.pt_phase is not None:
                        txt += " PTPhase={PT}".format(PT=self.phase_mapping(i.pt_phase))

                txt += "\n\n"
                feeder_text_map[substation_name + "_" + feeder_name] = txt
        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(
                            output_folder, self.output_filenames["capacitors"]
                        ),
                        "w",
                    ) as fp:
                        fp.write(txt)

                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(
                                feeder_name, self.output_filenames["capacitors"]
                            )
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["capacitors"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["capacitors"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(
                            output_redirect, self.output_filenames["capacitors"]
                        )
                    )

        return 1

    def write_lines(self, model):
        """Write the lines to an OpenDSS file (Lines.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """

        substation_text_map = {}
        feeder_text_map = {}
        # First, we have to decide if we want to output using LineGeometries and WireData or using LineCodes
        # We divide the lines in 2 groups:
        # - if we have enough information about the wires and the spacing,
        #  then the line goes to the linegeometry group
        # - otherwise it goes to the linecode group
        lines_to_geometrify = []
        lines_to_linecodify = []
        for i in model.models:
            if isinstance(i, Line):
                use_linecodes = False

                # Find out if we have all the information we need to export
                # the line using geometries. If we miss something, use LineCodes.
                #
                # For overhead (and undefined lines...)
                if i.line_type != "underground":
                    if len(i.wires) == 0:
                        use_linecodes = True
                    for wire in i.wires:
                        # If we are missing the position of at least one wire, default to linecodes
                        if wire.X is None or wire.Y is None:
                            use_linecodes = True
                        # If we are missing the GMR of at least one wire, default to linecodes
                        if wire.gmr is None:
                            use_linecodes = True
                        # If we are missing the diameter of at least one wire, default to linecodes
                        if wire.diameter is None:
                            use_linecodes = True
                        # If we are missing the ampacity of at least one wire, default to linecodes
                        if wire.ampacity is None:
                            use_linecodes = True
                # For underground lines, we need a lot of data...
                else:
                    if len(i.wires) == 0:
                        use_linecodes = True  # For empty lines
                    for wire in i.wires:
                        # If we are missing the position of at least one wire, default to linecodes
                        if wire.X is None or wire.Y is None:
                            use_linecodes = True
                        # If we are missing the GMR of at least one phase conductor, default to linecodes
                        if wire.gmr is None:
                            use_linecodes = True
                        # If we are missing the diameter of at least one phase conductor, default to linecodes
                        if wire.diameter is None:
                            use_linecodes = True
                        # If we are missing the ampacity of at least one wire, default to linecodes
                        if wire.ampacity is None:
                            use_linecodes = True
                        # If we are missing the neutral strand GMR for at least one cable, default to linecodes
                        if wire.concentric_neutral_gmr is None:
                            use_linecodes = True
                        # If we are missing the neutral strand resistance for at least one cable, default to linecodes
                        if wire.concentric_neutral_resistance is None:
                            use_linecodes = True
                        # If we are missing the neutral strand diameter for at least one cable, default to linecodes
                        if wire.concentric_neutral_diameter is None:
                            use_linecodes = True
                        # If we are missing the outside diameter for at least one cable, default to linecodes
                        if wire.concentric_neutral_outside_diameter is None:
                            use_linecodes = True
                        # If we are missing the number of neutral strands for at least one cable, default to linecodes
                        if wire.concentric_neutral_nstrand is None:
                            use_linecodes = True

                if use_linecodes:
                    lines_to_linecodify.append(i)
                else:
                    lines_to_geometrify.append(i)

        self.write_wiredata(
            lines_to_geometrify
        )  # No feeder data specified as these are written to the base folder
        self.write_linegeometry(lines_to_geometrify)
        self.write_linecodes(lines_to_linecodify)

        for i in model.models:
            if isinstance(i, Line):
                if (
                    self.separate_feeders
                    and hasattr(i, "feeder_name")
                    and i.feeder_name is not None
                ):
                    feeder_name = i.feeder_name
                else:
                    feeder_name = "DEFAULT"
                if (
                    self.separate_substations
                    and hasattr(i, "substation_name")
                    and i.substation_name is not None
                ):
                    substation_name = i.substation_name
                else:
                    substation_name = "DEFAULT"

                if not substation_name in substation_text_map:
                    substation_text_map[substation_name] = set([feeder_name])
                else:
                    substation_text_map[substation_name].add(feeder_name)
                txt = ""
                if substation_name + "_" + feeder_name in feeder_text_map:
                    txt = feeder_text_map[substation_name + "_" + feeder_name]

                # Name
                if hasattr(i, "name") and i.name is not None:
                    txt += "New Line." + i.name
                else:
                    continue

                # Set the units in miles for comparison (IEEE 13 nodes feeder)
                # TODO: Let the user specify the export units
                txt += " Units=km"

                # Length
                if hasattr(i, "length") and i.length is not None:
                    txt += " Length={length}".format(
                        length=max(
                            0.001, self.convert_from_meters(np.real(i.length), u"km")
                        )
                    )

                # nominal_voltage (Not mapped)

                # line type (Not mapped)

                # from_element
                if hasattr(i, "from_element") and i.from_element is not None:
                    txt += " bus1={from_el}".format(from_el=i.from_element)
                    if hasattr(i, "wires") and i.wires is not None:
                        for wire in i.wires:
                            if (
                                hasattr(wire, "phase")
                                and wire.phase is not None
                                and wire.phase not in ["N", "N1", "N2"]
                            ):
                                txt += ".{p}".format(p=self.phase_mapping(wire.phase))

                # to_element
                if hasattr(i, "to_element") and i.to_element is not None:
                    txt += " bus2={to_el}".format(to_el=i.to_element)
                    if hasattr(i, "wires") and i.wires is not None:
                        for wire in i.wires:
                            if (
                                hasattr(wire, "phase")
                                and wire.phase is not None
                                and wire.phase not in ["N", "N1", "N2"]
                            ):
                                txt += ".{p}".format(p=self.phase_mapping(wire.phase))

                # is_switch or is_breaker
                if (hasattr(i, "is_switch") and i.is_switch == 1) or (
                    hasattr(i, "is_breaker") and i.is_breaker == 1
                ):
                    txt += " switch=y"
                else:
                    txt += " switch=n"

                if hasattr(i, "wires") and i.wires is not None and len(i.wires) > 0:
                    closed_phase = np.sort(
                        [
                            wire.phase
                            for wire in i.wires
                            if (wire.is_open == 0 or wire.is_open is None)
                            and wire.phase is not None
                            and wire.phase not in ["N", "N1", "N2"]
                        ]
                    )
                    if len(closed_phase) == 0:
                        txt += " enabled=n"
                    else:
                        txt += " enabled=y"

                # is_fuse
                if hasattr(i, "is_fuse") and i.is_fuse == 1:
                    fuse_line = "New Fuse.Fuse_{name} monitoredobj=Line.{name} enabled=y".format(
                        name=i.name
                    )
                    if hasattr(i, "wires") and i.wires is not None:
                        currt_rating = -1
                        all_current_ratings = [
                            w.interrupting_rating
                            for w in i.wires
                            if w.interrupting_rating is not None
                        ]
                        if len(all_current_ratings) > 0:
                            current_rating = max(all_current_ratings)
                            if current_rating > 0:
                                fuse_line += " ratedcurrent={curr}".format(
                                    curr=current_rating
                                )

                else:
                    fuse_line = ""

                # N_phases
                if hasattr(i, "wires") and i.wires is not None:
                    phase_wires = [w for w in i.wires if w.phase in ["A", "B", "C"]]
                    txt += " phases=" + str(len(phase_wires))

                if i in lines_to_geometrify:
                    txt += " geometry={g}".format(g=i.nameclass)
                elif i in lines_to_linecodify:
                    txt += " Linecode={c}".format(c=i.nameclass)

                txt += "\n\n"
                if fuse_line != "":
                    txt += fuse_line
                    txt += "\n\n"

                feeder_text_map[substation_name + "_" + feeder_name] = txt

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if txt != "":
                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    with open(
                        os.path.join(output_folder, self.output_filenames["lines"]), "w"
                    ) as fp:
                        fp.write(txt)

                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(feeder_name, self.output_filenames["lines"])
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["lines"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["lines"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(output_redirect, self.output_filenames["lines"])
                    )

        return 1

    def write_wiredata(self, list_of_lines, feeder_name=None, substation_name=None):
        """
        Write the wires to an OpenDSS file (WireData.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        cnt = 1
        # Loop over the objects
        for i in list_of_lines:
            # If we get a line object
            if isinstance(i, Line):
                # If the line is overhead, then export to WireData
                # If line_type wasn't defined, try to export as for overhead...
                if i.line_type != "underground":
                    # Loop over the wires of this line
                    for wire in i.wires:
                        # Parse the wire to get a dictionary with all the available attributes
                        parsed_wire = self.parse_wire(wire)
                        if len(parsed_wire) > 0:
                            # If we have a nameclass, then use it to ID the wire
                            if wire.nameclass is not None:
                                # If the nameclass is not in self.all_wires, then just add it
                                if wire.nameclass not in self.all_wires:
                                    self.all_wires[wire.nameclass] = parsed_wire
                                # Otherwise, there is nothing to do unless the dictionary we previously has is not
                                # exactly the one we currently have
                                else:
                                    if self.all_wires[wire.nameclass] != parsed_wire:
                                        self.all_wires[
                                            wire.nameclass + "_" + str(cnt)
                                        ] = parsed_wire
                                        wire.nameclass = wire.nameclass + "_" + str(cnt)
                                        cnt += 1
                            # If we don't have a nameclass, we use fake names "wire_1", "wire_2"...
                            else:
                                wire_found = False
                                for k, v in self.all_wires.items():
                                    if parsed_wire == v:
                                        wire_found = True
                                        wire.nameclass = k
                                if not wire_found:
                                    self.all_wires[
                                        "Wire_{n}".format(n=cnt)
                                    ] = parsed_wire
                                    wire.nameclass = "Wire_{n}".format(n=cnt)
                                    cnt += 1
                else:
                    # Loop over the wires of this line
                    for wire in i.wires:
                        # Parse the wire to get a dictionary with all the available attributes
                        parsed_cable = self.parse_cable(wire)
                        if len(parsed_cable) > 0:
                            # If we have a nameclass, then use it to ID the wire
                            if wire.nameclass is not None:
                                # If the nameclass is not in self.all_wires, then just add it
                                if wire.nameclass not in self.all_cables:
                                    self.all_cables[wire.nameclass] = parsed_cable
                                # Otherwise, there is nothing to do unless the dictionary we previously has is not
                                # exactly the one we currently have
                                else:
                                    if self.all_cables[wire.nameclass] != parsed_cable:
                                        self.all_cables[
                                            wire.nameclass + "_" + str(cnt)
                                        ] = parsed_cable
                                        wire.nameclass = wire.nameclass + "_" + str(cnt)
                                        cnt += 1
                            # If we don't have a nameclass, we use fake names "cncable_1", "cncable_2"...
                            else:
                                cable_found = False
                                for k, v in self.all_cables.items():
                                    if parsed_cable == v:
                                        cable_found = True
                                        wire.nameclass = k
                                if not cable_found:
                                    self.all_cables[
                                        "CNCable_{n}".format(n=cnt)
                                    ] = parsed_cable
                                    wire.nameclass = "CNCable_{n}".format(n=cnt)
                                    cnt += 1

        if len(self.all_wires) > 0 or len(self.all_cables) > 0:
            output_folder = None
            output_redirect = None
            if self.separate_substations and substation_name is not None:
                output_folder = os.path.join(self.output_path, substation_name)
                output_redirect = substation_name
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
            else:
                output_folder = os.path.join(self.output_path)
                output_redirect = ""
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

            if self.separate_feeders and feeder_name is not None:
                output_folder = os.path.join(output_folder, feeder_name)
                output_redirect = os.path.join(output_redirect, feeder_name)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

        if len(self.all_wires) > 0:
            fp = open(
                os.path.join(output_folder, self.output_filenames["wiredata"]), "w"
            )

            if (
                self.separate_substations
                and self.separate_feeders
                and feeder_name is not None
                and substation_name is not None
            ):
                if substation_name not in self.substations_redirect:
                    self.substations_redirect[substation_name] = []
                self.substations_redirect[substation_name].append(
                    os.path.join(feeder_name, self.output_filenames["wiredata"])
                )
            elif self.separate_substations and substation_name is not None:
                if substation_name not in self.substations_redirect:
                    self.substations_redirect[substation_name] = []
                self.substations_redirect[substation_name].append(
                    self.output_filenames["wiredata"]
                )
            if self.separate_feeders and feeder_name is not None:
                combined_feeder_sub = os.path.join(substation_name, feeder_name)
                if combined_feeder_sub not in self.feeders_redirect:
                    self.feeders_redirect[combined_feeder_sub] = []
                self.feeders_redirect[combined_feeder_sub].append(
                    self.output_filenames["wiredata"]
                )

            self.files_to_redirect.append(
                os.path.join(output_redirect, self.output_filenames["wiredata"])
            )
            for wire_name, wire_data in self.all_wires.items():
                fp.write("New WireData.{name}".format(name=wire_name))
                for key, value in wire_data.items():
                    fp.write(" {k}={v}".format(k=key, v=value))
                fp.write("\n\n")

        if len(self.all_cables) > 0:
            fp = open(os.path.join(output_folder, self.output_filenames["CNDATA"]), "w")

            if (
                self.separate_substations
                and self.separate_feeders
                and feeder_name is not None
                and substation_name is not None
            ):
                if substation_name not in self.substations_redirect:
                    self.substations_redirect[substation_name] = []
                self.substations_redirect[substation_name].append(
                    os.path.join(feeder_name, self.output_filenames["CNDATA"])
                )
            elif self.separate_substations and substation_name is not None:
                if substation_name not in self.substations_redirect:
                    self.substations_redirect[substation_name] = []
                self.substations_redirect[substation_name].append(
                    self.output_filenames["CNDATA"]
                )
            if self.separate_feeders and feeder_name is not None:
                combined_feeder_sub = os.path.join(substation_name, feeder_name)
                if combined_feeder_sub not in self.feeders_redirect:
                    self.feeders_redirect[combined_feeder_sub] = []
                self.feeders_redirect[combined_feeder_sub].append(
                    self.output_filenames["CNDATA"]
                )

            self.files_to_redirect.append(
                os.path.join(output_redirect, self.output_filenames["CNDATA"])
            )
            for cable_name, cable_data in self.all_cables.items():
                fp.write("New CNDATA.{name}".format(name=cable_name))
                for key, value in cable_data.items():
                    fp.write(" {k}={v}".format(k=key, v=value))
                fp.write("\n\n")

        return 1

    def write_linegeometry(self, list_of_lines, feeder_name=None, substation_name=None):
        """
        Write the Line geometries to an OpenDSS file (LineGeometry.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int

        .. warning:: This must be called after write_wiredata()
        """
        cpt = 1
        for i in list_of_lines:
            if isinstance(i, Line):
                parsed_line = self.parse_line_geometry(i)
                if len(parsed_line) > 0:
                    if i.nameclass is not None:
                        if i.nameclass not in self.all_geometries:
                            self.all_geometries[i.nameclass] = parsed_line
                        else:
                            if self.all_geometries[i.nameclass] != parsed_line:
                                self.all_geometries[
                                    i.nameclass + "_" + str(cpt)
                                ] = parsed_line
                                i.nameclass = i.nameclass + "_" + str(cpt)
                                cpt += 1
                    else:
                        geometry_found = False
                        for k, v in self.all_geometries.items():
                            if parsed_line == v:
                                geometry_found = True
                                i.nameclass = k
                        if not geometry_found:
                            self.all_geometries[
                                "Geometry_{n}".format(n=cpt)
                            ] = parsed_line
                            i.nameclass = "Geometry_{n}".format(n=cpt)
                            cpt += 1

        if len(self.all_geometries) > 0:
            output_folder = None
            output_redirect = None
            if self.separate_substations and substation_name is not None:
                output_folder = os.path.join(self.output_path, substation_name)
                output_redirect = substation_name
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
            else:
                output_folder = os.path.join(self.output_path)
                output_redirect = ""
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

            if self.separate_feeders and feeder_name is not None:
                output_folder = os.path.join(output_folder, feeder_name)
                output_redirect = os.path.join(output_redirect, feeder_name)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

            fp = open(
                os.path.join(output_folder, self.output_filenames["linegeometry"]), "w"
            )
            if (
                self.separate_substations
                and self.separate_feeders
                and substation_name is not None
                and feeder_name is not None
            ):
                if substation_name not in self.substations_redirect:
                    self.substations_redirect[substation_name] = []
                self.substations_redirect[substation_name].append(
                    os.path.join(feeder_name, self.output_filenames["linegeometry"])
                )
            elif self.separate_substations and substation_name is not None:
                if substation_name not in self.substations_redirect:
                    self.substations_redirect[substation_name] = []
                self.substations_redirect[substation_name].append(
                    self.output_filenames["linegeometry"]
                )
            if self.separate_feeders and feeder_name is not None:
                combined_feeder_sub = os.path.join(substation_name, feeder_name)
                if combined_feeder_sub not in self.feeders_redirect:
                    self.feeders_redirect[combined_feeder_sub] = []
                self.feeders_redirect[combined_feeder_sub].append(
                    self.output_filenames["linegeometry"]
                )

            self.files_to_redirect.append(
                os.path.join(output_redirect, self.output_filenames["linegeometry"])
            )
            for geometry_name, geometry_data in self.all_geometries.items():
                fp.write("New LineGeometry.{name}".format(name=geometry_name))
                if "nconds" in geometry_data:
                    fp.write(" Nconds={n}".format(n=geometry_data["nconds"]))
                if "nphases" in geometry_data:
                    fp.write(" Nphases={n}".format(n=geometry_data["nphases"]))
                if "units" in geometry_data:
                    fp.write(" Units={u}".format(u=geometry_data["units"]))
                for conductor in geometry_data["conductor_list"]:
                    fp.write(" Cond={c}".format(c=conductor["cond"]))
                    for k, v in conductor.items():
                        if k != "cond":
                            fp.write(" {k}={v}".format(k=k, v=v))
                if "reduce" in geometry_data:
                    fp.write(" Reduce={r}".format(r=geometry_data["reduce"]))
                fp.write("\n\n")

        return 1

    def write_linecodes(self, list_of_lines, feeder_name=None, substation_name=None):
        """Write the linecodes to an OpenDSS file (Linecodes.dss by default).

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int

        .. note::

            Since there is no linecode object equivalent in DiTTo, we have to re-construct them from the line objects.
            Therefore, when doing DSS--->DiTTo--->DSS for the same circuit, the new linecodes will have different names than the old ones.
        """
        cnt = 0
        substation_text_map = {}
        feeder_text_map = {}
        substation_feeder_lookup = {}
        for i in list_of_lines:
            if isinstance(i, Line):

                parsed_line = self.parse_line(i)
                if len(parsed_line) > 0:

                    if (
                        self.separate_feeders
                        and hasattr(i, "feeder_name")
                        and i.feeder_name is not None
                    ):
                        feeder_name = i.feeder_name
                    else:
                        feeder_name = "DEFAULT"
                    if (
                        self.separate_substations
                        and hasattr(i, "substation_name")
                        and i.substation_name is not None
                    ):
                        substation_name = i.substation_name
                    else:
                        substation_name = "DEFAULT"

                    if not substation_name in substation_text_map:
                        substation_text_map[substation_name] = set([feeder_name])
                    else:
                        substation_text_map[substation_name].add(feeder_name)
                    txt = {}
                    if substation_name + "_" + feeder_name in feeder_text_map:
                        txt = feeder_text_map[substation_name + "_" + feeder_name]
                    substation_feeder_lookup[substation_name + "_" + feeder_name] = (
                        substation_name,
                        feeder_name,
                    )

                    if i.nameclass is not None:
                        if "nphases" in parsed_line:
                            n_phases = str(parsed_line["nphases"])
                        else:
                            n_phases = ""
                        nameclass_phase = i.nameclass + "_" + n_phases
                        if nameclass_phase not in self.all_linecodes:
                            self.all_linecodes[nameclass_phase] = parsed_line
                            txt[nameclass_phase] = parsed_line
                            i.nameclass = nameclass_phase
                        elif nameclass_phase not in txt:
                            txt[nameclass_phase] = parsed_line
                            i.nameclass = nameclass_phase
                        else:
                            if self.all_linecodes[nameclass_phase] != parsed_line:
                                found_subnumber = False
                                for j in range(cnt):
                                    if (
                                        nameclass_phase + "_" + str(j)
                                        in self.all_linecodes
                                    ):
                                        i.nameclass = nameclass_phase + "_" + str(j)
                                        found_subnumber = True
                                        if i.nameclass not in txt:
                                            txt[i.nameclass] = parsed_line
                                        break
                                if not found_subnumber:
                                    self.all_linecodes[
                                        nameclass_phase + "_" + str(cnt)
                                    ] = parsed_line
                                    txt[nameclass_phase + "_" + str(cnt)] = parsed_line
                                    i.nameclass = nameclass_phase + "_" + str(cnt)
                                    cnt += 1
                            else:
                                i.nameclass = nameclass_phase

                    else:
                        linecode_found = False
                        for k, v in self.all_linecodes.items():
                            if parsed_line == v:
                                linecode_found = True
                                i.nameclass = k
                        if not linecode_found:
                            nameclass = ""
                            if hasattr(i, "wires") and i.wires is not None:
                                phase_wires = [
                                    w for w in i.wires if w.phase in ["A", "B", "C"]
                                ]
                                nameclass += str(len(phase_wires)) + "P_"

                            if hasattr(i, "line_type") and i.line_type == "overhead":
                                nameclass += "OH_"

                            if hasattr(i, "line_type") and i.line_type == "underground":
                                nameclass += "UG_"
                            self.all_linecodes[
                                "{class_}Code{N}".format(class_=nameclass, N=cnt)
                            ] = parsed_line
                            txt[
                                "{class_}Code{N}".format(class_=nameclass, N=cnt)
                            ] = parsed_line
                            i.nameclass = "{class_}Code{N}".format(
                                class_=nameclass, N=cnt
                            )
                            cnt += 1
                    feeder_text_map[substation_name + "_" + feeder_name] = txt

        for substation_name in substation_text_map:
            for feeder_name in substation_text_map[substation_name]:
                txt = feeder_text_map[substation_name + "_" + feeder_name]
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                if len(txt) != 0:

                    output_folder = None
                    output_redirect = None
                    if self.separate_substations:
                        output_folder = os.path.join(self.output_path, substation_name)
                        output_redirect = substation_name
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                    else:
                        output_folder = os.path.join(self.output_path)
                        output_redirect = ""
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_feeders:
                        output_folder = os.path.join(output_folder, feeder_name)
                        output_redirect = os.path.join(output_redirect, feeder_name)
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)

                    if self.separate_substations and self.separate_feeders:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            os.path.join(
                                feeder_name, self.output_filenames["linecodes"]
                            )
                        )
                    elif self.separate_substations:
                        if substation_name not in self.substations_redirect:
                            self.substations_redirect[substation_name] = []
                        self.substations_redirect[substation_name].append(
                            self.output_filenames["linecodes"]
                        )
                    if self.separate_feeders:
                        combined_feeder_sub = os.path.join(substation_name, feeder_name)
                        if combined_feeder_sub not in self.feeders_redirect:
                            self.feeders_redirect[combined_feeder_sub] = []
                        self.feeders_redirect[combined_feeder_sub].append(
                            self.output_filenames["linecodes"]
                        )

                    self.files_to_redirect.append(
                        os.path.join(
                            output_redirect, self.output_filenames["linecodes"]
                        )
                    )

                    fp = open(
                        os.path.join(output_folder, self.output_filenames["linecodes"]),
                        "w",
                    )

                    for linecode_name, linecode_data in txt.items():
                        fp.write("New Linecode.{name}".format(name=linecode_name))
                        for k, v in linecode_data.items():
                            fp.write(" {k}={v}".format(k=k, v=v))
                        fp.write("\n\n")

        return 1

    def parse_line(self, line):
        """
        This function is used to associate lines to linecodes or linegeometry.
        Multiple lines can share the same parameters (like length, resistance matrix,...), such that these lines will be be associated with the same linecode.

        :param line: Line diTTo object
        :type line: Line diTTo object
        :returns: result
        :rtype: dict
        """
        result = {}
        uni = "km"
        result["units"] = "km"  # DiTTO is in meters

        # N_phases
        if hasattr(line, "wires") and line.wires is not None:
            phase_wires = [w for w in line.wires if w.phase in ["A", "B", "C"]]
            result["nphases"] = len(phase_wires)

        # faultrate
        if hasattr(line, "faultrate") and line.faultrate is not None:
            result["Faultrate"] = line.faultrate

        # If we have the impedance matrix, we need to extract both
        # the resistance and reactance matrices
        R = None
        X = None
        if (
            hasattr(line, "impedance_matrix")
            and line.impedance_matrix is not None
            and line.impedance_matrix != []
        ):
            # Use numpy arrays since it is much easier for complex numbers
            try:
                Z = np.array(line.impedance_matrix)
                R = np.real(Z)  # Resistance matrix
                X = np.imag(Z)  # Reactance  matrix
            except:
                logger.error(
                    "Problem with impedance matrix in line {name}".format(
                        name=line.name
                    )
                )
        # Provide small impedance matrix for switches and breakers with no impedance matrix
        elif (
            (hasattr(line, "is_switch") and line.is_switch)
            or (hasattr(line, "is_breaker") and line.is_breaker)
            or (hasattr(line, "is_fuse") and line.is_fuse)
            or (hasattr(line, "is_recloser") and line.is_recloser)
            and "nphases" in result
        ):
            X = [
                [0 for i in range(result["nphases"])] for j in range(result["nphases"])
            ]
            for i in range(result["nphases"]):
                X[i][i] = 0.00000001
            R = [
                [0 for i in range(result["nphases"])] for j in range(result["nphases"])
            ]
            for i in range(result["nphases"]):
                R[i][i] = 0.00000001

        if R is not None and X is not None:
            result["Rmatrix"] = "("
            for row in R:
                for elt in row:
                    result["Rmatrix"] += "{e} ".format(
                        e=self.convert_from_meters(np.real(elt), uni, inverse=True)
                    )
                result["Rmatrix"] += "| "
            result["Rmatrix"] = result["Rmatrix"][
                :-2
            ]  # Remove the last "| " since we do not need it
            result["Rmatrix"] += ")"

            result["Xmatrix"] = "("
            for row in X:
                for elt in row:
                    result["Xmatrix"] += "{e} ".format(
                        e=self.convert_from_meters(np.real(elt), uni, inverse=True)
                    )
                result["Xmatrix"] += "| "
            result["Xmatrix"] = result["Xmatrix"][
                :-2
            ]  # Remove the last "| " since we do not need it
            result["Xmatrix"] += ")"

        if (
            hasattr(line, "capacitance_matrix")
            and line.capacitance_matrix is not None
            and line.capacitance_matrix != []
        ):
            C = np.array(line.capacitance_matrix)
            result["Cmatrix"] = "("
            for row in C:
                for elt in row:
                    result["Cmatrix"] += "{e} ".format(
                        e=self.convert_from_meters(np.real(elt), uni, inverse=True)
                    )
                result["Cmatrix"] += "| "
            result["Cmatrix"] = result["Cmatrix"][
                :-2
            ]  # Remove the last "| " since we do not need it
            result["Cmatrix"] += ")"

        # Ampacity
        if (
            hasattr(line, "wires")
            and line.wires is not None
            and len(line.wires) > 0
            and hasattr(line.wires[0], "ampacity")
            and line.wires[0].ampacity is not None
        ):
            result["normamps"] = line.wires[0].ampacity

        # Emergency ampacity
        if (
            hasattr(line, "wires")
            and line.wires is not None
            and len(line.wires) > 0
            and hasattr(line.wires[0], "emergency_ampacity")
            and line.wires[0].emergency_ampacity is not None
        ):
            result["emergamps"] = line.wires[0].emergency_ampacity

        return result

    def parse_cable(self, wire):
        """
        Takes a wire DiTTo object as input and outputs a dictionary with the attribute of
        the concentric neutral cable it represents.

        :param wire: Wire diTTo object
        :type wire: Wire diTTo object
        :returns: result
        :rtype: dict
        """
        result = {}
        # Insulator thickness
        if (
            hasattr(wire, "insulation_thickness")
            and wire.insulation_thickness is not None
        ):
            result["InsLayer"] = wire.insulation_thickness
            if hasattr(wire, "diameter") and wire.diameter is not None:
                result["DiaIns"] = wire.diameter + 2 * wire.insulation_thickness

        # Number of concentric neutral strands
        if (
            hasattr(wire, "concentric_neutral_nstrand")
            and wire.concentric_neutral_nstrand is not None
        ):
            result["k"] = wire.concentric_neutral_nstrand

        # Diameter of the neutral strands
        if (
            hasattr(wire, "concentric_neutral_diameter")
            and wire.concentric_neutral_diameter is not None
        ):
            result["DiaStrand"] = wire.concentric_neutral_diameter

        # Resistance of the neutral strand
        if (
            hasattr(wire, "concentric_neutral_resistance")
            and wire.concentric_neutral_resistance is not None
        ):
            result["Rstrand"] = wire.concentric_neutral_resistance

        # Diameter of the phase conductor
        # Here wire.diameter is used
        #
        if hasattr(wire, "diameter") and wire.diameter is not None:
            result["Diam"] = wire.diameter

        # Outside diameter of the cable
        if (
            hasattr(wire, "concentric_neutral_outside_diameter")
            and wire.concentric_neutral_outside_diameter is not None
        ):
            result["DiaCable"] = wire.concentric_neutral_outside_diameter

        # Resistance of the phase conductor
        # Here wire.resistance is used
        # since the neutral resistance has its own attribute, there is no confict
        #
        if hasattr(wire, "resistance") and wire.resistance is not None:
            result["Rac"] = wire.resistance

        # GMR of the neutral strand
        if (
            hasattr(wire, "concentric_neutral_gmr")
            and wire.concentric_neutral_gmr is not None
        ):
            result["GmrStrand"] = wire.concentric_neutral_gmr

        # GMR of the phase conductor
        # Here wire.gmr is used
        #
        if hasattr(wire, "gmr") and wire.gmr is not None:
            result["GMRac"] = wire.gmr

        # While the units are being integrated into DiTTo, we assume that
        # everything is in meters here, even if it doesn't make much sense for cable properties...
        result["Runits"] = "m"
        result["Radunits"] = "m"
        result["GMRunits"] = "m"

        return result

    def parse_wire(self, wire):
        """
        Takes a wire diTTo object as input and outputs a dictionary with the attributes of the wire.

        :param wire: Wire diTTo object
        :type wire: Wire diTTo object
        :returns: result
        :rtype: dict
        """
        result = {}

        # GMR
        if hasattr(wire, "gmr") and wire.gmr is not None:
            result["GMRac"] = wire.gmr
            result["GMRunits"] = "m"  # Let OpenDSS know we are in meters here

        # Diameter
        if hasattr(wire, "diameter") and wire.diameter is not None:
            result["Diam"] = wire.diameter
            result["Radunits"] = "m"  # Let OpenDSS know we are in meters here

        # Ampacity
        if hasattr(wire, "ampacity") and wire.ampacity is not None:
            result["normamps"] = wire.ampacity

        # Emergency ampacity
        if hasattr(wire, "emergency_ampacity") and wire.emergency_ampacity is not None:
            result["emergamps"] = wire.emergency_ampacity

        # Resistance
        if hasattr(wire, "resistance") and wire.resistance is not None:
            result["Rac"] = wire.resistance

        return result

    def parse_line_geometry(self, line):
        """
        Takes a Line object as input and outputs a dictionary for building a lineGeometry string.

        :param line: Line diTTo object
        :type line: Line
        :returns: result
        :rtype: dict

        .. note:: This model keeps the line neutrals in and doesn't reduce them out
        """
        result = {}
        wire_list = line.wires
        result["nconds"] = len(wire_list)
        phase_wires = [w for w in wire_list if w.phase in ["A", "B", "C"]]
        result["nphases"] = len(phase_wires)
        result["units"] = "m"
        result["conductor_list"] = []
        for cond, wire in enumerate(wire_list):
            result["conductor_list"].append({})
            cond += 1
            result["conductor_list"][-1]["cond"] = cond
            if wire.nameclass in self.all_wires:
                result["conductor_list"][-1]["Wire"] = wire.nameclass
            elif wire.nameclass in self.all_cables:
                result["conductor_list"][-1]["CNCable"] = wire.nameclass
            else:
                raise ValueError("Wire {name} not found.".format(name=wire.nameclass))

            if hasattr(wire, "X") and wire.X is not None:
                result["conductor_list"][-1]["X"] = wire.X

            if hasattr(wire, "Y") and wire.Y is not None:
                result["conductor_list"][-1]["H"] = wire.Y

            if hasattr(wire, "ampacity") and wire.ampacity is not None:
                result["conductor_list"][-1]["Normamps"] = wire.ampacity

            if (
                hasattr(wire, "emergency_ampacity")
                and wire.emergency_ampacity is not None
            ):
                result["conductor_list"][-1]["Emergamps"] = wire.emergency_ampacity

        if len(phase_wires) != len(wire_list):
            result["reduce"] = "y"
        else:
            result["reduce"] = "n"

        return result

    def write_master_file(self, model):
        """Write the master.dss file."""
        with open(
            os.path.join(self.output_path, self.output_filenames["master"]), "w"
        ) as fp:
            fp.write("Clear\n\nNew Circuit.Full_Network ")
            for obj in model.models:
                if (
                    isinstance(obj, PowerSource) and obj.is_sourcebus == 1
                ):  # For RNM datasets only one source exists.
                    if "_src" in obj.name:
                        cleaned_name = obj.name[:-4]
                    else:
                        cleaned_name = obj.name
                    if (
                        hasattr(obj, "connecting_element")
                        and obj.connecting_element is not None
                    ):
                        fp.write(
                            "bus1={name} pu={pu}".format(
                                name=obj.connecting_element, pu=obj.per_unit
                            )
                        )
                    else:
                        logger.warning(
                            "No valid name for connecting element of source {}. Using name of the source instead...".format(
                                cleaned_name
                            )
                        )
                        fp.write(
                            "bus1={name} pu={pu}".format(
                                name=cleaned_name, pu=obj.per_unit
                            )
                        )

                    if (
                        hasattr(obj, "nominal_voltage")
                        and obj.nominal_voltage is not None
                    ):
                        fp.write(
                            " basekV={volt}".format(volt=obj.nominal_voltage * 10 ** -3)
                        )  # DiTTo in volts

                    if (
                        hasattr(obj, "positive_sequence_impedance")
                        and obj.positive_sequence_impedance is not None
                    ):
                        R1 = obj.positive_sequence_impedance.real
                        X1 = obj.positive_sequence_impedance.imag
                        fp.write(
                            " R1={R1} X1={X1}".format(
                                R1=self.float_to_str(R1), X1=self.float_to_str(X1)
                            )
                        )

                    if (
                        hasattr(obj, "zero_sequence_impedance")
                        and obj.zero_sequence_impedance is not None
                    ):
                        R0 = obj.zero_sequence_impedance.real
                        X0 = obj.zero_sequence_impedance.imag
                        fp.write(
                            " R0={R0} X0={X0}".format(
                                R0=self.float_to_str(R0), X0=self.float_to_str(X0)
                            )
                        )

            fp.write("\n\n")

            # Write WireData.dss first if it exists
            if self.output_filenames["wiredata"] in self.files_to_redirect:
                fp.write(
                    "Redirect {f}\n".format(f=self.output_filenames["wiredata"])
                )  # Currently wire data is in the base folder
                self.files_to_redirect.remove(self.output_filenames["wiredata"])

            # Write CNDATA.dss first if it exists
            if self.output_filenames["CNDATA"] in self.files_to_redirect:
                fp.write(
                    "Redirect {f}\n".format(f=self.output_filenames["CNDATA"])
                )  # Currently wire data is in the base folder
                self.files_to_redirect.remove(self.output_filenames["CNDATA"])

            # Write LineGeometry.dss then if it exists
            if self.output_filenames["linegeometry"] in self.files_to_redirect:
                fp.write(
                    "Redirect {f}\n".format(f=self.output_filenames["linegeometry"])
                )  # Currently line geometry is in the base folder
                self.files_to_redirect.remove(self.output_filenames["linegeometry"])

            # Write LineCodes.dss then if it exists
            if self.output_filenames["linecodes"] in self.files_to_redirect:
                fp.write("Redirect {f}\n".format(f=self.output_filenames["linecodes"]))
                self.files_to_redirect.remove(self.output_filenames["linecodes"])

            # Write Lines.dss then if it exists
            if self.output_filenames["lines"] in self.files_to_redirect:
                fp.write("Redirect {f}\n".format(f=self.output_filenames["lines"]))
                self.files_to_redirect.remove(self.output_filenames["lines"])

            # Write Transformers.dss then if it exists
            if self.output_filenames["transformers"] in self.files_to_redirect:
                fp.write(
                    "Redirect {f}\n".format(f=self.output_filenames["transformers"])
                )
                self.files_to_redirect.remove(self.output_filenames["transformers"])

            # Then, redirect the rest (the order should not matter anymore)
            # Buscoords is not included here, only the combined buscoords file is included in the master file
            for file in self.files_to_redirect:
                if (
                    file[-1 * len(self.output_filenames["buses"]) :]
                    != self.output_filenames["buses"]
                ):
                    fp.write("Redirect {file}\n".format(file=file))

            _baseKV_list_ = list(self._baseKV_)
            _baseKV_list_ = sorted(_baseKV_list_)
            fp.write("\nSet Voltagebases={}\n".format(_baseKV_list_))

            fp.write("\nCalcvoltagebases\n\n")

            if (
                self.output_filenames["buses"] in self.files_to_redirect
            ):  # Only write combined bus file to masterfile
                fp.write(
                    "Buscoords {f}\n".format(f=self.output_filenames["buses"])
                )  # The buscoords are also written to base folder as well as the subfolders

            fp.write("\nSolve")
        for i in model.models:
            if isinstance(i, Node) and i.is_substation_connection:
                feeder_name = i.feeder_name
                substation_name = i.substation_name
                feeder_name = feeder_name.replace(">", "-")
                substation_name = substation_name.replace(">", "-")
                # Note that subtransmission has no substation_connection and hence doesn't have a master file, even though it does have other .dss files
                if (
                    feeder_name == "" and i.nominal_voltage < 30000
                ):  # A hack to deal with dangling feeders. TODO: Fix this in layerstack
                    continue
                with open(
                    os.path.join(
                        self.output_path,
                        substation_name,
                        feeder_name,
                        self.output_filenames["master"],
                    ),
                    "w",
                ) as fp:

                    if (
                        substation_name in self.substations_redirect
                        and feeder_name == ""
                    ):  # i.e. it's a substation
                        fp.write(
                            "Clear\n\nNew Circuit.substation_{name} ".format(
                                name=i.name
                            )
                        )

                    if (
                        os.path.join(substation_name, feeder_name)
                        in self.feeders_redirect
                        and not os.path.join(substation_name, feeder_name).strip("/")
                        in self.substations_redirect
                    ):  # i.e. it's a feeder
                        fp.write(
                            "Clear\n\nNew Circuit.feeder_{name} ".format(name=i.name)
                        )
                    fp.write("bus1={name} pu={pu}".format(name=i.name, pu=i.setpoint))
                    if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                        fp.write(
                            " basekV={volt}".format(volt=i.nominal_voltage * 10 ** -3)
                        )  # DiTTo in volts
                    fp.write(
                        " R1={R1} X1={X1}".format(R1=0.00001, X1=0.00001)
                    )  # Infinite source bus
                    fp.write(
                        " R0={R0} X0={X0}".format(R0=0.00001, X0=0.00001)
                    )  # Infinite source bus
                    fp.write("\n\n")
                    if (
                        substation_name in self.substations_redirect
                        and feeder_name == ""
                    ):  # i.e. it's a substation
                        for element in self.substations_redirect[substation_name]:
                            fp.write("Redirect " + element + "\n")
                    if (
                        os.path.join(substation_name, feeder_name)
                        in self.feeders_redirect
                        and not os.path.join(substation_name, feeder_name).strip("/")
                        in self.substations_redirect
                    ):  # i.e. it's a feeder
                        for element in self.feeders_redirect[
                            os.path.join(substation_name, feeder_name)
                        ]:
                            fp.write("Redirect " + element + "\n")
                    if i.substation_name + "_" + i.feeder_name in self._baseKV_feeders_:
                        _baseKV_list_ = list(
                            self._baseKV_feeders_[
                                i.substation_name + "_" + i.feeder_name
                            ]
                        )
                    else:
                        _baseKV_list_ = []
                    _baseKV_list_ = sorted(_baseKV_list_)
                    fp.write("\nSet Voltagebases={}\n".format(_baseKV_list_))

                    fp.write("\nCalcvoltagebases\n\n")

                    if (
                        self.output_filenames["buses"] in self.files_to_redirect
                    ):  # Only write combined bus file to masterfile
                        fp.write(
                            "Buscoords {f}\n".format(f=self.output_filenames["buses"])
                        )  # The buscoords are also written to base folder as well as the subfolders

                    fp.write("\nSolve")
