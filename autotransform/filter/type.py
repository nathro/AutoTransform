# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The Filter type enum"""

from enum import Enum


class FilterType(str, Enum):
    """A simple enum for 1:1 Filter to type mapping.

    Note:
        Custom types should be placed in the CUSTOM TYPES section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    CONTENT_REGEX = "content_regex"
    EXTENSION = "extension"
    REGEX = "regex"
