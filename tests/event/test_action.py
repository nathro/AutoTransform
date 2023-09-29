# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.event.action import ManageActionEvent, ManageActionEventData
from autotransform.event.type import EventType
from autotransform.event.logginglevel import LoggingLevel
from autotransform.step.action.base import Action
from autotransform.change.base import Change
from autotransform.step.base import Step


class MockAction(Action):
    def run(self, change):
        pass


class MockChange(Change):
    def abandon(self):
        pass

    def add_labels(self, labels):
        pass

    def add_reviewers(self, reviewers, team_reviewers):
        pass

    def comment(self, body):
        pass

    def get_batch(self):
        pass

    def get_created_timestamp(self):
        pass

    def get_labels(self):
        pass

    def get_last_updated_timestamp(self):
        pass

    def get_mergeable_state(self):
        pass

    def get_review_state(self):
        pass

    def get_reviewers(self):
        pass

    def get_schema(self):
        pass

    def get_state(self):
        pass

    def get_team_reviewers(self):
        pass

    def get_test_state(self):
        pass

    def merge(self):
        pass

    def remove_label(self, label):
        pass

    # Add other required methods here...


class MockStep(Step):
    def continue_management(self, change):
        pass

    def get_actions(self, change):
        pass


def test_get_type():
    """Test if get_type method returns the correct EventType."""
    assert ManageActionEvent.get_type() == EventType.MANAGE_ACTION


def test_get_logging_level():
    """Test if get_logging_level method returns the correct LoggingLevel."""
    assert ManageActionEvent.get_logging_level() == LoggingLevel.INFO


def test_get_message():
    """Test if _get_message method returns the correct string message."""
    action = MockAction()
    change = MockChange()
    step = MockStep()
    event_data = ManageActionEventData(action=action, change=change, step=step)
    event = ManageActionEvent(data=event_data)
    assert event._get_message() == f"Performing action: {action!r}\nOn Change: {change!r}"


@pytest.mark.parametrize(
    "event_data",
    [
        ({}),
        ({"action": MockAction()}),
        ({"change": MockChange()}),
    ],
)
def test_get_message_missing_fields(event_data):
    """Test if _get_message method handles correctly when the action or change fields in the data dictionary are missing."""
    with pytest.raises(KeyError):
        event = ManageActionEvent(data=event_data)
        event._get_message()


def test_get_message_empty_data():
    """Test if _get_message method handles correctly when the data dictionary is empty."""
    with pytest.raises(TypeError):
        event = ManageActionEvent(data=None)
        event._get_message()
