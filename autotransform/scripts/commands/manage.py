# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The manage command is used to manage outstanding Changes for AutoTransform."""

import json
from argparse import ArgumentParser, Namespace

from autotransform.event.action import ManageActionEvent
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import ScriptRunEvent
from autotransform.repo.factory import RepoFactory
from autotransform.runner.factory import RunnerFactory
from autotransform.step.action import ActionType
from autotransform.step.factory import StepFactory


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to run a schema.

    Args:
        parser (ArgumentParser): The parser for the schema run.
    """

    parser.add_argument(
        "manager",
        metavar="manager",
        type=str,
        help="A file path to the JSON encoded manager information.",
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
    """The main method for the schedule command, handles the actual execution of scheduling runs.

    Args:
        args (Namespace): The arguments supplied to the schedule command, such as the JSON file.
    """

    # pylint: disable=unspecified-encoding

    event_args = {}
    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.DEBUG)

    # Get Schedule Data
    manager_file = args.manager
    event_args["manager_file"] = manager_file
    with open(manager_file, "r") as file:
        manager_json = file.read()
    event_args["manager"] = manager_json
    event_handler.handle(DebugEvent({"message": f"Manager: ({args.manager})\n{manager_json}"}))
    manager_data = json.loads(manager_json)

    event_handler.handle(ScriptRunEvent({"script": "manage", "args": event_args}))

    # Get needed info/objects for scheduling
    runner = RunnerFactory.get(manager_data["runner"])
    repo = RepoFactory.get(manager_data["repo"])
    steps = [StepFactory.get(step) for step in manager_data["steps"]]
    changes = repo.get_outstanding_changes()

    for change in changes:
        event_handler.handle(DebugEvent({"message": f"Checking steps for {str(change)}"}))
        for step in steps:
            event_handler.handle(DebugEvent({"message": f"Checking step {str(step)}"}))
            action = step.get_action(change)
            if action["type"] != ActionType.NONE:
                event_handler.handle(
                    ManageActionEvent({"action": action, "change": change, "step": step})
                )
                change.take_action(action["type"], runner)
            if action["stop_steps"]:
                event_handler.handle(
                    DebugEvent({"message": f"Steps ended for change {str(change)}"})
                )
                break
