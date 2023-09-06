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


def test_codeowners_filter_initialization():
    """Test if the CodeownersFilter class is correctly initialized."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter.codeowners_file_path == "path/to/codeowners"
    assert codeowners_filter.owner == "@owner"


def test_path_legacy_setting_validator():
    """Test if the path_legacy_setting_validator method correctly validates the codeowners_file_path."""
    with pytest.raises(ValueError):
        CodeownersFilter(
            codeowners_file_path="path/to/codeowners", codeowners_location="path/to/legacy"
        )


def test_owners():
    """Test if the _owners method correctly parses the CodeOwners file."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(
            codeowners_file_path="path/to/codeowners", owner="@owner"
        )
        assert isinstance(codeowners_filter._owners, CodeOwners)


def test_formatted_owner():
    """Test if the _formatted_owner method correctly formats the owner."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


def test_is_valid():
    """Test if the _is_valid method correctly checks whether the Item is a file owned by the supplied owner."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(
            codeowners_file_path="path/to/codeowners", owner="@owner"
        )
        item = FileItem(path="path/to/file", key="key")
        assert codeowners_filter._is_valid(item) is True


def test_is_valid_unowned():
    """Test if the _is_valid method correctly checks for unowned files when no owner is supplied."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner=None)
        item = FileItem(path="path/to/file", key="key")
        assert not codeowners_filter._is_valid(item)


def test_is_valid_not_file_item():
    """Test if the _is_valid method returns False when the Item is not an instance of FileItem."""
    with patch("builtins.open", mock_open(read_data="* @owner")):
        codeowners_filter = CodeownersFilter(
            codeowners_file_path="path/to/codeowners", owner="@owner"
        )
        item = "not a FileItem"
        assert not codeowners_filter._is_valid(item)


def test_name():
    """Test if the name attribute of the CodeownersFilter class is correctly set."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter.name == FilterName.CODEOWNERS
