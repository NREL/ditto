
import os

import pytest

from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.position import Position
from ditto.readers.opendss.read import Reader
from ditto.store import Store, DuplicateNameError, ElementNotFoundError, \
    InvalidElementType


MASTER = "tests/data/small_cases/opendss/ieee_4node/master.dss"
BUS_COORDS = "tests/data/small_cases/opendss/ieee_13node/buscoord.dss"


def test_store():
    model = Store()
    r = Reader(master_file=MASTER, buscoordinates_file=BUS_COORDS)
    r.parse(model)

    # Test list/iteration variations.
    lines = model.list_elements(Line)
    assert len(lines) == 2
    assert isinstance(lines[0], Line)
    line = lines[0]
    name = line.name

    found = False
    for ln in model.iter_elements(Line, lambda x: x.name == name):
        assert ln.name == name

    elements = model.list_elements()
    # There should be more than just lines.
    assert len(elements) > 2

    # Test forms of get.
    assert model.get_element(Line, name) is line
    assert model[name] is line

    with pytest.raises(DuplicateNameError):
        model.add_element(line)

    with pytest.raises(InvalidElementType):
        model.add_element("invalid")

    # Position doesn't have a name.
    with pytest.raises(InvalidElementType):
        model.add_element(Position())

    # Add a Load with the same name.
    load = Load()
    load.name = name
    model.add_element(load)
    with pytest.raises(DuplicateNameError):
        model[name]

    # Call get with missing element type
    for load in model.list_elements(Load):
        model.remove_element(load)
    assert not model.list_elements(Load)
    with pytest.raises(ElementNotFoundError):
        model.get_element(Load, name)

    model.remove_element(line)
    with pytest.raises(ElementNotFoundError):
        model.get_element(Line, name)
    with pytest.raises(ElementNotFoundError):
        model[name]

    # Test forms of set.
    model.add_element(line)
    assert model.get_element(Line, name) is line
    model.remove_element(line)
    model[name] = line
    assert model.get_element(Line, name) is line

    # Test clear.
    model.clear_elements()
    assert not model.list_elements()
