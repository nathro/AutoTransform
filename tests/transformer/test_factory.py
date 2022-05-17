# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the TransformerFactory has all types included."""

from autotransform.transformer.factory import TransformerFactory
from autotransform.transformer.type import TransformerType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = [
        transformer_type
        for transformer_type in TransformerType
        # pylint: disable=protected-access
        if transformer_type not in TransformerFactory._map
    ]
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
