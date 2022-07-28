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
from autotransform.step.condition.base import ComparisonCondition, ConditionName
from autotransform.step.condition.comparison import ComparisonType


class ChangeStateCondition(ComparisonCondition[ChangeState]):
    """A condition which checks the ChangeState against the state supplied using the supplied
    comparison. Note: only equals and not equals are valid, all others will result in an error.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (ChangeState): The state to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: ChangeState

    name: ClassVar[ConditionName] = ConditionName.CHANGE_STATE

    def get_val_from_change(self, change: Change) -> ChangeState:
        """Gets the state from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            ChangeState: The state of the Change.
        """

        return change.get_state()
