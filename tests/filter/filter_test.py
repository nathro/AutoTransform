# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Utility methods for testing Filter components."""

from typing import Dict

from autotransform.filter.base import Filter


def run_filter_tests(filt: Filter, test_cases: Dict[str, bool]) -> None:
    """A simple utility method for handling running tests of Filter components

    Args:
        filt (Filter): The Filter being tests.
        test_cases (Dict[str, bool]): A mapping from test case key to expected result.
    """
    for key, result in test_cases.items():
        assert filt.is_valid(key) == result
