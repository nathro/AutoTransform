# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the InputFactory has all types included."""

from autotransform.input.factory import InputFactory
from autotransform.input.type import InputType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for input_type in InputType:
        # pylint: disable=protected-access
        if input_type not in InputFactory._map:
            missing_values.append(input_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
