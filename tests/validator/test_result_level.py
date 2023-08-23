# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that ValidationResultLevel works as expected."""

from autotransform.validator.base import ValidationResultLevel

# pylint: disable=unneeded-not


def test_comparisons():
    """Test that comparison checks work"""
    levels = [
        ValidationResultLevel.NONE,
        ValidationResultLevel.WARNING,
        ValidationResultLevel.ERROR,
    ]
    for i, level1 in enumerate(levels):
        for j, level2 in enumerate(levels):
            assert (level1 > level2) == (i > j)
            assert (level1 >= level2) == (i >= j)
            assert (level1 < level2) == (i < j)
            assert (level1 <= level2) == (i <= j)
            assert (level1 == level2) == (i == j)
            assert (level1 != level2) == (i != j)
