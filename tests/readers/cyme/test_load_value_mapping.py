import pytest

from ditto.readers.cyme.read import Reader


@pytest.mark.parametrize('load_type, v1, v2, expected', [
    # '0', 0, or 'kw_kvar' modes just return the values
    ('0', 1, 2, (1, 2)),
    (0, 1, 2, (1, 2)),
    ('kw_kvar', 1, 2, (1, 2)),

    # '1', 1, or 'kva_pf' modes. v1 is kva, v2 is pf
    ('1', 100, 0.9, (90, pytest.approx(43.58898))),
    (1, 100, 0.9, (90, pytest.approx(43.58898))),
    ('kva_pf', 100, 0.9, (90, pytest.approx(43.58898))),

    # Edge conditions. pf 1.0 and 0.0
    (1, 100, 1.0, (100, 0.0)),
    (1, 100, 0.0, (0.0, 100.0)),

    # '2', 2, or 'kw_pf' modes. v1 is kw, v2 is pf
    ('2', 90, 0.9, (90, pytest.approx(43.58898))),
    (2, 90, 0.9, (90, pytest.approx(43.58898))),
    ('kw_pf', 90, 0.9, (90, pytest.approx(43.58898))),

    # Edge condition, pf of 1.0
    ('2', 90, 1.0, (90, 0.0)),
])
def test_load_value_mapping(load_type, v1, v2, expected):
    reader = Reader()
    actual = reader.load_value_type_mapping(
      load_type, v1, v2
    )
    assert actual == expected


def test_load_value_mapping_invalid_type():
    reader = Reader()

    with pytest.raises(ValueError):
        reader.load_value_type_mapping(0.0, 100, 10)


@pytest.mark.parametrize('v1, v2', [
    ('a', 10),
    (10, 'b'),
])
def test_load_value_mapping_invalid_value(v1, v2):
    reader = Reader()

    with pytest.raises(ValueError):
        reader.load_value_type_mapping(0, v1, v2)


@pytest.mark.parametrize('load_type', [
    3,
    '3',
    'amp_pf',
])
def test_load_value_mapping_amp_pf_not_impl(load_type):
    reader = Reader()

    with pytest.raises(NotImplementedError):
        reader.load_value_type_mapping(load_type, 100, 0.9)
