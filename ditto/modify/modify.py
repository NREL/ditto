from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging
import os
from ditto.models.base import (
    DiTToHasTraits,
    Float,
    Complex,
    Unicode,
    Any,
    Int,
    List,
    observe,
    Instance,
)

from ditto.models.timeseries import Timeseries

logger = logging.getLogger(__name__)


class Modifier:
    """Modifier class."""

    def delete_element(self, model, obj):
        """ Recursively delete an object from the model"""
        for attr in obj.traits():
            class_name = str(type(obj.traits()[attr])).strip("<>'").split(".")[-1]
            if class_name == "List":
                if (
                    getattr(obj, attr) is None
                    or getattr(obj, attr) is None
                    or len(getattr(obj, attr)) == 0
                    or attr == "reactances"
                    or attr == "phases"
                    or attr == "impedance_matrix"
                    or attr == "capacitance_matrix"
                ):  # Reactances (PowerTransformer) and phases (Node) are a special case of lists that aren't classes TODO: Add type checking rather than looking at the attributes
                    continue
                for element in getattr(obj, attr):
                    # logger.debug('attr',attr,element)
                    self.delete_element(model, element)
        model.remove_element(
            obj
        )  # TODO: Improve this so the data isn't stored in a list
        return model

    def copy(self, model, obj):
        """ Create a new object within the model"""
        new_obj = type(obj)(model)
        for attr in obj.traits():
            class_name = str(type(obj.traits()[attr])).strip("<>'").split(".")[-1]
            if class_name == "List":
                if (
                    getattr(obj, attr) is None
                    or len(getattr(obj, attr)) == 0
                    or attr == "reactances"
                    or attr == "phases"
                    or attr == "impedance_matrix"
                    or attr == "capacitance_matrix"
                ):  # Reactances (PowerTransformer) and phases (Node) are a special case of lists that aren't classes
                    new_attr = getattr(obj, attr)
                    setattr(new_obj, attr, new_attr)
                    continue
                for list_obj in getattr(obj, attr):
                    new_list_obj = self.copy(model, list_obj)
                    getattr(new_obj, attr).append(new_list_obj)

            else:
                new_attr = getattr(obj, attr)
                setattr(new_obj, attr, new_attr)
        return new_obj

    def set_attributes(self, model_1, obj_1, obj_2, overwrite=True):
        """
        For all the attributes in obj_1 and obj_2, set the non-list attributes in obj_1 to those from obj_2 when they aren't None. If overwrite=False, attributes in object_1 which aren't empty aren't overwritten.
        Precondition: obj_1 and obj_2 are of the same class
        """
        for (
            attr
        ) in (
            obj_2.traits()
        ):  # Iterate through all attributes in obj_2. These should be the same traits as obj_1 assuming the precondition
            class_name = str(type(obj_2.traits()[attr])).strip("<>'").split(".")[-1]
            # TODO: check for reactance tuples: str(obj_2.traits()[attr]._trait.klass).strip("<>'").split('.')[-1] != (Int,Int,Int):

            if class_name == "List":
                phase_order = {
                    "A": 0,
                    "B": 1,
                    "C": 2,
                    "N": 3,
                }  # Should only have to deal with 3 phases.
                #
                # BUG WARNING: The order of objects in the list is important and is used to determine the changes that are made
                # Try to ensure that phases are specified to avoid this problem
                # If number of elements in obj_1 is 0, all elements of obj_2 are added
                # If number of elements is the same, they are modified with a 1-1 comparison
                # If number of elements in obj_2 is < obj_1, set the first values of obj_1 as obj_2
                # If number of elements in obj_2 is > obj_1, set the all the values in obj_1 in the order they'r in obj_2 and append the extras
                # This will fail if obj_1 is (A, B, C) and obj_2 is (A, C), as it'll assign phase C to phase B.
                # This will also fail if obj_1 is (C) and obj_2 is (A,B,C) as C will have A assigned to it.
                # This will also fail if obj_1 is (A,B) and obj_2 is (A,C) as B will have C assigned to it.
                list_1 = getattr(obj_1, attr)
                list_2 = getattr(obj_2, attr)
                if list_1 is None or len(list_1) == 0:
                    result_list = []
                    for element in list_2:
                        result_list.append(self.copy(model_1, element))
                    setattr(obj_1, attr, result_list)
                    continue
                elif list_2 is None or len(list_2) == 0:
                    continue

                # Almost all Lists are of objects which have phases. Exceptions being windings, reactances and positions
                # Require the phases to be specified in both systems to modify based on phase
                has_phases = True
                for i in range(len(list_1)):
                    if not (
                        hasattr(list_1[0], "phase") and list_1[0].phase is not None
                    ):
                        has_phases = False
                for i in range(len(list_2)):
                    if not (
                        hasattr(list_2[0], "phase") and list_2[0].phase is not None
                    ):
                        has_phases = False
                if has_phases and len(list_1) > 0 and len(list_2) > 0:
                    # Firstly sort the lists so they're in correct order by phase.
                    list_1.sort(key=lambda x: phase_order[x.phase])
                    list_2.sort(key=lambda x: phase_order[x.phase])
                    list_1_phase = phase_order[list_1[0].phase]
                    list_2_phase = phase_order[list_2[0].phase]
                    list_1_idx = 0
                    list_2_idx = 0
                    while list_1_idx < len(list_1) and list_2_idx < len(list_2):
                        if list_1_idx < len(list_1):
                            list_1_phase = phase_order[list_1[list_1_idx].phase]
                        else:
                            list_1_phase = 1000000
                        if list_2_idx < len(list_2):
                            list_2_phase = phase_order[list_2[list_2_idx].phase]
                        else:
                            list_2_phase = 1000001

                        # i.e. recurse
                        if list_1_phase == list_2_phase:
                            self.set_attributes(
                                model_1,
                                list_1[list_1_idx],
                                list_2[list_2_idx],
                                overwrite,
                            )
                            list_1_idx = list_1_idx + 1
                            list_2_idx = list_2_idx + 1
                        elif list_1_phase < list_2_phase:
                            list_1_idx = (
                                list_1_idx + 1
                            )  # e.g. obj_1 = (A, B, C) and obj_2 = (B). We don't update this phase

                        else:
                            getattr(obj_1, attr).append(list_2[list_2_idx])
                            list_2_idx = list_2_idx + 1

                elif len(list_1) == len(list_2):
                    for i in range(len(list_1)):
                        self.set_attributes(model_1, list_1[i], list_2[i], overwrite)

                elif len(list_1) > len(list_2):
                    for i in range(len(list_2)):
                        self.set_attributes(model_1, list_1[i], list_2[i], overwrite)

                else:  # i.e. len(list_1) < len(list_2):
                    for i in range(len(list_2)):
                        if i < len(list_1):
                            self.set_attributes(
                                model_1, list_1[i], list_2[i], overwrite
                            )
                        else:
                            getattr(obj_1, attr).append(list_2[i])

            else:
                value = getattr(obj_2, attr)
                if value is not None:
                    if getattr(obj_1, attr) is not None and overwrite == False:
                        continue
                    setattr(obj_1, attr, value)

    def merge(self, model_1, model_2, overwrite=True):
        """
        Find all the objects in model_1 with the same name as model_2 and augment them with the attributes with those from model_2 which have been set (are not None). If overwrite is True, any existing attributes are overwritten, otherwise they are skipped
        """
        model_1.set_names()
        model_2.set_names()
        for (
            obj_name
        ) in (
            model_2.model_names
        ):  # Iterate through all objects in model_2 which have a name
            if (
                obj_name in model_1.model_names
            ):  # Find the corresponding object in model_1
                if type(model_1.model_names[obj_name]) != type(
                    model_2.model_names[obj_name]
                ):
                    logger.debug(
                        type(model_1.model_names[obj_name]),
                        type(model_2.model_names[obj_name]),
                    )
                    logger.debug(obj_name)
                    raise Exception(
                        "Object types do not match for models with the same object names"
                    )

                obj_2 = model_2.model_names[obj_name]
                obj_1 = model_1.model_names[obj_name]
                self.set_attributes(model_1, obj_1, obj_2, overwrite)

        model_1.set_names()
        return model_1

    def add(self, model_1, model_2):
        """
        Add all the named objects in model_2 are added to model_1
        """
        model_1.set_names()
        model_2.set_names()
        for obj_name in model_2.model_names:
            new_obj = self.copy(model_1, model_2.model_names[obj_name])

        model_1.set_names()
        return model_1

    def delete(self, model_1, model_2):
        """
        Delete the named objects in model_2 (and their sub-objects) from model_1.
        NOTE that this only uses the names of the nodes to do the deletion
        """
        model_1.set_names()
        model_2.set_names()
        for obj_name in model_2.model_names:
            if (
                obj_name in model_1.model_names
            ):  # Find the corresponding object in model_1
                if type(model_1.model_names[obj_name]) != type(
                    model_2.model_names[obj_name]
                ):
                    raise Exception(
                        "Object types do not match for models with the same object names"
                    )

                obj_1 = model_1.model_names[obj_name]
                self.delete_element(
                    model_1, obj_1
                )  # model_1 updated automatically since passing by reference
        model_1.set_names()
        return model_1
