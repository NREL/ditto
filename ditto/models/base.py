# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from pydantic import BaseModel, Field, ValidationError
from pydantic.json import isoformat, timedelta_isoformat

import warnings
import logging

from .units import Voltage, VoltageUnit, Phase
from .position import Position

logger = logging.getLogger(__name__)


class DiTToBaseModel(BaseModel):
    """ Base pydantic class for all DiTTo models.
        A name is required for all DiTTo models.
    """

    class Config:
        """ Base pydantic configuration for all DiTTo models.
        """
        title = "DiTToBaseModel"
        validate_assignment = True
        validate_all = True
        extra = "forbid"
        use_enum_values = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    name: str = Field(
        description="Name of the element in the DiTTo model",
        title="name",
        cim_value="name"
    )

    substation_name: Optional[str] = Field(
        description="Name of the substation the element is under",
        title="substation_name"
        cim_value="EquipmentContainer.Substation.name"
    )

    feeder_name: Optional[str] = Field(
        description="Name of the feeder the element is on",
        title="feeder_name"
        cim_value="EquipmentContainer.name"
    )
            
    positions: Optional[List[Position]] = Field(
        description="A list of positions of the element. For single point elements, this list should have a length of one. For lines, this list may contain intermediate points.",
        title="positions"
        cim_value="Location.PositionPoints"
    )
