# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The WarningEvent is a simple, generic event used for logging warning information to
the console. This information is not expected to be logged to long term storage and
is used when encountering warnings in production environments. More specific events should be
created for long term storage cases.
"""

from typing import TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


class WarningEventData(TypedDict):
    """The data for a WarningEvent. Contains the information that will be
    logged when the event is triggered."""

    message: str


class WarningEvent(Event[WarningEventData]):
    """A simple, generic warning event used to log warning information to the console."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.WARNING

    @staticmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

        return LoggingLevel.WARNING

    def _get_message(self) -> str:
        """Gets a message representing the details of the event

        Returns:
            str: The message for the event
        """

        return self.data["message"]
