from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import (
    DiTToHasTraits,
    Float,
    Complex,
    Unicode,
    Any,
    Int,
    List,
    observe,
    Instance,
)

from .position import Position
from .phase_reactor import PhaseReactor

from ..constant import V


class Reactor(DiTToHasTraits):
    """
    TODO
    """

    name = Unicode(help="""Name of the Reactor object""", unit=None)
    nominal_voltage = Float(
        help="""This parameter defines the base voltage of the reactor.""",
        default_value=None,
        unit=V,
    )
    from_element = Any(
        help="""Name of the node which connects to the 'from' end of the reactor""",
        default_value=None,
        unit=None,
    )
    to_element = Any(
        help="""'Name of the node which connects to the 'to' end of the reactor. If set to None, shunt reactor is assumed.""",
        default_value=None,
        unit=None,
    )
    positions = List(
        Instance(Position),
        help="""This parameter is a list of positional points describing the line. The positions are objects containing elements of long, lat and elevation. The points can be used to map the position of the line.  """,
        default_value=None,
        unit=None,
    )
    connection_type = Unicode(
        help="""The connection type (D, Y, Z, A) for Delta, Wye, Zigzag.""",
        default_value=None,
        unit=None,
    )
    substation_name = Unicode(
        help="""The name of the substation to which the object is connected.""",
        default_value=None,
        unit=None,
    )
    feeder_name = Unicode(
        help="""The name of the feeder the object is on.""",
        default_value=None,
        unit=None,
    )
    is_substation = Int(
        help="""Flag that indicates wheter the element is inside a substation or not.""",
        default_value=0,
        unit=None,
    )

    faultrate = Float(
        help="""The number of faults that occur per year""",
        default_value=None,
        unit=None,
    )
    phase_reactors = List(
        Instance(PhaseReactor),
        help="""This parameter is a list of all the phase reactors composing the reactor.""",
        default_value=None,
        unit=None,
    )

    # NOT SURE ABOUT IMPEDANCE MATRIX....
    #
    # impedance_matrix = List(List(Complex),help='''This provides the matrix representation of the reactor impedance in complex form. Computed from the values of GMR and distances of individual wires. Kron reduction is applied to make this a 3x3 matrix.''')
    # capacitance_matrix = List(List(Complex),help='''This provides the matrix representation of the reactor capacitance in complex form. Computed from the values of diameters and distances of individual wires. Kron reduction is applied to make this a 3x3 matrix.''')

    def build(self, model):
        self._model = model
