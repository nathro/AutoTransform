# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from enum import Enum


class WorkerType(str, Enum):
    LOCAL = "local"

    # Section reserved for custom types to reduce merge conflicts
    # BEGIN CUSTOM TYPES
    # END CUSTOM TYPES
