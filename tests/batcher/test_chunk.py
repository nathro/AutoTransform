# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for SingleBatcher component."""

from autotransform.batcher.chunk import ChunkBatcher, ChunkBatcherParams
from autotransform.item.base import Item

from .batcher_test import check_batcher


def test_with_no_items():
    """Checks that the batcher works with no Items."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = []
    batcher = ChunkBatcher(ChunkBatcherParams(title=title, metadata=metadata, chunk_size=10))
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])


def test_with_one_item():
    """Checks that the batcher works with one Item."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    expected_title = "[1/1] foo"
    items = [Item("foo.py")]
    batcher = ChunkBatcher(ChunkBatcherParams(title=title, metadata=metadata, chunk_size=10))
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": expected_title}])


def test_with_one_item_no_metadata():
    """Checks that the batcher works with one Item and no metadata."""

    title = "foo"
    expected_title = "[1/1] foo"
    items = [Item("foo.py")]
    batcher = ChunkBatcher(ChunkBatcherParams(title=title, chunk_size=10))
    check_batcher(batcher, items, [{"items": items, "title": expected_title}])


def test_with_multiple_items():
    """Checks that the batcher works with multiple Items."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    expected_title = "[1/1] foo"
    items = [Item("foo.py"), Item("bar.py")]
    batcher = ChunkBatcher(ChunkBatcherParams(title=title, metadata=metadata, chunk_size=10))
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": expected_title}])


def test_with_multiple_files_and_multiple_batches():
    """Checks that the batcher works with multiple Items separated in to multiple batches."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    expected_title_1 = "[1/2] foo"
    expected_title_2 = "[2/2] foo"
    items = [Item("foo.py"), Item("bar.py"), Item("baz.py")]
    batcher = ChunkBatcher(ChunkBatcherParams(title=title, metadata=metadata, chunk_size=2))
    check_batcher(
        batcher,
        items,
        [
            {"metadata": metadata, "items": items[:2], "title": expected_title_1},
            {"metadata": metadata, "items": items[2:], "title": expected_title_2},
        ],
    )


def test_with_multiple_files_and_max_batches():
    """Checks that the batcher works with multiple Items separated in to multiple Batches, with max
    chunks used.
    """

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    expected_title_1 = "[1/2] foo"
    expected_title_2 = "[2/2] foo"
    items = [Item("foo.py"), Item("bar.py"), Item("baz.py")]
    batcher = ChunkBatcher(
        ChunkBatcherParams(title=title, metadata=metadata, chunk_size=1, max_chunks=2)
    )
    check_batcher(
        batcher,
        items,
        [
            {"metadata": metadata, "items": items[:2], "title": expected_title_1},
            {"metadata": metadata, "items": items[2:], "title": expected_title_2},
        ],
    )
