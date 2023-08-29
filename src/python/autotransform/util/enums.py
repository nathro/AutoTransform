# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Enums used by utilities of AutoTransform or across a number of components."""

from enum import Enum


class AggregatorType(Enum):
    """A list of possible comparisons."""

    ALL = "all"
    ANY = "any"

    def __str__(self):
        return self.value


class SchemaType(Enum):
    """Possible types of Schemas to use."""

    BUILDER = "builder"
    FILE = "file"

    def __str__(self):
        return self.value
