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
    BATCH_EXECUTION_FAILED = "batch_execution_failed"
    BATCH_NO_CHANGES = "batch_no_changes"
    BATCH_SKIP = "batch_skip"
    BATCH_SUBMIT = "batch_submit"
    BATCH_VALIDATION_FAILED = "batch_validation_failed"
    DEBUG = "debug"
    GITHUB_PULL_REQUEST_CREATED = "github_pull_request_created"
    MANAGE_ABANDON = "manage_abandon"
    MANAGE_ACTION = "manage_action"
    MANAGE_COMMENT = "manage_comment"
    MANAGE_MERGE = "manage_merge"
    MANAGE_UPDATE = "manage_update"
    MANAGE_REQUEST = "manage_request"
    RUNNER_FAILED = "runner_failed"
    RUNNER_RUN = "runner_run"
    RUNNER_UPDATE = "runner_update"
    UTIL_REVERT_FILE = "util_revert_file"
    RUN = "run"
    RUN_FAILED = "run_failed"
    RUN_COMMAND_FAILED = "run_command_failed"
    RUN_MANAGER = "run_manager"
    RUN_MANAGER_FAILED = "run_manager_failed"
    RUN_SCHEDULER = "run_scheduler"
    RUN_SCHEDULER_FAILED = "run_scheduler_failed"
    RUN_UPDATE = "run_update"
    RUN_UPDATE_FAILED = "run_update_failed"
    SCHEDULE_RUN = "schedule_run"
    SCRIPT_ERR = "script_err"
    SCRIPT_OUT = "script_out"
    SCRIPT_RUN = "script_run"
    VERBOSE = "verbose"
    WARNING = "warning"
