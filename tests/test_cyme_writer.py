# -*- coding: utf-8 -*-

"""
test_cyme_writer
----------------------------------

Tests for cyme writer
"""
import os
import pytest as pt
from ditto.store import Store
from ditto.writers.cyme.write import Writer

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_center_tap_load_writing():
    """
    Tests the writing of center tap loads.
    """
    from ditto.models.load import Load
    from ditto.models.phase_load import PhaseLoad

    m = Store()
    l = Load(m)
    l.name = "load1"
    l.is_center_tap = True
    l.center_tap_perct_1_N = 0.5
    l.center_tap_perct_N_2 = 0.5
    l.center_tap_perct_1_2 = 0

    pl = PhaseLoad(m)
    pl.p = 10
    pl.q = 8
    pl.phase = "C"
    l.phase_loads.append(pl)

    w = Writer(output_path=current_directory)
    w.write(m)

    with open(os.path.join(current_directory, "loads.txt"), "r") as fp:
        lines = fp.readlines()

    assert lines[-1] == ",SPOT,0,C,,,0,PQ,50.0,50.0,0.005,0.004,0.005,0.004,0\n"

    # Cleaning
    os.remove(os.path.join(current_directory, "loads.txt"))
    os.remove(os.path.join(current_directory, "equipment.txt"))
    os.remove(os.path.join(current_directory, "network.txt"))
