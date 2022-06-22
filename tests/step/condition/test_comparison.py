# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that comparisons for Conditions work as expected."""

from autotransform.step.condition.comparison import ComparisonType, compare


def test_equal_comparison():
    """Tests equal comparison checking."""

    assert compare(5, 0, ComparisonType.EQUAL) is False
    assert compare(0, 0, ComparisonType.EQUAL) is True
    assert compare(-5, 0, ComparisonType.EQUAL) is False


def test_not_equal_comparison():
    """Tests not equal comparison checking."""

    assert compare(5, 0, ComparisonType.NOT_EQUAL) is True
    assert compare(0, 0, ComparisonType.NOT_EQUAL) is False
    assert compare(-5, 0, ComparisonType.NOT_EQUAL) is True


def test_greater_than_comparison():
    """Tests greater than comparison checking."""

    assert compare(5, 0, ComparisonType.GREATER_THAN) is True
    assert compare(0, 0, ComparisonType.GREATER_THAN) is False
    assert compare(-5, 0, ComparisonType.GREATER_THAN) is False


def test_greater_than_or_equal_comparison():
    """Tests greater than or equal comparison checking."""

    assert compare(5, 0, ComparisonType.GREATER_THAN_OR_EQUAL) is True
    assert compare(0, 0, ComparisonType.GREATER_THAN_OR_EQUAL) is True
    assert compare(-5, 0, ComparisonType.GREATER_THAN_OR_EQUAL) is False


def test_less_than_comparison():
    """Tests less than comparison checking."""

    assert compare(5, 0, ComparisonType.LESS_THAN) is False
    assert compare(0, 0, ComparisonType.LESS_THAN) is False
    assert compare(-5, 0, ComparisonType.LESS_THAN) is True


def test_less_than_or_equal_comparison():
    """Tests less than or equal comparison checking."""

    assert compare(5, 0, ComparisonType.LESS_THAN_OR_EQUAL) is False
    assert compare(0, 0, ComparisonType.LESS_THAN_OR_EQUAL) is True
    assert compare(-5, 0, ComparisonType.LESS_THAN_OR_EQUAL) is True
