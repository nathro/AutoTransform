# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the RegexFilter component."""

from autotransform.filter.key_hash_shard import KeyHashShardFilter
from autotransform.item.file import FileItem


def test_key_hash_shard():
    """Runs simple tests on the key hash shard filter."""

    filt = KeyHashShardFilter(num_shards=5, valid_shard=1)
    test_cases = {
        "foo.py": False,
        "bar/foo.py": False,
        "bar/foo": True,
        "bar/baz": False,
        "ban/foo": False,
        "baz": False,
        "oof": True,
        "fizz/foo.py": False,
        "fizz/bar.py": True,
        "bar/fizz.py": False,
    }
    for path, result in test_cases.items():
        item = FileItem(key=path)
        assert filt.is_valid(item) == result


def test_inverted_key_hash_shard():
    """Runs simple tests on the inverted key hash shard filter."""

    filt = KeyHashShardFilter(num_shards=5, valid_shard=1, inverted=True)
    test_cases = {
        "foo.py": True,
        "bar/foo.py": True,
        "bar/foo": False,
        "bar/baz": True,
        "ban/foo": True,
        "baz": True,
        "oof": False,
        "fizz/foo.py": True,
        "fizz/bar.py": False,
        "bar/fizz.py": True,
    }
    for path, result in test_cases.items():
        item = FileItem(key=path)
        assert filt.is_valid(item) == result
