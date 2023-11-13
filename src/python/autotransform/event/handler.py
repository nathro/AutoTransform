# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The EventHandler receives event dispatches and triggers appropriate behavior for
the event, such as logging. Set AUTO_TRANSFORM_EVENT_HANDLER environment variable to
{
    class_name: <The name of a class extending EventHandler>,
    module: <The fully qualified module where the class is>
}
as JSON to override the default event handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from autotransform.config import get_config
from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel

if TYPE_CHECKING:
    from autotransform.event.notifier.base import EventNotifier


class EventHandler:
    """The handler that all Events are dispatched to that logs these events.

    Attributes:
        _logging_level (LoggingLevel): The level for which logs will be output to CLI.
        __instance (Optional[EventHandler]): The singleton instance of the EventHandler.
        __color_map (Dict[LoggingLevel, str]): A mapping from log level to ANSI color for CLI
            output.
    """

    _logging_level: LoggingLevel
    _notifiers: List[EventNotifier]
    __instance: Optional[EventHandler] = None

    def __init__(self):
        if EventHandler.__instance is not None:
            # pylint: disable=broad-exception-raised
            raise Exception("Trying to instantiate new EventHandler when one already present")
        self._notifiers = get_config().get_event_notifiers()
        self._logging_level = LoggingLevel.INFO

    @staticmethod
    def get() -> EventHandler:
        """Singleton method for getting the event handler.

        Returns:
            EventHandler: The singleton instance of the EventHandler.
        """

        if EventHandler.__instance is None:
            EventHandler.__instance = EventHandler()
        return EventHandler.__instance

    def set_logging_level(self, logging_level: LoggingLevel) -> None:
        """Sets the level of logs to include in console outputs.

        Args:
            logging_level (LoggingLevel): The logging level to output to console.
        """

        self._logging_level = logging_level

    def handle(self, event: Event) -> None:
        """Handles the given Event, logging and executing any hooks needed.

        Args:
            event (Event): The Event that was triggered.
        """

        if self._logging_level.value >= event.get_logging_level().value:
            for notifier in self._notifiers:
                notifier.notify(event)
