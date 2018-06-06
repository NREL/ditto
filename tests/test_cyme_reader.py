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
            if obj.name == "a":
                # The line should be a network protector...
                assert obj.is_network_protector
                # ...and it should have 4 wires: A, B, C, and N
                assert len(obj.wires) == 4

                for wire in obj.wires:
                    # All wires should be flaged as network protector
                    assert wire.is_network_protector

                    # All wires should be closed
                    assert not wire.is_open

                    # The breaker ampacity should be 100 amps for all wires
                    assert wire.ampacity == 100.0

                    # The network protector limit should be 600 amps for all wires
                    assert wire.interrupting_rating == 600.0

            # Section B is AC and the protector is closed on A only
            elif obj.name == "b":
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

                    # The network protector ampacity should be 100 amps for all wires
                    assert wire.ampacity == 100.0

                    # The network protector limit should be 600 amps for all wires
                    assert wire.interrupting_rating == 600.0

            else:
                raise ValueError("Unknown line name {name}".format(name=obj.name))


def test_breakers():
    """
    Tests the breakers parsing.
    """
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store
    from ditto.models.line import Line

    m = Store()
    r = Reader(
        data_folder_path=os.path.join(
            current_directory, "data", "ditto-validation", "cyme", "breakers"
        )
    )
    r.parse(m)
    for obj in m.models:
        if isinstance(obj, Line):
            # Section A is ABC and the breaker is closed on ABC
            if obj.name == "a":
                # The line should be a breaker...
                assert obj.is_breaker
                # ...and it should have 4 wires: A, B, C, and N
                assert len(obj.wires) == 4

                for wire in obj.wires:
                    # All wires should be flaged as breaker
                    assert wire.is_breaker

                    # All wires should be closed
                    assert not wire.is_open

                    # The breaker ampacity should be 100 amps for all wires
                    assert wire.ampacity == 100.0

                    # The breaker limit should be 600 amps for all wires
                    assert wire.interrupting_rating == 600.0

            # Section B is AC and the breaker is closed on C only
            elif obj.name == "b":
                # The line should be a breaker...
                assert obj.is_breaker
                # ...and it should have 3 wires: A, C, and N
                assert len(obj.wires) == 3

                for wire in obj.wires:
                    # Check phase is valid
                    assert wire.phase in ["A", "C", "N"]

                    # All wires should be flaged as a breaker
                    assert wire.is_breaker

                    # Wires C and N should be closed
                    if wire.phase in ["C", "N"]:
                        assert not wire.is_open
                    # And should be open on phase A
                    else:
                        assert wire.is_open

                    # The breaker ampacity should be 300 amps for all wires
                    assert wire.ampacity == 300.0

                    # The breaker limit should be 800 amps for all wires
                    assert wire.interrupting_rating == 800.0

            else:
                raise ValueError("Unknown line name {name}".format(name=obj.name))


def test_switches():
    """
    Tests the switches parsing.
    """
    from ditto.readers.cyme.read import Reader
    from ditto.store import Store
    from ditto.models.line import Line

    m = Store()
    r = Reader(
        data_folder_path=os.path.join(
            current_directory, "data", "ditto-validation", "cyme", "switches"
        )
    )
    r.parse(m)
    for obj in m.models:
        if isinstance(obj, Line):
            # Section A is ABC and the switch is closed on AC
            if obj.name == "a":
                # The line should be a switch...
                assert obj.is_switch
                # ...and it should have 4 wires: A, B, C, and N
                assert len(obj.wires) == 4

                for wire in obj.wires:
                    # All wires should be flaged as switch
                    assert wire.is_switch

                    # Wires A, C, and N should be closed
                    if wire.phase in ["A", "C", "N"]:
                        assert not wire.is_open
                    # And should be open on phase B
                    else:
                        assert wire.is_open

                    # The swictch ampacity should be 100 amps for all wires
                    assert wire.ampacity == 100.0

                    # The swicth should not have a limit
                    assert wire.interrupting_rating is None

            # Section B is AC and the switch is open
            elif obj.name == "b":
                # The line should be a switch...
                assert obj.is_switch
                # ...and it should have 3 wires: A, C, and N
                assert len(obj.wires) == 3

                for wire in obj.wires:
                    # Check phase is valid
                    assert wire.phase in ["A", "C", "N"]

                    # All wires should be flaged as a switch
                    assert wire.is_switch

                    # All wires should be open
                    assert wire.is_open

                    # The switch ampacity should be 300 amps for all wires
                    assert wire.ampacity == 300.0

                    # The swicth should not have a limit
                    assert wire.interrupting_rating is None

            else:
                raise ValueError("Unknown line name {name}".format(name=obj.name))
