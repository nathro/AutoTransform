# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import Mock
from autotransform.change.base import Change
from autotransform.event.update import RemoteUpdateEvent, RemoteUpdateEventData
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


def test_get_type():
    """Test if get_type() method returns the correct EventType.REMOTE_UPDATE value."""
    event = RemoteUpdateEvent(data={})
    assert event.get_type() == EventType.REMOTE_UPDATE


def test_get_logging_level():
    """Test if get_logging_level() method returns the correct LoggingLevel.INFO value."""
    event = RemoteUpdateEvent(data={})
    assert event.get_logging_level() == LoggingLevel.INFO


def test_get_message():
    """Test the _get_message() method to ensure it returns the correct string representation of the event details."""
    change = Mock(spec=Change)
    ref = "test_ref"
    data = RemoteUpdateEventData(change=change, ref=ref)
    event = RemoteUpdateEvent(data=data)
    assert event._get_message() == f"Remote update of {str(change)!r}: {ref}"


@pytest.mark.parametrize(
    "change, ref",
    [(Mock(spec=Change), ""), (Mock(spec=Change), None), (None, "test_ref"), (None, None)],
)
def test_get_message_edge_cases(change, ref):
    """Test the _get_message() method with various edge cases."""
    data = RemoteUpdateEventData(change=change, ref=ref)
    event = RemoteUpdateEvent(data=data)
    expected_message = f"Remote update of {str(change)!r}: {ref if ref is not None else 'None'}"
    assert event._get_message() == expected_message


def test_remote_update_event_with_additional_data():
    """Test the RemoteUpdateEvent with a RemoteUpdateEventData that includes additional unexpected data."""
    data = RemoteUpdateEventData(change=Mock(spec=Change), ref="test_ref", extra="extra_data")
    event = RemoteUpdateEvent(data=data)
    assert event._get_message() == f"Remote update of {str(data['change'])!r}: {data['ref']}"
