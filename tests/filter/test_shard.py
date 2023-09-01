# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Unit tests for the ShardFilter class."""

import pytest
from autotransform.item.base import Item
from autotransform.filter.shard import ShardFilter


class TestShardFilter:
    """Unit tests for the ShardFilter class."""

    class MockItem(Item):
        """A mock Item for testing."""

        def __init__(self, key: str):
            super().__init__(key=key)

    class MockShardFilter(ShardFilter):
        """A mock ShardFilter for testing."""

        def __init__(self, num_shards: int, valid_shard: int = -1):
            super().__init__(num_shards=num_shards, valid_shard=valid_shard)

        def _shard(self, item: Item) -> int:
            """A mock _shard method that always returns 0."""
            return 0

    def test_shard_filter_initialization(self):
        """Test that a ShardFilter can be initialized correctly."""
        shard_filter = self.MockShardFilter(5, 0)

        assert shard_filter.num_shards == 5
        assert shard_filter.valid_shard == 0

    def test_shard_filter_not_initialized(self):
        """Test that a ShardFilter raises an AssertionError if not initialized correctly."""
        shard_filter = self.MockShardFilter(5)

        with pytest.raises(AssertionError):
            shard_filter._is_valid(self.MockItem("test"))

    def test_shard_filter_is_valid(self):
        """Test that the _is_valid method works correctly."""
        shard_filter = self.MockShardFilter(5, 0)

        assert shard_filter._is_valid(self.MockItem("test")) is True

        shard_filter.valid_shard = 1

        assert shard_filter._is_valid(self.MockItem("test")) is False
