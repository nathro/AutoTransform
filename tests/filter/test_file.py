# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""
This module contains tests for the FileExistsFilter class from the autotransform.filter.file module.
"""

from autotransform.filter.file import FileExistsFilter
from autotransform.item.file import FileItem
from autotransform.item.base import Item


def test_file_exists_filter_initialization():
    """Test the initialization of FileExistsFilter with default values."""
    file_filter = FileExistsFilter()
    assert not file_filter.check_target_path
    assert file_filter.name.value == "file_exists"


def test_file_exists_filter_custom_initialization():
    """Test the initialization of FileExistsFilter with custom values."""
    file_filter = FileExistsFilter(check_target_path=True)
    assert file_filter.check_target_path


def test_is_valid_non_file_item():
    """Test the _is_valid method with a non-FileItem instance."""
    file_filter = FileExistsFilter()
    item = Item(key="key")
    assert not file_filter._is_valid(item)


def test_is_valid_none_path():
    """Test the _is_valid method with a None path."""
    file_filter = FileExistsFilter()
    item = FileItem(key="key")
    assert not file_filter._is_valid(item)


def test_is_valid_non_string_path():
    """Test the _is_valid method with a non-string path."""
    file_filter = FileExistsFilter()
    item = FileItem(key=123)
    assert not file_filter._is_valid(item)


def test_is_valid_invalid_file_path():
    """Test the _is_valid method with an invalid file path."""
    file_filter = FileExistsFilter()
    item = FileItem(key="invalid/path")
    assert not file_filter._is_valid(item)


def test_is_valid_non_existent_file():
    """Test the _is_valid method with a non-existent file."""
    file_filter = FileExistsFilter()
    item = FileItem(key="non_existent_file.txt")
    assert not file_filter._is_valid(item)


def test_is_valid_existing_file(tmp_path):
    """Test the _is_valid method with an existing file."""
    file_filter = FileExistsFilter()
    file = tmp_path / "test_file.txt"
    file.write_text("content")
    item = FileItem(key=str(file))
    assert file_filter._is_valid(item)


def test_is_valid_target_path_true_existing_file(tmp_path):
    """Test the _is_valid method with check_target_path=True and an existing file."""
    file_filter = FileExistsFilter(check_target_path=True)
    file = tmp_path / "test_file.txt"
    file.write_text("content")
    item = FileItem(key="key", extra_data={"target_path": str(file)})
    assert file_filter._is_valid(item)


def test_is_valid_target_path_true_non_existent_file():
    """Test the _is_valid method with check_target_path=True and a non-existent file."""
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="key", extra_data={"target_path": "non_existent_file.txt"})
    assert not file_filter._is_valid(item)


def test_is_valid_target_path_false_existing_file(tmp_path):
    """Test the _is_valid method with check_target_path=False and an existing file."""
    file_filter = FileExistsFilter(check_target_path=False)
    file = tmp_path / "test_file.txt"
    file.write_text("content")
    item = FileItem(key=str(file))
    assert file_filter._is_valid(item)


def test_is_valid_target_path_false_non_existent_file():
    """Test the _is_valid method with check_target_path=False and a non-existent file."""
    file_filter = FileExistsFilter(check_target_path=False)
    item = FileItem(key="non_existent_file.txt")
    assert not file_filter._is_valid(item)
