# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the CreatedAgoCondition."""

from __future__ import annotations

import time
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.step.condition.base import ConditionName, SortableComparisonCondition
from autotransform.step.condition.comparison import ComparisonType


class CreatedAgoCondition(SortableComparisonCondition[int]):
    """A condition which checks how long ago a Change was created against the supplied time, all
    in seconds, using the supplied comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (int): The number of seconds to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: int

    name: ClassVar[ConditionName] = ConditionName.CREATED_AGO

    def get_val_from_change(self, change: Change) -> int:
        """Gets how long ago the Change was created.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            int: How long ago the Change was created.
        """

        return int(time.time() - change.get_created_timestamp())
