// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The implementation for regex based filters, including RegexFilter and FileContentRegexFilter. */

import { Filter, FilterName } from 'autotransform/filter/base';
import { Item } from 'autotransform/item/base';
import { FileItem } from 'autotransform/item/file';

class RegexFilter extends Filter {
    /* A Filter which only passes Items where the Item's key matches a provided regex pattern.
    Uses re.search rather than re.match.

    Attributes:
        pattern (str): The pattern to use when checking the Item's key.
        name (ClassVar[FilterName]): The name of the component.
    */

    constructor(pattern) {
        super();
        this.pattern = pattern;
        this.name = FilterName.REGEX;
    }

    _is_valid(item) {
        /* Check whether the key contains the pattern.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        */

        return new RegExp(this.pattern).test(item.key);
    }
}

class RegexFileContentFilter extends Filter {
    /* A Filter which only passes FileItems where the file's content contains a match to the
    provided regex pattern. Uses re.search rather than re.match.

    Attributes:
        pattern (str): The pattern to use when checking the FileItem's content
        name (ClassVar[FilterName]): The name of the component.
    */

    constructor(pattern) {
        super();
        this.pattern = pattern;
        this.name = FilterName.REGEX_FILE_CONTENT;
    }

    _is_valid(item) {
        /* Check whether the contents of the file contains the pattern.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the file's content.
        */

        if (!(item instanceof FileItem)) {
            return false;
        }
        return new RegExp(this.pattern).test(item.get_content());
    }
}

export { RegexFilter, RegexFileContentFilter };