# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The tests for file filters."""

import pytest
from pathlib import Path
from autotransform.filter.file import FileExistsFilter
from autotransform.item.file import FileItem


def test_file_exists_filter():
    """Test the FileExistsFilter class."""

    # Test with a file that exists
    file_item = FileItem(path=Path(__file__))
    file_filter = FileExistsFilter()
    assert file_filter._is_valid(file_item) is True

    # Test with a file that does not exist
    file_item = FileItem(path=Path("non_existent_file.txt"))
    assert not file_filter._is_valid(file_item)

    # Test with a non-FileItem object
    non_file_item = "This is not a FileItem object"
    assert not file_filter._is_valid(non_file_item)

    # Test with check_target_path set to True and target_path exists
    file_item = FileItem(path=Path(__file__), extra_data={"target_path": str(Path(__file__))})
    file_filter = FileExistsFilter(check_target_path=True)
    assert file_filter._is_valid(file_item) is True

    # Test with check_target_path set to True and target_path does not exist
    file_item = FileItem(path=Path(__file__), extra_data={"target_path": "non_existent_file.txt"})
    assert not file_filter._is_valid(file_item)

    # Test with check_target_path set to True and target_path is not a string
    file_item = FileItem(path=Path(__file__), extra_data={"target_path": 123})
    assert not file_filter._is_valid(file_item)


if __name__ == "__main__":
    pytest.main()
