# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Runner events are used to handle events related to Runners in AutoTransform.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType

if TYPE_CHECKING:
    from autotransform.change.base import Change
    from autotransform.runner.base import Runner


class RunnerFailedEventData(TypedDict):
    """The data for a RunnerFailedEvent. Contains the information that will be
    logged when the event is triggered."""

    message: str
    runner: Runner


class RunnerFailedEvent(Event[RunnerFailedEventData]):
    """A RunnerFailedEvent is triggered whenever a Runner fails."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.RUNNER_FAILED

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

        return f"{self.data['message']}\n{self.data['runner']}"


class RunnerRunEventData(TypedDict):
    """The data for a RunnerRunEvent. Contains the information that will be
    logged when the event is triggered."""

    schema_name: str
    ref: Optional[str]
    runner: Runner


class RunnerRunEvent(Event[RunnerRunEventData]):
    """A RunnerRunEvent is triggered whenever a Runner successfully triggers a run."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.RUNNER_RUN

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

        return (
            f"{self.data['schema_name']} run with ref: {self.data['ref']}\n"
            + f"{self.data['runner']}"
        )


class RunnerUpdateEventData(TypedDict):
    """The data for a RunnerUpdateEvent. Contains the information that will be
    logged when the event is triggered."""

    change: Change
    ref: Optional[str]
    runner: Runner


class RunnerUpdateEvent(Event[RunnerUpdateEventData]):
    """A RunnerRunEvent is triggered whenever a Runner successfully triggers an update."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.RUNNER_UPDATE

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

        return (
            f"{str(self.data['change'])!r} updated with ref: {self.data['ref']}\n"
            + f"{self.data['runner']}"
        )
