# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.filter.codeowners import CodeownersFilter
from autotransform.item.file import FileItem
from autotransform.item.base import Item
from codeowners import CodeOwners
from unittest.mock import patch, mock_open


def test_path_legacy_setting_validator_both_supplied():
    with pytest.raises(ValueError):
        CodeownersFilter.path_legacy_setting_validator(
            {"codeowners_file_path": "path1", "codeowners_location": "path2"}
        )


def test_path_legacy_setting_validator_only_location_supplied():
    assert CodeownersFilter.path_legacy_setting_validator({"codeowners_location": "path"}) == {
        "codeowners_file_path": "path",
        "codeowners_location": "path",
    }


def test_path_legacy_setting_validator_only_path_supplied():
    assert CodeownersFilter.path_legacy_setting_validator({"codeowners_file_path": "path"}) == {
        "codeowners_file_path": "path"
    }


@patch("builtins.open", new_callable=mock_open, read_data="data")
def test__owners(mock_file):
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner=None)
    assert isinstance(codeowners_filter._owners, CodeOwners)


def test__formatted_owner_with_owner():
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


def test__formatted_owner_without_owner():
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner=None)
    assert codeowners_filter._formatted_owner is None


@patch.object(CodeOwners, "of")
@patch("builtins.open", new_callable=mock_open, read_data="data")
def test__is_valid_with_owned_file(mock_file, mock_of):
    mock_of.return_value = [("@owner", "@owner")]
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner="@owner")
    assert codeowners_filter._is_valid(FileItem(path="file_path", key="key")) is True


@patch.object(CodeOwners, "of")
@patch("builtins.open", new_callable=mock_open, read_data="data")
def test__is_valid_with_unowned_file(mock_file, mock_of):
    mock_of.return_value = []
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner="@owner")
    assert codeowners_filter._is_valid(FileItem(path="file_path", key="key")) is False


@patch.object(CodeOwners, "of")
@patch("builtins.open", new_callable=mock_open, read_data="data")
def test__is_valid_with_unowned_file_no_owner(mock_file, mock_of):
    mock_of.return_value = []
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner=None)
    assert codeowners_filter._is_valid(FileItem(path="file_path", key="key")) is True


@patch.object(CodeOwners, "of")
@patch("builtins.open", new_callable=mock_open, read_data="data")
def test__is_valid_with_owned_file_no_owner(mock_file, mock_of):
    mock_of.return_value = [("@owner", "@owner")]
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner=None)
    assert codeowners_filter._is_valid(FileItem(path="file_path", key="key")) is False


def test__is_valid_with_non_file_item():
    codeowners_filter = CodeownersFilter(codeowners_file_path="path", owner="@owner")
    assert codeowners_filter._is_valid(Item(key="key")) is False
