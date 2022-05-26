# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides utility methods for interacting with the scheduling of AutoTransform."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import List, TypedDict

from typing_extensions import NotRequired

from autotransform.filter.base import FilterBundle
from autotransform.filter.type import FilterType
from autotransform.runner.base import RunnerBundle
from autotransform.util.console import (
    choose_option,
    choose_yes_or_no,
    get_str,
    info,
    input_int,
    input_string,
)


class SchemaType(str, Enum):
    """Possible types of Schemas to use."""

    BUILDER = "builder"
    FILE = "file"

    @staticmethod
    def from_value(value: str) -> SchemaType:
        """Gets the enum value associated with a string value.

        Args:
            value (str): The value of a member of the enum.

        Returns:
            SchemaType: The associated enum value.
        """
        if value == SchemaType.BUILDER:
            return SchemaType.BUILDER
        if value == SchemaType.FILE:
            return SchemaType.FILE
        raise ValueError(f"Invalid value {value} for SchemaType")


class RepeatSchedule(str, Enum):
    """Possible repitition schedules."""

    DAILY = "daily"
    WEEKLY = "weekly"

    @staticmethod
    def from_value(value: str) -> RepeatSchedule:
        """Gets the enum value associated with a string value.

        Args:
            value (str): The value of a member of the enum.

        Returns:
            RepeatSchedule: The associated enum value.
        """
        if value == RepeatSchedule.DAILY:
            return RepeatSchedule.DAILY
        if value == RepeatSchedule.WEEKLY:
            return RepeatSchedule.WEEKLY
        raise ValueError(f"Invalid value {value} for RepeatSchedule")


class Sharding(TypedDict):
    """The sharding setting for a schedule."""

    num_shards: int
    shard_filter: FilterBundle


class Schedule(TypedDict):
    """A schedule for a Schema."""

    repeats: RepeatSchedule
    hour_of_day: int
    day_of_week: NotRequired[int]
    sharding: NotRequired[Sharding]


class ScheduledSchema(TypedDict):
    """A schema that is scheduled for automatic runs."""

    type: SchemaType
    schema: str
    schedule: Schedule


class ScheduleBundle(TypedDict):
    """The information required to set up scheduling of AutoTransform."""

    base_time: int
    runner: RunnerBundle
    excluded_days: List[int]
    schemas: List[ScheduledSchema]


def input_scheduled_schema() -> ScheduledSchema:
    """Gets a schema's schedule.

    Returns:
        Mapping[str, Any]: The schema with scheduling information.
    """

    schema = get_str("Enter the schema to schedule: ")

    schema_type = choose_option(
        "What is the type of the schema?",
        [(SchemaType.FILE, ["file", "f"]), (SchemaType.BUILDER, ["builder", "b"])],
    )
    schema_type = SchemaType.from_value(schema_type)

    repeats = choose_option(
        "How often should the schema run?",
        [(RepeatSchedule.DAILY, ["d"]), (RepeatSchedule.WEEKLY, ["w"])],
    )
    hour_of_day = input_int("What hour of the day should the schema run?", min_val=0, max_val=23)
    schedule: Schedule = {
        "repeats": repeats,
        "hour_of_day": hour_of_day,
    }

    if repeats == RepeatSchedule.WEEKLY:
        schedule["day_of_week"] = input_int(
            "What day of the week should the schema run?", min_val=0, max_val=6
        )

    if choose_yes_or_no("Do you want to use sharding for this schema?"):
        num_shards = input_int("How many shards would you like to use?", min_val=1)
        shard_filter = input_string(
            "Enter the JSON encoded shard filter:",
            "shard filter",
            default=json.dumps({"type": FilterType.KEY_HASH_SHARD, "params": {}}),
        )
        schedule["sharding"] = {"num_shards": num_shards, "shard_filter": json.loads(shard_filter)}

    return {
        "type": schema_type,
        "schema": schema,
        "schedule": schedule,
    }


def input_schedule_bundle(
    runner: RunnerBundle, use_sample_schema: bool = False, simple: bool = False
) -> ScheduleBundle:
    """Get the bundle needed to create the schedule.json file.

    Args:
        runner (Any): The runner bundle to use for scheduling.
        use_sample_schema (bool, optional): Whether to include the sample schema. Defaults to False.
        simple (bool, optional): Whether to use simple inputs. Defaults to False.

    Returns:
        Mapping[str, Any]: The schedule bundle.
    """

    info("Using local time to establish a base")
    info("Midnight Monday local is day_of_week 0, hour_of_day 0")
    if not simple and choose_yes_or_no("Apply a modifier to local time for scheduling?"):
        base_modifier = input_int("Enter the modifier in secords:")
    else:
        base_modifier = 0

    if not simple and choose_yes_or_no("Should AutoTransform schedule runs on weekends?"):
        excluded_days = []
    else:
        excluded_days = [5, 6]

    if use_sample_schema:
        schemas: List[ScheduledSchema] = [
            {
                "type": SchemaType.FILE,
                "schema": "autotransform/schemas/black_format.json",
                "schedule": {"repeats": RepeatSchedule.DAILY, "hour_of_day": 7},
            }
        ]
    else:
        schemas = []

    get_new_schema = not simple and choose_yes_or_no("Add a schema to the schedule?")
    while get_new_schema:
        schemas.append(input_scheduled_schema())
        get_new_schema = choose_yes_or_no("Would you like to add a schema to the schedule?")

    return {
        "base_time": int(datetime.fromisoformat("2022-05-23T00:00:00").timestamp()) + base_modifier,
        "runner": runner,
        "excluded_days": excluded_days,
        "schemas": schemas,
    }
