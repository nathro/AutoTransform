# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.event.schedulerun import ScheduleRunEvent, ScheduleRunEventData
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel


def test_get_type():
    """Test that ScheduleRunEvent.get_type() returns EventType.SCHEDULE_RUN"""
    assert ScheduleRunEvent.get_type() == EventType.SCHEDULE_RUN


def test_get_logging_level():
    """Test that ScheduleRunEvent.get_logging_level() returns LoggingLevel.INFO"""
    assert ScheduleRunEvent.get_logging_level() == LoggingLevel.INFO


@pytest.mark.parametrize(
    "schema_name, expected_message",
    [
        ("test_schema", "Scheduling run of test_schema"),
        ("", "Scheduling run of "),
        ("schema with spaces", "Scheduling run of schema with spaces"),
        ("special@#chars$", "Scheduling run of special@#chars$"),
        ("a" * 1000, "Scheduling run of " + "a" * 1000),
    ],
)
def test_get_message(schema_name, expected_message):
    """Test that ScheduleRunEvent._get_message() returns the correct message"""
    event = ScheduleRunEvent(data=ScheduleRunEventData(schema_name=schema_name))
    assert event._get_message() == expected_message
