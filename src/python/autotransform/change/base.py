# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Change components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, List

from autotransform.batcher.base import Batch
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent

if TYPE_CHECKING:
    from autotransform.runner.base import Runner
    from autotransform.schema.schema import AutoTransformSchema


class ChangeState(str, Enum):
    """A simple enum for the state of a given Change in code review or version
    control systems."""

    CLOSED = "closed"
    MERGED = "merged"
    OPEN = "open"


class ReviewState(str, Enum):
    """A simple enum for the review state of a given Change in code review or version
    control systems."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    NEEDS_REVIEW = "needs_review"


class TestState(str, Enum):
    """A simple enum for the test state of a given Change in code review or version
    control systems."""

    FAILURE = "failure"
    PENDING = "pending"
    SUCCESS = "success"


class ChangeName(str, Enum):
    """A simple enum for mapping."""

    GITHUB = "github"


class Change(NamedComponent):
    """The base for Change components. Used by AutoTransform to manage submissions to
    code review and source control systems.

    Attributes:
        name (ClassVar[ChangeName]): The name of the Component.
    """

    name: ClassVar[ChangeName]

    @abstractmethod
    def get_batch(self) -> Batch:
        """Gets the Batch that was used to produce the Change.

        Returns:
            Batch: The Batch used to produce the Change.
        """

    @abstractmethod
    def get_schema(self) -> AutoTransformSchema:
        """Gets the Schema that was used to produce the Change.

        Returns:
            AutoTransformSchema: The Schema used to produce the Change.
        """

    def get_schema_name(self) -> str:
        """Gets the name of the Schema that produced the Change.

        Returns:
            str: The name of the Schema.
        """

        return self.get_schema().config.schema_name

    @abstractmethod
    def get_state(self) -> ChangeState:
        """Gets the current state of the Change.

        Returns:
            ChangeState: The current state of the Change.
        """

    @abstractmethod
    def get_review_state(self) -> ReviewState:
        """Gets the current review state of the Change.

        Returns:
            ReviewState: The current review state of the Change.
        """

    @abstractmethod
    def get_test_state(self) -> TestState:
        """Gets the current test state of the Change.

        Returns:
            TestState: The current test state of the Change.
        """

    @abstractmethod
    def get_labels(self) -> List[str]:
        """Gets all labels for a Change.

        Returns:
            List[str]: The list of labels.
        """

    @abstractmethod
    def get_reviewers(self) -> List[str]:
        """Gets all reviewers for a Change.

        Returns:
            List[str]: The list of reviewers.
        """

    @abstractmethod
    def get_team_reviewers(self) -> List[str]:
        """Gets all team reviewers for a Change.

        Returns:
            List[str]: The list of team reviewers.
        """

    def get_created_timestamp(self) -> int:
        """Returns the timestamp when the Change was created.

        Returns:
            int: The timestamp in seconds when the Change was created.
        """

    def get_last_updated_timestamp(self) -> int:
        """Returns the timestamp when the Change was last updated.

        Returns:
            int: The timestamp in seconds when the Change was last updated.
        """

    @abstractmethod
    def abandon(self) -> bool:
        """Close out and abandon a Change, removing it from the code review
        and/or version control system.

        Returns:
            bool: Whether the abandon was completed successfully.
        """

    @abstractmethod
    def add_labels(self, labels: List[str]) -> bool:
        """Adds labels to an outstanding Change.

        Args:
            labels (List[str]): The labels to add.

        Returns:
            bool: Whether the labels were added successfully.
        """

    @abstractmethod
    def add_reviewers(self, reviewers: List[str], team_reviewers: List[str]) -> bool:
        """Adds reviewers to an outstanding Change.

        Args:
            reviewers (List[str]): The reviewers to add.
            team_reviewers (List[str]): Any team reviewers to add.

        Returns:
            bool: Whether the reviewers were added successfully.
        """

    @abstractmethod
    def comment(self, body: str) -> bool:
        """Comments on an outstanding Change.

        Args:
            body (str): The body of the comment.

        Returns:
            bool: Whether the comment was successful.
        """

    @abstractmethod
    def merge(self) -> bool:
        """Merges an approved change in to main.

        Returns:
            bool: Whether the merge was completed successfully.
        """

    @abstractmethod
    def remove_label(self, label: str) -> bool:
        """Removes a label from an outstanding Change.

        Args:
            label (str): The label to remove.

        Returns:
            bool: Whether the label was removed successfully.
        """

    def update(self, runner: Runner) -> bool:
        """Update an outstanding Change against the latest state of the codebase.

        Args:
            runner (Runner): The Runner to use to update the Change.

        Returns:
            bool: Whether the update was completed successfully.
        """

        runner.update(self)
        return True


FACTORY = ComponentFactory(
    {
        ChangeName.GITHUB: ComponentImport(
            class_name="GithubChange", module="autotransform.change.github"
        ),
    },
    Change,  # type: ignore [misc]
    "change.json",
)
