# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import patch, mock_open
from autotransform.filter.codeowners import CodeownersFilter
from autotransform.item.file import FileItem
from codeowners import CodeOwners
from pydantic import ValidationError


def test_codeownersfilter_instantiation():
    """Test that the CodeownersFilter class can be instantiated with the correct attributes."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="owner")
    assert codeowners_filter.codeowners_file_path == "path/to/codeowners"
    assert codeowners_filter.owner == "owner"


def test_path_legacy_setting_validator_raises_error():
    """Test that the path_legacy_setting_validator method raises a ValueError when both codeowners_file_path and codeowners_location are supplied."""
    with pytest.raises(ValidationError):
        CodeownersFilter(
            codeowners_file_path="path/to/codeowners", codeowners_location="path/to/location"
        )


def test_path_legacy_setting_validator_updates_path():
    """Test that the path_legacy_setting_validator method correctly updates the codeowners_file_path when only codeowners_location is supplied."""
    codeowners_filter = CodeownersFilter(codeowners_location="path/to/location")
    assert codeowners_filter.codeowners_file_path == "path/to/location"


@patch("builtins.open", new_callable=mock_open, read_data="owner: file")
def test_owners_method(mock_file):
    """Test that the _owners method correctly parses the CodeOwners file."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners")
    assert isinstance(codeowners_filter._owners, CodeOwners)


def test_formatted_owner_method():
    """Test that the _formatted_owner method correctly formats the owner."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


@patch("builtins.open", new_callable=mock_open, read_data="owner: file")
@patch.object(CodeOwners, "of", return_value=[("file", "@owner")])
def test_is_valid_method(mock_codeowners, mock_file):
    """Test that the _is_valid method correctly identifies a file owned by the supplied owner and an unowned file when no owner is supplied."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    file_item = FileItem(path="file", key="key")
    assert codeowners_filter._is_valid(file_item) is True

    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners")
    assert not codeowners_filter._is_valid(file_item)


def test_is_valid_method_returns_false():
    """Test that the _is_valid method returns False when the Item is not a FileItem."""
    codeowners_filter = CodeownersFilter(codeowners_file_path="path/to/codeowners", owner="@owner")
    non_file_item = "non_file_item"
    assert not codeowners_filter._is_valid(non_file_item)


def test_name_class_variable():
    """Test that the name class variable is correctly set to FilterName.CODEOWNERS."""
    assert CodeownersFilter.name.value == "codeowners"
