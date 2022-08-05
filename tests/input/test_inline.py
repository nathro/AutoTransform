# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for inline Inputs"""

from autotransform.input.inline import InlineFileInput, InlineGenericInput, InlineInput
from autotransform.item.base import Item, ItemName
from autotransform.item.file import FileItem


def test_inline_input():
    """Tests running InlineInput component."""
    inp_items = [Item(key="foo"), Item(key="bar")]
    inp = InlineInput(items=inp_items)
    assert inp.get_items() == inp_items


def test_inline_file_input():
    """Tests running InlineFileInput component."""
    files = ["foo.py", "bar.py"]
    inp = InlineFileInput(files=files)
    inp_items = inp.get_items()
    for item in inp_items:
        assert isinstance(item, FileItem)
    inp_files = [item.get_path() for item in inp_items]
    assert inp_files == files


def test_inline_generic_input():
    """Tests running InlineGenericInput component."""

    keys = ["foo", "bar"]
    inp = InlineGenericInput(keys=keys)
    inp_items = inp.get_items()
    for item in inp_items:
        assert item.name == ItemName.GENERIC
    inp_keys = [item.key for item in inp_items]
    assert inp_keys == keys
