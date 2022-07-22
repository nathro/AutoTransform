# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ConditionalStep."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Type

from autotransform.change.base import Change
from autotransform.step.action.base import FACTORY as action_factory
from autotransform.step.action.base import Action, ActionName
from autotransform.step.base import Step, StepName
from autotransform.step.condition.base import FACTORY as condition_factory
from autotransform.step.condition.base import Condition


class ConditionalStep(Step):
    """A step which takes action based on whether a particular condition is passed. Allows
    for creating customized steps based on different Change attributes readily through JSON.

    Attributes:
        actions (List[Action]): The Actions to perform if the Condition passes.
        condition (Condition): The condition to check.
        continue_if_passed (bool, optional): Whether to continue on to the next step after
            performing the action if the condition passes. Defaults to False.
        name (ClassVar[StepName]): The name of the component.
    """

    actions: List[Action]
    condition: Condition
    continue_if_passed: bool = False

    name: ClassVar[StepName] = StepName.CONDITIONAL

    def get_actions(self, change: Change) -> List[Action]:
        """Checks the Change against the provided Condition and returns the appropriate Actions
        based on whether or not the Condition is passed. If no Actions are returned, the Step
        is skipped.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            List[Action]: The Actions the Step wants to take.
        """

        if self.condition.check(change):
            return self.actions
        return []

    def continue_management(self, change: Change) -> bool:
        """Checks if management should be continued after this Step when Actions were provided.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            bool: Whether to continue management.
        """
        return self.continue_if_passed

    @classmethod
    def from_data(cls: Type[ConditionalStep], data: Dict[str, Any]) -> ConditionalStep:
        """Produces an instance of the component from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            ConditionalStep: An instance of the component.
        """

        if "action" in data:
            action_name = (
                data["action"]
                if isinstance(data["action"], ActionName)
                else ActionName(data["action"])
            )
            actions = [action_factory.get_instance({"name": action_name})]
        else:
            actions = [action_factory.get_instance(action) for action in data["actions"]]
        condition = condition_factory.get_instance(data["condition"])
        if "continue_if_passed" in data:
            continue_if_passed = bool(data["continue_if_passed"])
        else:
            continue_if_passed = False
        return cls(actions=actions, condition=condition, continue_if_passed=continue_if_passed)
