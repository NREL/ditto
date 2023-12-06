# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .base import DiTToBaseModel
from .units import Voltage, VoltageUnit, Phase
from .position import Position


class Node(DiTToHasTraits):
    
    nominal_voltage: Optional[Voltage] = Field( 
        description = "The nominal voltage at the node",
        title = "Nominal voltage",
        cim_value="nomU"
    )

    phases: Optional[List[Phase]] = Field( 
        description="Phases at the node",
        title="phases"
        cim_value="phases"
    )

    is_substation_connection: Optional[bool] = Field(
        description="1 if the node connects from inside a substation to outside, 0 otherwise. These indicate if a node connects a substation to a feeder or high voltage source",
        title="is_substation_connection",
        default=False,
        cim_value="NA"
    )

    setpoint: Optional[Voltage] = Field(
        description="Value that the node must be set to. This is typically used for feeder head points",
        title="setpoint",
        cim_value="NA"
    )
