# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

import pytest
from autotransform.event.verbose import VerboseEvent
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel


def test_get_type():
    """Test if the get_type method correctly returns EventType.VERBOSE"""
    event = VerboseEvent(data={"message": "Test message"})
    assert event.get_type() == EventType.VERBOSE


def test_get_logging_level():
    """Test if the get_logging_level method correctly returns LoggingLevel.VERBOSE"""
    event = VerboseEvent(data={"message": "Test message"})
    assert event.get_logging_level() == LoggingLevel.VERBOSE


def test_get_message():
    """Test if the _get_message method correctly returns the message from the VerboseEventData"""
    event = VerboseEvent(data={"message": "Test message"})
    assert event._get_message() == "Test message"


def test_get_message_no_message():
    """Test if the _get_message method handles the case where the VerboseEventData does not contain a message field"""
    event = VerboseEvent(data={})
    with pytest.raises(KeyError):
        event._get_message()


def test_get_message_non_string():
    """Test if the _get_message method handles the case where the VerboseEventData contains a message field that is not a string"""
    event = VerboseEvent(data={"message": 123})
    assert event._get_message() == 123
