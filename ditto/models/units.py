# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
import json

import warnings
import pint
import logging

logger = logging.getLogger(__name__)

#TODO: Make a general unit that things inherit from since we reuse this code a lot
class Distance(pint.Quantity):
    """This class is used to represent a distance value.
    """
    def __new__(cls, value, units, **kwargs):
        instance = super().__new__(cls, value, units, **kwargs)
        if not instance.is_compatible_with("meter"):
            raise ValueError(f"Distance must be compatible with meter, not {value.units}")
        return instance
    def json(self):
        return {"value":self.magnitude,"units":str(self.units)}

class Voltage(pint.Quantity):
    """This class is used to represent a voltage value.
       Must be constructued with a value and units.
    """
    def __new__(cls, value, units, **kwargs):
        instance = super().__new__(cls, value, units, **kwargs)
        if not instance.is_compatible_with("volt"):
            raise ValueError(f"Voltage must be compatible with volt, not {instance.units}")
        return instance
    def json(self):
        return {"value":self.magnitude,"units":str(self.units)}

class Phase(str, Enum):
    """This class is used to represent a single phase from a set of possible values.
    """
    A = "A"
    B = "B"
    C = "C"
    N = "N"
    s1 = "s1"
    s2 = "s2"
