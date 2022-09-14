import numpy as np
import math
import cmath
from ditto.store import Store
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding
from ditto.models.powertransformer import PowerTransformer
from six import string_types


def get_transformer_xhl_Rpercent(trfx: dict) -> tuple[float, float]:
    # Resistance
    # Note: Imported from Julietta's code
    Z1 = float(trfx["z1"])  # TODO default values
    Z0 = float(trfx["z0"])
    XR = float(trfx["xr"])
    XR0 = float(trfx["xr0"])
    if XR == 0:
        R1 = 0
        X1 = 0
    else:
        R1 = Z1 / math.sqrt(1 + XR * XR)
        X1 = Z1 / math.sqrt(1 + 1 / (XR * XR))
    if XR0 == 0:
        R0 = 0
        X0 = 0
    else:
        R0 = Z0 / math.sqrt(1 + XR0 * XR0)
        X0 = Z0 / math.sqrt(1 + 1 / (XR0 * XR0))
    complex0 = complex(R0, X0)
    complex1 = complex(R1, X1)
    matrix = np.array(
        [[complex0, 0, 0], [0, complex1, 0], [0, 0, complex1]]
    )
    a = 1 * cmath.exp(2 * math.pi * 1j / 3)
    T = np.array([[1.0, 1.0, 1.0], [1.0, a * a, a], [1.0, a, a * a]])
    T_inv = np.linalg.inv(T)
    Zabc = T * matrix * T_inv
    Z_perc = Zabc.item((0, 0))
    R_perc = Z_perc.real / 2.0
    xhl = Z_perc.imag
    return xhl, R_perc


def transformer_connection_configuration_mapping(value, winding):
    """
    Map the connection configuration for transformer (2 windings) objects from CYME to DiTTo.

    :param value: CYME value (either string or id)
    :type value: int or str
    :param winding: Number of the winding (0 or 1)
    :type winding: int
    :returns: DiTTo connection configuration for the requested winding
    :rtype: str

    **Mapping:**

    +----------+----------------+------------+
    |   Value  |       CYME     |  DiTTo     |
    +----------+----------------+-----+------+
    |          |                | 1st | 2nd  |
    +==========+================+=====+======+
    | 0 or '0' |      'Y_Y'     | 'Y' | 'Y'  |
    +----------+----------------+-----+------+
    | 1 or '1' |      'D_Y'     | 'D' | 'Y'  |
    +----------+----------------+-----+------+
    | 2 or '2' |      'Y_D'     | 'Y' | 'D'  |
    +----------+----------------+-----+------+
    | 3 or '3' |    'YNG_YNG'   | 'Y' | 'Y'  |
    +----------+----------------+-----+------+
    | 4 or '4' |      'D_D'     | 'D' | 'D'  |
    +----------+----------------+-----+------+
    | 5 or '5' |     'DO_DO'    | 'D' | 'D'  |
    +----------+----------------+-----+------+
    | 6 or '6' |     'YO_DO'    | 'Y' | 'D'  |
    +----------+----------------+-----+------+
    | 7 or '7' |     'D_YNG'    | 'D' | 'Y'  |
    +----------+----------------+-----+------+
    | 8 or '8' |     'YNG_D'    | 'Y' | 'D'  |
    +----------+----------------+-----+------+
    | 9 or '9' |     'Y_YNG'    | 'Y' | 'Y'  |
    +----------+----------------+-----+------+
    |10 or '10'|     'YNG_Y'    | 'Y' | 'Y'  |
    +----------+----------------+-----+------+
    |11 or '11'|     'Yg_Zg'    | 'Y' | 'Z'  |
    +----------+----------------+-----+------+
    |12 or '12'|     'D_Zg'     | 'D' | 'Z'  |
    +----------+----------------+-----+------+
    """
    if winding not in [0, 1]:
        raise ValueError(
            "transformer_connection_configuration_mapping expects an integer 0 or 1 for winding arg. {} was provided.".format(
                winding
            )
        )

    res = (None, None)

    if isinstance(value, int):
        if value == 0 or value == 3 or value == 9 or value == 10:
            res = ("Y", "Y")
        if value == 1 or value == 7:
            res = ("D", "Y")
        if value == 2 or value == 6 or value == 8:
            res = ("Y", "D")
        if value == 4 or value == 5:
            res = ("D", "D")
        if value == 11:
            res = ("Y", "Z")
        if value == 12:
            res = ("D", "Z")

    elif isinstance(value, string_types):
        if value == "0" or value.lower() == "y_y":
            res = ("Y", "Y")
        if value == "1" or value.lower() == "d_y":
            res = ("D", "Y")
        if value == "2" or value.lower() == "y_d":
            res = ("Y", "D")
        if value == "3" or value.lower() == "yng_yng":
            res = ("Y", "Y")
        if value == "4" or value.lower() == "d_d":
            res = ("D", "D")
        if value == "5" or value.lower() == "do_do":
            res = ("D", "D")
        if value == "6" or value.lower() == "yo_do":
            res = ("Y", "D")
        if value == "7" or value.lower() == "d_yng":
            res = ("D", "Y")
        if value == "8" or value.lower() == "yng_d":
            res = ("Y", "D")
        if value == "9" or value.lower() == "y_yng":
            res = ("Y", "Y")
        if value == "10" or value.lower() == "yng_y":
            res = ("Y", "Y")
        if value == "11" or value.lower() == "yg_zg":
            res = ("Y", "Z")
        if value == "12" or value.lower() == "d_zg":
            res = ("D", "Z")

    else:
        raise ValueError(
            "transformer_connection_configuration_mapping expects an integer or a string. {} was provided.".format(
                type(value)
            )
        )

    return res[winding]


def add_two_windings(
    api_transformer: PowerTransformer, 
    trfx_data: dict, 
    settings: dict,
    model: Store, 
    phases: str, 
    R_perc: float
    ) -> None:
    """
    Add Winding and PhaseWinding objects to PowerTransformer
    using `trfx_data` from the [TRANSFORMER] section
    and `settings` from either [TRANFORMER SETTINGS] or [TRANSFORMER BYPHASE SETTINGS]
    """

    # Here we know that we have two windings...
    for w in range(2):

        # Instanciate a Winding DiTTo object
        try:
            api_winding = Winding(model)
        except:
            raise ValueError("Unable to instanciate Winding DiTTo object.")

        # Set the rated power
        try:
            if w == 0:
                api_winding.rated_power = (
                    float(trfx_data["kva"]) * 10 ** 3
                )  # DiTTo in volt ampere
            if w == 1:
                api_winding.rated_power = (
                    float(trfx_data["kva"]) * 10 ** 3
                )  # DiTTo in volt ampere
        except:
            pass

        # Set the nominal voltage
        try:
            if w == 0:
                api_winding.nominal_voltage = (
                    float(trfx_data["kvllprim"]) * 10 ** 3
                )  # DiTTo in volt
            if w == 1:
                api_winding.nominal_voltage = (
                    float(trfx_data["kvllsec"]) * 10 ** 3
                )  # DiTTo in volt
        except:
            pass

        # Connection configuration
        try:
            api_winding.connection_type = transformer_connection_configuration_mapping(
                trfx_data["conn"], w
            )
        except:
            pass

        # Resistance
        try:
            api_winding.resistance = R_perc
        except:
            pass

        # For each phase...
        for p in phases:

            # Instanciate a PhaseWinding DiTTo object
            try:
                api_phase_winding = PhaseWinding(model)
            except:
                raise ValueError(
                    "Unable to instanciate PhaseWinding DiTTo object."
                )
            # Set the phase
            try:
                api_phase_winding.phase = p
            except:
                pass

            # set tap
            tapkey = "primtap" if w == 0 else "secondarytap"
            if (
                tapkey in settings.keys() and
                settings[tapkey] is not None
            ):
                api_phase_winding.tap_position = float(settings[tapkey]) / 100

            # Add the phase winding object to the winding
            api_winding.phase_windings.append(api_phase_winding)

        # Add the winding object to the transformer
        api_transformer.windings.append(api_winding)
    
    return None
