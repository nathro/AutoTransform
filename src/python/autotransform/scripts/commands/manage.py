# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The manage command is used to manage outstanding Changes for AutoTransform."""

from argparse import ArgumentParser, Namespace

from autotransform.config.default import DefaultConfigFetcher
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import ScriptRunEvent
from autotransform.util.manager import Manager


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to manage outstanding changes.

    Args:
        parser (ArgumentParser): The parser for the managing outstanding changes.
    """

    parser.add_argument(
        "--path",
        metavar="path",
        required=False,
        type=str,
        help="A file path to the JSON encoded file, only use if file is in a non-usual place.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="Tells the script to output verbose logs.",
    )
    parser.set_defaults(func=manage_command_main)


def manage_command_main(args: Namespace) -> None:
    """The main method for the manage command, handles the actual management of changes.

    Args:
        args (Namespace): The arguments supplied to the manage command, such as the JSON file.
    """

    # pylint: disable=unspecified-encoding

    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.DEBUG)

    manager_file = args.path
    if manager_file is None:
        manager_file = f"{DefaultConfigFetcher.get_repo_config_relative_path()}/manager.json"
    event_args = {"manager_file": manager_file}
    manager = Manager.read(manager_file)
    event_args["manager"] = manager
    event_handler.handle(ScriptRunEvent({"script": "manage", "args": event_args}))

    event_handler.handle(DebugEvent({"message": f"Running manager: {manager}"}))
    manager.run()
