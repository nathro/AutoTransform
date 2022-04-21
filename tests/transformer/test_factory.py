# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests that the TransformerFactory has all types included."""

from autotransform.transformer.factory import TransformerFactory
from autotransform.transformer.type import TransformerType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for transformer in TransformerType:
        # pylint: disable=protected-access
        if transformer not in TransformerFactory._map:
            missing_values.append(transformer)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
