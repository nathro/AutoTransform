# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ChangeStateCondition."""

from __future__ import annotations

from typing import ClassVar

from autotransform.change.base import Change, ChangeState
from autotransform.step.condition.base import Condition, ConditionName
from autotransform.step.condition.comparison import ComparisonType, compare


class ChangeStateCondition(Condition):
    """A condition which checks the ChangeState against the state supplied using the supplied
    comparison. Note: only equals and not equals are valid, all others willresult in an error.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        state (ChangeState): The state to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    state: ChangeState

    name: ClassVar[ConditionName] = ConditionName.CHANGE_STATE

    @staticmethod
    def get_type() -> ConditionName:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

        return ConditionName.CHANGE_STATE

    def check(self, change: Change) -> bool:
        """Checks whether the Change's state passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        assert self.comparison in [
            ComparisonType.EQUAL,
            ComparisonType.NOT_EQUAL,
        ], "ChangeStateCondition may only use equal or not_equal comparison"
        return compare(change.get_state(), self.state, self.comparison)
