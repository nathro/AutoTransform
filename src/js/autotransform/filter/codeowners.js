// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The implementation for the CodeownersFilter. */

import { Filter, FilterName } from 'autotransform/filter/base';
import { Item } from 'autotransform/item/base';
import { FileItem } from 'autotransform/item/file';
import { CodeOwners } from 'codeowners';
import { root_validator } from 'pydantic';

class CodeownersFilter extends Filter {
    /* A filter which uses Github CODEOWNERS files to separate changes by owner. Titles will
    be of the form 'prefix <owner>'

    Attributes:
        codeowners_file_path (str): The path of the CODEOWNERS file.
        owner (Optional[str]): The owner to allow files for. If None is provided, checks
            for unowned.
        name (ClassVar[FilterName]): The name of the Component.
    */

    constructor(codeowners_file_path, owner) {
        super();
        this.codeowners_file_path = codeowners_file_path;
        this.owner = owner;
        this.name = FilterName.CODEOWNERS;
    }

    static path_legacy_setting_validator(values) {
        /* Validates codeowners_file_path using legacy codeowners_location setting.

        Args:
            values (Dict[str, Any]): The values used to configure the CodeownersFilter.

        Raises:
            ValueError: Raised if both codeowners_file_path and codeowners_location are supplied.

        Returns:
            Mapping[str, Any]: The fixed values.
        */

        if (values.codeowners_location) {
            if (
                values.codeowners_file_path &&
                values.codeowners_file_path !== values.codeowners_location
            ) {
                throw new Error(
                    "Can not supply both codeowners_location and codeowners_file_path "
                    + "for DirectoryInput"
                );
            }
            values.codeowners_file_path = values.codeowners_location;
        }
        return values;
    }

    get _owners() {
        /* Gets the parsed CodeOwners as a cached property.

        Returns:
            CodeOwners: The parsed CodeOwners.
        */

        const codeowners_file = fs.readFileSync(this.codeowners_file_path, 'utf8');
        return new CodeOwners(codeowners_file);
    }

    get _formatted_owner() {
        if (this.owner === null) {
            return null;
        }
        return this.owner.replace("@", "");
    }

    _is_valid(item) {
        /* Checks whether the Item is a file owned by the supplied owner. If no owner
        is supplied, checks for whether the file is unowned.

        Args:
            item (Item): The Item the Filter is checking.

        Returns:
            bool: Whether the Item passes the Filter.
        */

        if (!(item instanceof FileItem)) {
            return false;
        }
        const owners = this._owners.of(item.get_path());

        if (this.owner === null) {
            return !owners;
        }

        return owners.some(owner => this._formatted_owner === owner[1].replace("@", ""));
    }
}