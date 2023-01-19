# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The VerboseEvent is a simple, generic event used for logging information to
the console. This information is not expected to be logged to long term storage and
is used to follow usage in production environments. More specific events should be created
for long term storage cases.
"""

from typing import TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


class VerboseEventData(TypedDict):
    """The data for a VerboseEvent. Contains the information that will be
    logged when the event is triggered."""

    message: str


class VerboseEvent(Event[VerboseEventData]):
    """A simple, generic event used to log verbose information to the console."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.VERBOSE

    @staticmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

        return LoggingLevel.VERBOSE

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return self.data["message"]
