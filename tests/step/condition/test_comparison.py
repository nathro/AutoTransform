# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that comparisons for Conditions work as expected."""

import pytest
from autotransform.step.condition.comparison import ComparisonType, compare


@pytest.mark.parametrize("a, b, expected", [(5, 0, False), (0, 0, True), (-5, 0, False)])
def test_equal_comparison(a, b, expected):
    """Tests equal comparison checking."""
    assert compare(a, b, ComparisonType.EQUAL) is expected


@pytest.mark.parametrize("a, b, expected", [(5, 0, True), (0, 0, False), (-5, 0, True)])
def test_not_equal_comparison(a, b, expected):
    """Tests not equal comparison checking."""
    assert compare(a, b, ComparisonType.NOT_EQUAL) is expected


@pytest.mark.parametrize("a, b, expected", [(5, [0, 1], False), (5, [0, 1, 5], True)])
def test_in_comparison(a, b, expected):
    """Tests in comparison checking."""
    assert compare(a, b, ComparisonType.IN) is expected


@pytest.mark.parametrize("a, b, expected", [(5, [0, 1], True), (5, [0, 1, 5], False)])
def test_not_in_comparison(a, b, expected):
    """Tests not in comparison checking."""
    assert compare(a, b, ComparisonType.NOT_IN) is expected


@pytest.mark.parametrize("a, b, expected", [(5, 0, True), (0, 0, False), (-5, 0, False)])
def test_greater_than_comparison(a, b, expected):
    """Tests greater than comparison checking."""
    assert compare(a, b, ComparisonType.GREATER_THAN) is expected


@pytest.mark.parametrize("a, b, expected", [(5, 0, True), (0, 0, True), (-5, 0, False)])
def test_greater_than_or_equal_comparison(a, b, expected):
    """Tests greater than or equal comparison checking."""
    assert compare(a, b, ComparisonType.GREATER_THAN_OR_EQUAL) is expected


@pytest.mark.parametrize("a, b, expected", [(5, 0, False), (0, 0, False), (-5, 0, True)])
def test_less_than_comparison(a, b, expected):
    """Tests less than comparison checking."""
    assert compare(a, b, ComparisonType.LESS_THAN) is expected


@pytest.mark.parametrize("a, b, expected", [(5, 0, False), (0, 0, True), (-5, 0, True)])
def test_less_than_or_equal_comparison(a, b, expected):
    """Tests less than or equal comparison checking."""
    assert compare(a, b, ComparisonType.LESS_THAN_OR_EQUAL) is expected


@pytest.mark.parametrize("a, b, expected", [([1, 2, 3], 0, False), ([1, 2, 3], 3, True)])
def test_contains_comparison(a, b, expected):
    """Tests contains comparison checking."""
    assert compare(a, b, ComparisonType.CONTAINS) is expected


@pytest.mark.parametrize("a, b, expected", [([1, 2, 3], 0, True), ([1, 2, 3], 3, False)])
def test_not_contains_comparison(a, b, expected):
    """Tests not contains comparison checking."""
    assert compare(a, b, ComparisonType.NOT_CONTAINS) is expected


@pytest.mark.parametrize("a, b, expected", [([], None, True), ([1, 2, 3], None, False)])
def test_empty_comparison(a, b, expected):
    """Tests empty comparison checking."""
    assert compare(a, b, ComparisonType.EMPTY) is expected


@pytest.mark.parametrize("a, b, expected", [([], None, False), ([1, 2, 3], None, True)])
def test_not_empty_comparison(a, b, expected):
    """Tests not empty comparison checking."""
    assert compare(a, b, ComparisonType.NOT_EMPTY) is expected
