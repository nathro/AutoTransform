# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for inline Inputs"""

import pytest
from autotransform.input.inline import InlineFileInput, InlineGenericInput, InlineInput
from autotransform.item.base import Item, ItemName
from autotransform.item.file import FileItem


@pytest.mark.parametrize("items", [[Item(key="foo"), Item(key="bar")]])
def test_inline_input(items):
    """Tests running InlineInput component."""
    inp = InlineInput(items=items)
    assert inp.get_items() == items


@pytest.mark.parametrize("files", [["foo.py", "bar.py"]])
def test_inline_file_input(files):
    """Tests running InlineFileInput component."""
    inp = InlineFileInput(files=files)
    inp_items = inp.get_items()
    for item in inp_items:
        assert isinstance(item, FileItem)
    assert [item.get_path() for item in inp_items] == files


@pytest.mark.parametrize("keys", [["foo", "bar"]])
def test_inline_generic_input(keys):
    """Tests running InlineGenericInput component."""
    inp = InlineGenericInput(keys=keys)
    inp_items = inp.get_items()
    for item in inp_items:
        assert item.name == ItemName.GENERIC
    assert [item.key for item in inp_items] == keys
