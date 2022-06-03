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
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from autotransform.config.default import DefaultConfigFetcher
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.schedulerun import ScheduleRunEvent
from autotransform.filter.base import FACTORY as filter_factory
from autotransform.filter.key_hash_shard import KeyHashShardFilter
from autotransform.filter.shard import ShardFilter
from autotransform.runner.base import FACTORY as runner_factory
from autotransform.runner.base import Runner
from autotransform.runner.github import GithubRunner
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.console import (
    choose_option,
    choose_yes_or_no,
    error,
    get_str,
    info,
    input_int,
    input_string,
)


class SchemaType(str, Enum):
    """Possible types of Schemas to use."""

    BUILDER = "builder"
    FILE = "file"


class RepeatSetting(str, Enum):
    """Possible repitition schedules."""

    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass(kw_only=True)
class SchemaScheduleSettings:
    """A schedule for a Schema.

    Attributes:
        repeats (RepeatSetting): How often the Schema will be run, daily or weekly.
        hour_of_day (int): The hour of the day to run the Schema, 0-23.
        day_of_week (Optional[int], optional): The day of the week to run a weekly Schema.
            Defaults to None.
        sharding (Optional[ShardingSettings], optional): The settings used to determine how
            to apply sharding to Schema runs. Defaults to None.
    """

    repeats: RepeatSetting
    hour_of_day: int
    day_of_week: Optional[int] = None
    sharding: Optional[ShardFilter] = None

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

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        bundle: Dict[str, Any] = {
            "repeats": self.repeats.value,
            "hour_of_day": self.hour_of_day,
        }

        if self.day_of_week is not None:
            bundle["day_of_week"] = self.day_of_week

        if self.sharding is not None:
            shard_bundle = self.sharding.bundle()
            del shard_bundle["valid_shard"]
            bundle["sharding"] = shard_bundle

        return bundle

    @staticmethod
    def from_data(data: Dict[str, Any], elapsed_days: int) -> SchemaScheduleSettings:
        """Produces an instance of the SchemaScheduleSettings from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.
            elapsed_days (int): The number of days elapsed since the start of the schedule.

        Returns:
            SchemaScheduleSettings: An instance of the SchemaScheduleSettings.
        """

        repeats = RepeatSetting(data["repeats"])
        hour_of_day = data["hour_of_day"]
        assert isinstance(hour_of_day, int)
        assert hour_of_day in range(24)
        day_of_week = data.get("day_of_week", None)
        if day_of_week is not None:
            assert isinstance(day_of_week, int)
            assert day_of_week in range(7)

        sharding = data.get("sharding", None)
        if sharding is not None:
            assert isinstance(sharding, Dict)
            num_shards = sharding["num_shards"]
            assert isinstance(num_shards, int)
            if repeats == RepeatSetting.DAILY:
                valid_shard = elapsed_days % num_shards
            else:
                valid_shard = (elapsed_days // 7) % num_shards
            sharding["valid_shard"] = valid_shard
            filter_instance = filter_factory.get_instance(sharding)
            assert isinstance(filter_instance, ShardFilter)
            shard_filter = filter_instance
        else:
            shard_filter = None

        return SchemaScheduleSettings(
            repeats=repeats, hour_of_day=hour_of_day, day_of_week=day_of_week, sharding=shard_filter
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
            "What hour of the day should the schema run?", min_val=0, max_val=23
        )

        # Get day_of_week
        if repeats == RepeatSetting.WEEKLY:
            day_of_week = input_int(
                "What day of the week should the schema run?", min_val=0, max_val=6
            )
        else:
            day_of_week = None

        # Get sharding
        if not simple and choose_yes_or_no("Do you want to use sharding for this schema?"):
            default_filter = KeyHashShardFilter(num_shards=10, valid_shard=0).bundle()
            del default_filter["valid_shard"]
            shard_filter: Optional[ShardFilter] = None
            while shard_filter is None:
                shard_filter_json = input_string(
                    "Enter the JSON encoded shard filter:",
                    "shard filter",
                    default=json.dumps(default_filter),
                )
                try:
                    shard_filter_bundle = json.loads(shard_filter_json)
                    if "valid_shard" not in shard_filter_bundle:
                        shard_filter_bundle["valid_shard"] = 0
                    filter_instance = filter_factory.get_instance(shard_filter_bundle)
                    if isinstance(filter_instance, ShardFilter):
                        shard_filter = filter_instance
                    else:
                        error("Invalid filter provided, please provide a shard filter.")
                except Exception:  # pylint: disable=broad-except
                    error("Failed to get shard filter from input, please try again.")
        else:
            shard_filter = None

        return SchemaScheduleSettings(
            repeats=repeats, hour_of_day=hour_of_day, day_of_week=day_of_week, sharding=shard_filter
        )


@dataclass(kw_only=True)
class ScheduledSchema:
    """A Schema that is scheduled for automatic runs.

    Attributes:
        type (SchemaType): The type of Schema that is specified, file or builder.
        schema (str): The Schema that is being scheduled.
        schedule (SchemaScheduleSettings): The settings used to determine when to run the Schema.
    """

    type: SchemaType
    schema: str
    schedule: SchemaScheduleSettings

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        return {"type": self.type.value, "schema": self.schema, "schedule": self.schedule.bundle()}

    @staticmethod
    def from_data(data: Dict[str, Any], elapsed_days: int) -> ScheduledSchema:
        """Produces an instance of the ScheduledSchema from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.
            elapsed_days (int): The number of days elapsed since the start of the schedule.

        Returns:
            ScheduledSchema: An instance of the ScheduledSchema.
        """

        schema_type = SchemaType(data["type"])
        schema = data["schema"]
        assert isinstance(schema, str)
        schedule = SchemaScheduleSettings.from_data(data["schedule"], elapsed_days)
        return ScheduledSchema(type=schema_type, schema=schema, schedule=schedule)

    @staticmethod
    def from_console() -> ScheduledSchema:
        """Gets a ScheduledSchema from console inputs.

        Returns:
            ScheduledSchema: The input ScheduledSchema.
        """

        schema = get_str("Enter the schema to schedule: ")

        schema_type = choose_option(
            "What is the type of the schema?",
            [(SchemaType.FILE, ["file", "f"]), (SchemaType.BUILDER, ["builder", "b"])],
        )

        return ScheduledSchema(
            schema=schema, type=schema_type, schedule=SchemaScheduleSettings.from_console()
        )


@dataclass(kw_only=True)
class Scheduler:
    """The information and functionality required to schedule Schemas.

    Attributes:
        base_time (int): The base time to use when determining hour_of_day, day_of_week,
            and valid shards. Considered day 0, hour 0.
        runner (Runner): The runner to use when triggering runs of a Schema.
        excluded_days (List[int]): A list of days of the week to skip running Schemas.
        schemas (List[ScheduledSchema]): A list of Schemas to schedule.
    """

    base_time: int
    excluded_days: List[int]
    runner: Runner
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
                DebugEvent(
                    {
                        "message": f"Day {day_of_week} is excluded, skipping run",
                    }
                )
            )
            return

        for scheduled_schema in self.schemas:
            # Get the Schema
            if scheduled_schema.type == SchemaType.BUILDER:
                try:
                    schema = json.loads(scheduled_schema.schema)
                except json.JSONDecodeError:
                    schema = {"name": scheduled_schema.schema}
                if isinstance(schema, str):
                    schema = {"name": schema}
                schema = schema_builder_factory.get_instance(schema).build()
            else:
                with open(scheduled_schema.schema, "r", encoding="UTF-8") as schema_file:
                    schema = AutoTransformSchema.from_json(schema_file.read())

            # Check if should run
            if not scheduled_schema.schedule.should_run(hour_of_day, day_of_week):
                EventHandler.get().handle(
                    DebugEvent(
                        {"message": f"Skipping run of schema: {schema.get_config().schema_name}"}
                    )
                )
                continue
            shard_filter = scheduled_schema.schedule.sharding
            if shard_filter is not None:
                EventHandler.get().handle(
                    DebugEvent(
                        {
                            "message": f"Sharding: valid = {shard_filter.valid_shard}, "
                            + f"num = {shard_filter.num_shards}",
                        }
                    )
                )
                schema.add_filter(shard_filter)
            EventHandler.get().handle(
                ScheduleRunEvent({"schema_name": schema.get_config().schema_name})
            )
            self.runner.run(schema)

    def write(self, file_path: str) -> None:
        """Writes the Scheduler to a file as JSON.

        Args:
            file_path (str): The file to write to.
        """

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+", encoding="UTF-8") as scheduler_file:
            scheduler_file.write(json.dumps(self.bundle(), indent=4))
            scheduler_file.flush()

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        return {
            "base_time": self.base_time,
            "excluded_days": self.excluded_days,
            "runner": self.runner.bundle(),
            "schemas": [schema.bundle() for schema in self.schemas],
        }

    @staticmethod
    def read(file_path: str, start_time: int) -> Scheduler:
        """Reads a Scheduler from a JSON encoded file.

        Args:
            file_path (str): The path where the JSON for the Schedule is located.
            start_time (int): The start time to use for setting up sharding/running.

        Returns:
            Scheduler: The Scheduler from the file.
        """

        with open(file_path, "r", encoding="UTF-8") as scheduler_file:
            scheduler_json = scheduler_file.read()
        EventHandler.get().handle(
            DebugEvent({"message": f"Scheduler: ({file_path})\n{scheduler_json}"})
        )
        return Scheduler.from_json(scheduler_json, start_time)

    @staticmethod
    def from_json(scheduler_json: str, start_time: int) -> Scheduler:
        """Builds a Scheduler from JSON encoded values.

        Args:
            scheduler_json (str): The JSON encoded Scheduler.
            start_time (int): The start time to use for setting up sharding/running.

        Returns:
            Scheduler: The Scheduler from the JSON.
        """

        return Scheduler.from_data(json.loads(scheduler_json), start_time)

    @staticmethod
    def from_data(data: Dict[str, Any], start_time: int) -> Scheduler:
        """Produces an instance of the Scheduler from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.
            start_time (int): The time that the schedule is starting to run on.

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
        runner = runner_factory.get_instance(data["runner"])
        elapsed_days = (start_time - base_time) // 60 // 60 // 24
        schemas = [
            ScheduledSchema.from_data(schema, elapsed_days) for schema in data.get("schemas", [])
        ]
        return Scheduler(
            base_time=base_time, excluded_days=excluded_days, runner=runner, schemas=schemas
        )

    @staticmethod
    def from_console(
        runner: Optional[Runner] = None, use_sample_schema: bool = False, simple: bool = False
    ) -> Scheduler:
        """Gets a Scheduler using console input.

        Args:
            runner (Optional[Runner], optional): The Runner for the Scheduler. Defaults to None.
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
            base_modifier = input_int("Enter the modifier in secords:")
        else:
            base_modifier = 0

        # Gets excluded days
        if not simple and choose_yes_or_no("Should AutoTransform schedule runs on weekends?"):
            excluded_days = []
        else:
            excluded_days = [5, 6]

        # Gets the Runner
        input_runner = runner_factory.from_console(
            "scheduler runner",
            previous_value=runner,
            default_value=GithubRunner(
                run_workflow="autotransform.run.yml",
                update_workflow="autotransform.update.yml",
            ),
            simple=simple,
            allow_none=False,
        )
        assert input_runner is not None

        # Gets Schemas
        if use_sample_schema:
            relative_path = DefaultConfigFetcher.get_repo_config_relative_path()
            schemas = [
                ScheduledSchema(
                    type=SchemaType.FILE,
                    schema=f"{relative_path}/schemas/black_format.json",
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
            runner=input_runner,
            schemas=schemas,
        )
