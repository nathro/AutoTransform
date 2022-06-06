# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for regex based filters, including RegexFilter and FileContentRegexFilter."""

from __future__ import annotations

from typing import ClassVar

from autotransform.filter.base import FilterName
from autotransform.filter.shard import ShardFilter
from autotransform.item.base import Item


class KeyHashShardFilter(ShardFilter):
    """A Filter which produces a shard from the key of an Item, using simple hashing.

    Attributes:
        inverted (bool, optional): Whether to invert the results of the filter. Defaults to False.
        name (ClassVar[FilterName]): The name of the component.
    """

    inverted: bool = False

    name: ClassVar[FilterName] = FilterName.KEY_HASH_SHARD

    @staticmethod
    def get_type() -> FilterName:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """

        return FilterName.KEY_HASH_SHARD

    def _shard(self, item: Item) -> int:
        """Produces a shard from an item.

        Args:
            item (Item): The Item to produce a shard number for.

        Returns:
            int: The shard number for the Item.
        """

        return hash(item.key) % self.num_shards
