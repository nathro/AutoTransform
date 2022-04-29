# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the StepFactory has all types included."""

from autotransform.step.factory import StepFactory
from autotransform.step.type import StepType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for change_type in StepType:
        # pylint: disable=protected-access
        if change_type not in StepFactory._map:
            missing_values.append(change_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
