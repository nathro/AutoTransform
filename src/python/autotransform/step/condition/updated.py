# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for all conditions handling when a Change was updated."""

from typing import ClassVar, List, Union

from autotransform.change.base import Change
from autotransform.step.condition.base import ConditionName, SortableComparisonCondition
from autotransform.step.condition.comparison import ComparisonType
from time import time as current_time


class UpdatedAgoCondition(SortableComparisonCondition[int]):
    """A condition which checks how long ago a Change was updated against the supplied time, all
    in seconds, using the supplied comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (Union[int, List[int]]): The number of seconds to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: Union[int, List[int]]

    name: ClassVar[ConditionName] = ConditionName.UPDATED_AGO

    def get_val_from_change(self, change: Change) -> int:
        """Gets how long ago the Change was updated.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            int: How long ago the Change was updated.
        """

        return int(current_time() - change.get_last_updated_timestamp())
