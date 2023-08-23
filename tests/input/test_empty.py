# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the EmptyInput component."""

from autotransform.input.empty import EmptyInput


def test_input():
    """Tests running EmptyInput component."""

    empty_input = EmptyInput()
    items = empty_input.get_items()

    assert isinstance(items, list), "get_items should return a list."
    assert len(items) == 0, "Empty Input should always return no Items."
