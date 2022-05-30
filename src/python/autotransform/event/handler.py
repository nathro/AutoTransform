# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The EventHandler receives event dispatches and triggers appropriate behavior for
the event, such as logging.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from colorama import Fore

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel


class EventHandler:
    """The handler that all Events are dispatched to that logs these events. Any hooks being added
    to AutoTransform Events should be added here.

    Attributes:
        _logging_level (LoggingLevel): The level for which logs will be output to CLI. All other
            events will be dropped.
        __instance (Optional[EventHandler]): The singleton instance of the EventHandler
        __color_map (Dict[LoggingLevel, str]): A mapping from log level to ANSI color for CLI
            output
    """

    _logging_level: LoggingLevel
    __instance: Optional[EventHandler] = None
    __color_map: Dict[LoggingLevel, str] = {
        LoggingLevel.ERROR: Fore.RED,
        LoggingLevel.WARNING: Fore.YELLOW,
        LoggingLevel.INFO: Fore.WHITE,
        LoggingLevel.DEBUG: Fore.CYAN,
    }

    def __init__(self):
        if EventHandler.__instance is not None:
            raise Exception("Trying to instantiate new EventHandler when one already present")
        self._logging_level = LoggingLevel.INFO

    @staticmethod
    def get() -> EventHandler:
        """Singleton method for getting the event handler.

        Returns:
            EventHandler: The singleton instance of the EventHandler
        """
        if EventHandler.__instance is None:
            EventHandler.__instance = EventHandler()
        return EventHandler.__instance

    def set_logging_level(self, logging_level: LoggingLevel) -> None:
        """_summary_

        Args:
            logging_level (LoggingLevel): The logging level to output
        """
        self._logging_level = logging_level

    def handle(self, event: Event) -> None:
        """Handles the given Event, logging and executing any hooks needed.

        Args:
            event (Event): The Event that was dispatched
        """
        if self._logging_level >= event.get_logging_level():
            self.output_to_cli(event)

    @staticmethod
    def output_to_cli(event: Event) -> None:
        """Outputs the event to CLI with appropriate coloring

        Args:
            event (Event): The event being logged
        """
        color = event.get_color_override()
        if color is None:
            color = EventHandler.__color_map[event.get_logging_level()]
        creation_string = datetime.fromtimestamp(event.create_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{creation_string}]{event.get_message()}{Fore.RESET}")
