// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The base class and associated classes for Filter components. */

import { Item } from 'autotransform/item/base';
import { ComponentFactory, ComponentImport, NamedComponent } from 'autotransform/util/component';

const FilterName = Object.freeze({
    AGGREGATE: "aggregate",
    CODEOWNERS: "codeowners",
    FILE_EXISTS: "file_exists",
    REGEX: "regex",
    REGEX_FILE_CONTENT: "regex_file_content",
    SCRIPT: "script",
    KEY_HASH_SHARD: "key_hash_shard"
});

class Filter extends NamedComponent {
    inverted = false;

    name = FilterName;

    is_valid(item) {
        return this.inverted !== this._is_valid(item);
    }

    _is_valid(item) {
        throw new Error('You have to implement the method _is_valid!');
    }
}

class BulkFilter extends Filter {
    _valid_keys = null;

    _get_valid_keys(items) {
        throw new Error('You have to implement the method _get_valid_keys!');
    }

    pre_process(items) {
        if (this._valid_keys === null) {
            this._valid_keys = this._get_valid_keys(items);
        }
    }

    _is_valid(item) {
        return this._valid_keys !== null && this._valid_keys.includes(item.key);
    }
}

const FACTORY = new ComponentFactory(
    {
        [FilterName.AGGREGATE]: new ComponentImport(
            "AggregateFilter", "autotransform/filter/aggregate"
        ),
        [FilterName.CODEOWNERS]: new ComponentImport(
            "CodeownersFilter", "autotransform/filter/codeowners"
        ),
        [FilterName.FILE_EXISTS]: new ComponentImport(
            "FileExistsFilter", "autotransform/filter/file"
        ),
        [FilterName.REGEX]: new ComponentImport(
            "RegexFilter", "autotransform/filter/regex"
        ),
        [FilterName.REGEX_FILE_CONTENT]: new ComponentImport(
            "RegexFileContentFilter", "autotransform/filter/regex"
        ),
        [FilterName.SCRIPT]: new ComponentImport(
            "ScriptFilter", "autotransform/filter/script"
        ),
        [FilterName.KEY_HASH_SHARD]: new ComponentImport(
            "KeyHashShardFilter", "autotransform/filter/key_hash_shard"
        ),
    },
    Filter,
    "filter.json",
);