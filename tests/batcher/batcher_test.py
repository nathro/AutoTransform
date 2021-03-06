# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Utility method for testing Batcher components."""

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

    assert len(actual) == len(expected)
    for idx, batches in enumerate(zip(actual, expected)):
        actual_batch, expected_batch = batches

        # Check metadata
        assert actual_batch.get("metadata", None) == expected_batch.get(
            "metadata", None
        ), f"Metadata for Batch {str(idx)} does not match"

        # Check title
        assert (
            actual_batch["title"] == expected_batch["title"]
        ), f"Title for Batch {str(idx)} does not match"

        # Check items
        actual_items = [item.key for item in actual_batch["items"]]
        expected_items = [item.key for item in expected_batch["items"]]
        assert actual_items == expected_items, f"Items for Batch {str(idx)} do not match"
