# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for all conditions handling when a Change was updated."""

from __future__ import annotations

import time
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.step.condition.base import Condition, ConditionName
from autotransform.step.condition.comparison import ComparisonType, compare


class UpdatedAgoCondition(Condition):
    """A condition which checks how long ago a Change was updated against the supplied time, all
    in seconds, using the supplied comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        time (int): The number of seconds to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    time: int

    name: ClassVar[ConditionName] = ConditionName.UPDATED_AGO

    def check(self, change: Change) -> bool:
        """Checks whether how long ago the Change was updated passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        time_since_updated = time.time() - change.get_last_updated_timestamp()
        return compare(time_since_updated, self.time, self.comparison)
