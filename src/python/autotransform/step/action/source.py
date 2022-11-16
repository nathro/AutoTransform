# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with handling source control options for a Change."""

from typing import ClassVar

from autotransform.change.base import Change
from autotransform.runner.base import Runner
from autotransform.step.action.base import Action, ActionName


class AbandonAction(Action):
    """Abandons an outstanding Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.ABANDON

    def run(self, change: Change) -> bool:
        """Abandons a specified Change.

        Args:
            change (Change): The Change to abandon.

        Returns:
            bool: Whether the Change was abandoned successfully.
        """

        return change.abandon()


class MergeAction(Action):
    """Merges an outstanding Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.MERGE

    def run(self, change: Change) -> bool:
        """Merges a specified Change.

        Args:
            change (Change): The Change to merge.

        Returns:
            bool: Whether the Change was merged successfully.
        """

        return change.merge()


class NoneAction(Action):
    """Performs no task.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.NONE

    def run(self, change: Change) -> bool:
        """Performs no action.

        Args:
            change (Change): The Change to having no action taken on it

        Returns:
            bool: Always returns True.
        """

        return True


class UpdateAction(Action):
    """Updates an outstanding Change.

    Attributes:
        _runner (ClassVar[Runner]): The runner to use for updating
        name (ClassVar[ActionName]): The name of the component.
    """

    _runner: ClassVar[Runner]

    name: ClassVar[ActionName] = ActionName.UPDATE

    @staticmethod
    def set_runner(runner: Runner) -> None:
        """Sets the runner for the Action to use.

        Args:
            runner (Runner): The Runner to use to update Changes.
        """

        UpdateAction._runner = runner

    def run(self, change: Change) -> bool:
        """Updates a specified Change.

        Args:
            change (Change): The Change to update.

        Returns:
            bool: Whether the Change was updated successfully.
        """

        return change.update(UpdateAction._runner)
