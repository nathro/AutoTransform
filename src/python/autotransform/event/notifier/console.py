# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ConsoleEventNotifier."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Dict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.notifier.base import EventNotifier, EventNotifierName
from colorama import Fore


class ConsoleEventNotifier(EventNotifier):
    """Logs the Event's message to the console to provide information to the user.

    Attributes:
        name (ClassVar[CommandName]): The name of the Component.
    """

    name: ClassVar[EventNotifierName] = EventNotifierName.CONSOLE

    def notify(self, event: Event) -> None:
        """Notifies the user about an Event that is triggered.

        Args:
            event (Event): The Event to notify the user about.
        """
        color = event.get_color_override()
        if color is None:
            color = self._color_map[event.get_logging_level()]
        creation_string = datetime.fromtimestamp(event.create_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{creation_string}]{event.get_message()}{Fore.RESET}")

    @property
    def _color_map(self) -> Dict[LoggingLevel, str]:
        """Gets the map from LoggingLevel to color for console logs.

        Returns:
            Dict[LoggingLevel, str]: The map from LoggingLevel to color.
        """

        return {
            LoggingLevel.ERROR: Fore.RED,
            LoggingLevel.WARNING: Fore.YELLOW,
            LoggingLevel.INFO: Fore.WHITE,
            LoggingLevel.VERBOSE: Fore.GREEN,
            LoggingLevel.DEBUG: Fore.CYAN,
        }
