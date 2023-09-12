# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import Mock
from autotransform.change.base import Change
from autotransform.step.condition.base import ConditionName
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.updated import UpdatedAgoCondition
from time import time as current_time


def test_updated_ago_condition_initialization():
    """Test that the UpdatedAgoCondition class is correctly initialized."""
    condition = UpdatedAgoCondition(comparison=ComparisonType.EQUAL, value=10)
    assert condition.comparison == ComparisonType.EQUAL
    assert condition.value == 10
    assert condition.name == ConditionName.UPDATED_AGO


def test_get_val_from_change():
    """Test that the get_val_from_change method correctly calculates and returns how long ago the Change was updated."""
    change = Mock(spec=Change)
    change.get_last_updated_timestamp.return_value = current_time() - 5
    condition = UpdatedAgoCondition(comparison=ComparisonType.EQUAL, value=10)
    assert condition.get_val_from_change(change) == 5


def test_get_val_from_change_no_update():
    """Test that the get_val_from_change method correctly handles a Change object that has not been updated."""
    change = Mock(spec=Change)
    change.get_last_updated_timestamp.return_value = current_time()
    condition = UpdatedAgoCondition(comparison=ComparisonType.EQUAL, value=10)
    assert condition.get_val_from_change(change) == 0


def test_get_val_from_change_future_update():
    """Test that the get_val_from_change method correctly handles a Change object that was updated in the future."""
    change = Mock(spec=Change)
    change.get_last_updated_timestamp.return_value = current_time() + 5
    condition = UpdatedAgoCondition(comparison=ComparisonType.EQUAL, value=10)
    assert condition.get_val_from_change(change) < 0


def test_get_val_from_change_no_method():
    """Test that the get_val_from_change method correctly handles a Change object that does not have a get_last_updated_timestamp method."""
    change = Mock()
    condition = UpdatedAgoCondition(comparison=ComparisonType.EQUAL, value=10)
    with pytest.raises(TypeError):
        condition.get_val_from_change(change)
