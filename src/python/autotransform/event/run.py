# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The RunEvent is triggered whenever an AutoTransform script is run and provides
information on the run.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType

if TYPE_CHECKING:
    from autotransform.change.base import Change
    from autotransform.schema.schema import AutoTransformSchema
    from autotransform.util.manager import Manager
    from autotransform.util.scheduler import Scheduler


class RunEventData(TypedDict):
    """The data for a RunEvent. Contains the information that will be
    logged when the event is triggered."""

    schema: AutoTransformSchema


class RunEvent(Event[RunEventData]):
    """An Event triggered when a schema is run using the run mode."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.RUN

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

        return f"{self.data['schema'].config.schema_name}"


class RunFailedEventData(TypedDict):
    """The data for a RunFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    schema: AutoTransformSchema
    error: Exception


class RunFailedEvent(Event[RunFailedEventData]):
    """An Event triggered when a schema run fails."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.RUN_FAILED

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

        return f"{self.data['schema'].config.schema_name}: {self.data['error']}"


class RunCommandFailedEventData(TypedDict):
    """The data for a RunCommandFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    error: Exception


class RunCommandFailedEvent(Event[RunCommandFailedEventData]):
    """An Event triggered when a command run fails."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.RUN_COMMAND_FAILED

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

        return f"{self.data['error']}"


class RunManagerEventData(TypedDict):
    """The data for a RunManagerEvent. Contains the information that will be
    logged when the event is triggered."""

    manager: Manager


class RunManagerEvent(Event[RunManagerEventData]):
    """An event triggered whenever the Manager is invoked."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.RUN_MANAGER

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

        return f"Managing repo: {self.data['manager'].repo}"


class RunManagerFailedEventData(TypedDict):
    """The data for a RunManagerFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    manager: Manager
    error: Exception


class RunManagerFailedEvent(Event[RunManagerFailedEventData]):
    """An event triggered when the Manager fails."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.RUN_MANAGER_FAILED

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

        return f"Failed to manage {self.data['manager'].repo}: {self.data['error']}"


class RunSchedulerEventData(TypedDict):
    """The data for a RunSchedulerEvent. Contains the information that will be
    logged when the event is triggered."""

    scheduler: Scheduler


class RunSchedulerEvent(Event[RunSchedulerEventData]):
    """An event triggered whenever the Scheduler is invoked."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.RUN_SCHEDULER

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

        return f"{self.data['scheduler']}"


class RunSchedulerFailedEventData(TypedDict):
    """The data for a RunSchedulerFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    scheduler: Scheduler
    error: Exception


class RunSchedulerFailedEvent(Event[RunSchedulerFailedEventData]):
    """An event triggered when the Scheduler fails."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.RUN_SCHEDULER_FAILED

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

        return f"{self.data['scheduler']}: {self.data['error']}"


class RunUpdateEventData(TypedDict):
    """The data for a RunUpdateEvent. Contains the information that will be
    logged when the event is triggered."""

    change: Change


class RunUpdateEvent(Event[RunUpdateEventData]):
    """An event triggered whenever an update is invoked."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.RUN_UPDATE

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

        return f"{self.data['change']}"


class RunUpdateFailedEventData(TypedDict):
    """The data for a RunUpdateFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    change: Change
    error: Exception


class RunUpdateFailedEvent(Event[RunUpdateFailedEventData]):
    """An event triggered when an update fails."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """
        return EventType.RUN_SCHEDULER_FAILED

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

        return f"{self.data['change']}: {self.data['error']}"
