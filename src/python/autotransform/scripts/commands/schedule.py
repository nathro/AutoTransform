# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The schedule command is used to schedule runs of AutoTransform."""

import time
from argparse import ArgumentParser, Namespace

from autotransform.config import get_config, get_repo_config_relative_path
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import RunEvent
from autotransform.event.verbose import VerboseEvent
from autotransform.runner.local import LocalRunner
from autotransform.util.scheduler import Scheduler


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to schedule runs.

    Args:
        parser (ArgumentParser): The parser for the schedule command.
    """

    parser.add_argument(
        "--path",
        metavar="path",
        required=False,
        type=str,
        help="A file path to the JSON encoded file, only use if file is in a non-usual place.",
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

    logging_level = parser.add_mutually_exclusive_group()
    logging_level.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="Tells the script to output verbose logs.",
    )
    logging_level.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        required=False,
        help="Tells the script to output debug logs.",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-l",
        "--local",
        dest="run_local",
        action="store_true",
        required=False,
        help="Tells the script to use the local runner.",
    )
    mode_group.add_argument(
        "-r",
        "--remote",
        dest="run_local",
        action="store_false",
        required=False,
        help="Tells the script to use the remote runner. This is the default mode.",
    )

    parser.set_defaults(run_local=False, func=schedule_command_main)


def schedule_command_main(args: Namespace) -> None:
    """The main method for the schedule command, handles the actual execution of scheduling runs.

    Args:
        args (Namespace): The arguments supplied to the schedule command, such as the JSON file.
    """

    # pylint: disable=unspecified-encoding

    start_time = int(args.time) if args.time is not None else int(time.time())
    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.VERBOSE)
    if args.debug:
        event_handler.set_logging_level(LoggingLevel.DEBUG)

    # Get Scheduler
    schedule_file = args.path
    if schedule_file is None:
        schedule_file = f"{get_repo_config_relative_path()}/scheduler.json"
    event_args = {"scheduler_file": schedule_file}
    scheduler = Scheduler.read(schedule_file)
    event_args["scheduler"] = scheduler
    event_handler.handle(RunEvent({"mode": "schedule", "args": event_args}))

    event_handler.get().handle(VerboseEvent({"message": f"Running scheduler: {scheduler!r}"}))
    if args.run_local:
        runner = get_config().local_runner
    else:
        runner = get_config().remote_runner
    scheduler.run(start_time, runner or LocalRunner())
