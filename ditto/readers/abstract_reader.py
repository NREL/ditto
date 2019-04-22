# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import sys
import logging

import cmath

from six import string_types
from ditto.default_values.default_values_json import Default_Values

import numpy as np

LOGGER = logging.getLogger(__name__)


class AbstractReader(object):
    """Abstract class for DiTTo readers.
    author: Nicolas Gensollen. October 2017.
    """

    register_names = []

    def __init__(self, **kwargs):
        """Abstract class CONSTRUCTOR."""

        # create logger
        self.logger = LOGGER

    @classmethod
    def register(cls, registration_dict):

        for name in cls.register_names:
            registration_dict[name] = cls

    def symmetrize(self, matrix):
        """Symmetrize a triangular matrix in list format.

        :param matrix: Matrix to symmetrize
        :type matrix: List
        :returns: Symmetric list of lists
        :rtype: list

        **Usage:**

        The function expects a list of lists, and turns it into a symmetric list of lists:

        >>> symmetrize([[.1], [.2,.1], [.4,.5,.1]])
        [[.1,.2,.4],[.2,.1,.5],[.4,.5,.1]]

        ..note:: Probably, many more elegant (and faster!) ways to do this...
        """

        N_rows = len(matrix)
        N_cols = max(map(lambda x: len(x), matrix))

        if N_rows != N_cols:
            self.logger.warning("Expects a square matrix here")
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
            matrix2[i, i] *= 0.5

        return matrix2.tolist()

    def convert_to_meters(self, quantity, unit, **kwargs):
        """Converts a distance in a given unit to meters.

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

        .. seealso:: convert_from_meters, unit_conversion
        """

        if "inverse" in kwargs and isinstance(kwargs["inverse"], bool):
            inverse = kwargs["inverse"]
        else:
            inverse = False

        if unit is None:
            return None

        if not isinstance(unit, string_types):
            self.logger.warning("convert_to_meters() expects a unit in string format")
            return None

        if quantity is None:
            return None

        if unit.lower() == "mi":
            if inverse:
                return quantity / 1609.34
            else:
                return 1609.34 * quantity

        elif unit.lower() == "km":
            if inverse:
                return quantity / 1000.0
            else:
                return 1000 * quantity

        elif unit.lower() == "kft":
            if inverse:
                return quantity / 304.8
            else:
                return 304.8 * quantity

        elif unit.lower() == "m":
            return quantity

        elif unit.lower() == "ft":
            if inverse:
                return quantity / 0.3048
            else:
                return 0.3048 * quantity

        elif unit.lower() == "in":
            if inverse:
                return quantity / 0.0254
            else:
                return 0.0254 * quantity

        elif unit.lower() == "cm":
            if inverse:
                return quantity / 0.01
            else:
                return 0.01 * quantity

        else:
            return None

    def convert_from_meters(self, quantity, unit, **kwargs):
        """Converts a distance in meters to a distance in given unit.

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

        .. seealso:: convert_to_meters, unit_conversion
        """

        if "inverse" in kwargs and isinstance(kwargs["inverse"], bool):
            inverse = kwargs["inverse"]
        else:
            inverse = False

        if unit is None:
            return None

        if not isinstance(unit, string_types):
            self.logger.warning("convert_from_meters() expects a unit in string format")
            return None

        if quantity is None:
            return None

        if unit.lower() == "mi":
            if inverse:
                return quantity / 0.000621371
            else:
                return 0.000621371 * quantity

        elif unit.lower() == "km":
            if inverse:
                return quantity / 10 ** -3
            else:
                return 10 ** -3 * quantity

        elif unit.lower() == "kft":
            if inverse:
                return quantity / 0.00328084
            else:
                return 0.00328084 * quantity

        elif unit.lower() == "m":
            return quantity

        elif unit.lower() == "ft":
            if inverse:
                return quantity / 3.28084
            else:
                return 3.28084 * quantity

        elif unit.lower() == "in":
            if inverse:
                return quantity / 39.3701
            else:
                return 39.3701 * quantity

        elif unit.lower() == "cm":
            if inverse:
                return quantity / 100
            else:
                return 100 * quantity

        else:
            return None

    def unit_conversion(self, quantity, unit_from, unit_to):
        """Converts a distance in unit_from to a distance in unit_to.
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

        .. seealso:: convert_to_meters, convert_from_meters
        """

        supported_units = ["km", "m", "ft", "kft", "in", "cm", "mi"]
        if unit_from not in supported_units:
            return None
        if unit_to not in supported_units:
            return None
        # Convert to meters
        in_meters = self.convert_to_meters(quantity, unit_from)

        # Convert from meters
        result = self.convert_from_meters(in_meters, unit_to)

        return result

    def distance(self, p1, p2):
        """Returns the euclidean distance between two points p1 and p2.

        :param p1: Coordinates of point 1
        :type p1: array,list,tuple
        :param p2: Coordinates of point 2
        :type p2: array,list,tuple
        :returns: distance between p1 and p2
        :rtype: float

        **Formula:**

        :math:`d(p,q)=\\sqrt{ \\sum_{i=1}^n ( p_i - q_i )^2 }`
        """

        N_dim = len(p1)
        if len(p2) != N_dim:
            raise ValueError(
                "Dimension mismatch between {p1} and {p2}.".format(p1=p1, p2=p2)
            )

        return np.sqrt(sum([(p1[i] - p2[i]) ** 2 for i in range(N_dim)]))

    def get_zero_sequence_impedance(self, sequence_impedance_matrix):
        """Get zero-sequence impedance from sequence impedance matrix."""

        try:
            return sequence_impedance_matrix[0, 0]
        except:
            raise ValueError("sequence_impedance_matrix is not valid.")

    def get_positive_sequence_impedance(self, sequence_impedance_matrix):
        """Get positive-sequence impedance from sequence impedance matrix."""

        try:
            return sequence_impedance_matrix[1, 1]
        except:
            raise ValueError("sequence_impedance_matrix is not valid.")

    def get_negative_sequence_impedance(self, sequence_impedance_matrix):
        """Get negative-sequence impedance from sequence impedance matrix."""

        try:
            return sequence_impedance_matrix[2, 2]
        except:
            raise ValueError("sequence_impedance_matrix is not valid.")

    def get_sequence_impedance_matrix(self, phase_impedance_matrix):
        """Get sequence impedance matrix from phase impedance matrix."""

        phase_impedance_matrix = np.array(phase_impedance_matrix)
        # If we have a 3 by 3 phase impedance matrix
        if phase_impedance_matrix.shape == (3, 3):
            a = cmath.exp(complex(0, 2.0 / 3 * cmath.pi))
            A = np.array(
                [
                    [complex(1.0, 0), complex(1.0, 0), complex(1.0, 0)],
                    [complex(1.0, 0), a ** 2, a],
                    [complex(1.0, 0), a, a ** 2],
                ]
            )
            A_inv = (
                1.0
                / 3.0
                * np.array(
                    [
                        [complex(1.0, 0), complex(1.0, 0), complex(1.0, 0)],
                        [complex(1.0, 0), a, a ** 2],
                        [complex(1.0, 0), a ** 2, a],
                    ]
                )
            )
        # if we have a 2 by 2 phase impedance matrix
        elif phase_impedance_matrix.shape == (2, 2):
            A = np.array([[1.0, 1.0], [1.0, -1.0]])
            A_inv = np.array([[0.5, 0.5], [0.5, -0.5]])
        else:
            return []
        return np.dot(A_inv, np.dot(phase_impedance_matrix, A))

    def kron_reduction(self, primitive_impedance_matrix, neutrals=None):
        """Performs Kron reduction on primitive impedance matrix.
           Neutrals is a list of elements that defines the indices of the neutrals
        """

        if neutrals is None:  # assume last row is neutral if nothing provided
            self.logger.warning(
                "Warning - last row assumed to be used for Kron reduction"
            )
            neutrals = [len(primitive_impedance_matrix) - 1]

        dim_neutrals = len(neutrals)
        dim_phase = len(primitive_impedance_matrix) - len(neutrals)
        zij = [[None for i in range(dim_phase)] for j in range(dim_phase)]
        znn = [[None for i in range(dim_neutrals)] for j in range(dim_neutrals)]
        zin = [[None for i in range(dim_neutrals)] for j in range(dim_phase)]  # z[i][n]
        znj = [[None for i in range(dim_phase)] for j in range(dim_neutrals)]  # z[n][j]

        cnts = {"zij": [0, 0], "zin": [0, 0], "znj": [0, 0], "znn": [0, 0]}
        i_phase = 0
        i_n = 0
        j_phase = 0
        j_n = 0
        for i in range(len(primitive_impedance_matrix)):
            changed_set = set()
            for j in range(len(primitive_impedance_matrix)):
                if i in neutrals and j in neutrals:
                    i_loc = cnts["znn"][0]
                    j_loc = cnts["znn"][1]
                    znn[i_loc][j_loc] = primitive_impedance_matrix[i][j]
                    cnts["znn"][0] += 1
                    changed_set.add("znn")
                elif (not i in neutrals) and (not j in neutrals):
                    i_loc = cnts["zij"][0]
                    j_loc = cnts["zij"][1]
                    zij[i_loc][j_loc] = primitive_impedance_matrix[i][j]
                    cnts["zij"][0] += 1
                    changed_set.add("zij")
                elif (not i in neutrals) and j in neutrals:
                    i_loc = cnts["zin"][0]
                    j_loc = cnts["zin"][1]
                    zin[i_loc][j_loc] = primitive_impedance_matrix[i][j]
                    cnts["zin"][0] += 1
                    changed_set.add("zin")
                elif i in neutrals and (not j in neutrals):
                    i_loc = cnts["znj"][0]
                    j_loc = cnts["znj"][1]
                    znj[i_loc][j_loc] = primitive_impedance_matrix[i][j]
                    cnts["znj"][0] += 1
                    changed_set.add("znj")

                else:
                    raise ValueError("Kron reduction failed")
            for zone in changed_set:
                cnts[zone][0] = 0
                cnts[zone][1] += 1

        # dim = len(primitive_impedance_matrix)
        # zij = primitive_impedance_matrix[: dim - 1, : dim - 1]
        # zin = primitive_impedance_matrix[: dim - 1, -1][:, np.newaxis]
        # znn = primitive_impedance_matrix[dim - 1, dim - 1]
        # znj = primitive_impedance_matrix[-1, : dim - 1]
        return zij - np.dot(zin, np.dot(np.linalg.inv(znn), znj))

    def carson_equation_self(self, ri, GMRi):
        """Carson's equation for self impedance."""
        if ri is None:
            raise ValueError("Resistance is None. Cannot compute Carson's equation.")
        if GMRi is None:
            raise ValueError("GMR is None. Cannot compute Carson's equation.")
        if GMRi == 0:
            raise ValueError("GMR is zero. Cannot compute Carson's equation.")
        return complex(ri + 0.0953, 0.12134 * (np.log(1.0 / GMRi) + 7.93402))

    def carson_equation(self, Dij):
        """Carson's equation for mutual impedance."""
        if Dij == 0:
            raise ValueError("Distance Dij is zero. Cannot compute Carson's equation.")
        return complex(0.09530, 0.12134 * (np.log(1.0 / Dij) + 7.93402))

    def get_primitive_impedance_matrix(self, dist_matrix, GMR_list, r_list):
        """Get primitive impedance matrix from distance matrix between the wires, GMR list, and resistance list."""

        primitive_impedance_matrix = []
        n_rows, n_cols = dist_matrix.shape
        for i in range(n_rows):
            primitive_impedance_matrix.append([])
            for j in range(n_cols):
                if i == j:
                    primitive_impedance_matrix[-1].append(
                        self.carson_equation_self(r_list[i], GMR_list[i])
                    )
                else:
                    primitive_impedance_matrix[-1].append(
                        self.carson_equation(dist_matrix[i, j])
                    )
        return np.array(primitive_impedance_matrix)

    def get_sequence_impedances(self, dist_matrix, GMR_list, r_list):
        """Get sequence impedances Z0, Z+, Z- from distance matrix between the wires, GMR list, and resistance list."""

        prim = self.get_primitive_impedance_matrix(dist_matrix, GMR_list, r_list)
        phase = self.kron_reduction(prim)
        seq = self.get_sequence_impedance_matrix(phase)
        return (
            self.get_zero_sequence_impedance(seq),
            self.get_positive_sequence_impedance(seq),
            self.get_negative_sequence_impedance(seq),
        )

    def get_phase_impedances(
        self, wire_list, distance_matrix=None, overhead=True, kron_reduce=None
    ):
        """ Compute phase impedances for wire list. Default parameters assume there is no neutral.
            A kron reduction will be automatically be done if the matrix size is 4x4.
            Otherwise no kron reduction is performed
            All input units are assumed to be DiTTo default units (meters for distance)
        """
        nphases = len(wire_list)
        if nphases == 4:
            kron_reduce = True
        elif kron_reduce is None:
            kron_reduce = False

        impedance_matrix = [[None for i in range(nphases)] for j in range(nphases)]

        if distance_matrix is None:
            distance_matrix = [[None for i in range(nphases)] for j in range(nphases)]
            for i in range(nphases):
                for j in range(nphases):
                    if overhead:
                        distance_matrix[i][j] = (
                            abs(i - j) * 0.6
                        )  # Assume 60 cm apart one above another or side by side.
                    else:
                        distance_matrix[i][j] = (
                            abs(i - j) * 0.3
                        )  # Assume 30 cm apart next to each other.

        distance_matrix_feet = [[None for i in range(nphases)] for j in range(nphases)]
        if nphases != len(distance_matrix):
            raise ValueError("Distance matrix must be same size as number of wires")

        for i in range(nphases):
            for j in range(nphases):
                distance_matrix_feet[i][j] = self.convert_from_meters(
                    distance_matrix[i][j], "ft"
                )

        if overhead:
            rs = []
            gmrs = []
            for i in range(nphases):
                if wire_list[i].gmr is None:
                    gmr_meters = 0.0088  # ACSR Hawk (477kcmil)
                    self.logger.warning("Warning - using default gmr of " + str(gmr))
                else:
                    gmr_meters = wire_list[i].gmr
                if wire_list[i].resistance is None:
                    resistance_meters = 0.1194 / 1000  # ACSR Hawk (477kcmil)
                    self.logger.warning(
                        "Warning - using default resistance of " + str(resistance)
                    )
                else:
                    resistance_meters = wire_list[i].resistance
                gmrs.append(self.convert_from_meters(gmr_meters, "ft"))
                rs.append(
                    self.convert_from_meters(resistance_meters, "ft", inverse=True)
                )
            impedance_matrix_imperial = self.get_primitive_impedance_matrix(
                np.array(distance_matrix_feet), gmrs, rs
            )
            if kron_reduce:
                impedance_matrix_imperial = self.kron_reduce(
                    impedance_matrix_imperial
                )  # automatically assumes last element ei
            for i in range(len(impedance_matrix)):
                for j in range(len(impedance_matrix)):
                    impedance_matrix[i][j] = self.convert_to_meters(
                        impedance_matrix_imperial[i][j], "mi", inverse=True
                    )  # works for complex
        else:
            # For underground cables create an n*2 x n*2 matrix which includes the neutrals. Then kron reduce the neutrals out to get an nxn matrix
            rs = []
            gmrs = []
            rs_neutral = []
            gmrs_neutral = []
            radius_neutral = []
            # Defaults from 600kcmil concentric neutral wires
            for i in range(nphases):
                if (
                    wire_list[i].concentric_neutral_gmr is None
                ):  # WARNING: this is the GMR of the neutral strand, not the computed GMR of all neutrals
                    concentric_neutral_gmr_meters = (
                        0.5 / 1000.0 * 0.7788
                    )  # half a mm gmr is the radius of the strand.
                    self.logger.warning(
                        "Warning - using default concentric_neutral_gmr of "
                        + str(concentric_neutral_gmr_meters)
                    )
                else:
                    concentric_neutral_gmr_meters = wire_list[i].concentric_neutral_gmr

                if wire_list[i].concentric_neutral_nstrand is None:
                    concentric_neutral_nstrand = 32  # Default value
                    self.logger.warning(
                        "Warning - using default concentric_neutral_nstrand of "
                        + str(concentric_neutral_nstrand)
                    )
                else:
                    concentric_neutral_nstrand = wire_list[i].concentric_neutral_nstrand

                if wire_list[i].concentric_neutral_diameter is None:
                    concentric_neutral_diameter_meters = (
                        1 / 1000.0
                    )  # 1 mm strand diameter
                    self.logger.warning(
                        "Warning - using default concentric_neutral_diameter of "
                        + str(concentric_neutral_diameter_meters)
                    )
                else:
                    concentric_neutral_diameter_meters = wire_list[
                        i
                    ].concentric_neutral_diameter

                if wire_list[i].concentric_neutral_outside_diameter is None:
                    concentric_neutral_outside_diameter_meters = 25.93 / 1000.0
                    self.logger.warning(
                        "Warning - using default concentric_neutral_outside_diameter of "
                        + str(concentric_neutral_outside_diameter_meters)
                    )
                else:
                    concentric_neutral_outside_diameter_meters = wire_list[
                        i
                    ].concentric_neutral_outside_diameter

                if wire_list[i].concentric_neutral_resistance is None:
                    concentric_neutral_resistance_meters = (
                        0.000269
                    )  # Aluminium wire resistivity per meter for 4/0 wire (Nexans)
                    self.logger.warning(
                        "Warning - using default concentric_neutral_resistance of "
                        + str(concentric_neutral_resistance_meters)
                    )
                else:
                    concentric_neutral_resistance_meters = wire_list[
                        i
                    ].concentric_neutral_resistance

                if wire_list[i].resistance is None:
                    resistance_meters = (
                        0.000269
                    )  # Aluminium wire resistivity per meter for 4/0 wire (Nexans)
                    self.logger.warning(
                        "Warning - using default resistance of "
                        + str(resistance_meters)
                    )
                else:
                    resistance_meters = wire_list[i].resistance

                if wire_list[i].gmr is None:
                    gmr_meters = (
                        13.26 / 2.0 / 1000.0 * 0.7788
                    )  # using 4/0 wire diameter of 13.26
                    self.logger.warning(
                        "Warning - using default gmr of " + str(gmr_meters)
                    )
                else:
                    gmr_meters = wire_list[i].gmr

                radius_meters = (
                    concentric_neutral_outside_diameter_meters
                    - concentric_neutral_diameter_meters
                ) / 2.0
                radius = self.convert_from_meters(radius_meters, "ft")
                concentric_neutral_gmr = self.convert_from_meters(
                    concentric_neutral_gmr_meters, "ft"
                )
                gmr_neutral = (
                    concentric_neutral_gmr
                    * concentric_neutral_nstrand
                    * (radius ** (concentric_neutral_nstrand - 1))
                ) ** (1 / concentric_neutral_nstrand)
                r_neutral = self.convert_from_meters(
                    concentric_neutral_resistance_meters, "mi", inverse=True
                ) / float(concentric_neutral_nstrand)
                gmrs.append(self.convert_from_meters(gmr_meters, "ft"))
                rs.append(
                    self.convert_from_meters(resistance_meters, "ft", inverse=True)
                )
                gmrs_neutral.append(gmr_neutral)
                rs_neutral.append(r_neutral)
                radius_neutral.append(radius)

            distance_matrix_cn = [
                [None for i in range(2 * nphases)] for j in range(2 * nphases)
            ]
            for i in range(nphases):
                for j in range(nphases):
                    distance_matrix_cn[i][j] = distance_matrix_feet[i][j]
                    distance_matrix_cn[i + nphases][j + nphases] = distance_matrix_feet[
                        i
                    ][j]

                    # As per Example 4.2 of Kersting. phase-neutral equals the concentric-neutral radius for same cable
                    if i == j:
                        distance_matrix_cn[i + nphases][j] = radius_neutral[i]
                        distance_matrix_cn[i][j + nphases] = radius_neutral[i]
                    # As per Example 4.2 of Kersting. phase-neutral = phase-phase distance for different cables
                    else:
                        distance_matrix_cn[i + nphases][j] = distance_matrix_feet[i][j]
                        distance_matrix_cn[i][j + nphases] = distance_matrix_feet[i][j]
            gmrs_cn = []
            rs_cn = []
            for i in range(nphases):
                gmrs_cn.append(gmrs[i])
                rs_cn.append(rs[i])
            for i in range(nphases):
                gmrs_cn.append(gmrs_neutral[i])
                rs_cn.append(rs_neutral[i])

            impedance_matrix_imperial = self.get_primitive_impedance_matrix(
                np.array(distance_matrix_cn), gmrs_cn, rs_cn
            )
            # Now Kron reduce out the nphases neutrals
            neutrals = []
            for i in range(nphases):
                neutrals.append(i + nphases)
            impedance_matrix_imperial = self.kron_reduction(
                impedance_matrix_imperial, neutrals=neutrals
            )

            for i in range(len(impedance_matrix)):
                for j in range(len(impedance_matrix)):
                    impedance_matrix[i][j] = self.convert_to_meters(
                        impedance_matrix_imperial[i][j], "mi", inverse=True
                    )  # works for complex

        return impedance_matrix

    def update_dict(self, d1, d2):
        for k2, v2 in d2.items():
            if k2 in d1:
                d1[k2].update(v2)
            else:
                d1[k2] = v2
        return d1

    def parse(self, model, **kwargs):
        """General parse function.
        Responsible for calling the sub-parsers and logging progress.

        :param model: DiTTo model
        :type model: DiTTo model
        :param verbose: Set verbose mode. Optional. Default=False
        :type verbose: bool
        :returns: 1 for success, -1 for failure
        :rtype: int"""

        # Verbose print the progress
        # This will be logged anyway
        if "verbose" in kwargs and isinstance(kwargs["verbose"], bool):
            self.verbose = kwargs["verbose"]
        else:
            self.verbose = False

        # Parse the nodes
        if self.verbose:
            self.logger.info("Parsing the nodes...")
        s = self.parse_nodes(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        # Parse the lines
        if self.verbose:
            self.logger.info("Parsing the lines...")
        s = self.parse_lines(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        # Parse the transformers
        if self.verbose:
            self.logger.info("Parsing the transformers...")
        s = self.parse_transformers(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        # Parse Loads
        if self.verbose:
            self.logger.info("Parsing the loads...")
        s = self.parse_loads(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        # Parse regulators
        if self.verbose:
            self.logger.info("Parsing the regulators...")
        s = self.parse_regulators(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        # Parse capacitors
        if self.verbose:
            self.logger.info("Parsing the capacitors...")
        s = self.parse_capacitors(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        if self.verbose:
            self.logger.info("Parsing done.")

        # Parse distributed generation
        if self.verbose:
            self.logger.info("Parsing the Distributed Generation...")
        s = self.parse_dg(model)
        if self.verbose and s != -1:
            self.logger.info("Succesful!")

        if self.verbose:
            self.logger.info("Parsing done.")

        if hasattr(self, "DSS_file_names"):
            if (
                self.DSS_file_names["default_values_file"]
                or self.DSS_file_names["remove_opendss_default_values_flag"] is True
            ):
                if self.verbose:
                    self.logger.info("Parsing the default values...")
                s = self.parse_default_values(model)
                if self.verbose and s != -1:
                    self.logger.info("Succesful!")

        return 1

    def parse_nodes(self, model):
        """Parse the node.
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def parse_lines(self, model):
        """Parse the lines.
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def parse_capacitors(self, model):
        """Parse the capacitors.
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def parse_transformers(self, model):
        """Parse the transformers.
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def parse_regulators(self, model):
        """Parse the regulators.
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def parse_loads(self, model):
        """Parse the loads.
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def parse_dg(self, model):
        """Parse the distributed generation (e.g. PV).
        .. note:: Has to be implemented in subclasses.
        """
        pass

    def set_default_values(self, obj, attr, value, *args):
        if not self.DSS_file_names["remove_opendss_default_values_flag"]:
            if hasattr(obj, attr):
                if attr == "capacitance_matrix":
                    new_cmatrix = np.array(value)
                    if new_cmatrix.ndim == 1:
                        new_cmatrix = [new_cmatrix.tolist()]
                    else:
                        new_cmatrix = new_cmatrix.tolist()
                    value = new_cmatrix
                elif attr == "impedance_matrix":
                    new_rmatrix = np.array(value)
                    new_xmatrix = np.array(args[0])
                    Z = new_rmatrix + 1j * new_xmatrix
                    if Z.ndim == 1:
                        Z = [Z.tolist()]
                    else:
                        Z = Z.tolist()
                    value = Z
        else:
            value = None
        setattr(obj, attr, value)

    def parse_default_values(self, model):
        model.set_names()
        parsed_values = {}
        parsed_values.setdefault("Line", {})
        if self.DSS_file_names["default_values_file"]:
            d_v = Default_Values(self.DSS_file_names["default_values_file"])
            parsed_values = d_v.parse()

        for obj in model.models:
            self.set_default_values(
                obj, "faultrate", parsed_values.get("Line", None).get("faultrate", None)
            )
            self.set_default_values(
                obj,
                "impedance_matrix",
                parsed_values.get("Line", None).get("rmatrix", None),
                parsed_values.get("Line", None).get("xmatrix", None),
            )
            self.set_default_values(
                obj,
                "capacitance_matrix",
                parsed_values.get("Line", None).get("cmatrix", None),
            )
            self.set_default_values(
                obj, "ampacity", parsed_values.get("Wire", {}).get("ampacity", None)
            )
            self.set_default_values(
                obj,
                "emergency_ampacity",
                parsed_values.get("Wire", {}).get("emergency_ampacity", None),
            )
            self.set_default_values(
                obj,
                "insulation_thickness",
                parsed_values.get("Wire", {}).get("insulation_thickness", None),
            )
            if type(obj).__name__ == "Capacitor":
                self.set_default_values(
                    obj,
                    "connection_type",
                    parsed_values.get("Capacitor", {}).get("connection_type", None),
                )
                self.set_default_values(
                    obj, "delay", parsed_values.get("Capacitor", {}).get("delay", None)
                )
                self.set_default_values(
                    obj,
                    "pt_ratio",
                    parsed_values.get("Capacitor", {}).get("pt_ratio", None),
                )
            self.set_default_values(
                obj, "low", parsed_values.get("Capacitor", {}).get("low", None)
            )
            self.set_default_values(
                obj, "high", parsed_values.get("Capacitor", {}).get("high", None)
            )
            self.set_default_values(
                obj,
                "ct_ratio",
                parsed_values.get("Capacitor", {}).get("ct_ratio", None),
            )
            self.set_default_values(
                obj,
                "pt_phase",
                parsed_values.get("Capacitor", {}).get("pt_phase", None),
            )
            if type(obj).__name__ == "Regulator":
                self.set_default_values(
                    obj,
                    "connection_type",
                    parsed_values.get("Regulator", {}).get("connection_type", None),
                )
                self.set_default_values(
                    obj, "delay", parsed_values.get("Regulator", {}).get("delay", None)
                )
                self.set_default_values(
                    obj,
                    "pt_ratio",
                    parsed_values.get("Regulator", {}).get("pt_ratio", None),
                )
            self.set_default_values(
                obj, "ct_prim", parsed_values.get("Regulator", {}).get("ct_prim", None)
            )
            self.set_default_values(
                obj,
                "highstep",
                parsed_values.get("Regulator", {}).get("highstep", None),
            )
            self.set_default_values(
                obj,
                "bandwidth",
                parsed_values.get("Regulator", {}).get("bandwidth", None),
            )
            self.set_default_values(
                obj,
                "bandcenter",
                parsed_values.get("Regulator", {}).get("bandcenter", None),
            )
            if type(obj).__name__ == "Transformer":
                self.set_default_values(
                    obj,
                    "connection_type",
                    parsed_values.get("Transformer", {}).get("connection_type", None),
                )
            self.set_default_values(
                obj,
                "reactances",
                parsed_values.get("Transformer", {}).get("reactances", None),
            )
            if type(obj).__name__ == "Load":
                self.set_default_values(
                    obj,
                    "connection_type",
                    parsed_values.get("Load", {}).get("connection_type", None),
                )
            self.set_default_values(
                obj, "vmin", parsed_values.get("Load", {}).get("vmin", None)
            )
            self.set_default_values(
                obj, "vmax", parsed_values.get("Load", {}).get("vmax", None)
            )
