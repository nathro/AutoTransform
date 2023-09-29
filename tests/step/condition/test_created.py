# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch, Mock
from autotransform.step.condition.created import CreatedAgoCondition
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.base import ConditionName


class TestCreatedAgoCondition:
    """Test cases for the CreatedAgoCondition class."""

    @patch("time.time", return_value=1000)
    def test_get_val_from_change(self, mock_time):
        """Test if the get_val_from_change method correctly calculates the time difference."""
        change = Mock()
        change.get_created_timestamp.return_value = 900
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == 100

    @patch("time.time", return_value=1000)
    def test_get_val_from_change_future_timestamp(self, mock_time):
        """Test if the get_val_from_change method handles a future timestamp correctly."""
        change = Mock()
        change.get_created_timestamp.return_value = 1100
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == -100

    @patch("time.time", return_value=1000)
    def test_get_val_from_change_current_timestamp(self, mock_time):
        """Test if the get_val_from_change method handles the current timestamp correctly."""
        change = Mock()
        change.get_created_timestamp.return_value = 1000
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == 0

    def test_name_attribute(self):
        """Test if the CreatedAgoCondition class correctly sets the name attribute."""
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.name == ConditionName.CREATED_AGO

    def test_comparison_attribute(self):
        """Test if the CreatedAgoCondition class correctly sets the comparison attribute."""
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.comparison == ComparisonType.EQUAL

    def test_value_attribute_single_int(self):
        """Test if the CreatedAgoCondition class correctly handles a single integer value."""
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.value == 100
