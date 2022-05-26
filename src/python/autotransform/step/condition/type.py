# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The type of Condition, used create a 1:1 mapping."""

from enum import Enum


class ConditionType(str, Enum):
    """A simple enum for 1:1 Condition to type mapping."""

    AGGREGATE = "aggregate"
    CHANGE_STATE = "change_state"
    CREATED_AGO = "created_ago"
    SCHEMA_NAME = "schema_name"
    UPDATED_AGO = "updated_ago"
