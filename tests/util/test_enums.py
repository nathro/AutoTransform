# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for enums used by utilities of AutoTransform or across a number of components."""

from autotransform.util.enums import AggregatorType, SchemaType


def test_aggregator_type_str_representation():
    """Test if the AggregatorType enum correctly returns its string representation."""
    assert AggregatorType.ALL == "all"
    assert AggregatorType.ANY == "any"


def test_schema_type_str_representation():
    """Test if the SchemaType enum correctly returns its string representation."""
    assert SchemaType.BUILDER == "builder"
    assert SchemaType.FILE == "file"


def test_aggregator_type_comparison_with_string():
    """Test if the AggregatorType enum can be correctly compared with a string."""
    assert AggregatorType.ALL == "all"
    assert AggregatorType.ANY == "any"


def test_schema_type_comparison_with_string():
    """Test if the SchemaType enum can be correctly compared with a string."""
    assert SchemaType.BUILDER == "builder"
    assert SchemaType.FILE == "file"


def test_aggregator_type_comparison_with_invalid_string():
    """Test if the AggregatorType enum returns False when compared with an invalid string."""
    assert AggregatorType.ALL != "none"
    assert AggregatorType.ANY != "none"


def test_schema_type_comparison_with_invalid_string():
    """Test if the SchemaType enum returns False when compared with an invalid string."""
    assert SchemaType.BUILDER != "none"
    assert SchemaType.FILE != "none"


def test_aggregator_type_iteration():
    """Test if the AggregatorType enum correctly iterates over its values."""
    assert list(AggregatorType) == [AggregatorType.ALL, AggregatorType.ANY]


def test_schema_type_iteration():
    """Test if the SchemaType enum correctly iterates over its values."""
    assert list(SchemaType) == [SchemaType.BUILDER, SchemaType.FILE]
