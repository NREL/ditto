# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from pydantic import BaseModel, Field, ValidationError
from pydantic.json import isoformat, timedelta_isoformat

import warnings
import logging

logger = logging.getLogger(__name__)

class Voltage(BaseModel):
    """This class is used to represent the voltage at a node or a line. It is a simple container for the voltage value and the unit.
    """
    value: float = Field(
        title="value",
        description="The value of the voltage",
    )
    unit: VoltageUnit = Field(
        description="The unit of the voltage",
        title="unit",
        default="V",
    )

class VoltageUnit(str, Enum):
    """This class is used to represent the possible units of voltage.
    """
    V = "V"
    kV = "kV"
    MV = "MV"


class Phase(str, Enum):
    """This class is used to represent a single phase from a set of possible values.
    """
    A = "A"
    B = "B"
    C = "C"
    N = "N"
    s1 = "s1"
    s2 = "s2"
