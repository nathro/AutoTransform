# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for DirectoryBatcher component."""

from autotransform.batcher.directory import DirectoryBatcher
from autotransform.item.file import FileItem

from .batcher_test import check_batcher


def create_batcher(prefix, metadata=None, items=None):
    """Helper function to create a DirectoryBatcher."""
    return DirectoryBatcher(prefix=prefix, metadata=metadata, items=items)


def test_with_no_items():
    """Checks that the Batcher works with no Items."""
    check_batcher(create_batcher("foo", {"summary": "bar", "tests": "baz"}), [], [])


def test_with_one_item():
    """Checks that the Batcher works with one Item."""
    items = [FileItem(key="foo/bar.py")]
    expected = [
        {"metadata": {"summary": "bar", "tests": "baz"}, "items": items, "title": "test: foo"}
    ]
    check_batcher(
        create_batcher("test", {"summary": "bar", "tests": "baz"}, items), items, expected
    )


def test_with_one_item_no_metadata():
    """Checks that the Batcher works with one Item and no metadata."""
    items = [FileItem(key="foo/bar.py")]
    expected = [{"items": items, "title": "test: foo"}]
    check_batcher(create_batcher("test", items=items), items, expected)


def test_with_multiple_items_single_directory():
    """Checks that the Batcher works with multiple Items in one directory."""
    items = [FileItem(key="foo/bar.py"), FileItem(key="foo/baz.py")]
    expected = [
        {"metadata": {"summary": "bar", "tests": "baz"}, "items": items, "title": "test: foo"}
    ]
    check_batcher(
        create_batcher("test", {"summary": "bar", "tests": "baz"}, items), items, expected
    )


def test_with_multiple_items_multiple_directories():
    """Checks that the Batcher works with Items in multiple directories."""
    items = [FileItem(key="foo/bar.py"), FileItem(key="fizz/baz.py")]
    expected = [
        {"metadata": {"summary": "bar", "tests": "baz"}, "items": items[:1], "title": "test: foo"},
        {"metadata": {"summary": "bar", "tests": "baz"}, "items": items[1:], "title": "test: fizz"},
    ]
    check_batcher(
        create_batcher("test", {"summary": "bar", "tests": "baz"}, items), items, expected
    )


def test_with_multiple_items_nested_directories():
    """Checks that the Batcher works with Items in nested directories."""
    items = [
        FileItem(key="test/foo/bar.py"),
        FileItem(key="test/fizz/baz.py"),
        FileItem(key="test/buzz.py"),
    ]
    expected = [
        {
            "metadata": {"summary": "bar", "tests": "baz"},
            "items": items[:1],
            "title": "test: test/foo",
        },
        {
            "metadata": {"summary": "bar", "tests": "baz"},
            "items": items[1:2],
            "title": "test: test/fizz",
        },
        {"metadata": {"summary": "bar", "tests": "baz"}, "items": items[2:], "title": "test: test"},
    ]
    check_batcher(
        create_batcher("test", {"summary": "bar", "tests": "baz"}, items), items, expected
    )
