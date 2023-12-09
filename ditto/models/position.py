from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from pydantic import BaseModel, Field
from .base import DiTToBaseModel
from .units import Voltage, Phase, Distance
import pint
import logging
from typing_extensions import Annotated
from typing import Optional, List

class Position(DiTToBaseModel):
    x_position: Annotated[float, Field(
        description="X coordinate with raw float. Projection is defined in the json_schema_extra. Default is longitude value",
        title="x_position",
        alias="long",
        json_schema_extra = {"cim_value":"Location.PositionPoint.xPosition", "projection": "longitude"}
    )]
    y_position: Annotated[float, Field(
        description="Y coordinate with raw float. Projection is defined in the json_schema_extra. Default is latitude value",
        title="y_position",
        alias="lat",
        json_schema_extra = {"cim_value":"Location.PositionPoint.yPosition", "projection": "latitude"}
    )]
    z_position: Annotated[Optional[Distance], Field(
        description="Z coordinate in distance units. Default is meters",
        title="z_position",
        alias="elevation",
        default = Distance(0,"m"),
        json_schema_extra = {"cim_value":"Location.PositionPoint.zPosition"} 
    )]


    def build(self, model):
        self._model = model
