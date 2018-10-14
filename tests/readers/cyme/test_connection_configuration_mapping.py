import pytest
from ditto.readers.cyme.read import Reader
from itertools import chain

@pytest.mark.parametrize('value, expected_configuration', list(chain(
    [(el, 'Y') for el in (0, "0", "Yg", "yg")],
    [(el, 'Y') for el in (1, "1", "Y", "y")],
    [(el, 'D') for el in (2, "2", "Delta", "delta")],
    [(el, 'D') for el in (3, "3", "Open Delta", "open delta")],
    [(el, 'D') for el in (4, "4", "Closed Delta", "closed delta")],
    [(el, 'Z') for el in (5, "5", "Zg", "zg")],
)))
def test_connection_configuration_mapping(value, expected_configuration):
    configuration = Reader().connection_configuration_mapping(value)
    assert configuration == expected_configuration


@pytest.mark.parametrize('value', [
    6, "6", 'ct',
    7, "7", 'dg',
])
def test_unmapped_inputs_to_connection_configuration_mapping(value):
    with pytest.raises(NotImplementedError):
        Reader().connection_configuration_mapping(value)

