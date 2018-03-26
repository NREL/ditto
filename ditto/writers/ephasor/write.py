from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
import os
import math
import logging
import numpy as np
import pandas as pd

# from ditto.readers.gridlabd.read import Reader
from ditto.store import Store
#DiTTo imports
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.power_source import PowerSource
from ditto.models.winding import Winding

from ditto.writers.abstract_writer import AbstractWriter

logger = logging.getLogger(__name__)

class Writer(AbstractWriter):
    """
    DiTTo--->ePHASOR writer class.
    Use to write a DiTTo model to OpenDSS format.

    :param log_file: Name/path of the log file. Optional. Default='./OpenDSS_writer.log'
    :type log_file: str
    :param linecodes_flag: Use OpenDSS linecodes rather than lineGeometries. Optional. Default=True
    :type linecodes_flag: bool
    :param output_path: Path to write the OpenDSS files. Optional. Default='./'
    :param output_name: Name of output file (with xlxs extension). Optional. Default='ephasor_model.xlsx'
    :type output_path: str

    **Constructor:**
    # >>> my_writer=Writer(log_file='./logs/my_log.log', output_path='./feeder_output/')

    **Output file names:**

    +-----------------+--------------------+
    |     Object      |    File name       |
    +=================+====================+
    |      Buses      |   buscoords.dss    |
    +-----------------+--------------------+
    |  Transformers   |   Transformers.dss |
    +-----------------+--------------------+
    |      Loads      |      Loads.dss     |
    +-----------------+--------------------+
    |   Regulators    |   Regulators.dss   |
    +-----------------+--------------------+
    |   Capacitors    |   Capacitors.dss   |
    +-----------------+--------------------+
    |     Lines       |      Lines.dss     |
    +-----------------+--------------------+
    |     Wires       |    WireData.dss    |
    +-----------------+--------------------+
    | Line Geometries |  LineGeometry.dss  |
    +-----------------+--------------------+
    |    Line Codes   |    Linecodes.dss   |
    +-----------------+--------------------+

    """

    def __init__(self, **kwargs):
        """
        Constructor for the ePhasor writer.

        """

        self.m = None
        self._lines = []
        self._nodes = []
        self._capacitors = []
        self._transformers = []
        self._regulators = []

        self._transformer_dict = {}
        self.all_linecodes = {}
        self.all_wires = {}
        self.all_geometries = {}
        self.compensator = {}

        #Call super
        super(Writer, self).__init__(**kwargs)

        log_file = 'ephasor_writer.log'
        if 'log_file' in kwargs:
            log_file = kwargs['log_file']

        self.linecodes_flag = True
        if 'linecodes_flag' in kwargs and isinstance(kwargs['linecodes_flag'], bool):
            self.linecodes_flag = kwargs['linecodes_flag']

        self.output_path = './'
        if 'output_path' in kwargs:
            self.output_path = kwargs['output_path']
        self.output_name = 'ephasor_model.xlsx'
        if 'output_name' in kwargs:
            self.output_name = kwargs['output_name']

    def write_bus_coordinates(self):
        """Write the bus coordinates to a CSV file ('buscoords.csv' by default), with the following format:

        >>> bus_name,coordinate_X,coordinate_Y

        :param model: DiTTo model
        :type model: DiTTo model
        :returns: 1 for success, -1 for failure
        :rtype: int

        """

        # Loop over the DiTTo objects
        nodes = [i for i in self.m.models if isinstance(i, Node)]
        logger.debug(len(nodes))
        for i in nodes:
            logger.debug(i.name)

        for i in self.m.models:
            # If we find a node
            if isinstance(i, Node):
                # Extract the name and the coordinates
                if ((hasattr(i, 'name') and i.name is not None) and (hasattr(i, 'positions') and i.positions is not None and len(i.positions) > 0)):
                    logger.debug('{name} {X} {Y}\n'.format(name=i.name.lower(), X=i.positions[0].lat, Y=i.positions[0].long))

        return 1

    def switch(self):
        obj_dict = {'From Bus': [], 'To Bus': [], 'Switch Name': [], 'Normal Status': []}

        for line in self._lines:
            if hasattr(line, 'is_switch') and line.is_switch == 1:

                if hasattr(line, 'from_element') and line.from_element is not None and hasattr(line, 'to_element') and line.to_element is not None:
                    logger.debug(' bus1={from_el}'.format(from_el=line.from_element))
                    if hasattr(line, 'wires') and line.wires is not None:
                        for wire in line.wires:
                            if hasattr(wire, 'phase') and wire.phase is not None and wire.phase != 'N':
                                # logger.debug('.{p}'.format(p=self.phase_mapping(wire.phase)))
                                obj_dict['From Bus'].append(line.from_element + "_" + wire.phase.lower())
                                obj_dict['To Bus'].append(line.to_element + "_" + wire.phase.lower())
                                obj_dict['Switch Name'].append(line.name + "_" + wire.phase.lower())
                                if hasattr(line, 'is_open') and line.is_open == 1:
                                    obj_dict['Normal Status'].append('0')
                                else:
                                    obj_dict['Normal Status'].append('1')

                                # obj_dict['bus1' + wire.phase.lower()][index] = line.to_element+ "_" + wire.phase.lower()

        df2 = pd.DataFrame(obj_dict)
        return df2

    def line(self):
        """Create line

        >>> line

        :param
        :type
        :returns: dataframe with line values
        :rtype: dataframe

        """

        count = 0
        for line in self.m.models:
            if isinstance(line, Line):
                count += 1
        logger.debug(count)

        # obj_dict= {  'bus0a': [],
        #              'bus0b': [],
        #              'bus0c': [],
        #              'bus1a': [],
        #              'bus1b': [],
        #              'bus1c': [],
        #              'name': [],
        #              'R_1 (ohm/Mile)': [],
        #              'X_1 (ohm/Mile)': [],
        #              'R_0 (ohm/Mile)': [],
        #              'X_0 (ohm/Mile)': [],
        #              'B_1 (uS/Mile)': [],
        #              'B_0 (uS/Mile)': [],
        #              'Length (Mile)': [],
        #              'R_11 (ohm/Mile)': [],
        #              'X_11 (ohm/Mile)': [],
        #              'R_21 (ohm/Mile)': [],
        #              'X_21 (ohm/Mile)': [],
        #              'R_22 (ohm/Mile)': [],
        #              'X_22 (ohm/Mile)': [],
        #              'R_31 (ohm/Mile)': [],
        #              'X_31 (ohm/Mile)': [],
        #              'R_32 (ohm/Mile)': [],
        #              'X_32 (ohm/Mile)': [],
        #              'R_33 (ohm/Mile)': [],
        #              'X_33 (ohm/Mile)': [],
        #              'B_11 (uS/Mile)': [],
        #              'B_21 (uS/Mile)': [],
        #              'B_22 (uS/Mile)': [],
        #              'B_31 (uS/Mile)': [],
        #              'B_32 (uS/Mile)': [],
        #              'B_33 (uS/Mile)': []}
        obj_dict = {
            'bus0a': [],
            'bus0b': [],
            'bus0c': [],
            'bus1a': [],
            'bus1b': [],
            'bus1c': [],
            'name': [],
            'Length (Mile)': [],
            'r0 (ohm/Mile)': [],
            'x0 (ohm/Mile)': [],
            'r1 (ohm/Mile)': [],
            'x1 (ohm/Mile)': [],
            'b0 (uS/Mile)': [],
            'b1 (uS/Mile)': [],
            'r11 (ohm/Mile)': [],
            'x11 (ohm/Mile)': [],
            'r21 (ohm/Mile)': [],
            'x21 (ohm/Mile)': [],
            'r22 (ohm/Mile)': [],
            'x22 (ohm/Mile)': [],
            'r31 (ohm/Mile)': [],
            'x31 (ohm/Mile)': [],
            'r32 (ohm/Mile)': [],
            'x32 (ohm/Mile)': [],
            'r33 (ohm/Mile)': [],
            'x33 (ohm/Mile)': [],
            'b11 (uS/Mile)': [],
            'b21 (uS/Mile)': [],
            'b22 (uS/Mile)': [],
            'b31 (uS/Mile)': [],
            'b32 (uS/Mile)': [],
            'b33 (uS/Mile)': []
        }
        valid = ['11', '21', '22', '31', '32', '33']

        index = -1
        for line in self._lines:
            # if isinstance(line, Line):
            # if(line.is_switch):
            #     continue

            if hasattr(line, 'is_switch') and line.is_switch == 1:
                continue

            index += 1
            for key, value in obj_dict.items():
                value.append(None)

            if hasattr(line, 'name') and line.name is not None:
                logger.debug('New Line.' + line.name)
                obj_dict['name'][index] = line.name
            else:
                obj_dict['name'][index] = "None"

            units = u'mi'
            result = "temp "
            logger.debug('Type ' + str(line.line_type))

            for wire in line.wires:
                logger.debug(wire.phase)
                logger.debug(wire.resistance)
                logger.debug(wire.gmr)
                logger.debug(wire.diameter)
            if line.line_type == 'underground':
                r_0 = 0

            # Length
            if hasattr(line, 'length') and line.length is not None:
                logger.debug(' Length={length}'.format(length=self.convert_from_meters(np.real(line.length), units)))
                # linelength.append(line.length)
                obj_dict['Length (Mile)'][index] = self.convert_from_meters(np.real(line.length), units)

            if hasattr(line, 'from_element') and line.from_element is not None:
                logger.debug(' bus1={from_el}'.format(from_el=line.from_element))
                if hasattr(line, 'wires') and line.wires is not None:
                    for temp_phase in ['a', 'b', 'c']:
                        obj_dict['bus0' + temp_phase][index] = line.from_element + "_" + temp_phase
                    for wire in line.wires:
                        if hasattr(wire, 'phase') and wire.phase is not None and wire.phase != 'N':
                            # logger.debug('.{p}'.format(p=self.phase_mapping(wire.phase)))
                            obj_dict['bus0' + wire.phase.lower()][index] = line.from_element + "_" + wire.phase.lower()
                            # obj_dict['bus1' + wire.phase.lower()][index] = line.to_element+ "_" + wire.phase.lower()

            if hasattr(line, 'to_element') and line.to_element is not None:
                logger.debug(' bus2={to_el}'.format(to_el=line.to_element))
                if hasattr(line, 'wires') and line.wires is not None:
                    for temp_phase in ['a', 'b', 'c']:
                        obj_dict['bus1' + temp_phase][index] = line.to_element + "_" + temp_phase
                    for wire in line.wires:
                        if hasattr(wire, 'phase') and wire.phase is not None and wire.phase != 'N':
                            # logger.debug('.{p}'.format(p=self.phase_mapping(wire.phase)))
                            obj_dict['bus1' + wire.phase.lower()][index] = line.to_element + "_" + wire.phase.lower()

                            # obj_dict['bus1' + wire.phase.lower()][index] = line.from_element

            if hasattr(line, 'faultrate') and line.faultrate is not None and not self.linecodes_flag:
                logger.debug(' Faultrate={fr}'.format(fr=line.faultrate))

                # Rmatrix, Xmatrix, and Cmatrix
                # Can also be defined through the linecodes (check linecodes_flag)
            if hasattr(line, 'impedance_matrix') and line.impedance_matrix is not None:
                # Use numpy arrays since it is much easier for complex numbers
                try:
                    zz = line.impedance_matrix
                    Z = np.array(line.impedance_matrix)
                    R = np.real(Z) # Resistance matrix
                    X = np.imag(Z) # Reactance  matrix
                except:
                    self.logger.error('Problem with impedance matrix in line {name}'.format(name=line.name))

                result += 'Rmatrix=('
                logger.debug(R.shape)

                for rc, row in enumerate(R):
                    for ec, elt in enumerate(row):
                        # num_str = str(rc + 1) + str(ec + 1)
                        num_str = str(ec + 1) + str(rc + 1)
                        if num_str in valid:
                            name = 'r' + num_str + ' (ohm/Mile)'
                            obj_dict[name][index] = self.convert_from_meters(np.real(elt), units, inverse=True)
                        result += '{e} '.format(e=self.convert_from_meters(np.real(elt), units, inverse=True))
                    result += '| '
                result = result[:-2] # Remove the last "| " since we do not need it
                result += ') '

                result += 'Xmatrix=('

                for rc, row in enumerate(X):
                    for ec, elt in enumerate(row):
                        num_str = str(ec + 1) + str(rc + 1)
                        if num_str in valid:
                            name = 'x' + num_str + ' (ohm/Mile)'
                            obj_dict[name][index] = self.convert_from_meters(np.real(elt), units, inverse=True)

                            # B = 1 /(np.real(R[rc,ec]) + np.imag(elt))
                            # B = 1 / Z[rc,ec]
                            # name = 'b' + num_str + ' (uS/Mile)'
                            # obj_dict[name][index] = self.convert_from_meters(np.imag(B), units, inverse=False)
                        result += '{e} '.format(e=self.convert_from_meters(np.real(elt), units, inverse=True))
                    result += '| '
                result = result[:-2] # Remove the last "| " since we do not need it
                result += ') '
            else:
                logger.debug("no matrix")

            if hasattr(line, 'capacitance_matrix') and line.capacitance_matrix is not None:
                C = np.array(line.capacitance_matrix)
                kf2mil = 0.189394
                result += 'Bmatrix=('
                for rc, row in enumerate(Z):
                    for ec, elt in enumerate(row):
                        num_str = str(ec + 1) + str(rc + 1)
                        if num_str in valid:
                            name = 'b' + num_str + ' (uS/Mile)'

                            logger.debug("length", line.length)
                            logger.debug("R", np.real(elt))
                            logger.debug("X", np.imag(elt))
                            logger.debug()

                            # -6.3581 line valie
                            # -.602 siemens per mile
                            # convet to micor se
                            B = 0
                            if (np.imag(elt) != 0):
                                B = 1 / self.convert_from_meters(np.imag(elt), units, inverse=True)
                                logger.debug("Sub ", B)
                                B = 1 / (np.imag(elt) * line.length)

                            logger.debug("Siemens line units ", B)
                            logger.debug(np.imag(B) * 0.000621371)
                            B = np.imag(B) * 0.000621371 * 1e6
                            logger.debug("done", B)

                            # B = self.convert_from_meters(np.imag(B), units, inverse=True)
                            # print B
                            # B = -np.real(elt) / (np.real(elt)**2 + np.imag(elt))
                            # B = -np.imag(elt) / (np.real(elt)**2 + np.imag(elt)**2)
                            # print self.convert_from_meters(B, units, inverse=True)
                            # B = - np.imag(elt) / np.abs(elt)**2
                            # print self.convert_from_meters(B, units, inverse=True)
                            # B = - self.convert_from_meters(np.imag(elt), units, inverse=True) / self.convert_from_meters(np.abs(elt), units, inverse=True) ** 2
                            # print B
                            # B = self.convert_from_meters(B, units, inverse=True)
                            # print name, self.convert_from_meters(B, units, inverse=False)
                            # B= elt
                            # B / kf2mil * 2.65
                            # B = B/1000 * 2.65
                            # obj_dict[name][index] = B
                            # print B
                            # print line.name
                            # exit(0)
                        result += '{e} '.format(e=self.convert_from_meters(np.real(elt), units, inverse=True))

                    result += '| '
                result = result[:-2] # Remove the last "| " since we do not need it
                result += ') '

                result += 'Cmatrix=('
                for rc, row in enumerate(C):
                    for ec, elt in enumerate(row):
                        num_str = str(ec + 1) + str(rc + 1)
                        if num_str in valid:
                            name = 'b' + num_str + ' (uS/Mile)'
                            logger.debug("C matrix")
                            logger.debug(line.length * 0.000621371)
                            logger.debug(np.real(elt))
                            logger.debug((np.real(elt) * line.length) * 0.000621371)
                            logger.debug((np.real(elt) * line.length) * 0.000621371 * 1e6)
                            B = (np.real(elt) * line.length * 0.000621371) * 1e6

                            B = np.real(elt) * line.length
                            logger.debug("line units ", B)
                            B = self.convert_from_meters(np.real(B), units, inverse=False)
                            B = B * 1e6
                            obj_dict[name][index] = B
                            # print "Siemens line units ", B /(2.6526)
                            # obj_dict[name][index] = B /(2.6526)

                            # kf2mil = 0.189394
                            # m2mil = 0.000621371
                            # convfactor = m2mil
                            # (convfactor * 2.6526)
                            # tb=np.real(elt) / kf2mil * line.length
                            # print tb
                            # tb = np.real(elt) * line.length
                            # print tb
                            # tb = (tb * m2mil/(2.6526)) * 1e6
                            # print tb
                            # obj_dict[name][index] = tb
                            # print line.name
                            # exit(0)

                            # obj_dict[name][index]=self.convert_from_meters(np.real(elt), units, inverse=True) * 2.65
                        result += '{e} '.format(e=self.convert_from_meters(np.real(elt), units, inverse=True))
                    result += '| '
                result = result[:-2] # Remove the last "| " since we do not need it
                result += ') '

            # # Ampacity
            # if hasattr(line.wires[0], 'ampacity') and line.wires[0].ampacity is not None:
            #     result += ' normamps={na}'.format(na=line.wires[0].ampacity)
            #
            # # Emergency ampacity
            # if hasattr(line.wires[0], 'ampacity_emergency') and line.wires[0].ampacity_emergency is not None:
            #     result += ' emergamps={emer}'.format(emer=line.wires[0].ampacity_emergency)

            logger.debug(result)
        df1 = pd.DataFrame(obj_dict)
        # df1 = df1[
        #     ['bus0a','bus0b','bus0c','bus1a','bus1b','bus1c','name','Length (Mile)','r0 (ohm / Mile)','x0 (ohm / Mile)','r1 (ohm / Mile)','x1 (ohm / Mile)','b0 (uS / Mile)','b1 (uS / Mile)','r11 (ohm / Mile)','x11 (ohm / Mile)','r21 (ohm / Mile)','x21 (ohm / Mile)','r22 (ohm / Mile)','x22 (ohm / Mile)','r31 (ohm / Mile)','x31 (ohm / Mile)','r32 (ohm / Mile)','x32 (ohm / Mile)','r33 (ohm / Mile)', 'x33 (ohm / Mile)','b11 (uS / Mile)','b21 (uS / Mile)','b22 (uS / Mile)','b31 (uS / Mile)','b32 (uS / Mile)','b33 (uS / Mile)']]

        return df1

    def transformer(self):
        """Create transformers

        >>> transformer

        :param
        :type
        :returns: dataframe with transformer values
        :rtype: dataframe

        """
        obj_dict = {
            'ID': [],
            'W1Bus A': [],
            'W1Bus B': [],
            'W1Bus C': [],
            'W1V (kV)': [],
            'W1S_base (kVA)': [],
            'W1R (pu)': [],
            'W1Conn. type': [],
            'W2Bus A': [],
            'W2Bus B': [],
            'W2Bus C': [],
            'W2V (kV)': [],
            'W2S_base (kVA)': [],
            'W2R (pu)': [],
            'W2Conn. type': [],
            'X (pu)': [],
            'Tap A': [],
            'Tap B': [],
            'Tap C': [],
            'Lowest Tap': [],
            'Highest Tap': [],
            'Min Range (%)': [],
            'Max Range (%)': []
        }

        ### Check for a sperated 3 phase transformer. Line to netural or whatever
        index = -1
        for i in self._transformers:
            # index += 1
            if len(i.windings[0].phase_windings) == 1:
                pp = str(i.windings[0].phase_windings[0].phase)
                # self._transformer_dict[i.from_element + str(pp)] =  i.name
                if i.from_element in self._transformer_dict:
                    self._transformer_dict[i.from_element]["combined"] = True
                    index = self._transformer_dict[i.from_element]['i']
                    #import pdb;pdb.set_trace()
                    self._transformer_dict[i.from_element]['kv1'] += i.windings[0].nominal_voltage
                    self._transformer_dict[i.from_element]['kva'] += i.windings[0].rated_power
                    self._transformer_dict[i.from_element]["Tap " + pp] = i.windings[0].phase_windings[0].tap_position,
                else:
                    for key, value in obj_dict.items():
                        value.append(None)
                    index += 1
                    logger.debug(i.windings[0].phase_windings[0].tap_position)
                    self._transformer_dict[i.from_element] = {
                        "combined": False,
                        "name": i.name,
                        "i": index,
                        "kv1": i.windings[0].nominal_voltage,
                        "Tap " + pp: i.windings[0].phase_windings[0].tap_position,
                        "kva": i.windings[0].rated_power
                    }
            else:
                for key, value in obj_dict.items():
                    value.append(None)

        index = -1
        for i in self._transformers:
            # for key, value in obj_dict.items():
            #     value.append(None)
            index += 1

            kv1 = 0
            kva = 0
            if len(i.windings[0].phase_windings) == 1:
                pp = i.windings[0].phase_windings[0].phase
                # self._transformer_dict[i.from_element + str(pp)] =  i.name
                if i.from_element in self._transformer_dict:
                    index = self._transformer_dict[i.from_element]['i']
                    kv1 = self._transformer_dict[i.from_element]['kv1']
                    kva = self._transformer_dict[i.from_element]['kva']
                # else:
                #     index += 1
                #     self._transformer_dict[i.from_element] = {"name": i.name,
                #                                               "i": index, "kv": i.winding[0].nominal_voltage}

            logger.debug(index)
            if hasattr(i, 'name') and i.name is not None:
                logger.debug('New Transformer.' + i.name)
                obj_dict['ID'][index] = i.name
            else:
                obj_dict['ID'][index] = 'None'

            is_regulator = False
            for r in self._regulators:
                if i.name == r.connected_transformer:
                    logger.debug("It is a regulator!")
                    is_regulator = True

            if len(i.windings) >= 2:

                logger.debug('here', i.reactances, i.reactances[0], i.name)
                obj_dict['X (pu)'][index] = i.reactances[
                    0
                ] # TODO check currently opendss reads in reactances is defined as [value1, value2, ...] for each winding type. May need to change.
                if hasattr(i, 'windings') and i.windings is not None:
                    N_phases = []
                    for winding_num, winding in enumerate(i.windings):
                        if winding_num > 1:
                            break
                        if i.from_element in self._transformer_dict and self._transformer_dict[i.from_element]["combined"]:
                            obj_dict['W' + str(winding_num + 1) + 'S_base (kVA)'][index] = round(kva / 1000, 2)
                            obj_dict['W' + str(winding_num + 1) + 'V (kV)'][index] = round((kv1 / math.sqrt(3)) / 1000, 2)
                        else:
                            obj_dict['W' + str(winding_num + 1) + 'S_base (kVA)'][index] = winding.rated_power / 1000
                            obj_dict['W' + str(winding_num + 1) + 'V (kV)'][index] = winding.nominal_voltage / 1000

                        obj_dict['W' + str(winding_num + 1) + 'R (pu)'][index] = winding.resistance
                        if hasattr(winding, 'connection_type') and winding.connection_type is not None:
                            if winding.connection_type == 'Y':
                                obj_dict['W' + str(winding_num + 1) + 'Conn. type'][index] = 'wye'
                            elif winding.connection_type == 'D':
                                obj_dict['W' + str(winding_num + 1) + 'Conn. type'][index] = 'delta'
                            else:
                                self.logger.error(
                                    'Unsupported type of connection {conn} for transformer {name}'.format(conn=winding.connection_type, name=i.name)
                                )

                        # if self.write_taps and hasattr(winding.phase_windings[0], 'tap_position') and \
                        #                 winding.phase_windings[0].tap_position is not None:
                        #     logger.debug(' Tap={tap}'.format(tap=winding.phase_windings[0].tap_position))
                        #
                        # logger.debug(winding.rated_power)
                        # logger.debug(winding.nominal_voltage)
                        # logger.debug(winding.resistance)
                        # This gets done twice ... IDK if that is a problem
                        if hasattr(winding, 'phase_windings') and winding.phase_windings is not None:
                            N_phases.append(len(winding.phase_windings))
                            for pw in winding.phase_windings:
                                obj_dict['W1Bus ' + pw.phase][index] = i.from_element + '_' + pw.phase
                                obj_dict['W2Bus ' + pw.phase][index] = i.to_element + '_' + pw.phase
                                tap_name = 'Tap ' + pw.phase
                                if pw.tap_position is None:
                                    obj_dict[tap_name][index] = 0
                                else:
                                    logger.debug(i.name, tap_name, pw.tap_position)
                                    obj_dict[tap_name][index] = pw.tap_position
                                    # if i.from_element in self._transformer_dict:
                                    #     print self._transformer_dict[i.from_element]
                                    #     obj_dict[tap_name][index] = self._transformer_dict[i.from_element][tap_name]
                                    # else:
                                    #     obj_dict[tap_name][index] = pw.tap_position

                    if len(np.unique(N_phases)) != 1:
                        self.logger.error('Did not find the same number of phases accross windings of transformer {name}'.format(name=i.name))

                    try:
                        logger.debug(' phases={Np}'.format(Np=N_phases[0]))
                        logger.debug(' windings={N}'.format(N=len(i.windings)))
                    except:
                        self.logger.error('Could not write the number of phases for transformer {name}'.format(name=i.name))

            # Loadloss
            if hasattr(i, 'loadloss') and i.loadloss is not None:
                logger.debug(' %loadloss=' + str(i.loadloss)) # OpenDSS in kWatts

            # install type (Not mapped)

            # noload_loss
            if hasattr(i, 'noload_loss') and i.noload_loss is not None:
                logger.debug(' %Noloadloss=' + str(i.noload_loss))

            # noload_loss
            if hasattr(i, 'normhkva') and i.normhkva is not None:
                logger.debug(' normhkva=' + str(i.normhkva))
                # obj_dict['S']
            # Idk where to get this
            obj_dict['Lowest Tap'][index] = -16
            obj_dict['Highest Tap'][index] = 16
            obj_dict['Min Range (%)'][index] = 10
            obj_dict['Max Range (%)'][index] = 10

        df4 = pd.DataFrame(obj_dict)
        logger.debug('df4')
        logger.debug(df4)

        df4 = df4[[
            'ID', 'W1Bus A', 'W1Bus B', 'W1Bus C', 'W1V (kV)', 'W1S_base (kVA)', 'W1R (pu)', 'W1Conn. type', 'W2Bus A', 'W2Bus B', 'W2Bus C',
            'W2V (kV)', 'W2S_base (kVA)', 'W2R (pu)', 'W2Conn. type', 'X (pu)', 'Tap A', 'Tap B', 'Tap C', 'Lowest Tap', 'Highest Tap',
            'Min Range (%)', 'Max Range (%)'
        ]]

        return df4

    def source(self):
        """Create source

        >>> source

        :param
        :type
        :returns: dataframe with source
        :rtype: dataframe

        """

        obj_dict = {
            'bus A': [],
            'bus B': [],
            'bus C': [],
            'ID': [],
            'V (kV)': [],
            'Angle (deg)': [],
            'SCL_1 (MVA)': [],
            'SCL_3 (MVA)': [],
            'R_pos (ohm)': [],
            'X_pos (ohm)': [],
            'R_zero (ohm)': [],
            'X_zero (ohm)': []
        }

        _transformer_dict = {i.from_element: i for i in self._transformers}

        for index, i in enumerate(self._powersources):
            for key, value in obj_dict.items():
                value.append(None)

            if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                transformer = _transformer_dict[i.connecting_element]
                obj_dict['ID'][index] = i.name
                obj_dict['Angle (deg)'][index] = i.phase_angle
                obj_dict['V (kV)'][index] = transformer.windings[1].nominal_voltage / 1000
                obj_dict['SCL_1 (MVA)'][index] = i.emergency_power / 1e6 # TODO should this be rated power?
                obj_dict['SCL_3 (MVA)'][index] = i.emergency_power / 1e6
                for pw in transformer.windings[1].phase_windings:
                    obj_dict['bus ' + pw.phase.upper()][index] = transformer.to_element + '_' + pw.phase.lower()
            else: #just a powersource object
                obj_dict['ID'][index] = i.name
                obj_dict['V (kV)'][index] = i.nominal_voltage
                for ph in i.phases:
                    if str(ph.default_value).lower() in set(['a', 'b', 'c']):
                        obj_dict['bus ' + str(ph.default_value).upper()][index] = i.name + '_' + str(ph.default_value).lower()

        df7 = pd.DataFrame(obj_dict)
        df7 = df7[[
            'bus A', 'bus B', 'bus C', 'ID', 'V (kV)', 'Angle (deg)', 'SCL_1 (MVA)', 'SCL_3 (MVA)', 'R_pos (ohm)', 'X_pos (ohm)', 'R_zero (ohm)',
            'X_zero (ohm)'
        ]]

        return df7

    def bus(self):
        """Create bus

        >>> bus

        :param
        :type
        :returns: dataframe with bus
        :rtype: dataframe

        """
        obj_dict = {'Bus': [], 'Voltage (V)': [], 'Angle (deg)': []}
        nodes = [i for i in self.m.models if isinstance(i, Node)]
        index = 0
        # for c,i in enumerate(nodes):
        #     if i.phases is not None:
        #         for phase in i.phases:
        #             for key, value in obj_dict.items():
        #                 value.append(None)
        #             obj_dict['Bus'][index] = i.name + '_' + str(phase.default_value).lower()
        #             obj_dict['Voltage (V)'][index] = i.nominal_voltage
        #             index+=1
        for node in self._nodes + self._powersources:
            if hasattr(node, 'name'):
                letter_phases = set()
                for phase in node.phases:
                    if phase.default_value == 'A' or phase.default_value == 'B' or phase.default_value == 'C':
                        letter_phases.add(phase.default_value)
                        obj_dict['Bus'].append(node.name + '_' + phase.default_value)
                        obj_dict['Voltage (V)'].append(node.nominal_voltage)
                if len(letter_phases) == 1:
                    obj_dict['Angle (deg)'].append(0)
                if len(letter_phases) == 2:
                    obj_dict['Angle (deg)'].append(0)
                    obj_dict['Angle (deg)'].append(180)
                if len(letter_phases) == 3:
                    obj_dict['Angle (deg)'].append(0)
                    obj_dict['Angle (deg)'].append(120)
                    obj_dict['Angle (deg)'].append(-120)
                index = index + 1
        """
        line_dict = {}
        for line in self._lines: #Done so that we know the phases of the bus elements
            if hasattr(line, 'from_element') and line.from_element is not None:
                logger.debug(' bus1={from_el}'.format(from_el=line.from_element))
                if hasattr(line, 'wires') and line.wires is not None:
                    # for temp_phase in ['a', 'b', 'c']:
                    #     obj_dict['Bus'][index] = line.from_element + "_" + temp_phase
                    for wire in line.wires:
                        if hasattr(wire, 'phase') and wire.phase is not None and wire.phase != 'N':
                            for key, value in obj_dict.items():
                                value.append(None)
                            obj_dict['Bus'][index] = line.from_element + "_" + wire.phase
                            line_dict[line.from_element + "_" + wire.phase] = line.from_element + "_" + wire.phase
                            obj_dict['Voltage (V)'][index] = line.nominal_voltage
                            index += 1

                            if line.to_element + "_" + wire.phase not in line_dict:
                                for key, value in obj_dict.items():
                                    value.append(None)
                                obj_dict['Bus'][index] = line.from_element + "_" + wire.phase
                                line_dict[line.from_element + "_" + wire.phase] = line.from_element + "_" + wire.phase
                                obj_dict['Voltage (V)'][index] = line.nominal_voltage
                                index += 1
        """
        # columns = pd.MultiIndex.from_tuples([('one','Bus'), ('two','Voltage (V)'), ('two','Angle (deg)')])
        # index = pd.Index(['1'], name='ID')
        # df9 = pd.DataFrame(obj_dict, columns=columns)
        df9 = pd.DataFrame(obj_dict)
        df9 = df9[['Bus', 'Voltage (V)', 'Angle (deg)']]
        logger.debug(obj_dict)
        return df9

    def load(self):
        """Create loads


        :param
        :type
        :returns: dataframe with loads
        :rtype: dataframe

        """
        obj_dict = {
            'Bus A': [],
            'Bus B': [],
            'Bus C': [],
            'ID': [],
            'Type': [],
            'P_a (kW)': [],
            'Q_a (kVAr)': [],
            'P_b (kW)': [],
            'Q_b (kVAr)': [],
            'P_c (kW)': [],
            'Q_c (kVAr)': [],
            'V (kV)': [],
            'Bandwidth (pu)': [],
            'Conn. type': [],
            'K_z': [],
            'K_i': [],
            'K_p': [],
            'Status': [],
            'Use initial voltage?': []
        }

        nodes = [i for i in self.m.models if isinstance(i, Node)]
        for i in nodes:
            logger.debug(i)

        loads = [i for i in self.m.models if isinstance(i, Load)]
        # loadnames = [i.name for i in self.m.models if isinstance(i, Load)]
        # print (loadnames)

        load_dict = {}
        logger.debug(len(loads))
        index = -1
        for x, i in enumerate(loads):
            ##
            #  Keep the index/row location of
            ##
            if hasattr(i, 'name') and i.name is not None:
                logger.debug('New Load.' + i.name)
                if i.name[-1].lower() == 'a' or i.name[-1].lower() == 'b' or i.name[-1].lower() == 'c':
                    n_name = i.name[0:-1]
                    if not n_name in load_dict:
                        for key, value in obj_dict.items():
                            value.append(None)
                        index += 1
                        load_dict[n_name] = index
                        obj_dict['ID'][index] = n_name

                    else:
                        index = load_dict[n_name]
                else:
                    for key, value in obj_dict.items():
                        value.append(None)
                    index += 1
                    obj_dict['ID'][index] = i.name

            if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                # logger.debug('    nominal_voltage {nv};'.format(nv=i.nominal_voltage))
                obj_dict['V (kV)'][index] = i.nominal_voltage / 1000.0

            if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                # logger.debug('    parent n{ce};'.format(ce=i.connecting_element))
                for temp_phase in ['a', 'b', 'c']:
                    obj_dict['Bus ' + temp_phase.upper()][index] = i.connecting_element + "_" + temp_phase

            if hasattr(i, 'phase_loads') and i.phase_loads is not None:
                phases = ''
                for j in i.phase_loads:
                    if hasattr(j, 'phase') and j.phase is not None:
                        phases = phases + j.phase
                        logger.debug('here', i.name, str(j.p), j.phase)

                        if hasattr(j, 'use_zip') and j.use_zip is not None:
                            if j.use_zip == 1: # This means that all the required values are not None
                                logger.debug('    current_fraction_{phase} {cf};\n'.format(phase=j.phase, cf=(j.ppercentcurrent + j.qpercentcurrent)))
                                logger.debug(
                                    '    current_pf_{phase} {cpf};\n'.format(
                                        phase=j.phase, cpf=(j.ppercentcurrent / (j.ppercentcurrent + j.qpercentcurrent))
                                    )
                                )
                                logger.debug('    power_fraction_{phase} {pf};\n'.format(phase=j.phase, pf=(j.ppercentpower + j.qpercentpower)))
                                logger.debug(
                                    '    power_pf_{phase} {ppf};\n'.format(
                                        phase=j.phase, ppf=(j.ppercentpower / (j.ppercentpower + j.qpercentpower))
                                    )
                                )
                                logger.debug(
                                    '    impedance_fraction_{phase} {iff};\n'.format(phase=j.phase, iff=(j.ppercentimpedance + j.qpercentimpedance))
                                )
                                logger.debug(
                                    '    impedance_pf_{phase} {ipf};\n'.format(
                                        phase=j.phase, ipf=(j.ppercentimpedance / (j.ppercentimpedance + j.qpercentimpedance))
                                    )
                                )
                                logger.debug('    base_power_{phase} {bp};\n'.format(phase=j.phase, bp=complex(j.p, j.q)))
                                obj_dict['Type'][index] = 'ZIP'
                                obj_dict['P_' + j.phase.lower() + ' (kW)'][index] = j.p / 1000.0
                                obj_dict['Q_' + j.phase.lower() + ' (kVAr)'][index] = j.q / 1000.0
                                obj_dict['K_p'][index] = j.ppercentpower + j.qpercentpower
                                obj_dict['K_i'][index] = j.ppercentcurrent + j.qpercentcurrent
                                obj_dict['K_z'][index] = j.ppercentimpedance + j.qpercentimpedance
                                # TODO add the K_z K_i and K_p values for ZIP entries
                            else:
                                logger.debug(j)
                                logger.debug(obj_dict['ID'][index])
                                obj_dict['Type'][index] = ''

                                if hasattr(j, 'p') and j.p is not None and hasattr(j, 'q') and j.q is not None and hasattr(
                                    j, 'phase'
                                ) and j.phase is not None:
                                    logger.debug('    constant_power_{phase} {cp};\n'.format(phase=j.phase, cp=str(complex(j.p, j.q)).strip('()')))
                                    obj_dict['P_' + j.phase.lower() + ' (kW)'][index] = abs(j.p) / 1000.0
                                    obj_dict['Q_' + j.phase.lower() + ' (kVAr)'][index] = abs(j.q) / 1000.0

                                if hasattr(j, 'model') and j.model == 1:
                                    obj_dict['K_p'][index] = 1
                                    obj_dict['K_i'][index] = 0
                                    obj_dict['K_z'][index] = 0
                                    obj_dict['Type'][index] = 'ZIP'

                                if hasattr(j, 'model') and j.model == 2:
                                    obj_dict['K_p'][index] = 0
                                    obj_dict['K_i'][index] = 0
                                    obj_dict['K_z'][index] = 1
                                    obj_dict['Type'][index] = 'ZIP'

                                if hasattr(j, 'model') and j.model == 5:
                                    obj_dict['K_p'][index] = 0
                                    obj_dict['K_i'][index] = 1
                                    obj_dict['K_z'][index] = 0
                                    obj_dict['Type'][index] = 'ZIP'

        df3 = pd.DataFrame(obj_dict)
        df3 = df3[[
            'Bus A', 'Bus B', 'Bus C', 'ID', 'Type', 'P_a (kW)', 'Q_a (kVAr)', 'P_b (kW)', 'Q_b (kVAr)', 'P_c (kW)', 'Q_c (kVAr)', 'V (kV)',
            'Bandwidth (pu)', 'Conn. type', 'K_z', 'K_i', 'K_p', 'Status', 'Use initial voltage?'
        ]]

        return df3

    def write(self, m):
        """ Write model to file

        >>> write, model

        :param
        :type
        :returns: None
        :rtype: None

        """

        self.m = m
        self._lines = [i for i in self.m.models if isinstance(i, Line)]
        self._nodes = [i for i in self.m.models if isinstance(i, Node)]
        self._capacitors = [i for i in self.m.models if isinstance(i, Capacitor)]
        self._transformers = [i for i in self.m.models if isinstance(i, PowerTransformer)]
        self._regulators = [i for i in self.m.models if isinstance(i, Regulator)]
        self._powersources = [i for i in self.m.models if isinstance(i, PowerSource)]

        df7 = self.source()
        df1 = self.line()
        df2 = self.switch()
        df3 = self.load()
        df4 = self.transformer()

        df9 = self.bus()
        writer = pd.ExcelWriter(self.output_path + self.output_name, engine='xlsxwriter')

        df1.to_excel(writer, 'Line 3-phase', index=False)
        # workbook = writer.book
        worksheet = writer.sheets['Line 3-phase']

        worksheet.set_column(0, 25, 16)

        df2.to_excel(writer, 'Switch', index=False)
        # workbook = writer.book
        worksheet = writer.sheets['Switch']

        worksheet.set_column(0, 25, 16)

        df3.to_excel(writer, 'Load 3-phase', index=False)
        # workbook = writer.book
        worksheet = writer.sheets['Load 3-phase']

        worksheet.set_column(0, 19, 16)

        df4.to_excel(writer, 'Transformer 3-phase', index=False)
        # workbook  = writer.book
        worksheet = writer.sheets['Transformer 3-phase']

        worksheet.set_column(0, 19, 16)

        df7.to_excel(writer, 'Vsource 3-phase', index=False)
        # workbook = writer.book
        worksheet = writer.sheets['Vsource 3-phase']

        worksheet.set_column(0, 25, 16)

        df9.to_excel(writer, 'Bus', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Bus']

        worksheet.set_column(0, 3, 16)


if __name__ == '__main__':
    # self.m = Store()
    from ditto.readers.opendss.read import Reader
    m = Store()
    _reader = Reader()

    # modelfile = '/Users/jsimpson/git/DiTTo/ditto/readers/gridlabd/13node_simplified.glm'
    # reader.parse(self.m, modelfile)

    modelfile = '../../validation/inputs/opendss/ieee_13_node/master.dss'
    _reader.build_opendssdirect(modelfile)
    _reader.set_dss_file_names({'Nodes': '../../validation/inputs/opendss/ieee_13_node/IEEE13Node_BusXY.csv'})
    _reader.parse(m, verbose=True)
    writer = Writer(output_path="./")

    writer.write(m)
    # writer.write_bus_coordinates()
