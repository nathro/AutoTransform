# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the FileItem component."""

from autotransform.item.file import FileItem


def test_get_content(tmpdir):
    """Tests getting content from a file using FileItem's get_content function."""

    root_dir = tmpdir.mkdir("root_dir")
    test_file = root_dir.join("test.txt")
    test_content = "test"
    test_file.write(test_content)
    assert FileItem(key=str(test_file)).get_content() == test_content


def test_write_content(tmpdir):
    """Tests writing content to a file using FileItem's write_content function."""

    root_dir = tmpdir.mkdir("root_dir")
    test_file = root_dir.join("test.txt")
    test_content = "test"
    test_file.write("")
    FileItem(key=str(test_file)).write_content(test_content)
    assert test_file.read() == test_content
