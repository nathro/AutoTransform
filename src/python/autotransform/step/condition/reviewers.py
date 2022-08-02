# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for Conditions based on reviewers."""

from __future__ import annotations

from typing import ClassVar, List, Optional

from autotransform.change.base import Change
from autotransform.step.condition.base import ConditionName, ListComparisonCondition
from autotransform.step.condition.comparison import ComparisonType


class ReviewersCondition(ListComparisonCondition[str]):
    """A condition which checks the reviewers for a Change.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (optional, Optional[str]): The reviewer to check for. Defaults to None.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: Optional[str] = None

    name: ClassVar[ConditionName] = ConditionName.REVIEWERS

    def get_val_from_change(self, change: Change) -> List[str]:
        """Gets the reviewers from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            List[str]: The reviewers of the Change.
        """

        return change.get_reviewers()


class TeamReviewersCondition(ListComparisonCondition[str]):
    """A condition which checks the team reviewers for a Change.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (optional, Optional[str]): The team reviewer to check for. Defaults to None.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: Optional[str] = None

    name: ClassVar[ConditionName] = ConditionName.TEAM_REVIEWERS

    def get_val_from_change(self, change: Change) -> List[str]:
        """Gets the team reviewers from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            List[str]: The team reviewers of the Change.
        """

        return change.get_team_reviewers()
