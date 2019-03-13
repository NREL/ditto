import pytest

from ditto.readers.cyme.read import Reader


@pytest.mark.parametrize('cyme_value, expected', [
    (0, 'Y'),
    (1, 'Y'),
    (2, 'D'),
    ('0', 'Y'),
    ('1', 'Y'),
    ('2', 'D'),
    (3, 3),  # Non conversion case
])
def test_cap_connection_mapping(cyme_value, expected):
    reader = Reader()
    actual = reader.capacitors_connection_mapping(cyme_value)
    assert actual == expected


def test_cap_connection_mapping_invalid_type():
    reader = Reader()

    with pytest.raises(ValueError):
        reader.capacitors_connection_mapping(0.0)
