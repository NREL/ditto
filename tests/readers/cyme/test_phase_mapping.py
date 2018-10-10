import pytest

from ditto.readers.cyme.read import Reader


@pytest.mark.parametrize('cyme_value, expected', [
    (0, [None]),
    (1, ['A']),
    (2, ['B']),
    (3, ['C']),
    (4, ['A', 'B']),
    (5, ['A', 'C']),
    (6, ['B', 'C']),
    (7, ['A', 'B', 'C']),
    ('ABC', ['A', 'B', 'C']),
])
def test_phase_mapping(cyme_value, expected):
    reader = Reader()
    actual = reader.phase_mapping(cyme_value)
    assert actual == expected
