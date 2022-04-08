# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The Event class represents an event happening in AutoTransform and
serves as a base that can be used to provide consistent typing and
messaging for similar events.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, Optional, TypeVar

from colorama import Fore

from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class Event(Generic[TParams], ABC):
    """The base for Events. Used to

    Attributes:
        params (TParams): The paramaters that represent details of the Event
        create_time (float): The current timestamp
    """

    params: TParams
    time: float

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Batcher
        """
        self.params = params
        self.create_time = time.time()

    @staticmethod
    @abstractmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event
        """

    @staticmethod
    @abstractmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event
        """

    @abstractmethod
    def _get_message(self) -> str:
        """Gets a message representing the details of the event

        Returns:
            str: The message for the event
        """

    @staticmethod
    def get_color_override() -> Optional[Fore]:
        """Used to override logging color for specific events where needed

        Returns:
            Optional[Fore]: An optional color to use to override defaults when logging
        """
        return None

    def get_message(self) -> str:
        """Gets a message that can be output to logs representing the event

        Returns:
            str: The loggable message
        """
        return f"[{self.get_type().upper()}] {self._get_message()}"
