# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for SingleBatcher component."""

from autotransform.batcher.single import SingleBatcher
from autotransform.item.base import Item

from .batcher_test import check_batcher


def setup_batcher(title, metadata=None, items=None, skip_empty_batch=False):
    """Setup SingleBatcher with given parameters."""
    return SingleBatcher(
        title=title, metadata=metadata, items=items, skip_empty_batch=skip_empty_batch
    )


def test_with_no_items():
    """Checks that the Batcher works with no Items."""
    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = []
    batcher = setup_batcher(title, metadata, items)
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])


def test_with_no_items_skip_empty():
    """Checks that the Batcher works with no Items and skip empty set to True."""
    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = []
    batcher = setup_batcher(title, metadata, items, True)
    check_batcher(batcher, items, [])


def test_with_one_item():
    """Checks that the Batcher works with one Item."""
    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [Item(key="bar.py")]
    batcher = setup_batcher(title, metadata, items)
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])


def test_with_one_item_no_metadata():
    """Checks that the Batcher works with one Item and no metadata."""
    title = "foo"
    items = [Item(key="bar.py")]
    batcher = setup_batcher(title, items=items)
    check_batcher(batcher, items, [{"items": items, "title": title}])


def test_with_multiple_items():
    """Checks that the Batcher works with multiple Items."""
    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [Item(key="bar.py"), Item(key="baz.py")]
    batcher = setup_batcher(title, metadata, items)
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])
