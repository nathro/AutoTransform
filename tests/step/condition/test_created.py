# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

from unittest.mock import Mock, patch
from autotransform.change.base import Change
from autotransform.step.condition.created import CreatedAgoCondition
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.base import ConditionName


class TestCreatedAgoCondition:
    """Test cases for the CreatedAgoCondition class."""

    @patch("time.time", return_value=1000)
    def test_get_val_from_change(self, mock_time):
        """Test if the get_val_from_change method correctly calculates the time difference."""
        change = Mock(spec=Change)
        change.get_created_timestamp.return_value = 900
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == 100

    @patch("time.time", return_value=1000)
    def test_get_val_from_change_type(self, mock_time):
        """Test if the get_val_from_change method returns an integer."""
        change = Mock(spec=Change)
        change.get_created_timestamp.return_value = 900
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert isinstance(condition.get_val_from_change(change), int)

    @patch("time.time", return_value=1000)
    def test_get_val_from_change_future_timestamp(self, mock_time):
        """Test if the get_val_from_change method handles future timestamps correctly."""
        change = Mock(spec=Change)
        change.get_created_timestamp.return_value = 1100
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == -100

    @patch("time.time", return_value=1000)
    def test_get_val_from_change_past_timestamp(self, mock_time):
        """Test if the get_val_from_change method handles past timestamps correctly."""
        change = Mock(spec=Change)
        change.get_created_timestamp.return_value = 900
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == 100

    @patch("time.time", return_value=1000)
    def test_get_val_from_change_current_timestamp(self, mock_time):
        """Test if the get_val_from_change method handles current timestamps correctly."""
        change = Mock(spec=Change)
        change.get_created_timestamp.return_value = 1000
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.get_val_from_change(change) == 0

    def test_name_attribute(self):
        """Test if the CreatedAgoCondition class correctly sets its name attribute."""
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.name == ConditionName.CREATED_AGO

    def test_comparison_value_attributes(self):
        """Test if the CreatedAgoCondition class correctly sets its comparison and value attributes."""
        condition = CreatedAgoCondition(comparison=ComparisonType.EQUAL, value=100)
        assert condition.comparison == ComparisonType.EQUAL
        assert condition.value == 100
