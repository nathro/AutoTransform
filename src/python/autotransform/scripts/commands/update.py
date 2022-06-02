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

import autotransform.config
from autotransform.change.base import FACTORY as change_factory
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import ScriptRunEvent
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

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="Tells the script to output verbose logs.",
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
        event_handler.set_logging_level(LoggingLevel.DEBUG)
    change = args.change
    event_handler.handle(DebugEvent({"message": f"Change: ({args.change_type}) {args.change}"}))
    event_args = {"change": args.change, "change_type": args.change_type}
    if args.change_type == "file":
        with open(change, "r") as change_file:
            change = change_factory.get_instance(json.loads(change_file.read()))
    elif args.change_type == "environment":
        change = os.getenv(change)
        assert isinstance(change, str)
        change = change_factory.get_instance(json.loads(change))
    else:
        change = change_factory.get_instance(json.loads(change))

    if args.change_type != "string":
        event_handler.handle(DebugEvent({"message": f"JSON Change: {json.dumps(change.bundle())}"}))

    if args.run_local:
        event_handler.handle(DebugEvent({"message": "Running locally"}))
        event_args["remote"] = False
        config_runner = autotransform.config.CONFIG.local_runner
        if config_runner is None:
            event_handler.handle(DebugEvent({"message": "No runner defined, using default"}))
            runner: Runner = LocalRunner()
        else:
            runner = config_runner
    else:
        event_handler.handle(DebugEvent({"message": "Running remote"}))
        event_args["remote"] = True
        config_runner = autotransform.config.CONFIG.remote_runner
        assert config_runner is not None
        runner = config_runner

    event_args["runner"] = json.dumps(runner.bundle())
    event_handler.handle(ScriptRunEvent({"script": "update", "args": event_args}))
    runner.update(change)
