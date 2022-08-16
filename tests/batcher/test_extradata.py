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


def test_with_no_items():
    """Checks that the Batcher works with no Items."""

    items = []
    batcher = ExtraDataBatcher(group_by="foo")
    check_batcher(batcher, items, [])


def test_with_one_item():
    """Checks that the Batcher works with one Item."""

    items = [Item(key="i1.py", extra_data={"foo": "g1"})]
    batcher = ExtraDataBatcher(group_by="foo")
    check_batcher(batcher, items, [{"items": items, "title": "g1"}])


def test_with_one_item_and_metadata():
    """Checks that the Batcher works with one Item including metadata."""

    items = [Item(key="i1.py", extra_data={"foo": "g1", "bar": 1})]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(batcher, items, [{"items": items, "title": "g1", "metadata": {"bar": [1]}}])


def test_with_one_item_and_metadata_with_list():
    """Checks that the Batcher works with one Item including metadata with list in extra data."""

    items = [Item(key="i1.py", extra_data={"foo": "g1", "bar": [1, 2]})]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(batcher, items, [{"items": items, "title": "g1", "metadata": {"bar": [1, 2]}}])


def test_with_multiple_items():
    """Checks that the Batcher works with multiple Items."""

    items = [
        Item(key="i1.py", extra_data={"foo": "g1"}),
        Item(key="i2.py", extra_data={"foo": "g1"}),
    ]
    batcher = ExtraDataBatcher(group_by="foo")
    check_batcher(batcher, items, [{"items": items, "title": "g1"}])


def test_with_multiple_items_with_metadata():
    """Checks that the Batcher works with multiple Items with metadata."""

    items = [
        Item(key="i1.py", extra_data={"foo": "g1", "bar": 1}),
        Item(key="i2.py", extra_data={"foo": "g1", "bar": [2, 3]}),
    ]
    batcher = ExtraDataBatcher(group_by="foo", metadata_keys=["bar"])
    check_batcher(batcher, items, [{"items": items, "title": "g1", "metadata": {"bar": [1, 2, 3]}}])


def test_with_multiple_groups_with_metadata():
    """Checks that the Batcher works with multiple Items and groups with metadata."""

    items = [
        Item(key="i1.py", extra_data={"foo": "g1", "bar": 1}),
        Item(key="i2.py", extra_data={"foo": "g1", "bar": [2, 3]}),
        Item(key="i3.py", extra_data={"foo": "g2", "bar": [4, 5]}),
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
