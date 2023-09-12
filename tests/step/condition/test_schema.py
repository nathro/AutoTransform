# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the SchemaNameCondition class."""

from unittest.mock import Mock
from autotransform.change.base import Change
from autotransform.step.condition.base import ComparisonCondition, ConditionName
from autotransform.step.condition.schema import SchemaNameCondition
from autotransform.step.condition.comparison import ComparisonType


def test_schema_name_condition_initialization():
    """Test that the SchemaNameCondition class can be instantiated correctly."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    assert isinstance(condition, SchemaNameCondition)


def test_schema_name_condition_comparison_attribute():
    """Test the comparison attribute of a SchemaNameCondition instance."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    assert condition.comparison == ComparisonType.EQUAL


def test_schema_name_condition_value_attribute():
    """Test the value attribute of a SchemaNameCondition instance."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    assert condition.value == "TestSchema"


def test_schema_name_condition_name_attribute():
    """Test the name attribute of a SchemaNameCondition instance."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    assert condition.name == ConditionName.SCHEMA_NAME


def test_get_val_from_change():
    """Test the get_val_from_change method."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    change = Mock(spec=Change)
    change.get_schema_name.return_value = "TestSchema"
    assert condition.get_val_from_change(change) == "TestSchema"


def test_get_val_from_change_return_type():
    """Test the return type of the get_val_from_change method."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    change = Mock(spec=Change)
    change.get_schema_name.return_value = "TestSchema"
    assert isinstance(condition.get_val_from_change(change), str)


def test_schema_name_condition_inheritance():
    """Test that the SchemaNameCondition class correctly inherits from the ComparisonCondition class."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    assert isinstance(condition, ComparisonCondition)


def test_schema_name_condition_implements_required_methods():
    """Test that the SchemaNameCondition class correctly implements the required methods of the ComparisonCondition class."""
    condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="TestSchema")
    assert callable(condition.get_val_from_change)
