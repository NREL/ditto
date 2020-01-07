# -*- coding: utf-8 -*-

"""
test_JSON
----------------------------------

Tests for JSON parsers.
"""
import os
import six
import pytest as pt
from ditto.store import Store

if six.PY2:
    from backports import tempfile
else:
    import tempfile

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_opendss_to_json():
    """Test the JSON writer with OpenDSS models as input."""
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.json.write import Writer

    opendss_models = [
        f
        for f in os.listdir(
            os.path.join(current_directory, "data/small_cases/opendss/")
        )
        if not f.startswith(".")
    ]
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(
                current_directory,
                "data/small_cases/opendss/{model}/master.dss".format(model=model),
            ),
            buscoordinates_file=os.path.join(
                current_directory,
                "data/small_cases/opendss/{model}/buscoord.dss".format(model=model),
            ),
        )
        r.parse(m)
        m.set_names()
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=output_path.name)
        w.write(m)


def test_cyme_to_json():
    """Test the JSON writer with CYME models as input."""
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store
    from ditto.writers.json.write import Writer

    cyme_models = [
        f
        for f in os.listdir(os.path.join(current_directory, "data/small_cases/cyme/"))
        if not f.startswith(".")
    ]
    for model in cyme_models:
        m = Store()
        r = Reader(
            data_folder_path=os.path.join(
                current_directory, "data/small_cases/cyme", model
            )
        )
        r.parse(m)
        m.set_names()
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=output_path.name)
        w.write(m)


def test_json_reader():
    """Test the JSON reader."""
    # TODO
    pass


def test_json_serialize_deserialize():
    """Write a model to JSON, read it back in, and test that both models match."""
    from ditto.readers.opendss.read import Reader
    from ditto.store import Store
    from ditto.writers.json.write import Writer
    from ditto.readers.json.read import Reader as json_reader

    opendss_models = [
        f
        for f in os.listdir(
            os.path.join(current_directory, "data/small_cases/opendss/")
        )
        if not f.startswith(".")
    ]
    opendss_models.remove("storage_test")
    for model in opendss_models:
        m = Store()
        r = Reader(
            master_file=os.path.join(
                current_directory,
                "data/small_cases/opendss/{model}/master.dss".format(model=model),
            ),
            buscoordinates_file=os.path.join(
                current_directory,
                "data/small_cases/opendss/{model}/buscoord.dss".format(model=model),
            ),
        )
        r.parse(m)
        m.set_names()
        w = Writer(output_path="./")
        w.write(m)
        jr = json_reader(input_file="./Model.json")
        jr.parse(m)
        jr.model.set_names()

        for obj in m.models:
            if hasattr(obj, "name"):
                json_obj = jr.model[obj.name]
                assert compare(obj, json_obj)

        for json_obj in jr.model.models:
            if hasattr(json_obj, "name"):
                obj = m[json_obj.name]
                assert compare(json_obj, obj)

        os.remove("./Model.json")


def compare(obj1, obj2):
    """
        Compare 2 objects.
        Return True if they are equal and False otherwise.
        This code is really ugly, more elegant way to do that??
    """

    try:
        attributes_1 = sorted([x for x in obj1.class_trait_names()])
        attributes_2 = sorted([x for x in obj2.class_trait_names()])
    except:
        try:
            return obj1.default_value == obj2.default_value
        except:
            return obj1 == obj2

    # If the 2 objets do not have the same traits, return False
    if attributes_1 != attributes_2:
        return False

    # For each attribute...
    for attribute in attributes_1:

        # Handle the case where the attribute is a list (ex: PowerTransformer.windings)
        if isinstance(getattr(obj1, attribute), list):

            # The attribute for the other object should also be a list...
            if isinstance(getattr(obj2, attribute), list):

                # ...and the length should match
                if len(getattr(obj1, attribute)) != len(getattr(obj2, attribute)):
                    return False
                else:
                    # For every element of the list, call compare recursively
                    for x, y in zip(getattr(obj1, attribute), getattr(obj2, attribute)):
                        return compare(x, y)
            else:
                return False

        # Just make sure we are not missing the case where the attribute is not a list for obj1
        # but IS a list for obj2...
        elif isinstance(getattr(obj2, attribute), list):
            if isinstance(getattr(obj1, attribute), list):
                pass
            else:
                if len(getattr(obj1, attribute)) != len(getattr(obj2, attribute)):
                    return False
                else:
                    for x, y in zip(getattr(obj1, attribute), getattr(obj2, attribute)):
                        return compare(x, y)

        # If not a list, then test the equality
        else:
            if getattr(obj1, attribute) != getattr(obj2, attribute):
                return False
    return True
