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
from ditto.modify.system_structure import system_structure_modifier

from ..abstract_writer import AbstractWriter

logger = logging.getLogger(__name__)


class Writer(AbstractWriter):

    register_names = ["demo", "Demo"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write(self, model, **kwargs):
        """
        General writing function responsible for calling the sub-functions.

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

        with open(os.path.join(self.output_path, "Model.txt"), "w") as fp:

            # Write lines
            logger.info("Writing the Lines...")
            if self.verbose:
                logger.debug("Writing the Lines...")
            s = self.write_lines(model, fp)
            if self.verbose:
                logger.debug("Succesful!")

    def write_lines(self, model, fp):
        configuration_count = 1
        for i in model.models:
            if isinstance(i, Line):
                if hasattr(i, "from_element") and hasattr(i, "to_element"):
                    fp.write(
                        "{frome} {toe}:\n".format(
                            frome=i.from_element.upper(), toe=i.to_element.upper()
                        )
                    )
                    phase_map = {"A": 1, "B": 2, "C": 3, "1": 1, "2": 2}
                    dic = {}
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
                        all_z = [
                            [complex(0, 0) for posi in range(3)] for posj in range(3)
                        ]
                        lc = i.impedance_matrix
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
                                if len(lc) == 0:
                                    all_z[j][
                                        k
                                    ] = 0  # Default 0 impedance if no impedance matrix
                                else:
                                    all_z[j][k] = complex(lc[j_cnt][k_cnt])
                                if len(lc) < 3:
                                    j = j_cnt
                                    k = k_cnt
                        fp.write("Impedance:\n")
                        for j in range(3):
                            for k in range(3):
                                fp.write(
                                    "%.6f+%.6fj  "
                                    % (all_z[j][k].real * 1000, all_z[j][k].imag * 1000)
                                )  # Output in units of capacitance per km
                            fp.write("\n")
                        fp.write("\n")

                    if (
                        hasattr(i, "capacitance_matrix")
                        and i.capacitance_matrix is not None
                    ):
                        all_c = [
                            [complex(0, 0) for posi in range(3)] for posj in range(3)
                        ]
                        lc = i.capacitance_matrix
                        if len(phases) != len(lc):
                            logger.debug(
                                "Warning - capacitance matrix size different from number of phases for line {ln}".format(
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
                                if len(lc) == 0:
                                    all_c[j][
                                        k
                                    ] = 0  # Default 0 impedance if no impedance matrix
                                else:
                                    all_c[j][k] = complex(lc[j_cnt][k_cnt])
                                if len(lc) < 3:
                                    j = j_cnt
                                    k = k_cnt

                        #                                impedance = str(lc[j][k]).strip('()')
                        #                                pattern = re.compile('[^e]-')
                        #
                        #                                if not '+' in impedance and not len(pattern.findall(impedance)) > 0:
                        #                                    impedance = '0+' + impedance
                        #                                dic['z{one}{two}'.format(one=phase_map[j_val], two=phase_map[k_val])] = impedance
                        fp.write("Shunt Capacitance:\n")
                        for j in range(3):
                            for k in range(3):
                                if all_c[j][k].real < 0:
                                    fp.write(
                                        "%.6f%.6fj  " % (0, all_c[j][k].real * 1000)
                                    )  # Output in units of capacitance per km
                                else:
                                    fp.write(
                                        "%.6f+%.6fj  " % (0, all_c[j][k].real * 1000)
                                    )  # Output in units of capacitance per km
                            fp.write("\n")
                        fp.write("\n")

                else:
                    logger.warning(
                        "Line missing from and to elements. Nothing written for line {}".format(
                            i.name
                        )
                    )

                    """
                    dic = {}
                    phase_map = {'A': 1, 'B': 2, 'C': 3, '1': 1, '2': 2}
                    phases = []
                    if hasattr(i, 'wires') and i.wires is not None:
                        for w in i.wires:
                            if hasattr(w, 'phase') and w.phase is not None and w.phase != 'N':
                                phases.append(w.phase)
                    phases.sort()
                    if hasattr(i, 'impedance_matrix') and i.impedance_matrix is not None:
                        lc = i.impedance_matrix
                        #logger.debug(i.name,i.from_element, i.to_element)
                        #logger.debug(phases)
                        #logger.debug(lc)
                        if (len(phases) != len(lc)):
                            logger.debug('Warning - impedance matrix size different from number of phases for line {ln}'.format(ln=i.name))
                            logger.debug(i.name, i.from_element, i.to_element)
                            logger.debug(phases)
                            logger.debug(lc)
                        for j_cnt in range(len(phases)): # For 3x3 matrices or 2x2 secondary matrices
                            for k_cnt in range(len(phases)):
                                j_val = phases[j_cnt]
                                k_val = phases[k_cnt]
                                j = phase_map[j_val] - 1
                                k = phase_map[k_val] - 1
                                if len(lc) < 3:
                                    j = j_cnt
                                    k = k_cnt
                                impedance = str(lc[j][k]).strip('()')
                                pattern = re.compile('[^e]-')

                                if not '+' in impedance and not len(pattern.findall(impedance)) > 0:
                                    impedance = '0+' + impedance
                                dic['z{one}{two}'.format(one=phase_map[j_val], two=phase_map[k_val])] = impedance

                    dic_set = set()
                    for a, b in dic.items():
                        dic_set.add((a, b))
                    dic_set = frozenset(dic_set)

                    if dic_set in self.line_configurations:
                        self.line_configurations_name[i.name] = self.line_configurations[dic_set]
                        continue

                    self.line_configurations[dic_set] = 'line_config_{num}'.format(num=configuration_count)
                    dic['name'] = 'line_config_{num}'.format(num=configuration_count)
                    self.line_configurations_name[i.name] = 'line_config_{num}'.format(num=configuration_count)
                    fp.write('object line_configuration {\n')
                    for j in dic:
                        fp.write('    {key} {value};\n'.format(key=j, value=dic[j]))
                    fp.write('};\n\n')
                    configuration_count = configuration_count + 1
"""
