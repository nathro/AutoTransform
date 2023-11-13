# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for EventNotifier components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import ClassVar

from autotransform.event.base import Event
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class EventNotifierName(str, Enum):
    """A simple enum for mapping."""

    CONSOLE = "console"


class EventNotifier(NamedComponent):
    """The base for EventNotifier components. Used by AutoTransform to provide logs to
    the user.

    Attributes:
        name (ClassVar[CommandName]): The name of the Component.
    """

    name: ClassVar[EventNotifierName]

    @abstractmethod
    def notify(self, event: Event) -> None:
        """Notifies the user about an Event that is triggered.

        Args:
            event (Event): The Event to notify the user about.
        """


FACTORY = ComponentFactory(
    {
        EventNotifierName.CONSOLE: ComponentImport(
            class_name="ConsoleEventNotifier", module="autotransform.event.notifier.console"
        ),
    },
    EventNotifier,  # type: ignore [type-abstract]
    "event_notifier.json",
)
