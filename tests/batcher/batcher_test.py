# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Utility methods for testing batcher components."""

from typing import List

from autotransform.batcher.base import Batch, Batcher
from autotransform.util.cachedfile import CachedFile


def check_batcher(batcher: Batcher, files: List[CachedFile], expected: List[Batch]):
    """A convenience function to perform the actual testing of a Batcher.

    Args:
        batcher (Batcher): The Batcher being tests
        files (List[CachedFile]): The input files for batching
        expected (List[Batch]): The expected output batches
    """
    actual = batcher.batch(files)

    # pylint: disable=consider-using-enumerate

    for i in range(len(actual)):
        assert i < len(expected), "More batches found than expected"
        actual_batch = actual[i]
        expected_batch = expected[i]
        assert actual_batch["metadata"] == expected_batch["metadata"], (
            "Metadata for batch " + str(i) + " does not match"
        )
        actual_paths = [file.path for file in actual_batch["files"]]
        expected_paths = [file.path for file in expected_batch["files"]]
        assert actual_paths == expected_paths, "Files for batch " + str(i) + " do not match"
