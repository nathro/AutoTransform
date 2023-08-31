# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The tests for the CodeownersFilter."""

from unittest.mock import patch, mock_open
from autotransform.filter.codeowners import CodeownersFilter
from autotransform.item.file import FileItem


def test_owners():
    """Test the _owners method."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
        assert codeowners_filter._owners.of("/path/to/file") == [("*", "@owner")]


def test_formatted_owner():
    """Test the _formatted_owner method."""
    codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


def test_is_valid():
    """Test the _is_valid method."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
        item = FileItem(path="/path/to/file")
        assert codeowners_filter._is_valid(item) is True

        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner=None)
        assert not codeowners_filter._is_valid(item)

        item = "not a FileItem"
        assert not codeowners_filter._is_valid(item)


def test_is_valid_with_different_owner():
    """Test the _is_valid method with a different owner."""
    with patch("builtins.open", mock_open(read_data="* @other_owner")):
        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
        item = FileItem(path="/path/to/file")
        assert not codeowners_filter._is_valid(item)
