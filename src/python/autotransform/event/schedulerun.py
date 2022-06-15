# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The ScheduleRunEvent is triggered whenever an AutoTransformSchema is scheduled to be run
by the schedule command of the AutoTransform script.
"""

from typing import TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


class ScheduleRunEventData(TypedDict):
    """The data for a ScheduleRunEvent. Contains the information that will be
    logged when the event is triggered."""

    schema_name: str


class ScheduleRunEvent(Event[ScheduleRunEventData]):
    """A ScheduleRunEvent is triggered whenever an AutoTransformSchema is scheduled to be
    run by the schedule command and logs the schedule.
    """

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.SCHEDULE_RUN

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

        return f"Scheduling run of {self.data['schema_name']}"
