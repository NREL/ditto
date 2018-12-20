"""
test_capacitor_writing.py
----------------------------------

Tests for writing Capacitor objects from DiTTo to OpenDSS.
"""

import os
import math
import pytest
import tempfile
import numpy as np

from ditto.store import Store
from ditto.writers.opendss.write import Writer
from ditto.models.capacitor import Capacitor
from ditto.models.phase_capacitor import PhaseCapacitor

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_single_phase_capacitor_writing():
    m = Store()

    # Create a one phase, 100kVar capacitor on phase A
    cap1 = Capacitor(m)
    cap1.name = "cap1"
    cap1.nominal_voltage = 4.16 * 10 ** 3
    cap1.connecting_element = "bus23"
    cap1_A = PhaseCapacitor(m)
    cap1_A.phase = "A"
    cap1_A.var = 100 * 10 ** 3
    cap1.phase_capacitors.append(cap1_A)

    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    w.write(m)

    # Check that the OpenDSS writer created a Master file
    assert os.path.exists(os.path.join(output_path, "Master.dss"))

    # Check that the OpenDSS writer created a Capacitors.dss file
    assert os.path.exists(os.path.join(output_path, "Capacitors.dss"))

    with open(os.path.join(output_path, "Capacitors.dss"), "r") as fp:
        lines = fp.readlines()

    assert (
        len(lines) == 2
    )  # There is one line with the capacitor string and one empty line
    assert lines[0] == "New Capacitor.cap1 Bus1=bus23.1 phases=1 Kv=4.16 Kvar=100.0\n"


def test_three_phase_capacitor_writing():
    m = Store()

    # Create a three phase, 900kVar capacitor
    cap1 = Capacitor(m)
    cap1.connecting_element = "bus66"
    cap1.nominal_voltage = 4.16 * 10 ** 3
    cap1.name = "cap1"

    for phase in ["A", "B", "C"]:
        cap1.phase_capacitors.append(PhaseCapacitor(m, phase=phase, var=300 * 10 ** 3))

    output_path = tempfile.gettempdir()
    w = Writer(output_path=output_path)
    w.write(m)

    # Check that the OpenDSS writer created a Master file
    assert os.path.exists(os.path.join(output_path, "Master.dss"))

    # Check that the OpenDSS writer created a Capacitors.dss file
    assert os.path.exists(os.path.join(output_path, "Capacitors.dss"))

    with open(os.path.join(output_path, "Capacitors.dss"), "r") as fp:
        lines = fp.readlines()

    assert (
        len(lines) == 2
    )  # There is one line with the capacitor string and one empty line
    assert lines[0] == "New Capacitor.cap1 Bus1=bus66 phases=3 Kv=4.16 Kvar=900.0\n"
