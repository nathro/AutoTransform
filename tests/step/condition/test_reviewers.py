# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

from unittest.mock import Mock
from autotransform.change.base import Change
from autotransform.step.condition.reviewers import ReviewersCondition, TeamReviewersCondition
from autotransform.step.condition.base import ConditionName
from autotransform.step.condition.comparison import ComparisonType


def test_reviewers_condition_get_val_from_change():
    """Test the get_val_from_change method of the ReviewersCondition class."""
    change = Mock(spec=Change)
    change.get_reviewers.return_value = ["reviewer1", "reviewer2"]
    condition = ReviewersCondition(comparison=ComparisonType.CONTAINS, value="reviewer1")
    assert condition.get_val_from_change(change) == ["reviewer1", "reviewer2"]


def test_team_reviewers_condition_get_val_from_change():
    """Test the get_val_from_change method of the TeamReviewersCondition class."""
    change = Mock(spec=Change)
    change.get_team_reviewers.return_value = ["team1", "team2"]
    condition = TeamReviewersCondition(comparison=ComparisonType.CONTAINS, value="team1")
    assert condition.get_val_from_change(change) == ["team1", "team2"]


def test_reviewers_condition_name():
    """Test the name attribute of the ReviewersCondition class."""
    condition = ReviewersCondition(comparison=ComparisonType.CONTAINS, value="reviewer1")
    assert condition.name == ConditionName.REVIEWERS


def test_team_reviewers_condition_name():
    """Test the name attribute of the TeamReviewersCondition class."""
    condition = TeamReviewersCondition(comparison=ComparisonType.CONTAINS, value="team1")
    assert condition.name == ConditionName.TEAM_REVIEWERS


def test_reviewers_condition_comparison():
    """Test the comparison attribute of the ReviewersCondition class."""
    condition = ReviewersCondition(comparison=ComparisonType.CONTAINS, value="reviewer1")
    assert condition.comparison == ComparisonType.CONTAINS


def test_team_reviewers_condition_comparison():
    """Test the comparison attribute of the TeamReviewersCondition class."""
    condition = TeamReviewersCondition(comparison=ComparisonType.CONTAINS, value="team1")
    assert condition.comparison == ComparisonType.CONTAINS


def test_reviewers_condition_value():
    """Test the value attribute of the ReviewersCondition class."""
    condition = ReviewersCondition(comparison=ComparisonType.CONTAINS, value="reviewer1")
    assert condition.value == "reviewer1"


def test_team_reviewers_condition_value():
    """Test the value attribute of the TeamReviewersCondition class."""
    condition = TeamReviewersCondition(comparison=ComparisonType.CONTAINS, value="team1")
    assert condition.value == "team1"
