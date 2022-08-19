# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Enums used by utilities of AutoTransform."""

from enum import Enum


class SchemaType(str, Enum):
    """Possible types of Schemas to use."""

    BUILDER = "builder"
    FILE = "file"
