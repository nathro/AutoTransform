# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The RemoteRunEvent is triggered whenever an AutoTransformSchema is triggered for a run
on remote infrastructure.
"""

from typing import TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


class RemoteRunEventData(TypedDict):
    """The data for a RemoteRunEvent. Contains the information that will be
    logged when the event is triggered."""

    schema_name: str
    ref: str


class RemoteRunEvent(Event[RemoteRunEventData]):
    """A RemoteRunEvent is triggered whenever an AutoTransformSchema is triggered for a run
    on remote infrastructure.
    """

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.REMOTE_RUN

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

        return f"Remote run of {self.data['schema_name']}: {self.data['ref']}"
