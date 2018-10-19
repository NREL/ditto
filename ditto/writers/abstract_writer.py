# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
import sys
import logging
from six import string_types

LOGGER = logging.getLogger(__name__)


class AbstractWriter(object):
    """Abstract class for DiTTo writers.
    author: Nicolas Gensollen. October 2017.
    """

    register_names = []

    def __init__(self, **kwargs):
        """Abstract class CONSTRUCTOR."""

        # create logger
        self.logger = LOGGER

        self.output_path = kwargs.get("output_path", "./")

        if "log_file" in kwargs:
            # log_file = kwargs["log_file"]
            self.logger.warning(
                "Log file currently not supported, please contact the developers for information on how to generate log files"
            )

    @classmethod
    def register(cls, registration_dict):
        for name in cls.register_names:
            registration_dict[name] = cls

    # @abstractmethod
    def write(self, model, **kwargs):
        """Write abstract method.
        .. note:: To be implemented in subclasses.
        """
        pass

    def convert_from_meters(self, quantity, unit, **kwargs):
        """Converts a distance in meters to a distance in given unit.

        :param quantity: Distance in meter to convert
        :type quantity: float
        :param unit: The unit to convert to
        :type unit: str (see below the units supported)
        :param inverse: Use inverse ration (see below)
        :type inverse: bool
        :returns: The distance in the requested unit
        :rtype: float

        **Units supported:**

        The units supported are the OpenDSS available units:

                - miles ('mi')
                - kilometers ('km')
                - kilofeet ('kft')
                - meters ('m')
                - feet ('ft')
                - inches ('in')
                - centimeters ('cm')


        **Ratios:**

        The ratios used are the ones provided by Google. The following table summerize the multipliers to obtain the unit:

        +--------+------------+
        |  Unit  | Multiplier |
        +========+============+
        |   mi   | 0.000621371|
        +--------+------------+
        |   km   |    0.001   |
        +--------+------------+
        |   kft  | 0.00328084 |
        +--------+------------+
        |    m   |     1      |
        +--------+------------+
        |   ft   |   3.28084  |
        +--------+------------+
        |   in   |   39.3701  |
        +--------+------------+
        |   cm   |     100    |
        +--------+------------+

        .. note:: If the unit is not one of these, the function returns None

        .. warning:: This function is a duplicate (also exists for the OpenDSS reader). Reproduce here for convenience.

        .. seealso:: convert_to_meters, unit_conversion

        """
        if "inverse" in kwargs and isinstance(kwargs["inverse"], bool):
            inverse = kwargs["inverse"]
        else:
            inverse = False

        if unit is None:
            return None

        if not isinstance(unit, string_types):
            self.logger.warning("convert_from_meters() expects a unit in string format")
            return None

        if quantity is None:
            return None

        if unit.lower() == "mi":
            if inverse:
                return quantity / 0.000621371
            else:
                return 0.000621371 * quantity

        elif unit.lower() == "km":
            if inverse:
                return quantity / 10 ** -3
            else:
                return 10 ** -3 * quantity

        elif unit.lower() == "kft":
            if inverse:
                return quantity / 0.00328084
            else:
                return 0.00328084 * quantity

        elif unit.lower() == "m":
            return quantity

        elif unit.lower() == "ft":
            if inverse:
                return quantity / 3.28084
            else:
                return 3.28084 * quantity

        elif unit.lower() == "in":
            if inverse:
                return quantity / 39.3701
            else:
                return 39.3701 * quantity

        elif unit.lower() == "cm":
            if inverse:
                return quantity / 100
            else:
                return 100 * quantity

        else:
            return None
