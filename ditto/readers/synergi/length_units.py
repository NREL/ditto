from enum import Enum


class SynergiValueType(Enum):
    SUL = "SUL"
    MUL = "MUL"
    LUL = "LUL"
    Per_LUL = "Per_LUL"


def convert_length_unit(value, value_type, length_units):
    """
    Converts a Synergi value to an SI type.

    The value is interpreted based on:
    +----------+----------------+------------+
    |value_type|  length_units  |   Unit     |
    +==========+================+============+
    |   SUL    |    English2    |    inch    |
    +----------+----------------+------------+
    |   SUL    |    English1    |    inch    |
    +----------+----------------+------------+
    |   SUL    |    English     |    inch    |
    +----------+----------------+------------+
    |   SUL    |     Metric     |     mm     |
    +----------+----------------+------------+
    |   MUL    |    English2    |    foot    |
    +----------+----------------+------------+
    |   MUL    |    English1    |    foot    |
    +----------+----------------+------------+
    |   MUL    |    English     |    foot    |
    +----------+----------------+------------+
    |   MUL    |     Metric     |     m      |
    +----------+----------------+------------+
    |   LUL    |    English2    |    mile    |
    +----------+----------------+------------+
    |   LUL    |    English1    |    kft     |
    +----------+----------------+------------+
    |   LUL    |    English     |    kft     |
    +----------+----------------+------------+
    |   LUL    |     Metric     |     km     |
    +----------+----------------+------------+
    |  Per_LUL |    English2    |  per mile  |
    +----------+----------------+------------+
    |  Per_LUL |    English1    |  per kft   |
    +----------+----------------+------------+
    |  Per_LUL |    English     |  per kft   |
    +----------+----------------+------------+
    |  Per_LUL |     Metric     |   per km   |
    +----------+----------------+------------+

    The return value is based on

    SUL: metres
    MUL: metres
    LUL: metres
    Per_LUL: per metre
    """

    if not isinstance(value_type, SynergiValueType):
        raise ValueError(
            "convert_length_unit received an invalid value_type value"
            " of {}".format(value_type)
        )

    if not isinstance(length_units, str):
        raise ValueError(
            "convert_length_unit must be passed a string length_units"
            " parameter. {} was received.".format(length_units)
        )

    if length_units.lower() not in {"english", "english2", "english1", "metric"}:
        raise ValueError(
            "convert_length_unit received an invalid length unit {}".format(
                length_units
            )
        )

    CONVERSION_FACTORS = {
        "english2": {
            SynergiValueType.SUL: 0.0254,
            SynergiValueType.MUL: 0.3048,
            SynergiValueType.LUL: 1609.34,
            SynergiValueType.Per_LUL: 1 / 1609.34,
        },
        "english1": {
            SynergiValueType.SUL: 0.0254,
            SynergiValueType.MUL: 0.3048,
            SynergiValueType.LUL: 304.8,
            SynergiValueType.Per_LUL: 3.28084 * 10 ** -3,
        },
        "metric": {
            SynergiValueType.SUL: 10 ** -3,
            SynergiValueType.MUL: 1.0,
            SynergiValueType.LUL: 1e3,
            SynergiValueType.Per_LUL: 10 ** -3,
        },
        "english": {
            SynergiValueType.SUL: 0.0254,
            SynergiValueType.MUL: 0.3048,
            SynergiValueType.LUL: 304.8,
            SynergiValueType.Per_LUL: 3.28084 * 10 ** -3,
        },
    }

    factor = CONVERSION_FACTORS[length_units][value_type]
    return value * factor
