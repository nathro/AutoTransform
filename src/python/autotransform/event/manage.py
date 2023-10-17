# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Events related to Actions being taken on outstanding Changes.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType
from autotransform.step.action.base import ActionName

if TYPE_CHECKING:
    from autotransform.change.base import Change
    from autotransform.step.action.base import Action
    from autotransform.step.base import Step
    from autotransform.util.manager import Manager


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

        return f"Performing action: {self.data['action']!r}\nOn Change: {self.data['change']!r}"

    @staticmethod
    def get_event(data: ManageActionEventData) -> "ManageActionEvent":
        """Gets the most specific version of the event for an Action.

        Args:
            data (ManageActionEventData): The data for the Action.

        Returns:
            ManageActionEvent: The specific Event.
        """

        if data["action"].name == ActionName.ABANDON:
            return ManageAbandonEvent(data)

        return ManageActionEvent(data)


class ManageAbandonEvent(ManageActionEvent):
    """An event triggered whenever a Step attempts to abandon a Change."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.MANAGE_ABANDON

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"{self.data['change']!r}"


class ManageCommentEvent(ManageActionEvent):
    """An event triggered whenever a Step attempts to comment on a Change."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.MANAGE_COMMENT


class ManageMergeEvent(ManageActionEvent):
    """An event triggered whenever a Step attempts to merge a Change."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.MANAGE_MERGE

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"{self.data['change']!r}"


class ManageUpdateEvent(ManageActionEvent):
    """An event triggered whenever a Step attempts to update a Change."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.MANAGE_UPDATE

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"{self.data['change']!r}"


class ManageRequestEvent(ManageActionEvent):
    """An event triggered whenever a Step attempts to submit a request for a Change."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.MANAGE_REQUEST
