# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the ConditionFactory has all types included."""

from autotransform.step.condition.factory import ConditionFactory
from autotransform.step.condition.type import ConditionType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = [
        change_type
        for change_type in ConditionType
        # pylint: disable=protected-access
        if change_type not in ConditionFactory._map
    ]
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
