# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""An enum representing a type of comparison. Used by Conditions to make determinations
on the type of check to perform. Includes a compare function those Conditions will use."""

from enum import Enum
from typing import Any


class ComparisonType(str, Enum):
    """A list of possible comparisons."""

    # Base Comparisons
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"

    # Sortable Comparisons
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"

    # List Comparisons
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    EMPTY = "empty"
    NOT_EMPTY = "not_empty"


# pylint: disable=too-many-return-statements
def compare(first_val: Any, second_val: Any, comparison: ComparisonType) -> bool:
    """Performs the comparison specified by a ComparisonType.

    Args:
        first_val (Any): The first value of the comparison.
        second_val (Any): The second value of the comparison.
        comparison (ComparisonType): The type of comparison to perform.

    Raises:
        ValueError: Raised when the comparison is not a valid type.

    Returns:
        bool: The results of the comparison.
    """

    if comparison == ComparisonType.EQUAL:
        return first_val == second_val
    if comparison == ComparisonType.NOT_EQUAL:
        return first_val != second_val

    if comparison == ComparisonType.GREATER_THAN:
        return first_val > second_val
    if comparison == ComparisonType.GREATER_THAN_OR_EQUAL:
        return first_val >= second_val
    if comparison == ComparisonType.LESS_THAN:
        return first_val < second_val
    if comparison == ComparisonType.LESS_THAN_OR_EQUAL:
        return first_val <= second_val

    if comparison == ComparisonType.CONTAINS:
        return second_val in first_val
    if comparison == ComparisonType.NOT_CONTAINS:
        return second_val not in first_val
    if comparison == ComparisonType.EMPTY:
        return len(first_val) == 0
    if comparison == ComparisonType.NOT_EMPTY:
        return len(first_val) > 0

    raise ValueError(f"{comparison} is not a valid ComparisonType")
