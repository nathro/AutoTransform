# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The SchemaBuilder name enum"""

from enum import Enum


class SchemaBuilderName(str, Enum):
    """A simple enum for 1:1 SchemaBuilder to name mapping.

    Note:
        Custom names should be placed in the CUSTOM NAMES section.
        This will reduce merge conflicts when merging in upstream changes.
    """
