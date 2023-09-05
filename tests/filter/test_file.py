# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the FileExistsFilter class in the file.py module."""

import pytest
from pathlib import Path
from unittest.mock import patch
from autotransform.filter.base import Filter, FilterName
from autotransform.filter.file import FileExistsFilter
from autotransform.item.base import Item
from autotransform.item.file import FileItem


def test_file_exists_filter_inheritance():
    """Test that FileExistsFilter is a subclass of Filter."""
    assert issubclass(FileExistsFilter, Filter)


def test_file_exists_filter_attributes():
    """Test the default attributes of FileExistsFilter."""
    file_filter = FileExistsFilter()
    assert not file_filter.check_target_path
    assert file_filter.name == FilterName.FILE_EXISTS


def test_is_valid_non_file_item():
    """Test _is_valid method with a non-FileItem instance."""
    file_filter = FileExistsFilter()
    item = Item(key="test")
    assert not file_filter._is_valid(item)


@pytest.mark.parametrize("path, exists", [(Path.cwd(), True), (Path("nonexistent"), False)])
@patch.object(Path, "is_file")
def test_is_valid_with_file_item(mock_is_file, path, exists):
    """Test _is_valid method with a FileItem instance."""
    mock_is_file.return_value = exists
    file_filter = FileExistsFilter()
    item = FileItem(key=str(path))
    assert file_filter._is_valid(item) == exists


@pytest.mark.parametrize("path, exists", [(Path.cwd(), True), (Path("nonexistent"), False)])
@patch.object(Path, "is_file")
def test_is_valid_with_target_path(mock_is_file, path, exists):
    """Test _is_valid method with target_path in extra_data."""
    mock_is_file.return_value = exists
    file_filter = FileExistsFilter()
    file_filter.check_target_path = True
    item = FileItem(key=str(Path.cwd()), extra_data={"target_path": str(path)})
    assert file_filter._is_valid(item) == exists


def test_is_valid_with_none_target_path():
    """Test _is_valid method with None target_path in extra_data."""
    file_filter = FileExistsFilter()
    file_filter.check_target_path = True
    item = FileItem(key=str(Path.cwd()), extra_data={"target_path": None})
    assert not file_filter._is_valid(item)


def test_is_valid_with_non_string_target_path():
    """Test _is_valid method with non-string target_path in extra_data."""
    file_filter = FileExistsFilter()
    file_filter.check_target_path = True
    item = FileItem(key=str(Path.cwd()), extra_data={"target_path": 123})
    assert not file_filter._is_valid(item)
