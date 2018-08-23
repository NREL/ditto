# coding: utf8

from .parser import Parser
import numpy as np
import math
from .. import ureg


class LineParser(Parser):
    """
    LineParser class.
    author: Nicolas Gensollen.
    """

    def __init__(self, name, n_phase, n_cond, inference=False):
        """
        LineParser class constructor.
        **Inputs:**
            - name: Name of the line
            - n_phase: Number of phases for this line
            - n_cond: Number of conductors for this line. Should be >= n_phase.
            - inference: Flag to activate missing parameters inference. Default=False.
        """
        # Call super
        Parser.__init__(self, name, inference)

        # Set the number of phases on this line
        self.n_phase = n_phase

        # Set the number of conductors for this line
        self.n_cond = n_cond
        # There should be more conductors than phases
        if self.n_phase > self.n_cond:
            raise ValueError(
                "LineParser constructor received {n_phase} phases and {n_cond} conductors. The number of conductors should be >= than the number of phases...".format(
                    n_cond=self.n_cond, n_phase=self.n_phase
                )
            )

        # Initialize the line parameters to None.
        # Use the set functions to provide these parameters
        #
        # Length of the line
        self.length = None

        # Nominal voltage
        self.nominal_voltage = None

        # Ampacity of the conductors.
        self.ampacity = [None for _ in range(self.n_cond)]

        # Emergency ampacity of the conductors
        self.emergency_ampacity = [None for _ in range(self.n_cond)]

        # Resistance of the conductors.
        self.resistance = [None for _ in range(self.n_cond)]  # Initialized as empty

        # GMR of the conductors
        self.GMR = [None for _ in range(self.n_cond)]  # Initialized as empty

        # Diameters of the conductors
        self.diameters = [None for _ in range(self.n_cond)]  # Initialized as empty

        # Outside diameters
        self.outside_diameters = [None for _ in range(self.n_cond)]

        # Positions of the conductors
        self.positions = [
            (None, None) for _ in range(self.n_cond)
        ]  # Initialized as empty

        # Mutual phase impedance matrix z_ij
        self.z_ij = np.empty((self.n_phase, self.n_phase), dtype=np.complex)

        # Mutual phase neutral impedance matrix z_in
        self.z_in = np.empty(
            (self.n_phase, self.n_cond - self.n_phase), dtype=np.complex
        )

        # Mutual neutral phase impedance matrix z_nj
        self.z_nj = np.empty(
            (self.n_cond - self.n_phase, self.n_phase), dtype=np.complex
        )

        # Self neutral impedance matrix z_nn
        self.z_nn = np.empty(
            (self.n_cond - self.n_phase, self.n_cond - self.n_phase), dtype=np.complex
        )

        # Impedance matrix of the line
        self.impedance_matrix = np.empty(
            (self.n_cond, self.n_cond)
        )  # Initialized as empty

    def mutual_impedance(self, distance, unit):
        """
        Carson equation to compute mutual impedance between conductors.
        **Inputs:**
            - distance: Distance between the 2 conductors. Should be a Pint object.
            - unit: Unit the mutual impedance should be in. Ex: ohm/mi, ohm/km, ohm/in...
        **Outputs:**
            - zij: Mutual impedance in the desired unit.
        **Reference:**
            This equation is based on Kersting's book, page 92, equation 4.77
        """
        # The equation assumes distance in feet.
        distance_ = distance.to(ureg.feet)

        # The equation returns a value in Ohm/mi
        z_ij = complex(
            0.0953, 0.12134 * (math.log(1.0 / distance_.magnitude) + 7.93402)
        ) * ureg.parse_expression("ohm/mi")

        return z_ij.to(ureg.parse_expression(unit))

    def self_impedance(self, resistance, GMR, unit):
        """
        Carson equation for the self impedance of a conductor.
        **Inputs:**
            - resistance: Per unit resistance of the conductor. Should be a Pint object.
            - GMR: GMR of the conductor. Should be a Pint object.
            - unit: Desired unit for the impedance. Ex: ohm/mi, ohm/km, ohm/m
        **Outputs:**
            - z_ii: Self impedance in the desired unit.
        **Reference:**
            This equation is based on Kersting's book, page 92, equation 4.75
        """
        # The equation assumes a resistance in Ohm/mi
        resistance_ = resistance.to(ureg.parse_expression("ohm/mi"))

        # And a GMR in feet
        GMR_ = GMR.to(ureg.feet)

        # And returns a value in Ohm/mi
        z_ii = complex(
            resistance_.magnitude + 0.0953,
            0.12134 * (math.log(1.0 / GMR_.magnitude) + 7.93402),
        ) * ureg.parse_expression("ohm/mi")

        return z_ii.to(ureg.parse_expression(unit))

    def compute_impedance_matrix(self, unit, use_n_cond=False):
        """
        Compute the impedance matrix.
        Has to be implemented in the subclasses.
        """
        # If use_n_cond is set to True, we use the number of conductors instead
        # of the number of phases when computing z_ij.
        # This little trick enables to compute the primitive sequence impedance
        # of overhead lines in a single call to this function.
        if use_n_cond:
            N = self.n_cond
            self.z_ij = np.empty((self.n_cond, self.n_cond), dtype=np.complex)
        else:
            N = self.n_phase

        # Mutual phase impedance matrix z_ij
        for i in range(N):
            for j in range(N):
                if i == j:
                    self.z_ij[i][j] = self.self_impedance(
                        self.resistance[i], self.GMR[i], unit
                    ).magnitude
                else:
                    self.z_ij[i][j] = self.mutual_impedance(
                        self.distance(self.positions[i], self.positions[j], "ft"), unit
                    ).magnitude
