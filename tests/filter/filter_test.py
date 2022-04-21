# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Utility methods for testing Filter components."""

from typing import List, Tuple

from autotransform.filter.base import Filter
from autotransform.item.base import Item


def run_filter_tests(filt: Filter, test_cases: List[Tuple[Item, bool]]) -> None:
    """A simple utility method for handling running tests of Filter components

    Args:
        filt (Filter): The Filter being tests.
        test_cases (List[Tuple[Item, bool]]): A list of test Items with their expected result.
    """

    for item, result in test_cases:
        assert filt.is_valid(item) == result
