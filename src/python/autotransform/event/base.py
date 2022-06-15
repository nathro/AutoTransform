# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Event class represents an event happening in AutoTransform and
serves as a base that can be used to provide consistent typing and
messaging for similar events.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, Optional, TypeVar

from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType

TData = TypeVar("TData", bound=Mapping[str, Any])


class Event(Generic[TData], ABC):
    """The base for Events. Used to construct a loggable event that can be hooked in to
    through the EventHandler to store logs in custom deployments.

    Attributes:
        data (TData): The data that represents details of the Event.
        create_time (float): The current timestamp when the event is created.
    """

    data: TData
    create_time: float

    def __init__(self, data: TData):
        """A simple constructor.

        Args:
            data (TData): The data that represents details of the Event.
        """

        self.data = data
        self.create_time = time.time()

    @staticmethod
    @abstractmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

    @staticmethod
    @abstractmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

    @abstractmethod
    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

    @staticmethod
    def get_color_override() -> Optional[str]:
        """Used to override logging color for specific events where needed. Should use
        colorama ANSI codes.

        Returns:
            Optional[str]: An optional color to use to override defaults when logging.
        """

        return None

    def get_message(self) -> str:
        """Gets a message that can be output to logs representing the event. Converts type from
        lowercase with underscores to capitalized words for the message.

        Returns:
            str: The loggable message.
        """

        type_str = "".join([w.capitalize() for w in self.get_type().split("_")])
        message = self._get_message()
        if message.startswith("["):
            return f"[{type_str}]{message}"
        return f"[{type_str}] {message}"
