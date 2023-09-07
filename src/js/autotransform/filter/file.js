// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The implementation for file filters. */

const fs = require('fs');
const path = require('path');
const Filter = require('autotransform/filter/base').Filter;
const FilterName = require('autotransform/filter/base').FilterName;
const Item = require('autotransform/item/base').Item;
const FileItem = require('autotransform/item/file').FileItem;

class FileExistsFilter extends Filter {
    /* A Filter which checks whether a File associated with the FileItem exists.

    Attributes:
        check_target_path (bool, optional): Check the target_path, rather than the key
            of the FileItem. Defaults to False.
        name (ClassVar[FilterName]): The name of the component.
    */

    constructor() {
        super();
        this.check_target_path = false;
        this.name = FilterName.FILE_EXISTS;
    }

    _is_valid(item) {
        /* Check whether the key contains the pattern.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        */

        if (!(item instanceof FileItem)) {
            return false;
        }

        let path_to_check = this.check_target_path ? item.extra_data?.target_path : item.get_path();

        if (path_to_check === null || typeof path_to_check !== 'string') {
            return false;
        }

        return fs.existsSync(path.resolve(path_to_check));
    }
}

module.exports = FileExistsFilter;