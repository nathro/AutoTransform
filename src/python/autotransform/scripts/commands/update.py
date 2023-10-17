# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The update command is used to update an outstanding Change."""

import json
import os
from argparse import ArgumentParser, Namespace

from autotransform.change.base import FACTORY as change_factory
from autotransform.config import get_config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import RunUpdateEvent, RunUpdateFailedEvent
from autotransform.event.runner import RunnerFailedEvent
from autotransform.event.verbose import VerboseEvent
from autotransform.runner.base import Runner
from autotransform.runner.local import LocalRunner


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to update a change.

    Args:
        parser (ArgumentParser): The parser for the change update.
    """

    parser.add_argument(
        "change",
        metavar="change",
        type=str,
        help="The change that will be updated. Could be a file path, string, "
        + "or environment variable name.",
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

    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        "-f",
        "--file",
        dest="change_type",
        action="store_const",
        const="file",
        required=False,
        help="Tells the script to interpret the change as a file path.",
    )
    type_group.add_argument(
        "-s",
        "--string",
        dest="change_type",
        action="store_const",
        const="string",
        required=False,
        help="Tells the script to interpret the change as a JSON encoded string",
    )
    type_group.add_argument(
        "-e",
        "--environment",
        dest="change_type",
        action="store_const",
        const="environment",
        required=False,
        help="Tells the script to interpret the change as an environment variable storing the JSON "
        + "encoded change.",
    )

    # Update Mode
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-l",
        "--local",
        dest="run_local",
        action="store_true",
        required=False,
        help="Tells the script to run locally, local is the default mode.",
    )
    mode_group.add_argument(
        "-r",
        "--remote",
        dest="run_local",
        action="store_false",
        required=False,
        help="Tells the script to run remote using the remote component from the config.",
    )

    parser.set_defaults(change_type="file", run_local=True, func=run_command_main)


def run_command_main(args: Namespace) -> None:
    """The main method for the update command, handles the actual execution of an update.

    Args:
        args (Namespace): The arguments supplied to the update command, such as the change.
    """

    # pylint: disable=unspecified-encoding

    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.VERBOSE)
    if args.debug:
        event_handler.set_logging_level(LoggingLevel.DEBUG)
    change = args.change
    event_handler.handle(DebugEvent({"message": f"Change: ({args.change_type}) {args.change}"}))
    if args.change_type == "file":
        with open(change, "r") as change_file:
            change = change_factory.get_instance(json.loads(change_file.read()))
    elif args.change_type == "environment":
        change = os.getenv(change)
        assert isinstance(change, str)
        change = change_factory.get_instance(json.loads(change))
    else:
        change = change_factory.get_instance(json.loads(change))

    event_handler.handle(RunUpdateEvent({"change": change}))
    try:
        if args.run_local:
            event_handler.handle(VerboseEvent({"message": "Running locally"}))
            config_runner = get_config().local_runner
            if config_runner is None:
                event_handler.handle(DebugEvent({"message": "No runner defined, using default"}))
                runner: Runner = LocalRunner()
            else:
                runner = config_runner
        else:
            event_handler.handle(VerboseEvent({"message": "Running remote"}))
            config_runner = get_config().remote_runner
            assert config_runner is not None
            runner = config_runner

        event_handler.handle(RunUpdateEvent({"change": change}))
        try:
            runner.update(change)
        except Exception as e:  # pylint: disable=broad-except
            event_handler.handle(
                RunnerFailedEvent({"message": f"Failed run: {e}", "runner": runner})
            )
            raise e
    except Exception as e:  # pylint: disable=broad-except
        event_handler.handle(RunUpdateFailedEvent({"change": change, "error": e}))
        raise e
