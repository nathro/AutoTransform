# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.event.remoterun import RemoteRunEvent, RemoteRunEventData
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel


def test_get_type():
    """Test that get_type method returns EventType.REMOTE_RUN"""
    assert RemoteRunEvent.get_type() == EventType.REMOTE_RUN


def test_get_logging_level():
    """Test that get_logging_level method returns LoggingLevel.INFO"""
    assert RemoteRunEvent.get_logging_level() == LoggingLevel.INFO


def test_get_message():
    """Test that _get_message method returns a string in the correct format"""
    event_data = RemoteRunEventData(schema_name="TestSchema", ref="TestRef")
    event = RemoteRunEvent(data=event_data)
    assert event._get_message() == "Remote run of TestSchema: TestRef"


@pytest.mark.parametrize(
    "event_data, expected",
    [
        (RemoteRunEventData(schema_name="TestSchema", ref=""), "Remote run of TestSchema: "),
        (RemoteRunEventData(schema_name="", ref="TestRef"), "Remote run of : TestRef"),
    ],
)
def test_get_message_with_missing_data(event_data, expected):
    """Test that _get_message method handles cases where schema_name or ref are missing"""
    event = RemoteRunEvent(data=event_data)
    assert event._get_message() == expected
