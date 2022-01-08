# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for the DirectoryInput component"""

import pathlib
from typing import List

from autotransform.input.directory import DirectoryInput


def assert_directory_content(directory: str, expected_files: List[str]):
    """Helper function that handles the logic of actually testing given inputs and expected results

    Args:
        directory (str): The directory within the tests data to search
        expected_files (List[str]): The relative paths of all expected results
    """
    file_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    test_data_path = file_dir + "/data/directory_input_test/"
    dir_to_check = test_data_path + directory

    inp: DirectoryInput = DirectoryInput({"path": dir_to_check})
    files = [file.replace("\\", "/") for file in inp.get_files()]
    missing_files = []
    for file in expected_files:
        if dir_to_check + "/" + file not in files:
            missing_files.append(file)
    assert not missing_files, "The following files were expected but not found: " + ", ".join(
        missing_files
    )

    extra_files = []
    for file in files:
        stripped_file = file.removeprefix(dir_to_check + "/")
        if stripped_file not in expected_files:
            extra_files.append(stripped_file)
    assert not extra_files, "The following files were found but not expected: " + ", ".join(
        extra_files
    )


def test_empty_dir():
    """Tests running DirectoryInput against a directory with no files in it."""
    directory = "empty_dir"
    expected_files = []
    assert_directory_content(directory, expected_files)


def test_non_empty_dir():
    """Tests running DirectoryInput against a directory with a single file in it."""
    directory = "non_empty_dir"
    expected_files = ["test.txt"]
    assert_directory_content(directory, expected_files)


def test_recursive_dir():
    """Tests running DirectoryInput against a directory that has files within a
    subdirectory as well as a sub directory with no files in it."""
    directory = "recursive_dir"
    expected_files = ["non_empty_subdir/test.txt", "non_empty_subdir/test2.txt"]
    assert_directory_content(directory, expected_files)
