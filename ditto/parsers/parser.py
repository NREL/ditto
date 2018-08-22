# coding: utf8

from pint import UnitRegistry

ureg = UnitRegistry()


class Parser:
    """
    Parser class.
    All specific parsers inherit from this class.
    Provides the general methods used by all parsers.

    author: Nicolas Gensollen.
    """

    def __init__(self, name, inference=False):
        """
        Parser class constructor.
        **Inputs:**
            - name: Name of the Parser.
            - inference: Flag to activate missing parameters inference. Default=False.
        """
        self.name = name
        self.inference = inference

    def set_property(self, property_name, property_value):
        """
        This function sets the property to the given value.
        TODO: Add safety checks here...
        """
        if not hasattr(self, property_name):
            raise AttributeError(
                "{name} has no attribute {att}.".format(
                    name=self.name, att=property_name
                )
            )
        if getattr(self, property_name) is not None and type(
            getattr(self, property_name)
        ) != type(property_value):
            raise ValueError(
                "Property {p} of {name} should be a {t1}. A {t2} was received.".format(
                    p=property_name,
                    name=self.name,
                    t2=type(property_value),
                    t1=type(getattr(self, property_name)),
                )
            )
        setattr(self, property_name, property_value)

    def distance(self, pos1, pos2, unit):
        """
        Compute the Euclidean distance between two positions.
        **Inputs:**
            - pos1: Tuple (x,y) of coordinates. Must be Pint objects. The unit is then included in the object.
            - pos2: Same as pos1 but for the second position.
            - unit: The unit length the distance should be in. Must be Pint-parsable. Ex: "ft", "mi", "m"...
        **Returns:**
            - distance: Euclidean distance between pos1 and pos2 in specified unit.
        """
        return (
            ((pos2[0] - pos1[0]) ** (2.0) + (pos2[1] - pos1[1]) ** (2.0)) ** (1.0 / 2.0)
        ).to(ureg.parse_expression(unit))
