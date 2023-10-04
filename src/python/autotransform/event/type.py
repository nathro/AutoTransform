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

    AI_MODEL_COMMAND_FAILURE = "ai_model_command_failure"
    AI_MODEL_COMPLETION = "ai_model_completion"
    AI_MODEL_COMPLETION_FAILURE = "ai_model_completion_failure"
    DEBUG = "debug"
    MANAGE_ACTION = "manage_action"
    REMOTE_RUN = "remote_run"
    REMOTE_UPDATE = "remote_update"
    RUN = "run"
    SCHEDULE_RUN = "schedule_run"
    SCRIPT_ERR = "script_err"
    SCRIPT_OUT = "script_out"
    SCRIPT_RUN = "script_run"
    VERBOSE = "verbose"
    WARNING = "warning"
