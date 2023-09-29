# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from pathlib import Path
from autotransform.filter.file import FileExistsFilter
from autotransform.item.file import FileItem
from autotransform.item.base import Item


def test_is_valid_non_file_item():
    """Test _is_valid method with non-FileItem instance."""
    file_filter = FileExistsFilter()
    item = Item(key="test")
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_no_path():
    """Test _is_valid method with FileItem instance but no path."""
    file_filter = FileExistsFilter()
    item = FileItem(key="test")
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_non_string_path():
    """Test _is_valid method with FileItem instance but non-string path."""
    file_filter = FileExistsFilter()
    item = FileItem(key="test")
    item.extra_data = {"target_path": 123}
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_non_existent_path():
    """Test _is_valid method with FileItem instance but non-existent path."""
    file_filter = FileExistsFilter()
    item = FileItem(key="test")
    item.extra_data = {"target_path": "/non/existent/path"}
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_existent_path(tmp_path):
    """Test _is_valid method with FileItem instance and existent path."""
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test")
    item.extra_data = {"target_path": str(tmp_path / "test.txt")}
    Path(item.extra_data["target_path"]).touch()
    assert file_filter._is_valid(item)


def test_is_valid_file_item_no_target_path():
    """Test _is_valid method with FileItem instance but no target_path."""
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test")
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_non_string_target_path():
    """Test _is_valid method with FileItem instance but non-string target_path."""
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test")
    item.extra_data = {"target_path": 123}
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_non_existent_target_path():
    """Test _is_valid method with FileItem instance but non-existent target_path."""
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test")
    item.extra_data = {"target_path": "/non/existent/path"}
    assert not file_filter._is_valid(item)


def test_is_valid_file_item_existent_target_path(tmp_path):
    """Test _is_valid method with FileItem instance and existent target_path."""
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test")
    item.extra_data = {"target_path": str(tmp_path / "test.txt")}
    Path(item.extra_data["target_path"]).touch()
    assert file_filter._is_valid(item)
