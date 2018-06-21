""" Read CSV file into raw ditto form. The rows represent different DiTTo equipment objects. Each column is the attribute that is being added. The column headers are delimited by colons. e.g. For the Var value of a capacitor on phase A, the column would be "Capacitor.phase_capacitors[0].var". This specifies the value of the var attribute of a PhaseCapacitor value of a capacitor.

Empty cells are left as None
"""

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging
import math
import sys
import os
import json

import numpy as np
import pandas as pd

from ditto.store import Store
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.timeseries import Timeseries
from ditto.models.position import Position

from ditto.formats.gridlabd import gridlabd
from ditto.formats.gridlabd import base
from ditto.models.base import Unicode

logger = logging.getLogger(__name__)


class reader:
    class_list = set(
        [
            "Node",
            "Line",
            "Capacitor",
            "Load",
            "PhaseLoad",
            "Regulator",
            "Wire",
            "PhaseCapacitor",
            "PowerTransformer",
            "Winding",
            "PhaseWinding",
            "Position",
        ]
    )

    def parse(self, model, input_file):
        dataframe = pd.read_csv(input_file)
        for row_idx in range(dataframe.shape[0]):
            if row_idx % 100 == 0:
                logger.debug(row_idx)
            # TODO add tracking for each column so that we don't have different objects being created for the same thing (which is what's happening now)
            # Iterate through all the columns first to build the required data structure to store the info. Each row should be completely different though

            all_objs = {}  # Create a new set of objects for each row of the csv file
            for column in dataframe.columns:
                layers = column.split(".")
                if len(layers) < 2:
                    raise Exception(
                        "At least two period delimited names are required to specify an object and attribute"
                    )

                if dataframe.iloc[row_idx][column] == "" or (
                    isinstance(dataframe.iloc[row_idx][column], float)
                    and math.isnan(dataframe.iloc[row_idx][column])
                ):  # Entries with empty attributes aren't created
                    continue

                if layers[0] not in all_objs:
                    base_obj = globals()[layers[0]](model)
                    all_objs[layers[0]] = base_obj
                parent_obj = all_objs[
                    layers[0]
                ]  # We recursively update the parent object for each subelement
                for i in range(
                    1, len(layers) - 1
                ):  # i.e. all the object lists that need to be called
                    layer_name = layers[i].split("[")[0]  # subclass element name
                    layer_number = int(
                        layers[i].split("[")[1].strip("]")
                    )  # subclass element index.
                    klass = parent_obj.traits()[
                        layer_name
                    ]._trait.klass  # find the objects that the list contains
                    klassname = (
                        str(klass).strip("<>'").split(".")[-1]
                    )  # Get the name of the class from the klass string

                    full_name = ".".join(
                        layers[: i + 1]
                    )  # Make the lookup identifier include all the parents of the elemtn
                    if full_name not in all_objs:
                        if (
                            getattr(parent_obj, layer_name) is None
                        ):  # If the list hasn't already been created, add an empty list
                            setattr(parent_obj, layer_name, [])
                        for j in range(layer_number + 1):
                            earlier_element = (
                                ".".join(layers[:i])
                                + "."
                                + layer_name
                                + "["
                                + str(j)
                                + "]"
                            )  # The name used to lookup objects in the all_objs dictionary includes the index
                            if (
                                earlier_element in all_objs
                            ):  # This elment has already been created and added to the list
                                continue

                            nxt_obj = globals()[klassname](
                                model
                            )  # Create the object to be added to the array
                            getattr(parent_obj, layer_name).append(
                                nxt_obj
                            )  # Add the element to the list which it belongs to
                            all_objs[earlier_element] = nxt_obj

                    parent_obj = all_objs[full_name]

                if layers[-1] == "name":
                    setattr(
                        parent_obj, layers[-1], dataframe.iloc[row_idx][column].lower()
                    )  # The attribute is always the last element of layers
                else:
                    setattr(
                        parent_obj, layers[-1], dataframe.iloc[row_idx][column]
                    )  # The attribute is always the last element of layers

        model.set_names()
