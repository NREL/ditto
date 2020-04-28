# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import os
import re
import math
import logging

# DiTTo imports
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding

from ..abstract_writer import AbstractWriter

logger = logging.getLogger(__name__)


class Writer(AbstractWriter):

    register_names = ["glm", "gridlabd"]

    line_configurations = {}
    line_configurations_name = {}
    transformer_configurations = {}
    transformer_configurations_name = {}
    regulator_configurations = {}
    regulator_configurations_name = {}
    regulator_phases = {}
    regulator_seen = set()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        # Whether or not to write wires (default is to write impdence matrix)
        if "write_wires" in kwargs and isinstance(kwargs["write_wires"], bool):
            self.write_wires = True
        else:
            self.write_wires = False

        with open(os.path.join(self.output_path, "Model.glm"), "w") as fp:

            # Write the modules
            logger.info("Writing the Module...")
            if self.verbose:
                logger.debug("Writing the Module...")
            fp.write(
                "module powerflow{\n    solver_method NR;\n    NR_iteration_limit 50;\n};\n\n"
            )
            if self.verbose:
                logger.debug("Succesful!")

            # Write the nodes
            logger.info("Writing the Nodes...")
            if self.verbose:
                logger.debug("Writing the Nodes...")
            _ = self.write_nodes(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write the capacitors
            logger.info("Writing the Capacitors...")
            if self.verbose:
                logger.debug("Writing the Capacitors...")
            _ = self.write_capacitors(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write the loads
            logger.info("Writing the Loads...")
            if self.verbose:
                logger.debug("Writing the Loads...")
            _ = self.write_loads(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write transformer configurations
            logger.info("Writing the Transformer Configurations...")
            if self.verbose:
                logger.debug("Writing the Transformer Configurations...")
            _ = self.write_transformer_configurations(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write transformers
            logger.info("Writing the Transformers...")
            if self.verbose:
                logger.debug("Writing the Transformers...")
            _ = self.write_transformers(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write regulator configurations
            logger.info("Writing the Regulator Configurations...")
            if self.verbose:
                logger.debug("Writing the Regulator Configurations...")
            _ = self.write_regulator_configurations(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write regulators
            logger.info("Writing the Regulators...")
            if self.verbose:
                logger.debug("Writing the Regulators...")
            _ = self.write_regulators(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write line configurations
            logger.info("Writing the Line Configurations...")
            if self.verbose:
                logger.debug("Writing the Line Configurations...")
            _ = self.write_line_configurations(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

            # Write lines
            logger.info("Writing the Lines...")
            if self.verbose:
                logger.debug("Writing the Lines...")
            _ = self.write_lines(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

    def write_nodes(self, model, fp, sourcebus="sourcebus"):
        """ Write the Nodes into the existing file.
        Positions not written into gridlab-d
        Assume there is always a neutral phase if non-neutral phases exist

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int
        """
        for i in model.models:
            if isinstance(i, Node):
                fp.write("object node {\n")

                # Name
                if hasattr(i, "name") and i.name is not None:
                    fp.write("    name n{name};\n".format(name=i.name))
                    if i.name == sourcebus:
                        fp.write("    bustype SWING;\n")

                # Phases
                if hasattr(i, "phases") and i.phases is not None and len(i.phases) > 0:
                    fp.write("    phases ")
                    for phase in i.phases:
                        fp.write(phase.default_value)
                    fp.write("N;\n")

                # Nominal Voltage
                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    fp.write(
                        "     nominal_voltage {nv};\n".format(nv=i.nominal_voltage)
                    )
                else:
                    fp.write(
                        "    nominal_voltage 12470;\n"
                    )  # TODO: FIX THIS so that the nomainl voltage is computed internally for all nodes

                fp.write("};\n\n")

        return 1

    def write_capacitors(self, model, fp):
        for i in model.models:
            if isinstance(i, Capacitor):
                fp.write("object capacitor {\n")

                if hasattr(i, "name") and i.name is not None:
                    fp.write("    name n{name};\n".format(name=i.name))

                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    fp.write("    nominal_voltage {nv};\n".format(nv=i.nominal_voltage))

                if hasattr(i, "delay") and i.delay is not None:
                    fp.write("    time_dela {td};\n".format(td=i.delay))

                if hasattr(i, "mode") and i.mode is not None:
                    fp.write("    control {mode};\n".format(mode=i.mode))

                if hasattr(i, "low") and i.low is not None:
                    fp.write("    voltage_set_low {low};\n".format(low=i.low))

                if hasattr(i, "high") and i.low is not None:
                    fp.write("    voltage_set_high {high};\n".format(high=i.high))

                if hasattr(i, "pt_phase") and i.pt_phase is not None:
                    fp.write("    pt_phase {pt};\n".format(pt=i.pt_phase))

                if (
                    hasattr(i, "connecting_element")
                    and i.connecting_element is not None
                ):
                    fp.write("    parent n{ce};\n".format(ce=i.connecting_element))

                if hasattr(i, "phase_capacitors") and i.phase_capacitors is not None:
                    phases = ""
                    for j in i.phase_capacitors:
                        if hasattr(j, "phase") and j.phase is not None:
                            phases = phases + j.phase
                            logger.debug(j.var)
                            if hasattr(j, "var") and j.var is not None:
                                fp.write(
                                    "    capacitor_{phase} {var};\n".format(
                                        phase=j.phase, var=j.var / 1000000.0
                                    )
                                )
                            if hasattr(j, "switch") and j.var is not None:
                                if j.switch == 1:
                                    fp.write("    switch" + j.phase + " OPEN;\n")
                                else:
                                    fp.write("    switch" + j.phase + " CLOSED;\n")

                    if phases != "":
                        fp.write("    phases {ps};\n".format(ps=phases))

                else:
                    logger.debug(
                        "Warning - No phases provided for the Capacitor. No vars will be supplied"
                    )
                fp.write("};\n\n")

    def write_loads(self, model, fp):
        for i in model.models:
            if isinstance(i, Load):
                fp.write("object load {\n")
                if hasattr(i, "name") and i.name is not None:
                    fp.write("    name n{name};\n".format(name=i.name))

                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    fp.write("    nominal_voltage {nv};\n".format(nv=i.nominal_voltage))

                if (
                    hasattr(i, "connecting_element")
                    and i.connecting_element is not None
                ):
                    fp.write("    parent n{ce};\n".format(ce=i.connecting_element))

                if hasattr(i, "phase_loads") and i.phase_loads is not None:
                    phases = ""
                    for j in i.phase_loads:
                        if hasattr(j, "phase") and j.phase is not None:
                            phases = phases + j.phase

                            if hasattr(j, "use_zip") and j.use_zip is not None:
                                if (
                                    j.use_zip == 1
                                ):  # This means that all the required values are not None
                                    fp.write(
                                        "    current_fraction_{phase} {cf};\n".format(
                                            phase=j.phase,
                                            cf=(j.ppercentcurrent + j.qpercentcurrent),
                                        )
                                    )
                                    fp.write(
                                        "    current_pf_{phase} {cpf};\n".format(
                                            phase=j.phase,
                                            cpf=(
                                                j.ppercentcurrent
                                                / (
                                                    j.ppercentcurrent
                                                    + j.qpercentcurrent
                                                )
                                            ),
                                        )
                                    )
                                    fp.write(
                                        "    power_fraction_{phase} {pf};\n".format(
                                            phase=j.phase,
                                            pf=(j.ppercentpower + j.qpercentpower),
                                        )
                                    )
                                    fp.write(
                                        "    power_pf_{phase} {ppf};\n".format(
                                            phase=j.phase,
                                            ppf=(
                                                j.ppercentpower
                                                / (j.ppercentpower + j.qpercentpower)
                                            ),
                                        )
                                    )
                                    fp.write(
                                        "    impedance_fraction_{phase} {iff};\n".format(
                                            phase=j.phase,
                                            iff=(
                                                j.ppercentimpedance
                                                + j.qpercentimpedance
                                            ),
                                        )
                                    )
                                    fp.write(
                                        "    impedance_pf_{phase} {ipf};\n".format(
                                            phase=j.phase,
                                            ipf=(
                                                j.ppercentimpedance
                                                / (
                                                    j.ppercentimpedance
                                                    + j.qpercentimpedance
                                                )
                                            ),
                                        )
                                    )
                                    fp.write(
                                        "    base_power_{phase} {bp};\n".format(
                                            phase=j.phase, bp=complex(j.p, j.q)
                                        )
                                    )

                                else:
                                    if (
                                        hasattr(j, "p")
                                        and j.p is not None
                                        and hasattr(j, "q")
                                        and j.q is not None
                                        and hasattr(j, "phase")
                                        and j.phase is not None
                                    ):
                                        fp.write(
                                            "    constant_power_{phase} {cp};\n".format(
                                                phase=j.phase,
                                                cp=str(complex(j.p, j.q)).strip("()"),
                                            )
                                        )

                fp.write("};\n\n")

    def write_transformer_configurations(self, model, fp):
        configuration_count = 1
        for i in model.models:
            if isinstance(i, PowerTransformer):
                dic = {}
                if hasattr(i, "install_type") and i.install_type is not None:
                    dic["install_type"] = i.install_type
                if hasattr(i, "noload_loss") and i.noload_loss is not None:
                    dic["no_load_loss"] = i.noload_loss

                n_windings = 0
                if (
                    hasattr(i, "windings")
                    and i.windings is not None
                    and len(i.windings) > 1
                ):
                    winding1 = i.windings[
                        0
                    ]  # Assume winding1 is the primary and winding2 is the secondary unless otherwise stated
                    winding2 = i.windings[1]
                    logger.debug(winding1.nominal_voltage, winding2.nominal_voltage)
                    if len(i.windings) == 3:
                        dic["connect_type"] = "SINGLE_PHASE_CENTER_TAPPED"

                    elif (
                        hasattr(winding1, "connection_type")
                        and winding1.connection_type is not None
                        and hasattr(winding2, "connection_type")
                        and winding2.connection_type is not None
                    ):
                        conn_type = ""
                        if winding1.connection_type == "Y":
                            conn_type = "WYE_"
                        elif winding1.connection_type == "D":
                            conn_type = "DELTA_"
                        else:
                            conn_type = "ERR"
                        if winding2.connection_type == "Y":
                            if winding1.connection_type == "D":
                                conn_type = conn_type + "GWYE"
                            else:
                                conn_type = conn_type + "WYE"
                        elif winding2.connection_type == "D":
                            conn_type = conn_type + "DELTA"
                        else:
                            conn_type = conn_type + "ERR"

                        if conn_type[:3] != "ERR" and conn_type[-3:] != "ERR":
                            dic["connect_type"] = conn_type
                    if (
                        hasattr(winding1, "nominal_voltage")
                        and winding1.nominal_voltage is not None
                    ):
                        if (
                            hasattr(winding1, "voltage_type")
                            and winding1.voltage_type == 2
                        ):
                            dic["secondary_voltage"] = winding1.nominal_voltage
                        else:
                            dic["primary_voltage"] = winding1.nominal_voltage

                    if (
                        hasattr(winding2, "nominal_voltage")
                        and winding2.nominal_voltage is not None
                    ):
                        if (
                            hasattr(winding2, "voltage_type")
                            and winding2.voltage_type == 0
                        ):
                            dic["primary_voltage"] = winding2.nominal_voltage
                        else:
                            dic["secondary_voltage"] = winding2.nominal_voltage

                    if (
                        hasattr(winding1, "rated_power")
                        and winding1.rated_power is not None
                    ):
                        dic["power_rating"] = winding1.rated_power / 1000.0

                    n_windings = len(i.windings)
                else:
                    logger.debug("Warning - No windings included in the transformer")

                if hasattr(i, "reactances") and i.reactances is not None:
                    if len(i.reactances) == 1 and n_windings == 2:
                        dic["reactance"] = i.reactances[0]
                        dic["resistance"] = (
                            i.windings[0].resistance + i.windings[1].resistance
                        )
                    if len(i.reactances) == 3 and n_windings == 3:
                        resistance = i.windings[0].resistance * 2
                        dic[
                            "resistance"
                        ] = resistance  # The resistance of the whole transformer. TODO: Check if this is right...
                        dic["reactance"] = i.reactance[0]

                        dic["impedance1"] = complex(resistance, i.reactance[1])
                        dic["impedance2"] = complex(resistance, i.reactance[2])

                dic_set = set()
                for a, b in dic.items():
                    dic_set.add((a, b))
                dic_set = frozenset(dic_set)

                if dic_set in self.transformer_configurations:
                    logger.debug(i.name)
                    self.transformer_configurations_name[
                        i.name
                    ] = self.transformer_configurations[dic_set]
                    continue
                self.transformer_configurations[
                    dic_set
                ] = "transformer_config_{num}".format(num=configuration_count)
                dic["name"] = "transformer_config_{num}".format(num=configuration_count)
                self.transformer_configurations_name[
                    i.name
                ] = "transformer_config_{num}".format(num=configuration_count)
                fp.write("object transformer_configuration {\n")
                for j in dic:
                    fp.write("    {key} {value};\n".format(key=j, value=dic[j]))
                fp.write("};\n\n")
                configuration_count = configuration_count + 1

    def write_transformers(self, model, fp):
        for i in model.models:
            if isinstance(i, PowerTransformer):
                is_reg = False
                for j in model.models:
                    # TODO: More efficient way to do this - maybe an attribute in the transformer which gets set when it's created
                    if isinstance(j, Regulator) and j.name == i.name:
                        is_reg = True
                        break

                if is_reg:
                    continue

                fp.write("object transformer{\n")
                if hasattr(i, "name") and i.name is not None:
                    fp.write("    name n{name};\n".format(name=i.name))
                if hasattr(i, "from_element") and i.from_element is not None:
                    fp.write("    from n{fn};\n".format(fn=i.from_element))
                if hasattr(i, "to_element") and i.to_element is not None:
                    fp.write("    to n{tn};\n".format(tn=i.to_element))

                phase_set = set()
                if hasattr(i, "windings") and i.windings is not None:
                    for w in i.windings:
                        if (
                            hasattr(w, "phase_windings")
                            and w.phase_windings is not None
                        ):
                            for pw in w.phase_windings:
                                if hasattr(pw, "phase") and pw.phase is not None:
                                    phase_set.add(pw.phase)
                phase_set = sorted(list(phase_set))
                phases = ""
                for p in phase_set:
                    phases = phases + p

                if phases != "":
                    fp.write("    phases {pw};\n".format(pw=phases))

                if (
                    hasattr(i, "name")
                    and i.name is not None
                    and i.name in self.transformer_configurations_name
                ):
                    fp.write(
                        "    configuration {config};\n".format(
                            config=self.transformer_configurations_name[i.name]
                        )
                    )

                fp.write("};\n\n")

    def write_regulator_configurations(self, model, fp):
        configuration_count = 1
        for i in model.models:
            if isinstance(i, Regulator):
                dic = {}
                if hasattr(i, "delay") and i.delay is not None:
                    dic["time_delay"] = i.delay

                if hasattr(i, "highstep") and i.highstep is not None:
                    dic["raise_taps"] = i.highstep
                if hasattr(i, "lowstep") and i.lowstep is not None:
                    dic["lower_taps"] = i.lowstep
                elif hasattr(i, "highstep") and i.highstep is not None:
                    dic["lower_taps"] = i.highstep

                if hasattr(i, "pt_ratio") and i.pt_ratio is not None:
                    dic["power_transducer_ratio"] = i.pt_ratio

                if hasattr(i, "ct_ratio") and i.ct_ratio is not None:
                    dic["current_transducer_ratio"] = i.ct_ratio

                if hasattr(i, "bandwidth") and i.bandwidth is not None:
                    dic["band_width"] = i.bandwidth

                if hasattr(i, "bandcenter") and i.bandcenter is not None:
                    dic["band_center"] = i.bandcenter

                if hasattr(i, "pt_phase") and i.pt_phase is not None:
                    dic["pt_phase"] = i.pt_phase

                dic["connect_type"] = "WYE_WYE"  # All reguators in GLD are wye-wye

                dic_set = set()
                for a, b in dic.items():
                    dic_set.add((a, b))
                dic_set = frozenset(dic_set)

                if dic_set not in self.regulator_configurations:
                    self.regulator_phases[dic_set] = {}
                if (
                    hasattr(i, "connected_transformer")
                    and i.connected_transformer is not None
                ):
                    for j in model.models:
                        if (
                            isinstance(j, PowerTransformer)
                            and j.name == i.connected_transformer
                        ):
                            if hasattr(j, "windings") and j.windings is not None:
                                for w in j.windings:
                                    if (
                                        hasattr(w, "phase_windings")
                                        and w.phase_windings is not None
                                    ):
                                        for pw in w.phase_windings:
                                            if (
                                                hasattr(pw, "phase")
                                                and pw.phase is not None
                                            ):
                                                if hasattr(pw, "tap_position"):
                                                    self.regulator_phases[dic_set][
                                                        "tap_pos_{phase}".format(
                                                            phase=pw.phase
                                                        )
                                                    ] = pw.tap_position

                                                if (
                                                    hasattr(pw, "compensator_r")
                                                    and pw.compensator_r is not None
                                                ):
                                                    self.regulator_phases[dic_set][
                                                        "compensator_r_setting_{phase}".format(
                                                            phase=pw.phase
                                                        )
                                                    ] = pw.compensator_r
                                                if (
                                                    hasattr(pw, "compensator_x")
                                                    and pw.compensator_x is not None
                                                ):
                                                    self.regulator_phases[dic_set][
                                                        "compensator_r_setting_{phase}".format(
                                                            phase=pw.phase
                                                        )
                                                    ] = pw.compensator_r

                elif hasattr(i, "windings") and i.windings is not None:
                    for w in i.windings:
                        if (
                            hasattr(w, "phase_windings")
                            and w.phase_windings is not None
                        ):
                            for pw in w.phase_windings:
                                if hasattr(pw, "phase") and pw.phase is not None:
                                    if hasattr(pw, "tap_position"):
                                        self.regulator_phases[dic_set][
                                            "tap_pos_{phase}".format(phase=pw.phase)
                                        ] = pw.tap_position

                                    if (
                                        hasattr(pw, "compensator_r")
                                        and pw.compensator_r is not None
                                    ):
                                        self.regulator_phases[dic_set][
                                            "compensator_r_setting_{phase}".format(
                                                phase=pw.phase
                                            )
                                        ] = pw.compensator_r
                                    if (
                                        hasattr(pw, "compensator_x")
                                        and pw.compensator_x is not None
                                    ):
                                        self.regulator_phases[dic_set][
                                            "compensator_r_setting_{phase}".format(
                                                phase=pw.phase
                                            )
                                        ] = pw.compensator_r

                if dic_set in self.regulator_configurations:
                    logger.debug(i.name)
                    self.regulator_configurations_name[
                        i.name
                    ] = self.regulator_configurations[dic_set]
                    continue
                self.regulator_configurations[
                    dic_set
                ] = "regulator_config_{num}".format(num=configuration_count)
                dic["name"] = "regulator_config_{num}".format(num=configuration_count)
                self.regulator_configurations_name[
                    i.name
                ] = "regulator_config_{num}".format(num=configuration_count)
                configuration_count = configuration_count + 1
        for dic in self.regulator_configurations:
            fp.write("object regulator_configuration {\n")
            fp.write("    name {n};\n".format(n=self.regulator_configurations[dic]))
            for j in dic:
                fp.write("    {key} {value};\n".format(key=j[0], value=j[1]))
            for j in self.regulator_phases[dic]:
                logger.debug(j)
                fp.write(
                    "    {key} {value};\n".format(
                        key=j, value=self.regulator_phases[dic][j]
                    )
                )
            fp.write("};\n\n")

    def write_regulators(self, model, fp):
        for i in model.models:
            if isinstance(i, Regulator):
                if (
                    hasattr(i, "from_element")
                    and i.from_element is not None
                    and hasattr(i, "to_element")
                    and i.to_element is not None
                ):
                    if i.from_element + "_" + i.to_element in self.regulator_seen:
                        continue
                    self.regulator_seen.add(i.from_element + "_" + i.to_element)
                fp.write("object regulator{\n")
                if hasattr(i, "name") and i.name is not None:
                    fp.write("    name n{name};\n".format(name=i.name))
                if hasattr(i, "from_element") and i.from_element is not None:
                    fp.write("    from n{fn};\n".format(fn=i.from_element))
                if hasattr(i, "to_element") and i.to_element is not None:
                    fp.write("    to n{tn};\n".format(tn=i.to_element))

                phases = ""
                if (
                    hasattr(i, "connected_transformer")
                    and i.connected_transformer is not None
                ):
                    for j in model.models:
                        if (
                            isinstance(j, PowerTransformer)
                            and j.name == i.connected_transformer
                        ):
                            if hasattr(j, "windings") and j.windings is not None:
                                for w in j.windings:
                                    if (
                                        hasattr(w, "phase_windings")
                                        and w.phase_windings is not None
                                    ):
                                        for pw in w.phase_windings:
                                            if (
                                                hasattr(pw, "phase")
                                                and pw.phase is not None
                                            ):
                                                phases = phases + pw.phase

                elif hasattr(i, "windings") and i.windings is not None:
                    for w in i.windings:
                        if (
                            hasattr(w, "phase_windings")
                            and w.phase_windings is not None
                        ):
                            for pw in w.phase_windings:
                                if hasattr(pw, "phase") and pw.phase is not None:
                                    phases = phases + pw.phase

                if (
                    hasattr(i, "name")
                    and i.name is not None
                    and i.name in self.regulator_configurations_name
                ):
                    fp.write(
                        "    configuration {config};\n".format(
                            config=self.regulator_configurations_name[i.name]
                        )
                    )

                fp.write("};\n\n")

                # TODO: Deal with multiple regcontrols coming/going to the same from/to

    def write_line_configurations(self, model, fp):
        configuration_count = 1
        if self.write_wires:
            # TODO: Support for writing wires included
            pass
        else:
            for i in model.models:
                if isinstance(i, Line):
                    if (hasattr(i, "is_switch") and i.is_switch == 1) or (
                        hasattr(i, "is_fuse") and i.is_fuse == 1
                    ):
                        continue
                    dic = {}
                    phase_map = {"A": 1, "B": 2, "C": 3, "1": 1, "2": 2}
                    phases = []
                    if hasattr(i, "wires") and i.wires is not None:
                        for w in i.wires:
                            if (
                                hasattr(w, "phase")
                                and w.phase is not None
                                and w.phase != "N"
                            ):
                                phases.append(w.phase)
                    phases.sort()
                    if (
                        hasattr(i, "impedance_matrix")
                        and i.impedance_matrix is not None
                    ):
                        lc = i.impedance_matrix
                        # logger.debug(i.name,i.from_element, i.to_element)
                        # logger.debug(phases)
                        # logger.debug(lc)
                        if len(phases) != len(lc):
                            logger.debug(
                                "Warning - impedance matrix size different from number of phases for line {ln}".format(
                                    ln=i.name
                                )
                            )
                            logger.debug(i.name, i.from_element, i.to_element)
                            logger.debug(phases)
                            logger.debug(lc)
                        for j_cnt in range(
                            len(phases)
                        ):  # For 3x3 matrices or 2x2 secondary matrices
                            for k_cnt in range(len(phases)):
                                j_val = phases[j_cnt]
                                k_val = phases[k_cnt]
                                j = phase_map[j_val] - 1
                                k = phase_map[k_val] - 1
                                if len(lc) < 3:
                                    j = j_cnt
                                    k = k_cnt
                                impedance = str(lc[j][k]).strip("()")
                                pattern = re.compile("[^e]-")

                                if (
                                    "+" not in impedance
                                    and not len(pattern.findall(impedance)) > 0
                                ):
                                    impedance = "0+" + impedance
                                dic[
                                    "z{one}{two}".format(
                                        one=phase_map[j_val], two=phase_map[k_val]
                                    )
                                ] = impedance

                    dic_set = set()
                    for a, b in dic.items():
                        dic_set.add((a, b))
                    dic_set = frozenset(dic_set)

                    if dic_set in self.line_configurations:
                        self.line_configurations_name[
                            i.name
                        ] = self.line_configurations[dic_set]
                        continue

                    self.line_configurations[dic_set] = "line_config_{num}".format(
                        num=configuration_count
                    )
                    dic["name"] = "line_config_{num}".format(num=configuration_count)
                    self.line_configurations_name[i.name] = "line_config_{num}".format(
                        num=configuration_count
                    )
                    fp.write("object line_configuration {\n")
                    for j in dic:
                        fp.write("    {key} {value};\n".format(key=j, value=dic[j]))
                    fp.write("};\n\n")
                    configuration_count = configuration_count + 1

    def write_lines(self, model, fp):
        for i in model.models:
            if isinstance(i, Line):
                # Default is overhead_line
                if (
                    hasattr(i, "line_type")
                    and i.line_type is not None
                    and i.line_type == "underground"
                ):
                    fp.write("object underground_line{\n")
                    if hasattr(i, "length") and i.length is not None:
                        fp.write("    length {len};\n".format(len=i.length * 3.28084))
                    if (
                        hasattr(i, "name")
                        and i.name is not None
                        and i.name in self.line_configurations_name
                    ):
                        fp.write(
                            "    configuration {config};\n".format(
                                config=self.line_configurations_name[i.name]
                            )
                        )

                elif hasattr(i, "is_fuse") and i.is_fuse is not None and i.is_fuse == 1:
                    fp.write("object fuse{\n")
                elif (
                    hasattr(i, "is_switch")
                    and i.is_switch is not None
                    and i.is_switch == 1
                ):
                    fp.write("object switch{\n")
                elif hasattr(i, "line_type") and i.line_type is not None:
                    fp.write("object overhead_line{\n")

                    if hasattr(i, "length") and i.length is not None:
                        fp.write("    length {len};\n".format(len=i.length * 3.28084))
                    if (
                        hasattr(i, "name")
                        and i.name is not None
                        and i.name in self.line_configurations_name
                    ):
                        fp.write(
                            "    configuration {config};\n".format(
                                config=self.line_configurations_name[i.name]
                            )
                        )

                else:
                    fp.write("object overhead_line{\n")
                    if hasattr(i, "length") and i.length is not None:
                        fp.write("    length {len};\n".format(len=i.length * 3.28084))
                    if (
                        hasattr(i, "name")
                        and i.name is not None
                        and i.name in self.line_configurations_name
                    ):
                        fp.write(
                            "    configuration {config};\n".format(
                                config=self.line_configurations_name[i.name]
                            )
                        )

                if hasattr(i, "name") and i.name is not None:
                    fp.write("    name n{name};\n".format(name=i.name))
                if hasattr(i, "from_element") and i.from_element is not None:
                    fp.write("    from n{fn};\n".format(fn=i.from_element))
                if hasattr(i, "to_element") and i.to_element is not None:
                    fp.write("    to n{tn};\n".format(tn=i.to_element))

                phases = ""
                if hasattr(i, "wires") and i.wires is not None:
                    for w in i.wires:
                        if hasattr(w, "phase") and w.phase is not None:
                            phases = phases + w.phase

                if phases != "":
                    fp.write("    phases {ph};\n".format(ph=phases))

                fp.write("};\n\n")
