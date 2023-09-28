# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for Conditions based on labels."""

from typing import ClassVar, List, Optional

from autotransform.change.base import Change
from autotransform.step.condition.base import ConditionName, ListComparisonCondition
from autotransform.step.condition.comparison import ComparisonType


class LabelsCondition(ListComparisonCondition[str]):
    """A condition which checks the labels for a Change.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (Optional[str], optional): The label to check for. Defaults to None.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: Optional[str] = None
    name: ClassVar[ConditionName] = ConditionName.LABELS

    def get_val_from_change(self, change: Change) -> List[str]:
        """Gets the labels from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            List[str]: The labels of the Change.
        """
        if not isinstance(change, Change):
            raise TypeError(f"Expected instance of Change, got {type(change).__name__}")

        return change.get_labels()
