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
from codeowners import CodeOwners


def test__owners():
    """Test the _owners method."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
        assert isinstance(codeowners_filter._owners, CodeOwners)


def test__formatted_owner():
    """Test the _formatted_owner method."""
    codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


def test__is_valid():
    """Test the _is_valid method."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
        file_item = FileItem(path="file.py")
        assert codeowners_filter._is_valid(file_item) is True

        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner=None)
        assert not codeowners_filter._is_valid(file_item)

        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@other")
        assert not codeowners_filter._is_valid(file_item)


def test__is_valid_not_file_item():
    """Test the _is_valid method with an input that is not a FileItem."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_location="CODEOWNERS", owner="@owner")
        not_file_item = "not a file item"
        assert not codeowners_filter._is_valid(not_file_item)
