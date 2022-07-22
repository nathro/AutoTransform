# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The ManageActionEvent is triggered whenever an action is taken against an
outstanding Change.
"""

from typing import TypedDict

from autotransform.change.base import Change
from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType
from autotransform.step.action.base import Action
from autotransform.step.base import Step


class ManageActionEventData(TypedDict):
    """The data for a ManageActionEventData. Contains the information that will be
    logged when the event is triggered."""

    action: Action
    change: Change
    step: Step


class ManageActionEvent(Event[ManageActionEventData]):
    """An event triggered whenever a Step attempts to take an action against a Change."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.MANAGE_ACTION

    @staticmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

        return LoggingLevel.INFO

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"{str(self.data['change'])}: {self.data['action']}"
