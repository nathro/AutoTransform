// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The implementation for the KeyHashShardFilter. */

const crypto = require('crypto');

const FilterName = require('autotransform/filter/base');
const ShardFilter = require('autotransform/filter/shard');
const Item = require('autotransform/item/base');

class KeyHashShardFilter extends ShardFilter {
    /* A Filter which produces a shard from the key of an Item using md5 hashing.

    Attributes:
        name (ClassVar[FilterName]): The name of the component.
    */

    constructor() {
        super();
        this.name = FilterName.KEY_HASH_SHARD;
    }

    _shard(item) {
        /* Produces a shard from an item.

        Args:
            item (Item): The Item to produce a shard number for.

        Returns:
            int: The shard number for the Item.
        */

        // Ensure the key is encoded in UTF-8 before hashing
        let encoded_key = new Buffer.from(item.key, "utf8");
        let hashed_key = crypto.createHash('md5').update(encoded_key).digest('hex');

        // Convert the hexadecimal hash to an integer and return the shard number
        return parseInt(hashed_key, 16) % this.num_shards;
    }
}

module.exports = KeyHashShardFilter;