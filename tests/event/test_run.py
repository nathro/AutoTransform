# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.event.run import ScriptRunEvent
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel


def test_get_type():
    """Test if get_type() method returns the correct EventType."""
    event = ScriptRunEvent(data={"args": {}, "script": ""})
    assert event.get_type() == EventType.SCRIPT_RUN


def test_get_logging_level():
    """Test if get_logging_level() method returns the correct LoggingLevel."""
    event = ScriptRunEvent(data={"args": {}, "script": ""})
    assert event.get_logging_level() == LoggingLevel.INFO


@pytest.mark.parametrize("script", ["test_script", "", "!@#$%^&*()", "a" * 1000])
def test_get_message(script):
    """Test the _get_message() method with a variety of ScriptRunEventData inputs."""
    event = ScriptRunEvent(data={"args": {}, "script": script})
    assert event._get_message() == f"Running script command {script}"


def test_event_with_additional_fields():
    """Test the ScriptRunEvent with a ScriptRunEventData that has additional unexpected fields."""
    event = ScriptRunEvent(data={"args": {}, "script": "test_script", "extra": "field"})
    assert event._get_message() == "Running script command test_script"


def test_event_with_missing_fields():
    """Test the ScriptRunEvent with a ScriptRunEventData that is missing required fields."""
    event = ScriptRunEvent(data={"args": {}})
    with pytest.raises(KeyError):
        event._get_message()


def test_event_with_incorrect_field_types():
    """Test the ScriptRunEvent with a ScriptRunEventData that has fields of incorrect types."""
    event = ScriptRunEvent(data={"args": "not a dict", "script": 123})
    assert event._get_message() == "Running script command 123"
