import pytest

from ditto.readers.synergi.length_units import convert_length_unit, SynergiValueType


@pytest.mark.parametrize(
    "value, value_type, length_unit, expected",
    [
        (39.3701, SynergiValueType.SUL, "english2", pytest.approx(1.0)),
        (3.28084, SynergiValueType.MUL, "english2", pytest.approx(1.0)),
        (1.0, SynergiValueType.LUL, "english2", pytest.approx(1609.34)),
        (1609.34, SynergiValueType.Per_LUL, "english2", pytest.approx(1.0, abs=1e-5)),
        (39.3701, SynergiValueType.SUL, "english1", pytest.approx(1.0)),
        (3.28084, SynergiValueType.MUL, "english1", pytest.approx(1.0)),
        (1.0, SynergiValueType.LUL, "english1", pytest.approx(304.8)),
        (304.8, SynergiValueType.Per_LUL, "english1", pytest.approx(1.0)),
        (1000.0, SynergiValueType.SUL, "metric", 1.0),
        (2.0, SynergiValueType.MUL, "metric", 2.0),
        (1.0, SynergiValueType.LUL, "metric", 1000.0),
        (1000.0, SynergiValueType.Per_LUL, "metric", 1.0),
    ],
)
def test_convert_units(value, value_type, length_unit, expected):
    actual = convert_length_unit(value, value_type, length_unit)
    assert actual == expected


def test_raises_error_invalid_value_type():
    with pytest.raises(ValueError):
        convert_length_unit(1.0, "a", "english2")


def test_raises_error_invalid_unit_type():
    with pytest.raises(ValueError):
        convert_length_unit(1.0, SynergiValueType.SUL, 1)


def test_raises_error_invalid_unit_value():
    with pytest.raises(ValueError):
        convert_length_unit(1.0, SynergiValueType.SUL, "english3")
