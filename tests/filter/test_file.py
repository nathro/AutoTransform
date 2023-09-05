# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the implementation of file filters."""

from autotransform.filter.base import FilterName
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.filter.file import FileExistsFilter


def test_file_exists_filter():
    """Test the FileExistsFilter class."""

    # Test with a FileItem that has a valid file path
    file_item = FileItem(key="path/to/existing/file")
    file_filter = FileExistsFilter()
    assert file_filter._is_valid(file_item) is False

    # Test with a FileItem that has an invalid file path
    file_item = FileItem(key="path/to/nonexistent/file")
    assert file_filter._is_valid(file_item) is False

    # Test with a non-FileItem object
    item = Item(key="item")
    assert file_filter._is_valid(item) is False

    # Test with a FileItem that has a valid target_path
    file_item = FileItem(
        key="path/to/existing/file", extra_data={"target_path": "path/to/existing/target"}
    )
    file_filter = FileExistsFilter(check_target_path=True)
    assert file_filter._is_valid(file_item) is False

    # Test with a FileItem that has an invalid target_path
    file_item = FileItem(
        key="path/to/existing/file", extra_data={"target_path": "path/to/nonexistent/target"}
    )
    assert file_filter._is_valid(file_item) is False

    # Test with a FileItem that has a non-string target_path
    file_item = FileItem(key="path/to/existing/file", extra_data={"target_path": 123})
    assert file_filter._is_valid(file_item) is False

    # Test with a FileItem that has no target_path
    file_item = FileItem(key="path/to/existing/file", extra_data={})
    assert file_filter._is_valid(file_item) is False

    # Test with a FileItem that has no extra_data
    file_item = FileItem(key="path/to/existing/file")
    assert file_filter._is_valid(file_item) is False


def test_file_exists_filter_name():
    """Test the name attribute of the FileExistsFilter class."""
    file_filter = FileExistsFilter()
    assert file_filter.name == FilterName.FILE_EXISTS
