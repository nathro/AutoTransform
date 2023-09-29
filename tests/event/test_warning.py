# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

import pytest
from autotransform.event.warning import WarningEvent, WarningEventData
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel


def test_get_type():
    """Test that the get_type method returns EventType.WARNING"""
    assert WarningEvent.get_type() == EventType.WARNING


def test_get_logging_level():
    """Test that the get_logging_level method returns LoggingLevel.WARNING"""
    assert WarningEvent.get_logging_level() == LoggingLevel.WARNING


def test_get_message():
    """Test that the _get_message method returns the correct message"""
    event_data = WarningEventData(message="Test message")
    event = WarningEvent(data=event_data)
    assert event._get_message() == "Test message"


def test_get_message_no_message_key():
    """Test that the _get_message method raises an error when the data attribute does not contain a message key"""
    event = WarningEvent(data={})
    with pytest.raises(KeyError):
        event._get_message()


def test_get_message_data_not_dict():
    """Test that the _get_message method raises an error when the data attribute is not a dictionary-like object"""
    event = WarningEvent(data="Not a dict")
    with pytest.raises(TypeError):
        event._get_message()


def test_subclass_warning_event():
    """Test that the WarningEvent class can be successfully subclassed"""

    class SubWarningEvent(WarningEvent):
        pass

    assert issubclass(SubWarningEvent, WarningEvent)


def test_instantiate_warning_event():
    """Test that the WarningEvent class can be successfully instantiated with different WarningEventData instances"""
    event_data1 = WarningEventData(message="Test message 1")
    event1 = WarningEvent(data=event_data1)
    assert event1._get_message() == "Test message 1"

    event_data2 = WarningEventData(message="Test message 2")
    event2 = WarningEvent(data=event_data2)
    assert event2._get_message() == "Test message 2"
