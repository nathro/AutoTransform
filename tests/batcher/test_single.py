# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for SingleBatcher component."""
from autotransform.batcher.single import SingleBatcher
from autotransform.util.cachedfile import CachedFile

from .batcher_test import check_batcher


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
