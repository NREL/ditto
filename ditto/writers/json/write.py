# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import os
import json_tricks
from datetime import datetime

from ditto.writers.abstract_writer import AbstractWriter
from ditto.models.position import Position
from ditto.models.base import Unicode
from ditto.models.wire import Wire
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.phase_load import PhaseLoad
from ditto.models.phase_capacitor import PhaseCapacitor


class Writer(AbstractWriter):
    """
    DiTTo--->JSON Writer class

    The writer produce a file with the following format:

    {"model": [object_1,object_2,...,object_N],
     "metadata": {"time": time,
                  ...
                  }
    }

    The actual DiTTo model is stored in "model" as a list of objects.
    Each object is a dictionary object_1={'class':'PowerTransformer',
                                          'is_substationr':{'class':'int',
                                                            'value':'1'
                                                            },
                                          (...)
                                         }
    The special key 'class' indicates the type of the object considered.
    class can be:
        - a DiTTo object type like 'PowerTransformer' or 'Winding'
        - a "standard" type like 'int', 'float', or 'str'
        - a list ('list')
        - a complex number: 1+2j will be {'class':'complex', 'value':[1,2]}

    .. note:: For nested objects, this format can become a bit complex. See example below

    **Example:**

    object_1={'class':'PowerTransformer',
              'is_substation':{'class':'int',
                               'value':'1'
                             },
              'windings':{'class':'list',
                          'value':[{'class':'Winding',
                                    'rated_power':{'class':'float',
                                                   'value':'1000'
                                                   }
                                    'phase_windings':{'class':'list',
                                                      'value':[{'class':'PhaseWinding',
                                                                'phase':{'class':'Unicode',
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

    Author: Nicolas Gensollen. January 2018.
    """
    register_names = ["json", "Json", "JSON"]

    def __init__(self, **kwargs):
        """Class CONSTRUCTOR"""
        if "output_path" in kwargs:
            self.output_path = kwargs["output_path"]
        else:
            self.output_path = "./"

        if "filename" in kwargs:
            self.filename = kwargs["filename"]
        else:
            self.filename = "Model.json"

    def write(self, model):
        """
        Write a given DiTTo model to a JSON file.
        The output file is configured in the constructor.
        """

        # Initialize json_dump
        json_dump = {"model": [], "metadata": {}}

        # Set timestamp in metadata
        json_dump["metadata"]["time"] = str(datetime.now())

        # Set the size of the model in metadata
        json_dump["metadata"]["model_size"] = len(model.models)

        for obj in model.models:
            _class = type(obj).__name__
            if _class in [
                Winding,
                PhaseWinding,
                Wire,
                PhaseCapacitor,
                Position,
                PhaseLoad,
            ]:
                continue
            json_dump["model"].append({})
            json_dump["model"][-1]["class"] = _class

            try:
                json_dump["model"][-1]["name"] = {"class": "str", "value": obj.name}
            except:
                json_dump["model"][-1]["name"] = {"class": "str", "value": None}
                pass

            for key, value in obj._trait_values.items():
                if key in ["capacitance_matrix", "impedance_matrix", "reactances"]:
                    json_dump["model"][-1][key] = {"class": "list", "value": []}
                    for v in value:
                        if isinstance(v, complex):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "complex", "value": [v.real, v.imag]}
                            )
                        elif isinstance(v, list):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "list", "value": []}
                            )
                            for vv in v:
                                if isinstance(vv, complex):
                                    json_dump["model"][-1][key]["value"][-1][
                                        "value"
                                    ].append(
                                        {
                                            "class": "complex",
                                            "value": [vv.real, vv.imag],
                                        }
                                    )
                                else:
                                    json_dump["model"][-1][key]["value"][-1][
                                        "value"
                                    ].append(
                                        {
                                            "class": str(type(vv)).split("'")[1],
                                            "value": vv,
                                        }
                                    )
                        else:
                            json_dump["model"][-1][key]["value"].append(
                                {"class": str(type(v)).split("'")[1], "value": v}
                            )
                    continue
                if isinstance(value, list):
                    json_dump["model"][-1][key] = {"class": "list", "value": []}
                    for v in value:

                        if isinstance(v, complex):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "complex", "value": [v.real, v.imag]}
                            )

                        elif isinstance(v, Position):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "Position"}
                            )
                            for kkk, vvv in v._trait_values.items():
                                json_dump["model"][-1][key]["value"][-1][kkk] = {
                                    "class": str(type(vvv)).split("'")[1],
                                    "value": vvv,
                                }

                        elif isinstance(v, Unicode):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "Unicode", "value": v.default_value}
                            )

                        elif isinstance(v, Wire):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "Wire"}
                            )
                            for kkk, vvv in v._trait_values.items():
                                json_dump["model"][-1][key]["value"][-1][kkk] = {
                                    "class": str(type(vvv)).split("'")[1],
                                    "value": vvv,
                                }

                        elif isinstance(v, PhaseCapacitor):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "PhaseCapacitor"}
                            )
                            for kkk, vvv in v._trait_values.items():
                                json_dump["model"][-1][key]["value"][-1][kkk] = {
                                    "class": str(type(vvv)).split("'")[1],
                                    "value": vvv,
                                }

                        elif isinstance(v, Winding):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "Winding"}
                            )
                            for kkk, vvv in v._trait_values.items():
                                if kkk != "phase_windings":
                                    json_dump["model"][-1][key]["value"][-1][kkk] = {
                                        "class": str(type(vvv)).split("'")[1],
                                        "value": vvv,
                                    }
                            json_dump["model"][-1][key]["value"][-1][
                                "phase_windings"
                            ] = {"class": "list", "value": []}
                            for phw in v.phase_windings:
                                json_dump["model"][-1][key]["value"][-1][
                                    "phase_windings"
                                ]["value"].append({"class": "PhaseWinding"})
                                for kkkk, vvvv in phw._trait_values.items():
                                    json_dump["model"][-1][key]["value"][-1][
                                        "phase_windings"
                                    ]["value"][-1][kkkk] = {
                                        "class": str(type(vvvv)).split("'")[1],
                                        "value": vvvv,
                                    }

                        elif isinstance(v, PhaseLoad):
                            json_dump["model"][-1][key]["value"].append(
                                {"class": "PhaseLoad"}
                            )
                            for kkk, vvv in v._trait_values.items():
                                json_dump["model"][-1][key]["value"][-1][kkk] = {
                                    "class": str(type(vvv)).split("'")[1],
                                    "value": vvv,
                                }

                    continue

                if isinstance(value, complex):
                    json_dump["model"][-1][key] = {
                        "class": "complex",
                        "value": [value.real, value.imag],
                    }
                    continue

                json_dump["model"][-1][key] = {
                    "class": str(type(value)).split("'")[1],
                    "value": value,
                }

        with open(os.path.join(self.output_path, self.filename), "w") as f:
            f.write(
                json_tricks.dumps(json_dump, allow_nan=True, sort_keys=True, indent=4)
            )
