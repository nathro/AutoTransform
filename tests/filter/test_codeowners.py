# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import patch, mock_open
from autotransform.filter.codeowners import CodeownersFilter
from autotransform.filter.base import FilterName
from autotransform.item.file import FileItem
from codeowners import CodeOwners


def test_codeownersfilter_initialization():
    """Test that the CodeownersFilter class initializes correctly."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="owner")
    assert codeowners_filter.codeowners_file_path == "path/to/codeowners"
    assert codeowners_filter.owner == "owner"
    assert codeowners_filter.name == FilterName.CODEOWNERS


def test_path_legacy_setting_validator():
    """Test that path_legacy_setting_validator method works correctly."""
    with pytest.raises(ValueError):
        CodeownersFilter(
            codeowners_file_path="path/to/codeowners", codeowners_location="another/path"
        )


def test_owners():
    """Test that _owners method works correctly."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(
            codeowners_file_path="path/to/codeowners", owner="owner"
        )
        assert isinstance(codeowners_filter._owners, CodeOwners)


def test_formatted_owner():
    """Test that _formatted_owner method works correctly."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


def test_is_valid():
    """Test that _is_valid method works correctly."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(
            codeowners_file_path="path/to/codeowners", owner="@owner"
        )
        item = FileItem(path="path/to/file", key="key")
        assert codeowners_filter._is_valid(item) is True


def test_is_valid_unowned():
    """Test that _is_valid method works correctly for unowned files."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner=None)
        item = FileItem(path="path/to/file", key="key")
        assert not codeowners_filter._is_valid(item)


def test_is_valid_non_fileitem():
    """Test that _is_valid method returns False when the Item is not a FileItem."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(
            codeowners_file_path="path/to/codeowners", owner="@owner"
        )
        item = "not a FileItem"
        assert not codeowners_filter._is_valid(item)
