# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Github events are used to handle events related to usage of Github in AutoTransform.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from autotransform.event.base import Event
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.type import EventType

if TYPE_CHECKING:
    from autotransform.util.github import PullRequest


class GithubPullRequestCreatedEventData(TypedDict):
    """The data for a GithubPullRequestCreatedEvent. Contains the information that will be
    logged when the event is triggered."""

    pull: PullRequest


class GithubPullRequestCreatedEvent(Event[GithubPullRequestCreatedEventData]):
    """A simple event to log pull requests being created."""

    @staticmethod
    def get_type() -> EventType:
        """Used to represent the type of Event, output to logs.

        Returns:
            EventType: The unique type associated with this Event.
        """

        return EventType.GITHUB_PULL_REQUEST_CREATED

    @staticmethod
    def get_logging_level() -> LoggingLevel:
        """The logging level for events of this type.

        Returns:
            LoggingLevel: The logging detail required to log this event.
        """

        return LoggingLevel.VERBOSE

    def _get_message(self) -> str:
        """Gets a message representing the details of the event.

        Returns:
            str: The message for the event.
        """

        return f"Pull #{self.data['pull'].number}"
