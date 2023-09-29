# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the EventType enum."""

from enum import Enum
from autotransform.event.type import EventType


def test_inheritance():
    """Test if the EventType enum correctly inherits from both str and Enum classes."""
    assert issubclass(EventType, Enum)
    assert issubclass(EventType, str)


def test_instance():
    """Test if each member of the EventType enum is an instance of EventType."""
    for event_type in EventType:
        assert isinstance(event_type, EventType)


def test_string():
    """Test if each member of the EventType enum is also a string."""
    for event_type in EventType:
        assert isinstance(event_type, str)


def test_members():
    """Test if the EventType enum has the correct members."""
    expected_members = {
        "DEBUG",
        "MANAGE_ACTION",
        "REMOTE_RUN",
        "REMOTE_UPDATE",
        "SCHEDULE_RUN",
        "SCRIPT_RUN",
        "VERBOSE",
        "WARNING",
    }
    assert set(EventType.__members__) == expected_members


def test_values():
    """Test if each member of the EventType enum is associated with a string of the same name."""
    for event_type in EventType:
        assert event_type.value == event_type.name.lower()


def test_comparison():
    """Test if the EventType enum can be correctly used in a comparison operation."""
    assert EventType.DEBUG == EventType.DEBUG
    assert EventType.DEBUG != EventType.WARNING


def test_string_formatting():
    """Test if the EventType enum can be correctly used in a string formatting operation."""
    assert f"{EventType.DEBUG}" == "debug"


def test_switch_case_like():
    """Test if the EventType enum can be correctly used in a switch-case-like construct."""
    switch = {EventType.DEBUG: "debug", EventType.WARNING: "warning"}
    assert switch[EventType.DEBUG] == "debug"
    assert switch[EventType.WARNING] == "warning"
