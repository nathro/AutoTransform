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
from autotransform.step.action.base import Action
from autotransform.step.action.comments import CommentAction
from autotransform.step.action.labels import AddLabelsAction, RemoveLabelAction
from autotransform.step.action.reviewers import (
    AddOwnersAsReviewersAction,
    AddOwnersAsTeamReviewersAction,
    AddReviewersAction,
)
from autotransform.step.action.source import AbandonAction, MergeAction, NoneAction, UpdateAction
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent

if TYPE_CHECKING:
    from autotransform.runner.base import Runner
    from autotransform.schema.schema import AutoTransformSchema


class ChangeState(str, Enum):
    """A simple enum for the state of a given Change in code review or version
    control systems."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    CLOSED = "closed"
    MERGED = "merged"
    OPEN = "open"


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

    @abstractmethod
    def get_state(self) -> ChangeState:
        """Gets the current state of the Change.

        Returns:
            ChangeState: The current state of the Change.
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

    # pylint: disable=too-many-return-statements
    def take_action(self, action: Action, runner: Runner) -> bool:
        """Tells the Change to take an Action based on the results of a Step run.

        Args:
            action (Action): The Action to take.
            runner (Runner): A Runner which can be used to take an Action.

        Returns:
            bool: Whether the Action was taken successfully.
        """

        if isinstance(action, AbandonAction):
            return self._abandon()

        if isinstance(action, AddLabelsAction):
            return self._add_labels(action.labels)

        if isinstance(action, AddOwnersAsReviewersAction):
            return self._add_reviewers(self.get_schema().config.owners, [])

        if isinstance(action, AddOwnersAsTeamReviewersAction):
            return self._add_reviewers([], self.get_schema().config.owners)

        if isinstance(action, AddReviewersAction):
            return self._add_reviewers(action.reviewers, action.team_reviewers)

        if isinstance(action, CommentAction):
            return self._comment(action.body)

        if isinstance(action, MergeAction):
            return self._merge()

        if isinstance(action, NoneAction):
            return True

        if isinstance(action, RemoveLabelAction):
            return self._remove_label(action.label)

        if isinstance(action, UpdateAction):
            return self._update(runner)

        # No known way to handle the Action, so treat it as failed
        return False

    @abstractmethod
    def _abandon(self) -> bool:
        """Close out and abandon a Change, removing it from the code review
        and/or version control system.

        Returns:
            bool: Whether the abandon was completed successfully.
        """

    @abstractmethod
    def _add_labels(self, labels: List[str]) -> bool:
        """Adds labels to an outstanding Change.

        Args:
            labels (List[str]): The labels to add.

        Returns:
            bool: Whether the labels were added successfully.
        """

    @abstractmethod
    def _add_reviewers(self, reviewers: List[str], team_reviewers: List[str]) -> bool:
        """Adds reviewers to an outstanding Change.

        Args:
            reviewers (List[str]): The reviewers to add.
            team_reviewers (List[str]): Any team reviewers to add.

        Returns:
            bool: Whether the reviewers were added successfully.
        """

    @abstractmethod
    def _comment(self, body: str) -> bool:
        """Comments on an outstanding Change.

        Args:
            body (str): The body of the comment.

        Returns:
            bool: Whether the comment was successful.
        """

    @abstractmethod
    def _merge(self) -> bool:
        """Merges an approved change in to main.

        Returns:
            bool: Whether the merge was completed successfully.
        """

    @abstractmethod
    def _remove_label(self, label: str) -> bool:
        """Removes a label from an outstanding Change.

        Args:
            label (str): The label to remove.

        Returns:
            bool: Whether the label was removed successfully.
        """

    def _update(self, runner: Runner) -> bool:
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
