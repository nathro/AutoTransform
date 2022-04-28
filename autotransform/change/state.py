# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The state of a Change, used to handle potential updates for a change."""

from enum import Enum


class ChangeState(str, Enum):
    """A simple enum for the state of a given Change in code review or version
    control systems."""

    ACCEPTED = "accepted"
    CLOSED = "closed"
    MERGED = "merged"
    OPEN = "open"
