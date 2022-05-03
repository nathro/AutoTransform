# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The schedule command is used to schedule runs of AutoTransform."""

import json
import time
from argparse import ArgumentParser, Namespace

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import ScriptRunEvent
from autotransform.event.schedulerun import ScheduleRunEvent
from autotransform.filter.factory import FilterFactory
from autotransform.filter.shard import ShardFilter
from autotransform.runner.factory import RunnerFactory
from autotransform.schema.factory import SchemaBuilderFactory
from autotransform.schema.schema import AutoTransformSchema


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to run a schema.

    Args:
        parser (ArgumentParser): The parser for the schema run.
    """

    parser.add_argument(
        "schedule",
        metavar="schedule",
        type=str,
        help="A file path to the JSON encoded schedule of schema runs to execute.",
    )
    parser.add_argument(
        "-t",
        "--time",
        metavar="time",
        type=int,
        required=False,
        help="The timestamp to use in place of the current time, used in cases where delays in "
        + "scheduling are likely.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="Tells the script to output verbose logs.",
    )
    parser.set_defaults(func=schedule_command_main)


def schedule_command_main(args: Namespace) -> None:
    """The main method for the schedule command, handles the actual execution of scheduling runs.

    Args:
        args (Namespace): The arguments supplied to the schedule command, such as the JSON file.
    """

    # pylint: disable=unspecified-encoding

    if args.time is not None:
        start_time = int(args.time)
    else:
        start_time = int(time.time())
    event_args = {}
    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.DEBUG)

    # Get Schedule Data
    schedule_file = args.schedule
    event_args["schedule_file"] = schedule_file
    with open(schedule_file, "r") as file:
        schedule_json = file.read()
    event_args["schedule"] = schedule_json
    event_handler.handle(DebugEvent({"message": f"Schedule: ({args.schedule})\n{schedule_json}"}))
    schedule_data = json.loads(schedule_json)

    event_handler.handle(ScriptRunEvent({"script": "schedule", "args": event_args}))

    # Get needed info/objects for scheduling
    runner = RunnerFactory.get(schedule_data["runner"])
    excluded_days = [int(day) for day in schedule_data["excluded_days"]]
    elapsed_time = start_time - int(schedule_data["base_time"])

    elapsed_hours = int(elapsed_time / 60 / 60)
    hour_of_day = elapsed_hours % 24

    elapsed_days = int(elapsed_hours / 24)
    day_of_week = elapsed_days % 7

    elapsed_weeks = int(elapsed_days / 7)

    event_handler.handle(
        DebugEvent({"message": f"Running for hour {hour_of_day}, day {day_of_week}"})
    )
    event_handler.handle(
        DebugEvent({"message": f"Elaphsed days {elapsed_days}, weeks {elapsed_weeks}"})
    )

    if day_of_week in excluded_days:
        event_handler.handle(
            DebugEvent(
                {
                    "message": f"Day {day_of_week} is excluded, skipping run",
                }
            )
        )
        return

    for schema_data in schedule_data["schemas"]:
        # Get the Schema
        schema_type = schema_data["type"]
        if schema_type == "builder":
            schema = SchemaBuilderFactory.get(schema_data["schema"]).build()
        elif schema_type == "file":
            with open(schema_data["schema"], "r") as schema_file:
                schema = AutoTransformSchema.from_json(schema_file.read())

        # Check if should run
        schedule_info = schema_data["schedule"]
        repeats = schedule_info["repeats"]
        if schedule_info["hour_of_day"] != hour_of_day:
            event_handler.handle(
                DebugEvent(
                    {
                        "message": f"Skipping schema {schema.get_config().get_name()}:"
                        + f" only runs on hour {schedule_info['hour_of_day']}",
                    }
                )
            )
            continue
        if repeats == "weekly" and schedule_info["day_of_week"] != day_of_week:
            event_handler.handle(
                DebugEvent(
                    {
                        "message": f"Skipping schema {schema.get_config().get_name()}:"
                        + f" only runs on day {schedule_info['day_of_week']}",
                    }
                )
            )
            continue

        # Handle sharding
        shard_info = schedule_info.get("sharding")
        if shard_info is not None:
            num_shards = shard_info["num_shards"]
            if repeats == "daily":
                valid_shard = elapsed_days % num_shards
            else:
                valid_shard = elapsed_weeks % num_shards
            event_handler.handle(
                DebugEvent(
                    {
                        "message": f"Sharding: valid = {valid_shard}, num = {num_shards}",
                    }
                )
            )
            filter_bundle = shard_info["shard_filter"]
            filter_bundle["params"]["num_shards"] = num_shards
            filter_bundle["params"]["valid_shard"] = valid_shard
            shard_filter = FilterFactory.get(filter_bundle)
            assert isinstance(shard_filter, ShardFilter)
            schema.add_filter(shard_filter)

        event_handler.handle(ScheduleRunEvent({"schema_name": schema.get_config().get_name()}))
        runner.run(schema)
