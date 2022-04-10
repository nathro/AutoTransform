# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for the ExtensionFilter component."""

from autotransform.filter.extension import ExtensionFilter
from autotransform.util.cachedfile import CachedFile


def test_no_directory():
    """Checks that simple files are checked appropriately."""
    extensions = [".py", ".txt", ".json"]
    filt = ExtensionFilter({"extensions": extensions})
    assert filt.is_valid(CachedFile("test.py"))
    assert filt.is_valid(CachedFile("test.txt"))
    assert filt.is_valid(CachedFile("test.json"))
    assert not filt.is_valid(CachedFile("test.md"))


def test_in_subdir():
    """Checks that files within a subdir are checked appropriately."""
    extensions = [".py", ".txt", ".json"]
    filt = ExtensionFilter({"extensions": extensions})
    assert filt.is_valid(CachedFile("test_dir/test.py"))
    assert filt.is_valid(CachedFile("test_dir/test.txt"))
    assert filt.is_valid(CachedFile("test_dir/test.json"))
    assert not filt.is_valid(CachedFile("test_dir/test.md"))


def test_only_extension_no_directory():
    """Checks that files with no name are not returned (i.e. only extension)."""
    extensions = [".py", ".txt", ".json"]
    filt = ExtensionFilter({"extensions": extensions})
    assert not filt.is_valid(CachedFile(".py"))
    assert not filt.is_valid(CachedFile(".txt"))
    assert not filt.is_valid(CachedFile(".json"))
    assert not filt.is_valid(CachedFile(".md"))


def test_only_extension_in_subdir():
    """Checks that files with no name are not returned (i.e. only extension) when within a
    subdir.
    """
    extensions = [".py", ".txt", ".json"]
    filt = ExtensionFilter({"extensions": extensions})
    assert not filt.is_valid(CachedFile("test_dir/.py"))
    assert not filt.is_valid(CachedFile("test_dir/.txt"))
    assert not filt.is_valid(CachedFile("test_dir/.json"))
    assert not filt.is_valid(CachedFile("test_dir/.md"))
