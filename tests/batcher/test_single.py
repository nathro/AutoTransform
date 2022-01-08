# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for SingleBatcher component."""

from typing import List

from autotransform.batcher.base import Batch, Batcher
from autotransform.batcher.single import SingleBatcher
from autotransform.common.cachedfile import CachedFile


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


def test_with_no_files():
    """Checks that the batcher works with no input files."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    files = []
    batcher = SingleBatcher({"metadata": metadata})
    check_batcher(batcher, files, [{"metadata": metadata, "files": files}])


def test_with_one_files():
    """Checks that the batcher works with one input file."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    files = [CachedFile("foo.py")]
    batcher = SingleBatcher({"metadata": metadata})
    check_batcher(batcher, files, [{"metadata": metadata, "files": files}])


def test_with_multiple_files():
    """Checks that the batcher works with multiple input files."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    files = [CachedFile("foo.py"), CachedFile("bar.py")]
    batcher = SingleBatcher({"metadata": metadata})
    check_batcher(batcher, files, [{"metadata": metadata, "files": files}])
