# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the remote factory has all types included."""

from autotransform.runner.factory import RunnerFactory
from autotransform.runner.type import RunnerType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for runner_type in RunnerType:
        # pylint: disable=protected-access
        if runner_type not in RunnerFactory._map:
            missing_values.append(runner_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
