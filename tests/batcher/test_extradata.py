# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ChunkBatcher component."""

from autotransform.batcher.extradata import ExtraDataBatcher
from autotransform.item.base import Item

from .batcher_test import check_batcher


def create_item(key, group, metadata=None):
    """Helper function to create an Item with extra data."""
    extra_data = {"foo": group}
    if metadata is not None:
        extra_data.update(metadata)
    return Item(key=key, extra_data=extra_data)


def test_with_no_items():
    """Checks that the Batcher works with no Items."""
    batcher = ExtraDataBatcher(group_by="foo")
    check_batcher(batcher, [], [])


def test_with_one_item():
    """Checks that the Batcher works with one Item."""
    items = [create_item("i1.py", "g1")]
    batcher = ExtraDataBatcher(group_by="foo")
    check_batcher(batcher, items, [{"items": items, "title": "g1"}])


def test_with_one_item_and_metadata():
    """Checks that the Batcher works with one Item including metadata."""
    items = [create_item("i1.py", "g1", {"bar": 1})]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(batcher, items, [{"items": items, "title": "g1", "metadata": {"bar": [1]}}])


def test_with_one_item_and_metadata_with_list():
    """Checks that the Batcher works with one Item including metadata with list in extra data."""
    items = [create_item("i1.py", "g1", {"bar": [1, 2]})]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(batcher, items, [{"items": items, "title": "g1", "metadata": {"bar": [1, 2]}}])


def test_with_multiple_items():
    """Checks that the Batcher works with multiple Items."""
    items = [create_item("i1.py", "g1"), create_item("i2.py", "g1")]
    batcher = ExtraDataBatcher(group_by="foo")
    check_batcher(batcher, items, [{"items": items, "title": "g1"}])


def test_with_multiple_items_with_metadata():
    """Checks that the Batcher works with multiple Items with metadata."""
    items = [create_item("i1.py", "g1", {"bar": 1}), create_item("i2.py", "g1", {"bar": [2, 3]})]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(batcher, items, [{"items": items, "title": "g1", "metadata": {"bar": [1, 2, 3]}}])


def test_with_multiple_groups_with_metadata():
    """Checks that the Batcher works with multiple Items and groups with metadata."""
    items = [
        create_item("i1.py", "g1", {"bar": 1}),
        create_item("i2.py", "g1", {"bar": [2, 3]}),
        create_item("i3.py", "g2", {"bar": [4, 5]}),
    ]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(
        batcher,
        items,
        [
            {"items": items[:2], "title": "g1", "metadata": {"bar": [1, 2, 3]}},
            {"items": items[2:], "title": "g2", "metadata": {"bar": [4, 5]}},
        ],
    )
