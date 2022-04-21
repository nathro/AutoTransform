# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests that the ItemFactory has all types included."""

from autotransform.item.factory import ItemFactory
from autotransform.item.type import ItemType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for item_type in ItemType:
        # pylint: disable=protected-access
        if item_type not in ItemFactory._map:
            missing_values.append(item_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
