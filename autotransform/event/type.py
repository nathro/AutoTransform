# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The Event type enum"""

from enum import Enum


class EventType(str, Enum):
    """A simple enum for Event naming"""

    DEBUG = "debug"
    SCRIPT_RUN = "script_run"
