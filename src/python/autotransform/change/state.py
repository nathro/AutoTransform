# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The state of a Change, used to handle potential updates for a change."""

from enum import Enum
from typing import Any


class ChangeState(str, Enum):
    """A simple enum for the state of a given Change in code review or version
    control systems."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    CLOSED = "closed"
    MERGED = "merged"
    OPEN = "open"

    @staticmethod
    def has_value(value: Any) -> bool:
        """Checks is the provided value is a valid value for this enum.

        Args:
            value (Any): An unknown value.

        Returns:
            [bool]: Whether the value is present in the enum.
        """

        # pylint: disable=no-member

        return value in ChangeState._value2member_map_

    @staticmethod
    def from_name(name: str) -> Enum:
        """Gets the enum value associated with a name.

        Args:
            name (str): The name of a member of the enum.

        Returns:
            ChangeState: The associated enum value.
        """

        # pylint: disable=no-member

        return ChangeState._member_map_[name]

    @staticmethod
    def from_value(value: int) -> Enum:
        """Gets the enum value associated with an int value.

        Args:
            value (str): The value of a member of the enum.

        Returns:
            ChangeState: The associated enum value.
        """

        # pylint: disable=no-member

        return ChangeState._value2member_map_[value]
