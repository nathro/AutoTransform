# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The EventType enum."""

from enum import Enum


class EventType(str, Enum):
    """A simple enum for Event naming"""

    DEBUG = "debug"
    MANAGE_ACTION = "manage_action"
    REMOTE_RUN = "remote_run"
    REMOTE_UPDATE = "remote_update"
    SCHEDULE_RUN = "schedule_run"
    SCRIPT_RUN = "script_run"
    WARNING = "warning"
