# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ChangeStateCondition."""

from __future__ import annotations

from typing import Any, Mapping, TypedDict

from autotransform.change.base import Change
from autotransform.change.state import ChangeState
from autotransform.step.condition.base import Condition
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.type import ConditionType


class ChangeStateConditionParams(TypedDict):
    """The param type for a ChangeStateCondition."""

    comparison: ComparisonType
    state: ChangeState


class ChangeStateCondition(Condition[ChangeStateConditionParams]):
    """A condition which checks the ChangeState against the state supplied in the params,
    using the supplied comparison. Note: only equals and not equals are valid, all others will
    result in an error.

    Attributes:
        _params (TParams): The paramaters that control operation of the Condition.
            Should be defined using a TypedDict in subclasses.
    """

    _params: ChangeStateConditionParams

    @staticmethod
    def get_type() -> ConditionType:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

        return ConditionType.CHANGE_STATE

    def check(self, change: Change) -> bool:
        """Checks whether the Change passes the Condition.

        Args:
            change (Change): The Change the Condition checking.

        Returns:
            bool: Whether the Change passes the condition.
        """
        comparison = self._params["comparison"]
        assert comparison in [
            ComparisonType.EQUAL,
            ComparisonType.NOT_EQUAL,
        ], "ChangeStateCondition may only use equal or not_equal comparison"
        if comparison == ComparisonType.EQUAL:
            return change.get_state() == self._params["state"]
        return change.get_state() != self._params["state"]

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> Condition:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Condition: An instance of the Condition.
        """

        comparison = data["comparison"]
        if not ComparisonType.has_value(comparison):
            comparison = ComparisonType.from_name(comparison)
        else:
            comparison = ComparisonType.from_value(comparison)

        state = data["state"]
        if not ChangeState.has_value(state):
            state = ChangeState.from_name(state)
        else:
            state = ChangeState.from_value(state)

        return ChangeStateCondition({"comparison": comparison, "state": state})
