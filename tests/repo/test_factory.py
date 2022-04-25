# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the RepoFactory has all types included."""

from autotransform.repo.factory import RepoFactory
from autotransform.repo.type import RepoType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map."""

    missing_values = []
    for repo_type in RepoType:
        # pylint: disable=protected-access
        if repo_type not in RepoFactory._map:
            missing_values.append(repo_type)
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)
