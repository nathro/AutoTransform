# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Script events are used to handle STDOUT and STDERR messages from scripts run
by AutoTransform.
"""

from typing import List, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


class ScriptErrEventData(TypedDict):
    """The data for a ScriptErr. Contains the information that will be
    logged when the event is triggered."""

    stderr: str


class ScriptErrEvent(Event[ScriptErrEventData]):
    """A simple, generic event used to log script STDERR information to the console."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.SCRIPT_ERR

    @staticmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

        return LoggingLevel.WARNING

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return self.data["stderr"]


class ScriptOutEventData(TypedDict):
    """The data for a ScriptOut. Contains the information that will be
    logged when the event is triggered."""

    stdout: str


class ScriptOutEvent(Event[ScriptOutEventData]):
    """A simple, generic event used to log script STDOUT information to the console."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.SCRIPT_OUT

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

        return self.data["stdout"]


class ScriptRunEventData(TypedDict):
    """The data for a ScriptRun. Contains the information that will be
    logged when the event is triggered."""

    command: List[str]


class ScriptRunEvent(Event[ScriptRunEventData]):
    """A simple, generic event used to log when a script is run to the console."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.SCRIPT_RUN

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

        return f"{self.data['command']}"
