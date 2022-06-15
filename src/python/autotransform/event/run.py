# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The ScriptRunEvent is triggered whenever an AutoTransform script is run and provides
information on the run.
"""

from typing import Dict, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType


class ScriptRunEventData(TypedDict):
    """The data for a ScriptRunEvent. Contains the information that will be
    logged when the event is triggered."""

    args: Dict[str, str]
    script: str


class ScriptRunEvent(Event[ScriptRunEventData]):
    """A ScriptRunEvent is triggered whenever an AutoTransform script is run. Logs details
    of the run.
    """

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

        return LoggingLevel.INFO

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"Running script command {self.data['script']}"
