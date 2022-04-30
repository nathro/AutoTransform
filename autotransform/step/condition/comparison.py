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

    EQUAL = "eq"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    NOT_EQUAL = "neq"

    @staticmethod
    def has_value(value: Any) -> bool:
        """Checks is the provided value is a valid value for this enum.

        Args:
            value (Any): An unknown value.

        Returns:
            [bool]: Whether the value is present in the enum.
        """

        # pylint: disable=no-member

        return value in ComparisonType._value2member_map_

    @staticmethod
    def from_name(name: str) -> Enum:
        """Gets the enum value associated with a name.

        Args:
            name (str): The name of a member of the enum.

        Returns:
            ComparisonType: The associated enum value.
        """

        # pylint: disable=no-member

        return ComparisonType._member_map_[name]

    @staticmethod
    def from_value(value: int) -> Enum:
        """Gets the enum value associated with an int value.

        Args:
            value (str): The value of a member of the enum.

        Returns:
            ComparisonType: The associated enum value.
        """

        # pylint: disable=no-member

        return ComparisonType._value2member_map_[value]


def compare(first_val: Any, second_val: Any, comparison: ComparisonType) -> bool:
    """Performs the comparison specified by a ComparisonType

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
    raise ValueError(f"{comparison} is not a valid ComparisonType")
