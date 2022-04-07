# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The Remote type enum"""

from enum import Enum


class RemoteType(str, Enum):
    """A simple enum for 1:1 Remote to type mapping."""

    GITHUB = "github"
