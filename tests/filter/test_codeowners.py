# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import patch, MagicMock
from autotransform.filter.codeowners import CodeownersFilter
from autotransform.filter.base import FilterName
from autotransform.item.file import FileItem
from codeowners import CodeOwners


def test_codeowners_filter_initialization():
    """Test if the CodeownersFilter class is correctly initialized."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="owner")
    assert codeowners_filter.codeowners_file_path == "path/to/codeowners"
    assert codeowners_filter.owner == "owner"
    assert codeowners_filter.name == FilterName.CODEOWNERS


def test_path_legacy_setting_validator():
    """Test the path_legacy_setting_validator method."""
    with pytest.raises(ValueError):
        CodeownersFilter(
            codeowners_file_path="path/to/codeowners", codeowners_location="different/path"
        )
    codeowners_filter = CodeownersFilter(codeowners_location="path/to/codeowners")
    assert codeowners_filter.codeowners_file_path == "path/to/codeowners"


@patch("builtins.open", new_callable=MagicMock)
def test_owners(mock_open):
    """Test the _owners cached property."""
    mock_open.return_value.__enter__.return_value.read.return_value = "owner: /path/to/file"
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners")
    assert isinstance(codeowners_filter._owners, CodeOwners)


def test_formatted_owner():
    """Test the _formatted_owner cached property."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="owner")
    assert codeowners_filter._formatted_owner == "owner"
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners")
    assert codeowners_filter._formatted_owner is None


@patch.object(CodeOwners, "of")
@patch("builtins.open", new_callable=MagicMock)
def test_is_valid(mock_open, mock_of):
    """Test the _is_valid method."""
    mock_open.return_value.__enter__.return_value.read.return_value = "owner: /path/to/file"
    mock_of.return_value = [("owner", "@owner")]
    item = FileItem(path="/path/to/file", key="file_key")
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter._is_valid(item) is True
    codeowners_filter = CodeownersFilter(
        codeowners_file_path="path/to/codeowners", owner="@different_owner"
    )
    assert codeowners_filter._is_valid(item) is False
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners")
    assert codeowners_filter._is_valid(item) is False
    mock_of.return_value = []
    assert codeowners_filter._is_valid(item) is True
    assert codeowners_filter._is_valid("not a FileItem") is False
