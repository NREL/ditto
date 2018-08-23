# coding: utf8

from .line_parser import LineParser
import math
import numpy as np
from .. import ureg


class OverheadLineParser(LineParser):
    """
    This class should be used to parse overhead lines only.
    """

    def __init__(self, name, n_phase, n_cond, inference=False):
        """
        OverheadLineParser class constructor.
        **Inputs:**
            - name: Name of the underground line.
            - n_phase: Number of phases for this line.
            - n_cond: Number of conductors.
            - inference: Flag to activate missing parameters inference. Default=False.
        """
        # Call super
        LineParser.__init__(self, name, n_phase, n_cond)

    def compute_impedance_matrix(self, unit):
        """
        Compute the impedance matrix.
        """
        # Mutual phase impedance matrix z_ij
        # Here we just call the method from super and use the number of conductors
        # instead of the number of phases.
        LineParser.compute_impedance_matrix(self, unit, use_n_cond=True)

        # Then, we have the full primitive matrix already
        primitive_impedance_matrix = self.z_ij

        # To get the partitionned form, we just have to slice it!
        self.z_ij = primitive_impedance_matrix[: self.n_phase, : self.n_phase]
        self.z_nn = primitive_impedance_matrix[self.n_phase :, self.n_phase :]
        self.z_in = primitive_impedance_matrix[: self.n_phase, self.n_phase :]
        self.z_nj = primitive_impedance_matrix[self.n_phase :, : self.n_phase]

        self.impedance_matrix = self.z_ij - np.dot(
            self.z_in, np.dot(np.linalg.inv(self.z_nn), self.z_nj)
        )
