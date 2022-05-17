# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the CommandFactory has all types included."""

from autotransform.command.factory import CommandFactory
from autotransform.command.type import CommandType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = [
        command_type
        for command_type in CommandType
        # pylint: disable=protected-access
        if command_type not in CommandFactory._map
    ]
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
