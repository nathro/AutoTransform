# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import Mock
from autotransform.step.condition.schema import SchemaNameCondition
from autotransform.step.condition.comparison import ComparisonType


class TestSchemaNameCondition:
    """Test cases for the SchemaNameCondition class."""

    @pytest.fixture
    def change(self):
        """Fixture for creating a Change object with a specific schema name."""
        change = Mock()
        change.get_schema_name.return_value = "test_schema"
        return change

    def test_get_val_from_change(self, change):
        """Test if the get_val_from_change method correctly retrieves the schema name from a Change object."""
        condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="test_schema")
        assert condition.get_val_from_change(change) == "test_schema"

    def test_comparison(self, change):
        """Test if the SchemaNameCondition correctly performs a comparison."""
        condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="test_schema")
        assert condition.check(change)

        condition = SchemaNameCondition(comparison=ComparisonType.NOT_EQUAL, value="wrong_schema")
        assert condition.check(change)

    def test_empty_value(self, change):
        """Test if the SchemaNameCondition correctly handles a comparison when the value attribute is an empty string."""
        condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="")
        assert not condition.check(change)

    def test_partial_match(self, change):
        """Test if the SchemaNameCondition correctly handles a comparison when the value attribute partially matches a schema name in the Change object."""
        condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="test")
        assert not condition.check(change)

    def test_exact_match(self, change):
        """Test if the SchemaNameCondition correctly handles a comparison when the value attribute exactly matches a schema name in the Change object."""
        condition = SchemaNameCondition(comparison=ComparisonType.EQUAL, value="test_schema")
        assert condition.check(change)
