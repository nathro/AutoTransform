# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the BatcherFactory has all types included."""

from autotransform.batcher.factory import BatcherFactory
from autotransform.batcher.type import BatcherType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for batcher_type in BatcherType:
        # pylint: disable=protected-access
        if batcher_type not in BatcherFactory._map:
            missing_values.append(batcher_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
