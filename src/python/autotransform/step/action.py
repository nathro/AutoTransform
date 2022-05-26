# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Actions are returned by Steps to determine what should be done based on the Step."""

from enum import Enum
from typing import TypedDict


class ActionType(str, Enum):
    """An enum representing a possible action to take."""

    ABANDON = "abandon"
    MERGE = "merge"
    NONE = "none"
    UPDATE = "update"


class Action(TypedDict):
    """An Action represents the results of checking a Step to determine what should be
    done in response to it."""

    stop_steps: bool
    type: ActionType
