# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the KeyHashShardFilter."""

from hashlib import md5
from typing import ClassVar

from autotransform.filter.base import FilterName
from autotransform.filter.shard import ShardFilter
from autotransform.item.base import Item


class KeyHashShardFilter(ShardFilter):
    """A Filter which produces a shard from the key of an Item using md5 hashing.

    Attributes:
        name (ClassVar[FilterName]): The name of the component.
    """

    name: ClassVar[FilterName] = FilterName.KEY_HASH_SHARD

    def _shard(self, item: Item) -> int:
        """Produces a shard from an item.

        Args:
            item (Item): The Item to produce a shard number for.

        Returns:
            int: The shard number for the Item.
        """

        # Ensure the key is encoded in UTF-8 before hashing
        encoded_key = item.key.encode("UTF-8")
        hashed_key = md5(encoded_key).hexdigest()

        # Convert the hexadecimal hash to an integer and return the shard number
        return int(hashed_key, 16) % self.num_shards
