# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the FileExistsFilter class."""

import pytest
from pathlib import Path
from autotransform.filter.file import FileExistsFilter
from autotransform.filter.base import Filter, FilterName
from autotransform.item.file import FileItem
from autotransform.item.base import Item


def test_inheritance():
    """Test that FileExistsFilter correctly inherits from Filter."""
    assert issubclass(FileExistsFilter, Filter)


def test_default_check_target_path():
    """Test that check_target_path is False by default."""
    file_filter = FileExistsFilter()
    assert not file_filter.check_target_path


def test_name():
    """Test that name is correctly set to FilterName.FILE_EXISTS."""
    file_filter = FileExistsFilter()
    assert file_filter.name == FilterName.FILE_EXISTS


def test_is_valid_not_file_item():
    """Test _is_valid method when item is not a FileItem."""
    file_filter = FileExistsFilter()
    item = Item(key="test")
    assert not file_filter._is_valid(item)


@pytest.mark.parametrize("file_exists", [True, False])
def test_is_valid_check_path(file_exists, tmp_path):
    """Test _is_valid method when check_target_path is False."""
    file_filter = FileExistsFilter()
    path = str(tmp_path / "test.txt")
    file_item = FileItem(key=path)
    if file_exists:
        Path(path).touch()
    assert file_filter._is_valid(file_item) == file_exists


@pytest.mark.parametrize("file_exists", [True, False])
def test_is_valid_check_target_path(file_exists, tmp_path):
    """Test _is_valid method when check_target_path is True."""
    file_filter = FileExistsFilter(check_target_path=True)
    path = str(tmp_path / "test.txt")
    file_item = FileItem(key="test", extra_data={"target_path": path})
    if file_exists:
        Path(path).touch()
    assert file_filter._is_valid(file_item) == file_exists


def test_is_valid_path_none():
    """Test _is_valid method when path to check is None."""
    file_filter = FileExistsFilter()
    file_item = FileItem(key="test")
    assert not file_filter._is_valid(file_item)


def test_is_valid_path_not_string():
    """Test _is_valid method when path to check is not a string."""
    file_filter = FileExistsFilter()
    file_item = FileItem(key=123)
    assert not file_filter._is_valid(file_item)
