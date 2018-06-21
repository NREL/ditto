# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import json

from ditto.readers.abstract_reader import AbstractReader
from ditto.store import Store
from ditto.models.power_source import PowerSource
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.winding import Winding
from ditto.models.powertransformer import PowerTransformer
from ditto.models.regulator import Regulator
from ditto.models.position import Position
from ditto.models.wire import Wire
from ditto.models.phase_winding import PhaseWinding
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.capacitor import Capacitor
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.base import Unicode
from ditto.models.feeder_metadata import Feeder_metadata


class Reader(AbstractReader):
    """JSON-->DiTTo Reader class

    The reader expects the following format:

        - objects are stored in a list [object_1,object_2,...,object_N]
        - Each object is a dictionary object_1={'klass':'PowerTransformer',
                                                'is_substationr':{'klass':'int',
                                                                  'value':'1'
                                                                 },
                                                (...)
                                                }
        - The special key 'klass' indicates the type of the object considered.
        - klass can be:
                - a DiTTo object type like 'PowerTransformer' or 'Winding'
                - a "standard" type like 'int', 'float', or 'str'
                - a list ('list')
                - a complex number: 1+2j will be {'klass':'complex', 'value':[1,2]}

    .. note:: For nested objects, this format can become a bit complex. See example below

    **Example:**

    object_1={'klass':'PowerTransformer',
              'is_substation':{'klass':'int',
                               'value':'1'
                             },
              'windings':{'klass':'list',
                          'value':[{'klass':'Winding',
                                    'rated_power':{'klass':'float',
                                                   'value':'1000'
                                                   }
                                    'phase_windings':{'klass':'list',
                                                      'value':[{'klass':'PhaseWinding',
                                                                'phase':{'klass':'Unicode',
                                                                         'value':'C'
                                                                         },
                                                                (...)
                                                                },
                                                                (...)
                                                                ]
                                                    }
                                    (...)
                                    },
                                    (...)
                                  ]
                          },
                }

    .. TODO:: Better format?

    Author: Nicolas Gensollen. January 2018
    """
    register_names = ["json", "Json", "JSON"]

    def __init__(self, **kwargs):
        """Class CONSTRUCTOR"""
        if "input_file" in kwargs:
            self.input_file = kwargs["input_file"]
        else:
            raise ValueError("No input file provided to the reader.")

    def parse(self):
        """Parse a JSON file to a DiTTo model."""
        # Open the input file and get the data
        with open(self.input_file, "r") as f:
            input_data = json.load(f)

        ditto_klasses = [
            "PowerSource",
            "Node",
            "Line",
            "Winding",
            "PowerTransformer",
            "Position",
            "Wire",
            "PhaseWinding",
            "Load",
            "PhaseLoad",
            "Capacitor",
            "PhaseCapacitor",
            "Feeder_metadata",
            "Regulator",
        ]

        # Create a new empty model
        self.model = Store()

        # Loop over the objects...
        for _object in input_data:

            # Get the class of the element
            _klass = _object["klass"]

            # If it is a second level or third level class, ignore the object
            # These objects will be created when handling the first level object
            # Ex: When creating a PowerTransformer, corresponding Windings and
            # PhaseWindings will be created
            if _klass in [
                "Winding",
                "PhaseWinding",
                "Wire",
                "PhaseCapacitor",
                "Position",
                "PhaseLoad",
            ]:
                continue

            # Use the klass to instantiate the proper DiTTo object
            # Ex: PowerTransformer
            api_object = eval(_object["klass"])(self.model)

            # Loop over the object properties.
            # Ex: name, postion...
            for object_property, property_value in _object.items():

                if object_property != "klass":

                    # Get the type of the property
                    property_type = property_value["klass"]

                    # Depending on this type, there are a few different scenarios...
                    # First, if it is a list...
                    # Ex: list of windings
                    if property_type == "list":

                        # Create the list for this property
                        list_first_level = []

                        # Loop over the element in the list
                        # Ex: element will be a dict {'klass':Winding, 'rated_power':{'klass':'float','value':10},...}
                        for element in property_value["value"]:

                            # Get the type of each element
                            # Ex: Winding
                            element_type = element["klass"]

                            # Again, there are multiple possibilities
                            # First, it could be a DiTTo object.
                            # Ex: Winding
                            if element_type in ditto_klasses:

                                # Instanciate the proper DiTTo object
                                # Ex: Winding
                                api_object_one_level_deep = eval(element_type)(
                                    self.model
                                )

                                # Loop over the winding properties
                                # Ex: rated_power...
                                for element_property, element_value in element.items():

                                    if element_property != "klass":

                                        # Get the type of the property
                                        # Ex: float
                                        nested_element_type = element_value["klass"]

                                        # If it is a list...
                                        if nested_element_type == "list":

                                            # Create empty list to store the elements
                                            list_second_level = []

                                            # Loop over the elements...
                                            for element_deep in element_value["value"]:

                                                # Get the class
                                                element_deep_class = element_deep[
                                                    "klass"
                                                ]

                                                # If it is a DiTTo object
                                                if element_deep_class in ditto_klasses:

                                                    # Create the proper object
                                                    api_object_two_level_deep = eval(
                                                        element_deep_class
                                                    )(self.model)

                                                    # Amd loop over its attributes
                                                    for (
                                                        nested_object_property,
                                                        nested_object_property_value,
                                                    ) in element_deep.items():

                                                        if (
                                                            nested_object_property
                                                            != "klass"
                                                        ):

                                                            # At this point, it should be either a complex...
                                                            if (
                                                                nested_object_property_value[
                                                                    "klass"
                                                                ]
                                                                == "complex"
                                                            ):

                                                                setattr(
                                                                    api_object_two_level_deep,
                                                                    nested_object_property,
                                                                    complex(
                                                                        nested_object_property_value[
                                                                            "value"
                                                                        ][
                                                                            0
                                                                        ],
                                                                        nested_object_property_value[
                                                                            "value"
                                                                        ][
                                                                            1
                                                                        ],
                                                                    ),
                                                                )

                                                            # ...or a standard type
                                                            elif (
                                                                nested_object_property_value[
                                                                    "klass"
                                                                ]
                                                                != "NoneType"
                                                            ):

                                                                setattr(
                                                                    api_object_two_level_deep,
                                                                    nested_object_property,
                                                                    eval(
                                                                        nested_object_property_value[
                                                                            "klass"
                                                                        ]
                                                                    )(
                                                                        nested_object_property_value[
                                                                            "value"
                                                                        ]
                                                                    ),
                                                                )

                                                    # Add the DiTTo object to the list
                                                    list_second_level.append(
                                                        api_object_two_level_deep
                                                    )

                                                # if it is a complex number, cast and add to the list
                                                elif element_deep_class == "complex":

                                                    list_second_level.append(
                                                        complex(
                                                            element_deep["value"][0],
                                                            element_deep["value"][1],
                                                        )
                                                    )

                                                # If it is a standard type, cast and add to the list
                                                elif element_deep_class != "NoneType":

                                                    list_second_level.append(
                                                        eval(element_deep_class)(
                                                            element_deep["value"]
                                                        )
                                                    )

                                            # Set the object attribute with the list we just built
                                            setattr(
                                                api_object_one_level_deep,
                                                element_property,
                                                list_second_level,
                                            )

                                        # Or, it could be a complex number
                                        elif nested_element_type == "complex":

                                            setattr(
                                                api_object_one_level_deep,
                                                element_property,
                                                complex(
                                                    element_value["value"][0],
                                                    element_value["value"][1],
                                                ),
                                            )

                                        # Or, None or standard types
                                        elif nested_element_type != "NoneType":

                                            setattr(
                                                api_object_one_level_deep,
                                                element_property,
                                                eval(nested_element_type)(
                                                    element_value["value"]
                                                ),
                                            )

                                # Append the DiTTo object to the first level list
                                list_first_level.append(api_object_one_level_deep)

                            # If it is a list, this should be a matrix stored as a list of lists
                            elif element_type == "list":

                                # Create an empty inner list
                                inner_list = []

                                # Loop over the elements
                                for element_deep in element["value"]:

                                    # They could be complex numbers
                                    if element_deep["klass"] == "complex":

                                        inner_list.append(
                                            complex(
                                                element_deep["value"][0],
                                                element_deep["value"][1],
                                            )
                                        )

                                    # Or standard numbers (int or float)
                                    elif element_deep["klass"] != "NoneType":

                                        inner_list.append(
                                            eval(element_deep["klass"])(
                                                element_deep["value"]
                                            )
                                        )

                                # Add the row to the matrix
                                list_first_level.append(inner_list)

                            # Or, it could be a complex number (handled in a list format)
                            elif element_type == "complex":

                                list_first_level.append(
                                    complex(element["value"][0], element["value"][1])
                                )

                            # Otherwise, it is either None or a standard type
                            elif element_type != "NoneType":

                                list_first_level.append(
                                    eval(element_type)(element["value"])
                                )

                        # Finally, set the attribute
                        setattr(api_object, object_property, list_first_level)

                    # Otherwise, if it is a complex number,
                    # the representation used is a list [nb.real,nb.imag]
                    elif property_type == "complex":

                        setattr(
                            api_object,
                            object_property,
                            complex(
                                property_value["value"][0], property_value["value"][1]
                            ),
                        )

                    # If it is None, there is nothing to do
                    # Otherwise, it is a standard type like int, float, str...
                    elif property_type != "NoneType":

                        setattr(
                            api_object,
                            object_property,
                            eval(property_type)(property_value["value"]),
                        )
