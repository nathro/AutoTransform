# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""An enum representing a type of comparison. Used by Conditions to make determinations
on the type of check to perform."""

from enum import Enum
from typing import Any


class ComparisonType(str, Enum):
    """A list of possible comparisons."""

    EQUALS = "eq"
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
