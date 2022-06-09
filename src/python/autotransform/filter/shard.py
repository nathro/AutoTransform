# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A base for sharding filters used by schedule runs to shard Input items."""

from __future__ import annotations

from abc import abstractmethod

from autotransform.filter.base import Filter
from autotransform.item.base import Item


class ShardFilter(Filter):
    """A base for sharding filters that checks that an Item fits the current valid shard.

    Attributes:
        num_shards (int): The number of shards to split the items across.
        valid_shard (int): The current valid shard to use.
    """

    num_shards: int
    valid_shard: int = -1

    @abstractmethod
    def _shard(self, item: Item) -> int:
        """Produces a shard from an item.

        Args:
            item (Item): The Item to produce a shard number for.

        Returns:
            int: The shard number for the Item.
        """

    def _is_valid(self, item: Item) -> bool:
        """Check whether the item's shard matches the current shard.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the Item's shard matches the current valid shard.
        """

        assert self.valid_shard >= 0, "Shard filter not initialized correctly"
        return self._shard(item) == self.valid_shard
