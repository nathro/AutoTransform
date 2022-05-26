# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The type of Item, used create a 1:1 mapping."""

from enum import Enum


class ItemType(str, Enum):
    """A simple enum for 1:1 Type to type mapping."""

    FILE = "file"
    GENERIC = "generic"
