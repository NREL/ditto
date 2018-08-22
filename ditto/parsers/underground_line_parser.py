# coding: utf8

from .line_parser import LineParser
import math
import numpy as np
from pint import UnitRegistry

ureg = UnitRegistry()


class UndergroundLineParser(LineParser):
    """
    This class should be used to parse underground lines only.
    We assume here concentric neutral cables, one per phase.
    The equations are based on Kersting's book and the reference to the equation number and pages are given in the comments.
    author: Nicolas Gensollen.
    """

    def __init__(self, name, n_phase, n_strand):
        """
        UndergroundLineParser class constructor.
        **Inputs:**
            - name: Name of the underground line.
            - n_phase: Number of phases for this line.
            - n_strand: Number of concentric neutral strands.
        """
        n_cond = 2 * n_phase  # This is for LineParser compatibility
        LineParser.__init__(self, name, n_phase, n_cond)
        self.n_strand = float(n_strand)

        # Parameters are instanciated as Nones.
        # Use set methods to provide these
        #
        # Outside diameters of the cables
        self.outside_diameters = [None for _ in range(self.n_phase)]

        # radius of the circle passing through the center of the strands
        self.R = [None for _ in range(self.n_phase)]

        # The equivalent GMR of the concentric neutral
        self.equivalent_GMR = [None for _ in range(self.n_phase)]

        # The equivalent resistance of the concentric neutral
        self.equivalent_resistance = [None for _ in range(self.n_phase)]

    def compute_impedance_matrix(self, unit):
        """
        Compute the impedance matrix.

        TODO: This function will look at how much information has been provided to the Parser.
        If enough information is available, it will compute the impedance matrix from the geometries.
        """
        # radius of the circle passing through the center of the strands
        # See eq. 4.82 p. 97
        for i in range(self.n_phase):
            self.R[i] = (
                (self.outside_diameters[i] - self.diameters[self.n_phase + i]) / 2.0
            ).to(ureg.feet)  # In feet

        # The equivalent GMR of the concentric neutral
        # See eq. 4.81 p. 97
        for i in range(self.n_phase):
            self.equivalent_GMR[i] = (
                self.GMR[self.n_phase + i]
                * self.n_strand
                * self.R[i] ** (self.n_strand - 1)
            ) ** (1.0 / self.n_strand)  # In feet

        # The equivalent resistance of the concentric neutral
        # See eq. 4.83 p. 97
        for i in range(self.n_phase):
            self.equivalent_resistance[i] = (
                self.resistance[self.n_phase + i] / self.n_strand
            )  # In Ohms per mile

        # Mutual phase impedance matrix z_ij
        # Call super
        LineParser.compute_impedance_matrix(self, unit)

        # Mutual phase neutral impedance matrix z_in
        for i in range(self.n_phase):
            for n in [x - self.n_phase for x in range(self.n_phase, self.n_cond)]:
                # If we have a diagonal term, the mutual impedance is between the
                # cable and its own concentric neutral. So the distance is simply R[i]
                if i == n:
                    self.z_in[i][n] = self.mutual_impedance(self.R[i], unit).magnitude
                # Otherwise, the distance is between the cable and the concentric
                # neutral of another cable. Most of the time, we can approximate this
                # distance by the center-to-center distance since this will be much
                # greater than the radius R. For cables in conduit, that assumption is
                # not valid. Here we do not make the simplification, so the distance
                # is given by:
                # Dij = (Dnm^k - R^k)^(1/k) eq. 4.84 p.97
                else:
                    Dij = (
                        self.distance(self.positions[i], self.positions[n], "ft")
                        ** self.n_strand
                        - self.R[i] ** self.n_strand
                    ) ** (1.0 / self.n_strand)
                    self.z_in[i][n] = self.mutual_impedance(Dij, unit).magnitude

        # z_nj is simply the transpose of z_in
        self.z_nj = self.z_in.T

        # Self neutral impedance matrix z_nn
        for n1 in range(self.n_phase, self.n_cond):
            for n2 in range(self.n_phase, self.n_cond):
                # for diagonal terms, we compute the self impedance for the
                # concentric neutral using the equivalent resistance and equivalent
                # GMR computed above.
                if n1 == n2:
                    self.z_nn[n1 - self.n_phase][
                        n2 - self.n_phase
                    ] = self.self_impedance(
                        self.equivalent_resistance[n1 - self.n_phase],
                        self.equivalent_GMR[n1 - self.n_phase],
                        unit,
                    ).magnitude
                # For off diagnoal terms, we compute the mutual impedance between
                # concentric neutral of different cables
                else:
                    self.z_nn[n1 - self.n_phase][
                        n2 - self.n_phase
                    ] = self.mutual_impedance(
                        self.distance(
                            self.positions[n1 - self.n_phase],
                            self.positions[n2 - self.n_phase],
                            "ft",
                        ),
                        unit,
                    ).magnitude

        # The phase impedance matrix is computed from z_ij, z_in, z_nn, z_nj
        # imp = z_ij - z_in . z_nn^-1 . z_nj
        self.impedance_matrix = self.z_ij - np.dot(
            self.z_in, np.dot(np.linalg.inv(self.z_nn), self.z_nj)
        )
