# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that Manager functions as expected."""

import json
import pathlib

from autotransform.runner.github import GithubRunner
from autotransform.util.scheduler import (
    RepeatSetting,
    ScheduledSchema,
    Scheduler,
    SchemaScheduleSettings,
)


def get_sample_scheduler() -> Scheduler:
    """Gets a sample Scheduler.

    Returns:
        Scheduler: The sample Scheduler.
    """

    return Scheduler(
        base_time=1650870000,
        excluded_days=[5, 6],
        schemas=[
            ScheduledSchema(
                schema_name="Black Format",
                schedule=SchemaScheduleSettings(repeats=RepeatSetting.DAILY, hour_of_day=7),
            ),
        ],
    )


def test_decoding():
    """Tests that the Scheduler component is decoded properly."""

    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    manager = Scheduler.read(f"{parent_dir}/data/scheduler.json")
    assert manager == get_sample_scheduler()


def test_encoding():
    """Tests that the Scheduler component is encoded properly."""

    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(f"{parent_dir}/data/scheduler.json", "r", encoding="UTF-8") as file:
        assert json.dumps(get_sample_scheduler().bundle(), indent=4) == file.read()
