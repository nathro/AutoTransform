# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch
from autotransform.filter.file import FileExistsFilter
from autotransform.filter.base import Filter, FilterName
from autotransform.item.file import FileItem
from autotransform.item.base import Item


def test_file_exists_filter_subclass():
    assert issubclass(FileExistsFilter, Filter)


def test_check_target_path_default():
    file_filter = FileExistsFilter()
    assert not file_filter.check_target_path


def test_name_default():
    file_filter = FileExistsFilter()
    assert file_filter.name == FilterName.FILE_EXISTS


def test_is_valid_not_file_item():
    file_filter = FileExistsFilter()
    item = Item(key="test")
    assert not file_filter._is_valid(item)


@patch("pathlib.Path.is_file", return_value=True)
def test_is_valid_valid_path(mock_is_file):
    file_filter = FileExistsFilter()
    item = FileItem(key="valid_path", path="valid_path")
    assert file_filter._is_valid(item)


@patch("pathlib.Path.is_file", return_value=False)
def test_is_valid_invalid_path(mock_is_file):
    file_filter = FileExistsFilter()
    item = FileItem(key="invalid_path", path="invalid_path")
    assert not file_filter._is_valid(item)


@patch("pathlib.Path.is_file", return_value=True)
def test_is_valid_valid_target_path(mock_is_file):
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="valid_path", extra_data={"target_path": "valid_path"})
    assert file_filter._is_valid(item)


@patch("pathlib.Path.is_file", return_value=False)
def test_is_valid_invalid_target_path(mock_is_file):
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="invalid_path", extra_data={"target_path": "invalid_path"})
    assert not file_filter._is_valid(item)


def test_is_valid_no_extra_data():
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test")
    assert not file_filter._is_valid(item)


def test_is_valid_non_string_target_path():
    file_filter = FileExistsFilter(check_target_path=True)
    item = FileItem(key="test", extra_data={"target_path": 123})
    assert not file_filter._is_valid(item)
