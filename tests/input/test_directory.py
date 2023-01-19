# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the DirectoryInput component."""

from typing import List

import pytest
from autotransform.input.directory import DirectoryInput


def assert_directory_content(directory: str, expected_files: List[str]):
    """Helper function that handles the logic of actually testing given Inputs and expected results.

    Args:
        directory (str): The directory within the tests data to search
        expected_files (List[str]): The relative paths of all expected results
    """

    inp: DirectoryInput = DirectoryInput(paths=[directory])
    files = [item.get_path() for item in inp.get_items()]

    missing_files = [file for file in expected_files if file not in files]
    assert not missing_files, "The following files were expected but not found: " + ", ".join(
        missing_files
    )

    extra_files = [file for file in files if file not in expected_files]
    assert not extra_files, "The following files were found but not expected: " + ", ".join(
        extra_files
    )


def test_empty_dir(tmpdir):
    """Tests running DirectoryInput against a directory with no files in it."""

    empty_dir = tmpdir.mkdir("empty_dir")
    expected_files = []
    assert_directory_content(str(empty_dir), expected_files)


def test_non_empty_dir(tmpdir):
    """Tests running DirectoryInput against a directory with a single file in it."""

    non_empty_dir = tmpdir.mkdir("non_empty_dir")
    test_file = non_empty_dir.join("test.txt")
    test_file.write("test")
    expected_files = [str(test_file).replace("\\", "/")]
    assert_directory_content(str(non_empty_dir), expected_files)


def test_recursive_dir(tmpdir):
    """Tests running DirectoryInput against a directory that has files within a
    subdirectory as well as a sub directory with no files in it.
    """

    root_dir = tmpdir.mkdir("root_dir")
    non_empty_dir = root_dir.mkdir("non_empty_dir")
    test_file_1 = non_empty_dir.join("test1.txt")
    test_file_1.write("test")
    test_file_2 = non_empty_dir.join("test2.txt")
    test_file_2.write("test")
    root_dir.mkdir("empty_dir")
    expected_files = [str(test_file_1).replace("\\", "/"), str(test_file_2).replace("\\", "/")]
    assert_directory_content(str(root_dir), expected_files)


def test_legacy_migration(tmpdir):
    """Tests that DirectoryInput works successfully with legacy path setting."""

    empty_dir = tmpdir.mkdir("empty_dir")
    inp = DirectoryInput(path=str(empty_dir))
    assert len(inp.paths) == 1, "Only one path should be supplied"
    assert inp.paths[0] == str(empty_dir)
    with pytest.raises(ValueError, match="Can not supply both path and paths for DirectoryInput"):
        DirectoryInput(path=str(empty_dir), paths=[str(empty_dir)])
