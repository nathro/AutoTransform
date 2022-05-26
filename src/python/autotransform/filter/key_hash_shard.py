# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for regex based filters, including RegexFilter and FileContentRegexFilter."""

from __future__ import annotations

from typing import Any, Mapping

from autotransform.filter.shard import ShardFilter, ShardFilterParams
from autotransform.filter.type import FilterType
from autotransform.item.base import Item


class KeyHashShardFilterParams(ShardFilterParams):
    """The param type for a KeyHashShardFilter."""


class KeyHashShardFilter(ShardFilter):
    """A Filter which produces a shard from the key of an Item, using simple hashing.

    Attributes:
        _params (KeyHashShardFilterParams): Contains the valid shard and num shards.
    """

    _params: KeyHashShardFilterParams

    @staticmethod
    def get_type() -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """

        return FilterType.KEY_HASH_SHARD

    def _shard(self, item: Item) -> int:
        """Produces a shard from an item.

        Args:
            item (Item): The Item to produce a shard number for.

        Returns:
            int: The shard number for the Item.
        """

        return hash(item.get_key()) % self._params["num_shards"]

    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> KeyHashShardFilter:
        """Produces a KeyHashShardFilter from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            KeyHashShardFilter: An instance of the KeyHashShardFilter with the provided params.
        """

        num_shards = data["num_shards"]
        assert isinstance(num_shards, int)
        valid_shard = data["valid_shard"]
        assert isinstance(valid_shard, int)
        return KeyHashShardFilter({"num_shards": num_shards, "valid_shard": valid_shard})
