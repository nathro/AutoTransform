# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ConditionalStep."""

from __future__ import annotations

from typing import Any, Dict, Mapping, TypedDict

from typing_extensions import NotRequired

from autotransform.change.base import Change
from autotransform.step.action import Action, ActionType
from autotransform.step.base import Step, StepBundle
from autotransform.step.condition.base import Condition
from autotransform.step.condition.factory import ConditionFactory
from autotransform.step.type import StepType


class ConditionalStepParams(TypedDict):
    """The param type for a ConditionalStep."""

    condition: Condition
    action_type: ActionType
    continue_if_passed: NotRequired[bool]


class ConditionalStep(Step):
    """The base for Step components. Used by AutoTransform to manage outstanding
    Changes, determining what actions to take.

    Attributes:
        _params (TParams): The paramaters that control operation of the Step.
            Should be defined using a TypedDict in subclasses.
    """

    _params: ConditionalStepParams

    @staticmethod
    def get_type() -> StepType:
        """Used to map Step components 1:1 with an enum, allowing construction from JSON.

        Returns:
            StepType: The unique type associated with this Step.
        """

        return StepType.CONDITIONAL

    def get_action(self, change: Change) -> Action:
        """Checks the Change against the provided Condition and returns the appropriate action
        based on whether or not the Condition is passed.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            Action: The Action the Step wants to take.
        """

        if self._params["condition"].check(change):
            return {
                "type": self._params["action_type"],
                "stop_steps": not self._params.get("continue_if_passed", False),
            }
        return {
            "type": ActionType.NONE,
            "stop_steps": False,
        }

    def bundle(self) -> StepBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            StepBundle: The encodable bundle.
        """
        bundled_params: Dict[str, Any] = {
            "condition": self._params["condition"].bundle(),
            "action_type": self._params["action_type"],
        }
        continue_if_passed = self._params.get("continue_if_passed", None)
        if continue_if_passed is not None:
            bundled_params["continue_if_passed"] = continue_if_passed

        return {
            "params": bundled_params,
            "type": self.get_type(),
        }

    def __str__(self) -> str:
        return (
            f"Condition: {str(self._params['condition'])} - Action: {self._params['action_type']}"
        )

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> ConditionalStep:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            ConditionalStep: An instance of the ConditionalStep.
        """

        params: ConditionalStepParams = {
            "action_type": data["action_type"],
            "condition": ConditionFactory.get(data["condition"]),
        }

        continue_if_passed = data.get("continue_if_passed", None)
        if continue_if_passed is not None:
            params["continue_if_passed"] = continue_if_passed

        return ConditionalStep(params)
