# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The AIModel events are used to handle events related to usage of AI Models in AutoTransform.
"""

from typing import TypedDict

from autotransform.command.base import Command
from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType
from autotransform.item.base import Item


class AIModelCommandFailureEventData(TypedDict):
    """The data for a AIModelCommandFailureEvent. Contains the information that will be
    logged when the event is triggered."""

    item: Item
    command: Command
    exception: Exception


class AIModelCommandFailureEvent(Event[AIModelCommandFailureEventData]):
    """A simple event to log AIModel command run failures."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.AI_MODEL_COMMAND_FAILURE

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

        return (
            f"Item: {self.data['item'].key}\n"
            + f"Command: {self.data['command']}\n"
            + f"Error: {self.data['exception']}"
        )


class AIModelCompletionEventData(TypedDict):
    """The data for a AIModelCompletionEvent. Contains the information that will be
    logged when the event is triggered."""

    completion: str
    input_tokens: int
    output_tokens: int


class AIModelCompletionEvent(Event[AIModelCompletionEventData]):
    """A simple event to log AIModel completions."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.AI_MODEL_COMPLETION

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

        return (
            f"Input Tokens: {self.data['input_tokens']}\n"
            + f"Output Tokens: {self.data['output_tokens']}\n"
            + f"Completion:\n{self.data['completion']}"
        )


class AIModelCompletionFailureEventData(TypedDict):
    """The data for a AIModelCompletionFailureEvent. Contains the information that will be
    logged when the event is triggered."""

    item: Item
    exception: Exception


class AIModelCompletionFailureEvent(Event[AIModelCompletionFailureEventData]):
    """A simple event to log AIModel completion failures."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.AI_MODEL_COMPLETION_FAILURE

    @staticmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

        return LoggingLevel.ERROR

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"Failed on Item: {self.data['item'].key}\nError: {self.data['exception']}"
