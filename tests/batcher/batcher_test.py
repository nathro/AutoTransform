# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Utility methods for testing batcher components."""

from typing import List, Sequence

from autotransform.batcher.base import Batch, Batcher
from autotransform.item.base import Item


def check_batcher(batcher: Batcher, items: Sequence[Item], expected: List[Batch]):
    """A convenience function to perform the actual testing of a Batcher.

    Args:
        batcher (Batcher): The Batcher being tested.
        items (Sequence[Item]): The Items for batching.
        expected (List[Batch]): The expected output Batches.
    """
    actual = batcher.batch(items)

    # pylint: disable=consider-using-enumerate

    for i in range(len(actual)):
        assert i < len(expected), "More batches found than expected"
        actual_batch = actual[i]
        expected_batch = expected[i]
        assert actual_batch.get("metadata", None) == expected_batch.get("metadata", None), (
            "Metadata for Batch " + str(i) + " does not match"
        )
        assert actual_batch["title"] == expected_batch["title"], (
            "Title for Batch " + str(i) + " does not match"
        )
        actual_items = [item.get_key() for item in actual_batch["items"]]
        expected_items = [item.get_key() for item in expected_batch["items"]]
        assert actual_items == expected_items, "Items for Batch " + str(i) + " do not match"
