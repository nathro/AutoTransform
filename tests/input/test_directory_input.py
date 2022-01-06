# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pathlib
from typing import List

from autotransform.input.directory import DirectoryInput


def test_empty_dir():
    directory: str = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    inp: DirectoryInput = DirectoryInput(
        {"path": directory + "/data/directory_input_test_empty_dir"}
    )
    assert not inp.get_files()


def test_non_empty_dir():
    directory: str = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    inp: DirectoryInput = DirectoryInput(
        {"path": directory + "/data/directory_input_test_non_empty_dir"}
    )
    files: List[str] = inp.get_files()
    files = [file.replace("\\", "/") for file in files]
    assert directory + "/data/directory_input_test_non_empty_dir/test.txt" in files
