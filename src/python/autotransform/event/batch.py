# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Batch events are used to handle events related to running a Batch in AutoTransform.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType

if TYPE_CHECKING:
    from autotransform.batcher.base import Batch
    from autotransform.validator.base import ValidationResult


class BatchExecutionFailedEventData(TypedDict):
    """The data for a BatchExecutionFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    batch: Batch
    error: Exception


class BatchExecutionFailedEvent(Event[BatchExecutionFailedEventData]):
    """A simple, generic event used to log when a batch fails to execute."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.BATCH_EXECUTION_FAILED

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

        return f"{self.data['batch']['title']}: {self.data['error']}"


class BatchNoChangesEventData(TypedDict):
    """The data for a BatchNoChangesEvent. Contains the information that will be
    logged when the event is triggered."""

    batch: Batch


class BatchNoChangesEvent(Event[BatchNoChangesEventData]):
    """A simple, generic event used to log when a batch finishes without changes."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.BATCH_NO_CHANGES

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

        return self.data["batch"]["title"]


class BatchSkipEventData(TypedDict):
    """The data for a BatchSkipEvent. Contains the information that will be
    logged when the event is triggered."""

    batch: Batch


class BatchSkipEvent(Event[BatchSkipEventData]):
    """A simple, generic event used to log when a batch is skipped."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.BATCH_SKIP

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

        return self.data["batch"]["title"]


class BatchSubmitEventData(TypedDict):
    """The data for a BatchSubmitEvent. Contains the information that will be
    logged when the event is triggered."""

    batch: Batch


class BatchSubmitEvent(Event[BatchSubmitEventData]):
    """A simple, generic event used to log when a batch is submitted."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.BATCH_SUBMIT

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

        return self.data["batch"]["title"]


class BatchValidationFailedEventData(TypedDict):
    """The data for a BatchValidationFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    batch: Batch
    result: ValidationResult


class BatchValidationFailedEvent(Event[BatchValidationFailedEventData]):
    """A simple, generic event used to log when a batch fails validation."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.BATCH_VALIDATION_FAILED

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

        return f"{self.data['batch']['title']}: {self.data['result'].message}"
