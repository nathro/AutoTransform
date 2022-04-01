# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests that the schema factory has all types included."""

from autotransform.schema.factory import SchemaBuilderFactory
from autotransform.schema.name import SchemaBuilderName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory getters."""
    missing_values = []
    for schema in SchemaBuilderName:
        # pylint: disable=protected-access
        if schema not in SchemaBuilderFactory._map:
            missing_values.append(schema)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
