# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import (
    DiTToHasTraits,
    Float,
    Unicode,
    Any,
    Int,
    List,
    Bool,
    observe,
    Instance,
)

from .position import Position


class Wire(DiTToHasTraits):
    phase = Unicode(
        help="""The phase (A, B, C, N, s1, s2) of the wire""", default_value=None
    )
    nameclass = Unicode(
        help="""The nameclass (e.g. 1/0_ACSR) of the wire""", default_value=None
    )
    X = Float(
        help="""The horizontal placement of the wire on a cross section of the line w.r.t. some point of reference (typically one wire on the configuration)""",
        default_value=None,
    )
    Y = Float(
        help="""The vertical placement above (or below) ground of the wire on a cross section of the line w.r.t. some point of reference (typically one wire on the configuration)""",
        default_value=None,
    )
    diameter = Float(
        help="""The diameter of the conductor.
        If the wire is a concentric neutral cable, this is the diameter of the phase conductor.""",
        default_value=None,
    )
    gmr = Float(
        help="""The geometric mean radius of the wire.
        If the wire is a concentric neutral cable, this is the GMR of the phase conductor.""",
        default_value=None,
    )
    ampacity = Float(
        help="""The ampacity rating for the wire under nomal conditions""",
        default_value=None,
    )
    emergency_ampacity = Float(
        help="""The ampacity rating for the wire under emergency conditions""",
        default_value=None,
    )
    resistance = Float(
        help="""The total resistance of the wire.
        If the wire is a concentric neutral cable, this is the per-unit resistance of the phase conductor""",
        default_value=None,
    )
    insulation_thickness = Float(
        help="""Thickness of the insulation around the secondary live conductors""",
    ).tag(default=None)
    is_fuse = Bool(
        help="""This flag indicates whether or not this wire is also a fuse""",
        default_value=None,
    )
    is_switch = Bool(
        help="""This flag indicates whether or not this wire is also a switch""",
        default_value=None,
    )
    is_open = Bool(
        help="""This flag indicates whether or not the line is open (if it is a switch/fuse/breaker/recloser/sectionalizer/network protector).""",
        default_value=None,
    )
    # Modification: Nicolas Gensollen (June 2018)
    # fuse_limit --> interrupting_rating (more generic)
    interrupting_rating = Float(
        help="""The maximum current that can pass through the wire before the equipment disconnects.""",
        default_value=None,
    )

    # Concentric Neutral Specific
    # This section should be used to model the Wire object as a concentric neutral cable
    # If the wire is a basic bare conductor, leave undefined.
    #
    concentric_neutral_gmr = Float(
        help="""The geometric mean radius of the neutral strand for a concentric neutral cable.""",
        default_value=None,
    )
    concentric_neutral_resistance = Float(
        help="""The per-unit length resistance of the neutral strand for a concentric neutral cable.""",
        default_value=None,
    )
    concentric_neutral_diameter = Float(
        help="""The diameter of the neutral strand of the concentric neutral cable.""",
        default_value=None,
    )
    concentric_neutral_outside_diameter = Float(
        help="""The outside diameter of the concentric neutral cable.""",
        default_value=None,
    )
    concentric_neutral_nstrand = Int(
        help="""The number of strands for the concentric neutral cable.""",
        default_value=None,
    )
    ###############################################################

    # Modification: Nicolas Gensollen (December 2017)
    # Drop flag is used if we created objects in the reader that we do not want to output.
    # This is much faster than looping over objects to remove them in a pre/post-processing step
    drop = Bool(
        help="""Set to 1 if the object should be dropped in the writing process. Otherwise leave 0.""",
        default_value=False,
    )

    # Modification: Nicolas (December 2017)
    # Add a is_recloser attribute as an easy and quick way to handle reclosers in DiTTo
    is_recloser = Bool(
        help="""This flag indicates whether or not this wire is also a recloser""",
        default_value=None,
    )

    # Modification: Nicolas (January 2018)
    is_breaker = Bool(
        help="""This flag indicates whether or not this wire is also a recloser""",
        default_value=None,
    )

    # Modification: Nicolas (June 2018)
    is_network_protector = Bool(
        help="""This flag indicates whether or not this wire is also a network protector.""",
        default_value=None,
    )

    # Modification: Nicolas (August 2018)
    is_sectionalizer = Bool(
        help="""This flag indicates whether or not this wire is also a sectionalizer.""",
        default_value=None,
    )

    def build(self, model):
        self._model = model
        pass


#        self._wp = self._model.env.WirePosition()
#
#
#    @observe('phase', type='change')
#    def _set_phase(self, bunch):
#        self._wp.phase==bunch['new']
#
#    @observe('phase', type='fetch')
#    def _get_phase(self, bunch):
#        return self._wp.phase
#
#    @observe('X', type='change')
#    def _set_X(self, bunch):
#       self._wp.xCoord = self._model.env.Displacement(value=bunch['new'])
#
#    @observe('X', type='fetch')
#    def _get_X(self, bunch):
#        if self._wp.xCoord is None:
#            return None
#        return self._wp.xCoord.value
#
#    @observe('Y', type='change')
#    def _set_Y(self, bunch):
#       self._wp.yCoord = self._model.env.Displacement(value=bunch['new'])
#
#    @observe('Y', type='fetch')
#    def _get_Y(self, bunch):
#        if self._wp.yCoord is None:
#            return None
#        return self._wp.yCoord.value
#
#
#
#
