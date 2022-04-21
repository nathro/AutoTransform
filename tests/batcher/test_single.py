# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for SingleBatcher component."""

from autotransform.batcher.single import SingleBatcher
from autotransform.item.base import Item

from .batcher_test import check_batcher


def test_with_no_items():
    """Checks that the Batcher works with no Items."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = []
    batcher = SingleBatcher({"title": title, "metadata": metadata})
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])

def test_with_one_item():
    """Checks that the Batcher works with one Item."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [Item("bar.py")]
    batcher = SingleBatcher({"title": title, "metadata": metadata})
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])

def test_with_one_item_no_metadata():
    """Checks that the Batcher works with one Item and no metadata."""

    title = "foo"
    items = [Item("bar.py")]
    batcher = SingleBatcher({"title": title})
    check_batcher(batcher, items, [{"items": items, "title": title}])

def test_with_multiple_items():
    """Checks that the Batcher works with multiple Items."""

    title = "foo"
    metadata = {"summary": "bar", "tests": "baz"}
    items = [Item("bar.py"), Item("baz.py")]
    batcher = SingleBatcher({"title": title, "metadata": metadata})
    check_batcher(batcher, items, [{"metadata": metadata, "items": items, "title": title}])
