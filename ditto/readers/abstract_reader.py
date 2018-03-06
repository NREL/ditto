# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import sys
import logging
import numpy as np

LOGGER = logging.getLogger(__name__)


class abstract_reader:
    '''Abstract class for DiTTo readers.
    author: Nicolas Gensollen. October 2017.
    '''

    def __init__(self, **kwargs):
        '''Abstract class CONSTRUCTOR.'''

        # create logger
        self.logger = LOGGER

    def symmetrize(self, matrix):
        '''Symmetrize a triangular matrix in list format.

        :param matrix: Matrix to symmetrize
        :type matrix: List
        :returns: Symmetric list of lists
        :rtype: list

        **Usage:**

        The function expects a list of lists, and turns it into a symmetric list of lists:

        >>> symmetrize([[.1], [.2,.1], [.4,.5,.1]])
        [[.1,.2,.4],[.2,.1,.5],[.4,.5,.1]]

        ..note:: Probably, many more elegant (and faster!) ways to do this...
        '''

        N_rows = len(matrix)
        N_cols = max(map(lambda x: len(x), matrix))

        if N_rows != N_cols:
            self.logger.warning('Expects a square matrix here')
            return None

        matrix2 = []
        for row in matrix:
            matrix2.append([])
            matrix2[-1] += row
            while len(matrix2[-1]) != N_cols:
                matrix2[-1].append(0)

        matrix2 = np.array(matrix2)
        matrix2 += matrix2.T

        for i in range(N_cols):
            matrix2[i, i] *= .5

        return matrix2.tolist()

    def convert_to_meters(self, quantity, unit, **kwargs):
        '''Converts a distance in a given unit to meters.

        :param quantity: Distance to convert
        :type quantity: float
        :param unit: The unit of the distance argument
        :type unit: str (see below the units supported)
        :param inverse: Use inverse ration (see below)
        :type inverse: bool
        :returns: The distance in meters
        :rtype: float

        **Units supported:**

        The units supported are the OpenDSS available units:

                        - miles ('mi')
                        - kilometers ('km')
                        - kilofeet ('kft')
                        - meters ('m')
                        - feet ('ft')
                        - inches ('in')
                        - centimeters ('cm')

        **Ratios:**

        The ratios used are the ones provided by Google. The following table summerize the multipliers to obtain meters:

        +--------+------------+
        |  Unit  | Multiplier |
        +========+============+
        |   mi   |  1609.34   |
        +--------+------------+
        |   km   |    1000    |
        +--------+------------+
        |   kft  |   304.8    |
        +--------+------------+
        |    m   |     1      |
        +--------+------------+
        |   ft   |   0.3048   |
        +--------+------------+
        |   in   |   0.0254   |
        +--------+------------+
        |   cm   |    0.01    |
        +--------+------------+

        .. note::    If the unit is not one of these, the function returns None

        .. note::

                Inverse parameter: If True, use the inverse ratio for conversion.
                This is useful if we have a quantity in something per unit distance.
                For example, if we want to convert x Ohms per miles in Ohms per meters, then flag inverse as True.

        .. seealso:: convert_from_meters, unit_conversion'''

        if 'inverse' in kwargs and isinstance(kwargs['inverse'], bool):
            inverse = kwargs['inverse']
        else:
            inverse = False

        if unit is None:
            return None

        if not isinstance(unit, str):
            self.logger.warning('convert_to_meters() expects a unit in string format')
            return None

        if quantity is None:
            return None

        if unit.lower() == 'mi':
            if inverse:
                return quantity / 1609.34
            else:
                return 1609.34 * quantity

        elif unit.lower() == 'km':
            if inverse:
                return quantity / 1000.0
            else:
                return 1000 * quantity

        elif unit.lower() == 'kft':
            if inverse:
                return quantity / 304.8
            else:
                return 304.8 * quantity

        elif unit.lower() == 'm':
            return quantity

        elif unit.lower() == 'ft':
            if inverse:
                return quantity / 0.3048
            else:
                return 0.3048 * quantity

        elif unit.lower() == 'in':
            if inverse:
                return quantity / 0.0254
            else:
                return 0.0254 * quantity

        elif unit.lower() == 'cm':
            if inverse:
                return quantity / 0.01
            else:
                return 0.01 * quantity

        else:
            return None

    def convert_from_meters(self, quantity, unit, **kwargs):
        '''Converts a distance in meters to a distance in given unit.

        :param quantity: Distance in meter to convert
        :type quantity: float
        :param unit: The unit to convert to
        :type unit: str (see below the units supported)
        :param inverse: Use inverse ration (see below)
        :type inverse: bool
        :returns: The distance in the requested unit
        :rtype: float

        **Units supported:**

        The units supported are the OpenDSS available units:

                        - miles ('mi')
                        - kilometers ('km')
                        - kilofeet ('kft')
                        - meters ('m')
                        - feet ('ft')
                        - inches ('in')
                        - centimeters ('cm')


        **Ratios:**

        The ratios used are the ones provided by Google. The following table summerize the multipliers to obtain the unit:

        +--------+------------+
        |  Unit  | Multiplier |
        +========+============+
        |   mi   | 0.000621371|
        +--------+------------+
        |   km   |    0.001   |
        +--------+------------+
        |   kft  | 0.00328084 |
        +--------+------------+
        |    m   |     1      |
        +--------+------------+
        |   ft   |   3.28084  |
        +--------+------------+
        |   in   |   39.3701  |
        +--------+------------+
        |   cm   |     100    |
        +--------+------------+

        .. note:: If the unit is not one of these, the function returns None

        .. seealso:: convert_to_meters, unit_conversion'''

        if 'inverse' in kwargs and isinstance(kwargs['inverse'], bool):
            inverse = kwargs['inverse']
        else:
            inverse = False

        if unit is None:
            return None

        if not isinstance(unit, str):
            self.logger.warning('convert_from_meters() expects a unit in string format')
            return None

        if quantity is None:
            return None

        if unit.lower() == 'mi':
            if inverse:
                return quantity / 0.000621371
            else:
                return 0.000621371 * quantity

        elif unit.lower() == 'km':
            if inverse:
                return quantity / 10**-3
            else:
                return 10**-3 * quantity

        elif unit.lower() == 'kft':
            if inverse:
                return quantity / 0.00328084
            else:
                return 0.00328084 * quantity

        elif unit.lower() == 'm':
            return quantity

        elif unit.lower() == 'ft':
            if inverse:
                return quantity / 3.28084
            else:
                return 3.28084 * quantity

        elif unit.lower() == 'in':
            if inverse:
                return quantity / 39.3701
            else:
                return 39.3701 * quantity

        elif unit.lower() == 'cm':
            if inverse:
                return quantity / 100
            else:
                return 100 * quantity

        else:
            return None

    def unit_conversion(self, quantity, unit_from, unit_to):
        '''Converts a distance in unit_from to a distance in unit_to.
        Basically converts to meters and then to the desired unit.

        :param quantity: Distance to convert
        :type quantity: float
        :param unit_from: Unit of the quantity argument
        :type unit_from: str
        :param unit_to: Unit for conversion
        :type unit_to: str
        :returns: Distance in unit_to unit
        :rtype: float

        **Units supported:**

        The units supported are the OpenDSS available units:

                        - miles ('mi')
                        - kilometers ('km')
                        - kilofeet ('kft')
                        - meters ('m')
                        - feet ('ft')
                        - inches ('in')
                        - centimeters ('cm')

        .. note:: If the unit is not one of these, the function returns None

        .. seealso:: convert_to_meters, convert_from_meters'''

        supported_units = ['km', 'm', 'ft', 'kft', 'in', 'cm', 'mi']
        if unit_from not in supported_units:
            return None
        if unit_to not in supported_units:
            return None
        #Convert to meters
        in_meters = self.convert_to_meters(quantity, unit_from)

        #Convert from meters
        result = self.convert_from_meters(in_meters, unit_to)

        return result

    def distance(self, p1, p2):
        '''Returns the euclidean distance between two points p1 and p2.

        :param p1: Coordinates of point 1
        :type p1: array,list,tuple
        :param p2: Coordinates of point 2
        :type p2: array,list,tuple
        :returns: distance between p1 and p2
        :rtype: float

        **Formula:**

        :math:`d(p,q)=\\sqrt{ \\sum_{i=1}^n ( p_i - q_i )^2 }`'''

        N_dim = len(p1)
        if len(p2) != N_dim:
            raise ValueError('Dimension mismatch between {p1} and {p2}.'.format(p1=p1, p2=p2))

        return np.sqrt(sum([(p1[i] - p2[i])**2 for i in range(N_dim)]))

    def get_zero_sequence_impedance(self, sequence_impedance_matrix):
        '''Get zero-sequence impedance from sequence impedance matrix.'''

        try:
            return sequence_impedance_matrix[0, 0]
        except:
            raise ValueError('sequence_impedance_matrix is not valid.')

    def get_positive_sequence_impedance(self, sequence_impedance_matrix):
        '''Get positive-sequence impedance from sequence impedance matrix.'''

        try:
            return sequence_impedance_matrix[1, 1]
        except:
            raise ValueError('sequence_impedance_matrix is not valid.')

    def get_negative_sequence_impedance(self, sequence_impedance_matrix):
        '''Get negative-sequence impedance from sequence impedance matrix.'''

        try:
            return sequence_impedance_matrix[2, 2]
        except:
            raise ValueError('sequence_impedance_matrix is not valid.')

    def get_sequence_impedance_matrix(self, phase_impedance_matrix):
        '''Get sequence impedance matrix from phase impedance matrix.'''

        a = cmath.exp(complex(0, 2. / 3 * cmath.pi))
        A = np.array([[complex(1.0, 0), complex(1.0, 0), complex(1.0, 0)], [complex(1.0, 0), a**2, a], [complex(1.0, 0), a, a**2]])
        A_inv = 1. / 3.0 * np.array([[complex(1.0, 0), complex(1.0, 0), complex(1.0, 0)], [complex(1.0, 0), a, a**2], [complex(1.0, 0), a**2, a]])
        return np.dot(A_inv, np.dot(phase_impedance_matrix, A))

    def kron_reduction(self, primitive_impedance_matrix):
        '''Performs Kron reduction on primitive impedance matrix.'''

        dim = len(primitive_impedance_matrix)
        zij = primitive_impedance_matrix[:dim - 1, :dim - 1]
        zin = primitive_impedance_matrix[:dim - 1, -1][:, np.newaxis]
        znn = primitive_impedance_matrix[dim - 1, dim - 1]
        znj = primitive_impedance_matrix[-1, :dim - 1]
        return zij - np.dot(zin, np.dot(1.0 / znn, znj)[np.newaxis])

    def carson_equation_self(self, ri, GMRi):
        '''Carson's equation for self impedance.'''

        return complex(ri + .0953, .12134 * (np.log(1.0 / GMRi) + 7.93402))

    def carson_equation(self, Dij):
        '''Carson's equation for mutual impedance.'''

        return complex(.09530, .12134 * (np.log(1.0 / Dij) + 7.93402))

    def get_primitive_impedance_matrix(self, dist_matrix, GMR_list, r_list):
        '''Get primitive impedance matrix from distance matrix between the wires, GMR list, and resistance list.'''

        primitive_impedance_matrix = []
        n_rows, n_cols = dist_matrix.shape
        for i in range(n_rows):
            primitive_impedance_matrix.append([])
            for j in range(n_cols):
                if i == j:
                    primitive_impedance_matrix[-1].append(self.carson_equation_self(r_list[i], GMR_list[i]))
                else:
                    primitive_impedance_matrix[-1].append(self.carson_equation(dist_matrix[i, j]))
        return np.array(primitive_impedance_matrix)

    def get_sequence_impedances(self, dist_matrix, GMR_list, r_list):
        '''Get sequence impedances Z0, Z+, Z- from distance matrix between the wires, GMR list, and resistance list.'''

        prim = self.get_primitive_impedance_matrix(dist_matrix, GMR_list, r_list)
        phase = self.kron_reduction(prim)
        seq = self.get_sequence_impedance_matrix(phase)
        return self.get_zero_sequence_impedance(seq), self.get_positive_sequence_impedance(seq), self.get_negative_sequence_impedance(seq)

    def update_dict(self, d1, d2):
        for k2, v2 in d2.items():
            if k2 in d1:
                d1[k2].update(v2)
            else:
                d1[k2] = v2
        return d1

    def parse(self, model, **kwargs):
        '''General parse function.
        Responsible for calling the sub-parsers and logging progress.

        :param model: DiTTo model
        :type model: DiTTo model
        :param verbose: Set verbose mode. Optional. Default=False
        :type verbose: bool
        :returns: 1 for success, -1 for failure
        :rtype: int'''

        #Verbose print the progress
        #This will be logged anyway
        if 'verbose' in kwargs and isinstance(kwargs['verbose'], bool):
            self.verbose = kwargs['verbose']
        else:
            self.verbose = False

        #Parse the nodes
        if self.verbose: print('Parsing the nodes...')
        self.logger.info('Parsing the nodes...')
        s = self.parse_nodes(model)
        if self.verbose and s != -1: print('Succesful!')

        #Parse the lines
        if self.verbose: print('Parsing the lines...')
        self.logger.info('Parsing the lines...')
        s = self.parse_lines(model)
        if self.verbose and s != -1: print('Succesful!')

        #Parse the transformers
        if self.verbose: print('Parsing the transformers...')
        self.logger.info('Parsing the transformers...')
        s = self.parse_transformers(model)
        if self.verbose and s != -1: print('Succesful!')

        #Parse Loads
        if self.verbose: print('Parsing the loads...')
        self.logger.info('Parsing the loads...')
        s = self.parse_loads(model)
        if self.verbose and s != -1: print('Succesful!')

        #Parse regulators
        if self.verbose: print('Parsing the regulators...')
        self.logger.info('Parsing the regulators...')
        s = self.parse_regulators(model)
        if self.verbose and s != -1: print('Succesful!')

        #Parse capacitors
        if self.verbose: print('Parsing the capacitors...')
        self.logger.info('Parsing the capacitors...')
        s = self.parse_capacitors(model)
        if self.verbose and s != -1: print('Succesful!')

        if self.verbose: print('Parsing done.')

        return 1

    def parse_nodes(self, model):
        '''Parse the node.

        .. note:: Has to be implemented in subclasses.

        '''
        pass

    def parse_lines(self, model):
        '''Parse the lines.

        .. note:: Has to be implemented in subclasses.

        '''
        pass

    def parse_capacitors(self, model):
        '''Parse the capacitors.

        .. note:: Has to be implemented in subclasses.

        '''
        pass

    def parse_transformers(self, model):
        '''Parse the transformers.

        .. note:: Has to be implemented in subclasses.

        '''
        pass

    def parse_regulators(self, model):
        '''Parse the regulators.

        .. note:: Has to be implemented in subclasses.

        '''
        pass

    def parse_loads(self, model):
        '''Parse the loads.

        .. note:: Has to be implemented in subclasses.

        '''
        pass
