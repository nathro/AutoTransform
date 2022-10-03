# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ChangeStateCondition."""

from __future__ import annotations

from typing import ClassVar, List

from autotransform.change.base import Change, ChangeState, ReviewState, TestState
from autotransform.step.condition.base import ComparisonCondition, ConditionName
from autotransform.step.condition.comparison import ComparisonType


class ChangeStateCondition(ComparisonCondition[ChangeState]):
    """A condition which checks the ChangeState against the state supplied using the supplied
    comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (ChangeState | List[ChangeState]): The state(s) to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: ChangeState | List[ChangeState]

    name: ClassVar[ConditionName] = ConditionName.CHANGE_STATE

    def get_val_from_change(self, change: Change) -> ChangeState:
        """Gets the state from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            ChangeState: The state of the Change.
        """

        return change.get_state()


class ReviewStateCondition(ComparisonCondition[ReviewState]):
    """A condition which checks the ReviewState against the state supplied using the supplied
    comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (ReviewState | List[ReviewState]): The state(s) to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: ReviewState | List[ReviewState]

    name: ClassVar[ConditionName] = ConditionName.REVIEW_STATE

    def get_val_from_change(self, change: Change) -> ReviewState:
        """Gets the review state from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            ReviewState: The review state of the Change.
        """

        return change.get_review_state()


class TestStateCondition(ComparisonCondition[TestState]):
    """A condition which checks the TestState against the state supplied using the supplied
    comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (TestState | List[TestState]): The state(s) to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: TestState | List[TestState]

    name: ClassVar[ConditionName] = ConditionName.TEST_STATE

    def get_val_from_change(self, change: Change) -> TestState:
        """Gets the state from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            TestState: The test state of the Change.
        """

        return change.get_test_state()
