
import os

import pytest

from ditto.models.line import Line
from ditto.models.position import Position
from ditto.readers.opendss.read import Reader
from ditto.store import Store, DuplicateNameError, ElementNotFoundError, \
    InvalidElementType


MASTER = "tests/data/small_cases/opendss/ieee_4node/master.dss"
BUS_COORDS = "tests/data/small_cases/opendss/ieee_13node/buscoord.dss"


def test_store():
    m = Store()
    r = Reader(master_file=MASTER, buscoordinates_file=BUS_COORDS)
    r.parse(m)

    # Test list/iteration variations.
    lines = m.list_elements(Line)
    assert len(lines) == 2
    assert isinstance(lines[0], Line)
    line = lines[0]
    name = line.name

    found = False
    for ln in m.iter_elements(Line, lambda x: x.name == name):
        assert ln.name == name

    elements = m.list_elements()
    # There should be more than just lines.
    assert len(elements) > 2

    # Test forms of get.
    assert m.get_element(Line, name) is line
    assert m[name] is line

    with pytest.raises(DuplicateNameError):
        m.add_element(line)

    with pytest.raises(InvalidElementType):
        m.add_element("invalid")

    # Position doesn't have a name.
    with pytest.raises(InvalidElementType):
        m.add_element(Position())

    m.remove_element(line)
    with pytest.raises(ElementNotFoundError):
        m.get_element(Line, name)

    # Test forms of set.
    m.add_element(line)
    assert m.get_element(Line, name) is line
    m.remove_element(line)
    m[name] = line
    assert m.get_element(Line, name) is line

    # Test clear.
    m.clear_elements()
    assert not m.list_elements()
