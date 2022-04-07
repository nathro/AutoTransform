# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests that the inputsource factory has all types included."""

from autotransform.inputsource.factory import InputFactory
from autotransform.inputsource.type import InputType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory getters."""
    missing_values = []
    for inputsource_type in InputType:
        # pylint: disable=protected-access
        if inputsource_type not in InputFactory._getters:
            missing_values.append(inputsource_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
