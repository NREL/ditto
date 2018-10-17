import pytest

from ditto.readers.synergi.length_units import (
    convert_length_unit,
    SynergiValueType,
)


@pytest.mark.parametrize(
    'value, value_type, length_unit, expected',
    [
        (39.3701, SynergiValueType.SUL, 'English2', pytest.approx(1.0)),
        (3.28084, SynergiValueType.MUL, 'English2', pytest.approx(1.0)),
        (1.0, SynergiValueType.LUL, 'English2', pytest.approx(1609.34)),
        (
            1609.34,
            SynergiValueType.Per_LUL,
            'English2',
            pytest.approx(1.0, abs=1e-5)
        ),

        (39.3701, SynergiValueType.SUL, 'English1', pytest.approx(1.0)),
        (3.28084, SynergiValueType.MUL, 'English1', pytest.approx(1.0)),
        (1.0, SynergiValueType.LUL, 'English1', pytest.approx(304.8)),
        (304.8, SynergiValueType.Per_LUL, 'English1', pytest.approx(1.0)),

        (1000.0, SynergiValueType.SUL, 'Metric', 1.0),
        (2.0, SynergiValueType.MUL, 'Metric', 2.0),
        (1.0, SynergiValueType.LUL, 'Metric', 1000.0),
        (1000.0, SynergiValueType.Per_LUL, 'Metric', 1.0),
    ]
)
def test_convert_units(value, value_type, length_unit, expected):
    actual = convert_length_unit(value, value_type, length_unit)
    assert actual == expected


def test_raises_error_invalid_value_type():
    with pytest.raises(ValueError):
        convert_length_unit(1.0, 'a', 'English2')


def test_raises_error_invalid_unit_type():
    with pytest.raises(ValueError):
        convert_length_unit(1.0, SynergiValueType.SUL, 1)


def test_raises_error_invalid_unit_value():
    with pytest.raises(ValueError):
        convert_length_unit(1.0, SynergiValueType.SUL, 'English3')
