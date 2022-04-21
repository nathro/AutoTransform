# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests that the ValidatorFactory has all types included."""

from autotransform.validator.factory import ValidatorFactory
from autotransform.validator.type import ValidatorType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for validator_type in ValidatorType:
        # pylint: disable=protected-access
        if validator_type not in ValidatorFactory._map:
            missing_values.append(validator_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
