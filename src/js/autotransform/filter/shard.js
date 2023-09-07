// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* A base for sharding filters used by schedule runs to shard Input items. */

import { Filter } from 'autotransform/filter/base';
import { Item } from 'autotransform/item/base';

class ShardFilter extends Filter {
    /* A base for sharding filters that checks that an Item fits the current valid shard.

    Attributes:
        num_shards (int): The number of shards to split the items across.
        valid_shard (int): The current valid shard to use.
    */

    constructor() {
        super();
        this.num_shards = null;
        this.valid_shard = -1;
    }

    /* Produces a shard from an item.

    Args:
        item (Item): The Item to produce a shard number for.

    Returns:
        int: The shard number for the Item.
    */
    _shard(item) {
        throw new Error('You have to implement the method _shard!');
    }

    /* Check whether the item's shard matches the current shard.

    Args:
        item (Item): The Item to check.

    Returns:
        bool: Returns True if the Item's shard matches the current valid shard.
    */
    _is_valid(item) {
        if (this.valid_shard < 0) {
            throw new Error('Shard filter not initialized correctly');
        }
        return this._shard(item) === this.valid_shard;
    }
}

export { ShardFilter };