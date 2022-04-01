# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for SingleBatcher component."""
from copy import deepcopy

from autotransform.batcher.chunk import ChunkBatcher
from autotransform.common.cachedfile import CachedFile

from .batcher_test import check_batcher


def test_with_no_files():
    """Checks that the batcher works with no input files."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    files = []
    batcher = ChunkBatcher({"metadata": metadata, "chunk_size": 10})
    check_batcher(batcher, files, [{"metadata": metadata, "files": files}])


def test_with_one_files():
    """Checks that the batcher works with one input file."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    metadata_expected = deepcopy(metadata)
    metadata_expected["title"] = "[1/1] foo"
    files = [CachedFile("foo.py")]
    batcher = ChunkBatcher({"metadata": metadata, "chunk_size": 10})
    check_batcher(batcher, files, [{"metadata": metadata_expected, "files": files}])


def test_with_multiple_files():
    """Checks that the batcher works with multiple input files."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    metadata_expected = deepcopy(metadata)
    metadata_expected["title"] = "[1/1] foo"
    files = [CachedFile("foo.py"), CachedFile("bar.py")]
    batcher = ChunkBatcher({"metadata": metadata, "chunk_size": 10})
    check_batcher(batcher, files, [{"metadata": metadata_expected, "files": files}])


def test_with_multiple_files_and_multiple_batches():
    """Checks that the batcher works with multiple input files."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    metadata_1 = deepcopy(metadata)
    metadata_1["title"] = "[1/2] foo"
    metadata_2 = deepcopy(metadata)
    metadata_2["title"] = "[2/2] foo"
    files = [CachedFile("foo.py"), CachedFile("bar.py"), CachedFile("baz.py")]
    batcher = ChunkBatcher({"metadata": metadata, "chunk_size": 2})
    check_batcher(
        batcher,
        files,
        [
            {"metadata": metadata_1, "files": files[0:2]},
            {"metadata": metadata_2, "files": files[2:]},
        ],
    )


def test_with_multiple_files_and_max_batches():
    """Checks that the batcher works with multiple input files."""
    metadata = {"title": "foo", "summary": "bar", "tests": "baz"}
    metadata_1 = deepcopy(metadata)
    metadata_1["title"] = "[1/2] foo"
    metadata_2 = deepcopy(metadata)
    metadata_2["title"] = "[2/2] foo"
    files = [CachedFile("foo.py"), CachedFile("bar.py"), CachedFile("baz.py")]
    batcher = ChunkBatcher({"metadata": metadata, "chunk_size": 1, "max_chunks": 2})
    check_batcher(
        batcher,
        files,
        [
            {"metadata": metadata_1, "files": files[0:2]},
            {"metadata": metadata_2, "files": files[2:]},
        ],
    )
