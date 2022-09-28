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
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from pydantic import validator

from autotransform.config import get_config, get_repo_config_relative_path
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.schedulerun import ScheduleRunEvent
from autotransform.filter.base import FACTORY as filter_factory
from autotransform.filter.key_hash_shard import KeyHashShardFilter
from autotransform.filter.shard import ShardFilter
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.component import ComponentModel
from autotransform.util.console import (
    choose_option,
    choose_options_from_list,
    choose_yes_or_no,
    error,
    get_str,
    info,
    input_int,
    input_ints,
)
from autotransform.util.enums import SchemaType


class RepeatSetting(str, Enum):
    """Possible repitition schedules."""

    DAILY = "daily"
    WEEKLY = "weekly"


class SchemaScheduleSettings(ComponentModel):
    """A schedule for a Schema.

    Attributes:
        repeats (RepeatSetting): How often the Schema will be run, daily or weekly.
        hour_of_day (int, optional): The hour of the day to run the Schema, 0-23. Defaults to 0.
        day_of_week (Optional[int], optional): The day of the week to run a weekly Schema.
            Defaults to 0.
        shard_filter (Optional[ShardingSettings], optional): A shard filter to use for sharding
            the inputs across multiple runs. Defaults to None.
    """

    repeats: RepeatSetting
    hour_of_day: int = 0
    day_of_week: Optional[int] = 0
    shard_filter: Optional[ShardFilter] = None

    def should_run(self, hour_of_day: int, day_of_week: int) -> bool:
        """Whether the schema should be run.

        Args:
            hour_of_day (int): The hour of day to check.
            day_of_week (int): The day of week to check.

        Returns:
            bool: Whether the schema should run.
        """

        return self.hour_of_day == hour_of_day and (
            self.repeats == RepeatSetting.DAILY or self.day_of_week == day_of_week
        )

    @staticmethod
    def from_data(data: Dict[str, Any]) -> SchemaScheduleSettings:
        """Produces an instance of the SchemaScheduleSettings from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            SchemaScheduleSettings: An instance of the SchemaScheduleSettings.
        """

        repeats = RepeatSetting(data["repeats"])
        hour_of_day = data.get("hour_of_day", 0)
        assert isinstance(hour_of_day, int)
        assert hour_of_day in range(24)
        day_of_week = data.get("day_of_week", 0)
        if day_of_week is not None:
            assert isinstance(day_of_week, int)
            assert day_of_week in range(7)

        shard_filter = data.get("shard_filter", None)
        if shard_filter is not None:
            shard_filter = filter_factory.get_instance(shard_filter)
        else:
            shard_filter = None

        return SchemaScheduleSettings(
            repeats=repeats,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            shard_filter=shard_filter,
        )

    @staticmethod
    def from_console(simple: bool = False) -> SchemaScheduleSettings:
        """Gets a SchemaScheduleSettings from console inputs.

        Attributes:
            simple (bool, optional): Whether to use simple settings. Defaults to False.

        Returns:
            SchemaScheduleSettings: The input SchemaScheduleSettings.
        """

        # Get repeats
        repeats = choose_option(
            "How often should the schema run?",
            [(RepeatSetting.DAILY, ["d"]), (RepeatSetting.WEEKLY, ["w"])],
        )

        # Get hour_of_day
        hour_of_day = input_int(
            "Enter the hour of the day to run the schema", min_val=0, max_val=23
        )

        # Get day_of_week
        if repeats == RepeatSetting.WEEKLY:
            day_of_week = input_int(
                "Enter the day of the week to run the schema", min_val=0, max_val=6
            )
        else:
            day_of_week = None

        # Get shard_filter
        if not simple and choose_yes_or_no("Do you want to use sharding for this schema?"):
            shard_filter = filter_factory.from_console(
                "shard filter",
                default_value=KeyHashShardFilter(num_shards=10),
                allow_none=False,
            )
            while not isinstance(shard_filter, ShardFilter):
                assert shard_filter is not None
                error(f"{shard_filter.name} is not a shard filter")
                shard_filter = filter_factory.from_console(
                    "shard filter",
                    allow_none=False,
                )
        else:
            shard_filter = None

        return SchemaScheduleSettings(
            repeats=repeats,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            shard_filter=shard_filter,
        )


class ScheduledSchema(ComponentModel):
    """A Schema that is scheduled for automatic runs.

    Attributes:
        schema_name (str): The Schema that is being scheduled.
        schedule (SchemaScheduleSettings): The settings used to determine when to run the Schema.
        max_submissions (Optional[int], optional): The max number of submissions from a given
            scheduled run. No limit if None. Defaults to None.
    """

    schema_name: str
    schedule: SchemaScheduleSettings

    max_submissions: Optional[int] = None

    # pylint: disable=invalid-name
    @validator("max_submissions")
    @classmethod
    def max_submissions_is_positive(cls: Type[ScheduledSchema], v: Optional[int]) -> Optional[int]:
        """Validates that max submissions is positive.

        Args:
            cls (Type[ScheduledSchema]): The ScheduledSchema class.
            v (int): The maximum number of submissions.

        Raises:
            ValueError: Raised if the maximum number of submissions is not positive.

        Returns:
            Optional[int]: The unmodified maximum number of submissions.
        """

        if v is not None and v < 1:
            raise ValueError(f"Maximum number of submissions must be positive, {v} provided")
        return v

    @staticmethod
    def from_data(data: Dict[str, Any]) -> ScheduledSchema:
        """Produces an instance of the ScheduledSchema from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            ScheduledSchema: An instance of the ScheduledSchema.
        """

        schema_name = data["schema_name"]
        assert isinstance(schema_name, str)
        schedule = SchemaScheduleSettings.from_data(data["schedule"])
        max_submissions = data.get("max_submissions", None)
        if max_submissions is not None:
            assert isinstance(max_submissions, int)
        return ScheduledSchema(
            schema_name=schema_name, schedule=schedule, max_submissions=max_submissions
        )

    @staticmethod
    def from_console() -> ScheduledSchema:
        """Gets a ScheduledSchema from console inputs.

        Returns:
            ScheduledSchema: The input ScheduledSchema.
        """

        schema_name = get_str("Enter the schema to schedule: ")

        if choose_yes_or_no("Would you like to limit the maximum number of submissions?"):
            max_submissions = input_int("Enter the maximum number of submissions", min_val=1)
        else:
            max_submissions = None

        return ScheduledSchema(
            schema_name=schema_name,
            schedule=SchemaScheduleSettings.from_console(),
            max_submissions=max_submissions,
        )


class Scheduler(ComponentModel):
    """The information and functionality required to schedule Schemas.

    Attributes:
        base_time (int): The base time to use when determining hour_of_day, day_of_week,
            and valid shards. Considered day 0, hour 0.
        excluded_days (List[int]): A list of days of the week to skip running Schemas.
        schemas (List[ScheduledSchema]): A list of Schemas to schedule.
    """

    base_time: int
    excluded_days: List[int]
    schemas: List[ScheduledSchema]

    def run(self, start_time: int) -> None:
        """Runs the schedule.

        Args:
            start_time (int): The time that the schedule is run on.
        """

        elapsed_time = start_time - self.base_time

        elapsed_hours = int(elapsed_time / 60 / 60)
        elapsed_days, hour_of_day = divmod(elapsed_hours, 24)
        elapsed_weeks, day_of_week = divmod(elapsed_days, 7)

        EventHandler.get().handle(
            DebugEvent({"message": f"Running for hour {hour_of_day}, day {day_of_week}"})
        )
        EventHandler.get().handle(
            DebugEvent({"message": f"Elapsed days {elapsed_days}, weeks {elapsed_weeks}"})
        )

        if day_of_week in self.excluded_days:
            EventHandler.get().handle(
                DebugEvent({"message": f"Day {day_of_week} is excluded, skipping run"})
            )
            return

        runner = get_config().remote_runner
        assert runner is not None

        map_file_path = f"{get_repo_config_relative_path()}/schema_map.json"
        with open(map_file_path, "r", encoding="UTF-8") as map_file:
            schema_map = json.loads(map_file.read())

        for scheduled_schema in self.schemas:
            # Check if should run
            if not scheduled_schema.schedule.should_run(hour_of_day, day_of_week):
                EventHandler.get().handle(
                    DebugEvent(
                        {"message": f"Skipping run of schema: {scheduled_schema.schema_name}"}
                    )
                )
                continue
            schema_data = schema_map[scheduled_schema.schema_name]
            schema_type = SchemaType(schema_data["type"])
            if schema_type == SchemaType.BUILDER:
                schema = schema_builder_factory.get_instance(
                    {"name": schema_data["target"]}
                ).build()
            else:
                with open(schema_data["target"], "r", encoding="UTF-8") as schema_file:
                    schema = AutoTransformSchema.from_data(json.loads(schema_file.read()))
            shard_filter = scheduled_schema.schedule.shard_filter
            if shard_filter is not None:
                if scheduled_schema.schedule.repeats == RepeatSetting.DAILY:
                    shard_filter.valid_shard = elapsed_days % shard_filter.num_shards
                else:
                    shard_filter.valid_shard = (elapsed_days // 7) % shard_filter.num_shards
                EventHandler.get().handle(DebugEvent({"message": f"Sharding: {shard_filter!r}"}))
                schema.filters.append(shard_filter)
            if scheduled_schema.max_submissions is not None:
                schema.config.max_submissions = scheduled_schema.max_submissions
            EventHandler.get().handle(ScheduleRunEvent({"schema_name": schema.config.schema_name}))
            runner.run(schema)

    def write(self, file_path: str) -> None:
        """Writes the Scheduler to a file as JSON.

        Args:
            file_path (str): The file to write to.
        """

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+", encoding="UTF-8") as scheduler_file:
            scheduler_file.write(json.dumps(self.bundle(), indent=4))
            scheduler_file.flush()

    @staticmethod
    def read(file_path: str) -> Scheduler:
        """Reads a Scheduler from a JSON encoded file.

        Args:
            file_path (str): The path where the JSON for the Schedule is located.

        Returns:
            Scheduler: The Scheduler from the file.
        """

        with open(file_path, "r", encoding="UTF-8") as scheduler_file:
            scheduler_json = scheduler_file.read()
        EventHandler.get().handle(
            DebugEvent({"message": f"Scheduler: ({file_path})\n{scheduler_json}"})
        )
        return Scheduler.from_json(scheduler_json)

    @staticmethod
    def from_json(scheduler_json: str) -> Scheduler:
        """Builds a Scheduler from JSON encoded values.

        Args:
            scheduler_json (str): The JSON encoded Scheduler.
            start_time (int): The start time to use for setting up sharding/running.

        Returns:
            Scheduler: The Scheduler from the JSON.
        """

        return Scheduler.from_data(json.loads(scheduler_json))

    @staticmethod
    def from_data(data: Dict[str, Any]) -> Scheduler:
        """Produces an instance of the Scheduler from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            Scheduler: An instance of the Scheduler.
        """

        base_time = data["base_time"]
        assert isinstance(base_time, int)
        excluded_days = data["excluded_days"]
        assert isinstance(excluded_days, List)
        for day in excluded_days:
            assert isinstance(day, int)
            assert day in range(7)
        schemas = [ScheduledSchema.from_data(schema) for schema in data.get("schemas", [])]
        return Scheduler(base_time=base_time, excluded_days=excluded_days, schemas=schemas)

    @staticmethod
    def init_from_console(use_sample_schema: bool = False, simple: bool = False) -> Scheduler:
        """Gets a Scheduler using console input.

        Args:
            use_sample_schema (bool, optional): Whether to include the sample Schema. Defaults
                to False.
            simple (bool, optional): Whether to use simple settings. Defaults to False.

        Returns:
            Scheduler: The input Scheduler.
        """

        # Gets base time
        info("Using local time to establish a base")
        info("Midnight Monday local is day_of_week 0, hour_of_day 0")
        if not simple and choose_yes_or_no("Apply a modifier to local time for scheduling?"):
            base_modifier = input_int("Enter the modifier in seconds")
        else:
            base_modifier = 0

        # Gets excluded days
        if not simple and choose_yes_or_no("Should AutoTransform schedule runs on weekends?"):
            excluded_days = []
        else:
            excluded_days = [5, 6]

        # Gets Schemas
        if use_sample_schema:
            schemas = [
                ScheduledSchema(
                    schema_name="Black Format",
                    schedule=SchemaScheduleSettings(repeats=RepeatSetting.DAILY, hour_of_day=7),
                )
            ]
        else:
            schemas = []
        if not simple:
            while choose_yes_or_no("Add a schema to the schedule?"):
                schemas.append(ScheduledSchema.from_console())

        return Scheduler(
            base_time=int(datetime.fromisoformat("2022-05-23T00:00:00").timestamp())
            + base_modifier,
            excluded_days=excluded_days,
            schemas=schemas,
        )

    @staticmethod
    def from_console(prev_scheduler: Optional[Scheduler] = None) -> Scheduler:
        """Gets a Scheduler using console inputs.

        Args:
            prev_scheduler (Optional[Scheduler], optional): A previously input Scheduler.
                Defaults to None.

        Returns:
            Scheduler: The input Scheduler.
        """

        # Get Base Time
        if prev_scheduler and choose_yes_or_no(
            f"Use previous base time ({prev_scheduler.base_time})?"
        ):
            base_time = prev_scheduler.base_time
        else:
            base_time = int(datetime.fromisoformat("2022-05-23T00:00:00").timestamp())
            info("Using local time to establish a base")
            info("Midnight Monday local is day_of_week 0, hour_of_day 0")
            info(f"Associated timestamp is {base_time}")
            if choose_yes_or_no("Apply a modifier to local time for scheduling?"):
                base_time += input_int("Enter the modifier in seconds")

        # Get Excluded Days
        if prev_scheduler is not None and choose_yes_or_no(
            f"Use previous excluded days: {prev_scheduler.excluded_days!r}"
        ):
            excluded_days = prev_scheduler.excluded_days
        else:
            excluded_days = input_ints(
                "Enter excluded days", min_val=0, max_val=6, min_choices=0, max_choices=7
            )

        # Get Schemas
        if prev_scheduler is not None and bool(prev_scheduler.schemas):
            schemas = choose_options_from_list(
                "Choose schemas to keep",
                [(schema, f"{schema!r}") for schema in prev_scheduler.schemas],
                min_choices=0,
                max_choices=len(prev_scheduler.schemas),
            )
        else:
            schemas = []
        while choose_yes_or_no("Add a schema to the schedule?"):
            schemas.append(ScheduledSchema.from_console())
        return Scheduler(base_time=base_time, excluded_days=excluded_days, schemas=schemas)
