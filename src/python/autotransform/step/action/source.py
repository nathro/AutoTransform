# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with handling source control options for a Change."""

from functools import cached_property
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.config import get_config
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
        use_local_runner(optional, bool): Whether to use the local runner. Defaults to False.
        name (ClassVar[ActionName]): The name of the component.
    """

    use_local_runner: bool = False

    name: ClassVar[ActionName] = ActionName.UPDATE

    @cached_property
    def _runner(self) -> Runner:
        """A cached Runner from the config.

        Returns:
            Runner: The Runner to use to update Changes.
        """

        conf = get_config()
        runner = conf.local_runner if self.use_local_runner else conf.remote_runner
        assert runner is not None
        return runner

    def run(self, change: Change) -> bool:
        """Updates a specified Change.

        Args:
            change (Change): The Change to update.

        Returns:
            bool: Whether the Change was updated successfully.
        """

        return change.update(self._runner)
