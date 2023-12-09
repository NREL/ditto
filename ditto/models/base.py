# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from typing_extensions import Annotated
from typing import Optional, List

import warnings
import logging

from .units import Voltage, Phase

logger = logging.getLogger(__name__)


class DiTToBaseModel(BaseModel):
    """ Base pydantic class for all DiTTo models.
        A name is required for all DiTTo models.
    """

    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        use_enum_values = False,
        arbitrary_types_allowed = True,
        populate_by_name = True
    )

    name: Annotated[str,Field(
        description="Name of the element in the DiTTo model",
        title="name",
        json_schema_extra = {"cim_value":"name"}
    )]

    substation_name: Annotated[Optional[str], Field(
        description="Name of the substation the element is under",
        title="substation_name",
        default = "",
        json_schema_extra = {"cim_value":"EquipmentContainer.Substation.name"}
    )]

    feeder_name: Annotated[Optional[str],Field(
        description="Name of the feeder the element is on",
        title="feeder_name",
        default = "",
        json_schema_extra = {"cim_value":"EquipmentContainer.name"}
    )]
            
