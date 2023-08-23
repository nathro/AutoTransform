# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ChunkBatcher component."""

from autotransform.batcher.chunk import ChunkBatcher
from autotransform.item.base import Item

from .batcher_test import check_batcher

# Define common variables to avoid repetition
title = "foo"
metadata = {"summary": "bar", "tests": "baz"}


def test_with_no_items():
    """Checks that the Batcher works with no Items."""
    items = []
    batcher = ChunkBatcher(title=title, metadata=metadata, chunk_size=10)
    check_batcher(batcher, items, [])


def test_with_one_item():
    """Checks that the Batcher works with one Item."""
    expected_title = "[1/1] foo"
    items = [Item(key="foo.py")]
    batcher = ChunkBatcher(title=title, metadata=metadata, chunk_size=10)
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": expected_title}])


def test_with_one_item_no_metadata():
    """Checks that the Batcher works with one Item and no metadata."""
    expected_title = "[1/1] foo"
    items = [Item(key="foo.py")]
    batcher = ChunkBatcher(title=title, chunk_size=10)
    check_batcher(batcher, items, [{"items": items, "title": expected_title}])


def test_with_multiple_items():
    """Checks that the Batcher works with multiple Items."""
    expected_title = "[1/1] foo"
    items = [Item(key="foo.py"), Item(key="bar.py")]
    batcher = ChunkBatcher(title=title, metadata=metadata, chunk_size=10)
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": expected_title}])


def test_with_multiple_items_and_multiple_batches():
    """Checks that the batcher works with multiple Items separated in to multiple batches."""
    expected_title_1 = "[1/2] foo"
    expected_title_2 = "[2/2] foo"
    items = [Item(key="foo.py"), Item(key="bar.py"), Item(key="baz.py")]
    batcher = ChunkBatcher(title=title, metadata=metadata, chunk_size=2)
    check_batcher(
        batcher,
        items,
        [
            {"metadata": metadata, "items": items[:2], "title": expected_title_1},
            {"metadata": metadata, "items": items[2:], "title": expected_title_2},
        ],
    )


def test_with_multiple_items_and_max_batches():
    """Checks that the Batcher works with multiple Items separated in to multiple Batches, with max
    chunks used.
    """
    expected_title_1 = "[1/2] foo"
    expected_title_2 = "[2/2] foo"
    items = [Item(key="foo.py"), Item(key="bar.py"), Item(key="baz.py")]
    batcher = ChunkBatcher(title=title, metadata=metadata, chunk_size=1, max_chunks=2)
    check_batcher(
        batcher,
        items,
        [
            {"metadata": metadata, "items": items[:2], "title": expected_title_1},
            {"metadata": metadata, "items": items[2:], "title": expected_title_2},
        ],
    )
