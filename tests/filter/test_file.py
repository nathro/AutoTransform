# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the implementation of file filters."""

import pytest
from autotransform.filter.file import FileExistsFilter
from autotransform.item.file import FileItem
from autotransform.item.base import Item


def test_file_exists_filter():
    """Test the FileExistsFilter class."""

    # Test with a FileItem where the file does not exist
    item = FileItem(key="non_existent_file.txt")
    file_filter = FileExistsFilter()
    assert not file_filter._is_valid(item)

    # Test with a FileItem where the file does exist
    item = FileItem(key=__file__)  # use this test file as an existing file
    assert file_filter._is_valid(item)

    # Test with a non-FileItem
    item = Item(key="some_key")
    assert not file_filter._is_valid(item)

    # Test with a FileItem and check_target_path set to True
    file_filter.check_target_path = True
    item = FileItem(key="non_existent_file.txt", extra_data={"target_path": __file__})
    assert file_filter._is_valid(item)

    # Test with a FileItem and check_target_path set to True, but the target_path does not exist
    item = FileItem(
        key="non_existent_file.txt", extra_data={"target_path": "non_existent_file.txt"}
    )
    assert not file_filter._is_valid(item)

    # Test with a FileItem and check_target_path set to True, but the target_path is not a string
    item = FileItem(key="non_existent_file.txt", extra_data={"target_path": 123})
    assert not file_filter._is_valid(item)


if __name__ == "__main__":
    pytest.main([__file__])
