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


def test_with_no_items():
    """Checks that the Batcher works with no Items."""

    prefix = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = []
    batcher = DirectoryBatcher(prefix=prefix, metadata=metadata)
    check_batcher(batcher, items, [])


def test_with_one_item():
    """Checks that the Batcher works with one Item."""

    prefix = "test"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [FileItem(key="foo/bar.py")]
    batcher = DirectoryBatcher(prefix=prefix, metadata=metadata)
    check_batcher(
        batcher,
        items,
        [{"metadata": metadata, "items": items, "title": f"{prefix}: foo"}],
    )


def test_with_one_item_no_metadata():
    """Checks that the Batcher works with one Item and no metadata."""

    prefix = "test"
    items = [FileItem(key="foo/bar.py")]
    batcher = DirectoryBatcher(prefix=prefix)
    check_batcher(batcher, items, [{"items": items, "title": f"{prefix}: foo"}])


def test_with_multiple_items_single_directory():
    """Checks that the Batcher works with multiple Items in one directory."""

    prefix = "test"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [FileItem(key="foo/bar.py"), FileItem(key="foo/baz.py")]
    batcher = DirectoryBatcher(prefix=prefix, metadata=metadata)
    check_batcher(
        batcher,
        items,
        [{"metadata": metadata, "items": items, "title": f"{prefix}: foo"}],
    )


def test_with_multiple_items_multiple_directories():
    """Checks that the Batcher works with Items in multiple directories."""

    prefix = "test"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [FileItem(key="foo/bar.py"), FileItem(key="fizz/baz.py")]
    batcher = DirectoryBatcher(prefix=prefix, metadata=metadata)
    check_batcher(
        batcher,
        items,
        [
            {"metadata": metadata, "items": items[:1], "title": f"{prefix}: foo"},
            {"metadata": metadata, "items": items[1:], "title": f"{prefix}: fizz"},
        ],
    )


def test_with_multiple_items_nested_directories():
    """Checks that the Batcher works with Items in nested directories."""

    prefix = "test"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [
        FileItem(key="test/foo/bar.py"),
        FileItem(key="test/fizz/baz.py"),
        FileItem(key="test/buzz.py"),
    ]
    batcher = DirectoryBatcher(prefix=prefix, metadata=metadata)
    check_batcher(
        batcher,
        items,
        [
            {"metadata": metadata, "items": items[:1], "title": f"{prefix}: test/foo"},
            {"metadata": metadata, "items": items[1:2], "title": f"{prefix}: test/fizz"},
            {"metadata": metadata, "items": items[2:], "title": f"{prefix}: test"},
        ],
    )
