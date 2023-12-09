# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from pydantic import BaseModel, Field

from .base import DiTToBaseModel
from .units import Voltage, Phase, Distance
from .position import Position
from typing_extensions import Annotated
from typing import Optional, List


class Node(DiTToBaseModel):
    
    nominal_voltage: Annotated[Optional[Voltage], Field( 
        description = "The nominal voltage at the node",
        title = "Nominal voltage",
        default = None,
        json_schema_extra = {"cim_value":"nomU"}
    )]

    phases: Annotated[Optional[List[Phase]], Field( 
        description="Phases at the node",
        title="phases",
        default = [],
        json_schema_extra = {"cim_value":"phases"}
    )]

    is_substation_connection: Annotated[Optional[bool], Field(
        description="1 if the node connects from inside a substation to outside, 0 otherwise. These indicate if a node connects a substation to a feeder or high voltage source",
        title="is_substation_connection",
        default=False,
        json_schema_extra = {"cim_value":"NA"}
    )]

    setpoint: Annotated[Optional[Voltage], Field(
        description="Value that the node must be set to. This is typically used for feeder head points",
        title="setpoint",
        default = None,
        json_schema_extra={"cim_value": "NA"},
    )]
