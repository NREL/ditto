# -*- coding: utf-8 -*-

"""
test_cyme_reader
----------------------------------

Tests for cyme reader
"""
import os
import pytest as pt
from ditto.store import Store

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_network_protectors():
    """
    Tests the network protectors parsing.
    """
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store
    from ditto.models.line import Line

    m = Store()
    r = Reader(
        data_folder_path=os.path.join(
            current_directory, "data", "ditto-validation", "cyme", "network_protectors"
        )
    )
    r.parse(m)
    for obj in m.models:
        if isinstance(obj, Line):
            # Section A is ABC and the protector is closed on ABC
            if obj.name == "A":
                # The line should be a network protector...
                assert obj.is_network_protector
                # ...and it should have 4 wires: A, B, C, and N
                assert len(obj.wires) == 4

                for wire in obj.wires:
                    # All wires should be flaged as network protector
                    assert wire.is_network_protector

                    # All wires should be closed
                    assert not wire.is_open

                    # The network protector limit should be 600 amps for all wires
                    assert wire.network_protector_limit == 600.0

            # Section B is AC and the protector is closed on A only
            if obj.name == "B":
                # The line should be a network protector...
                assert obj.is_network_protector
                # ...and it should have 3 wires: A, C, and N
                assert len(obj.wires) == 3

                for wire in obj.wires:
                    # Check phase is valid
                    assert wire.phase in ["A", "C", "N"]

                    # All wires should be flaged as network protector
                    assert wire.is_network_protector

                    # Wires A and N should be closed
                    if wire.phase in ["A", "N"]:
                        assert not wire.is_open
                    # And should be open on phase C
                    else:
                        assert wire.is_open

                    # The network protector limit should be 600 amps for all wires
                    assert wire.network_protector_limit == 600.0
