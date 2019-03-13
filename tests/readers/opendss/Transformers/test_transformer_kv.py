# -*- coding: utf-8 -*-

"""
test_transformer_kv.py
----------------------------------

Tests for parsing nominal voltage values of Transformers from OpenDSS into DiTTo.
"""

import os
import math
import pytest
import numpy as np

from ditto.store import Store
from ditto.readers.opendss.read import Reader

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_transformer_kv():
    m = Store()
    r = Reader(master_file=os.path.join(current_directory, "test_transformer_kv.dss"))
    r.parse(m)
    m.set_names()

    # Substation is a 115kV/4.16kV step-down two windings transformer
    assert (
        len(m["substation"].windings) == 2
    )  # Transformer substation should have 2 Windings
    assert m["substation"].windings[0].nominal_voltage == 115 * 10 ** 3
    assert m["substation"].windings[1].nominal_voltage == 4.16 * 10 ** 3

    # reg1 is a 4.16kV/4.16kV two windings regulator
    assert len(m["reg1"].windings) == 2  # Transformer reg1 should have 2 Windings
    assert m["reg1"].windings[0].nominal_voltage == 4.16 * 10 ** 3
    assert m["reg1"].windings[1].nominal_voltage == 4.16 * 10 ** 3

    # xfm1 is a 4.16kV/0.48kV two windings distribution transformer
    assert len(m["xfm1"].windings) == 2  # Transformer xfm1 should have 2 Windings
    assert m["xfm1"].windings[0].nominal_voltage == 4.16 * 10 ** 3
    assert m["xfm1"].windings[1].nominal_voltage == 0.48 * 10 ** 3

    # TODO: Three windings, center-taps and so on...
