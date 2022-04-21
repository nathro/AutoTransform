# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests that the FilterFactory has all types included."""

from autotransform.filter.factory import FilterFactory
from autotransform.filter.type import FilterType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory getters."""
    missing_values = []
    for filter_type in FilterType:
        # pylint: disable=protected-access
        if filter_type not in FilterFactory._map:
            missing_values.append(filter_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
