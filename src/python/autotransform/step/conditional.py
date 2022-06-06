# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ConditionalStep."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, Type

from autotransform.change.base import Change
from autotransform.step.action import Action, ActionType
from autotransform.step.base import Step, StepName
from autotransform.step.condition.base import FACTORY as condition_factory
from autotransform.step.condition.base import Condition


class ConditionalStep(Step):
    """The base for Step components. Used by AutoTransform to manage outstanding
    Changes, determining what actions to take.

    Attributes:
        action (ActionType): The action to perform if the condition passes.
        condition (Condition): The condition to check.
        continue_if_passed (bool, optional): Whether to continue on to the next step after
            performing the action if the condition passes. Defaults to False.
        name (ClassVar[StepName]): The name of the component.
    """

    action: ActionType
    condition: Condition
    continue_if_passed: bool = False

    name: ClassVar[StepName] = StepName.CONDITIONAL

    def get_action(self, change: Change) -> Action:
        """Checks the Change against the provided Condition and returns the appropriate action
        based on whether or not the Condition is passed.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            Action: The Action the Step wants to take.
        """

        if self.condition.check(change):
            return {
                "type": self.action,
                "stop_steps": not self.continue_if_passed,
            }
        return {
            "type": ActionType.NONE,
            "stop_steps": False,
        }

    @classmethod
    def from_data(cls: Type[ConditionalStep], data: Dict[str, Any]) -> ConditionalStep:
        """Produces an instance of the component from decoded data. Override if
        the component had to be modified to encode.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            ConditionalStep: An instance of the component.
        """

        action = (
            data["action"] if isinstance(data["action"], ActionType) else ActionType(data["action"])
        )
        condition = condition_factory.get_instance(data["condition"])
        return cls(action=action, condition=condition)
