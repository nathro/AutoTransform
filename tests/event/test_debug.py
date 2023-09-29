# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.event.debug import DebugEvent, DebugEventData
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel


def test_get_type():
    """Test that DebugEvent.get_type() returns EventType.DEBUG."""
    assert DebugEvent.get_type() == EventType.DEBUG


def test_get_logging_level():
    """Test that DebugEvent.get_logging_level() returns LoggingLevel.DEBUG."""
    assert DebugEvent.get_logging_level() == LoggingLevel.DEBUG


def test_get_message():
    """Test that DebugEvent._get_message() returns the correct message from the event's data."""
    data = DebugEventData(message="Test message")
    event = DebugEvent(data)
    assert event._get_message() == "Test message"


def test_get_message_no_message_key():
    """Test that DebugEvent._get_message() raises an appropriate error if the event's data does not contain a "message" key."""
    data = DebugEventData()
    event = DebugEvent(data)
    with pytest.raises(KeyError):
        event._get_message()


def test_get_message_non_string_data():
    """Test that DebugEvent._get_message() handles non-string data correctly."""
    data = DebugEventData(message=123)
    event = DebugEvent(data)
    assert event._get_message() == 123


def test_get_message_empty_string():
    """Test that DebugEvent._get_message() handles empty strings correctly."""
    data = DebugEventData(message="")
    event = DebugEvent(data)
    assert event._get_message() == ""


def test_get_message_long_string():
    """Test that DebugEvent._get_message() handles long strings correctly."""
    long_string = "a" * 10000
    data = DebugEventData(message=long_string)
    event = DebugEvent(data)
    assert event._get_message() == long_string
