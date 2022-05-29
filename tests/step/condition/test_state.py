# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the ChangeStateCondition works as expected."""

import mock
import pytest

from autotransform.change.base import Change, ChangeState
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.state import ChangeStateCondition


def test_non_used_comparisons():
    """Checks that all unused comparisons assert as expected."""

    mock_change = mock.create_autospec(Change)
    mock_change.get_state.return_value = ChangeState.APPROVED

    condition = ChangeStateCondition(
        state=ChangeState.APPROVED, comparison=ComparisonType.GREATER_THAN
    )
    with pytest.raises(
        AssertionError, match="ChangeStateCondition may only use equal or not_equal comparison"
    ):
        condition.check(mock_change)

    condition = ChangeStateCondition(
        state=ChangeState.APPROVED, comparison=ComparisonType.GREATER_THAN_OR_EQUAL
    )
    with pytest.raises(
        AssertionError, match="ChangeStateCondition may only use equal or not_equal comparison"
    ):
        condition.check(mock_change)

    condition = ChangeStateCondition(
        state=ChangeState.APPROVED, comparison=ComparisonType.LESS_THAN
    )
    with pytest.raises(
        AssertionError, match="ChangeStateCondition may only use equal or not_equal comparison"
    ):
        condition.check(mock_change)

    condition = ChangeStateCondition(
        state=ChangeState.APPROVED, comparison=ComparisonType.LESS_THAN_OR_EQUAL
    )
    with pytest.raises(
        AssertionError, match="ChangeStateCondition may only use equal or not_equal comparison"
    ):
        condition.check(mock_change)
