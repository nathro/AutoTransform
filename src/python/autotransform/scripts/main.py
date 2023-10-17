# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The AutoTransform script, responsible for handling AutoTransform CLI invocations.
Different CLI commands are handled as subparsers."""

from argparse import ArgumentParser

from autotransform.event.handler import EventHandler
from autotransform.event.run import RunCommandFailedEvent
from autotransform.scripts.commands import initialize, manage, run, schedule, settings, update


def get_arg_parser() -> ArgumentParser:
    """Gets the argument parser for AutoTransform. Sets up each command as a sub parser.

    Returns:
        ArgumentParser: The arg parser with all args set up.
    """

    parser = ArgumentParser(
        description="AutoTransform is a tool for structured, automated code modifcation",
        prog="AutoTransform",
    )
    subparsers = parser.add_subparsers()

    commands = [
        ("run", "Execute a full run of AutoTransform", run),
        ("schedule", "Schedule runs of AutoTransform schemas", schedule),
        ("manage", "Manage outstanding Changes", manage),
        ("update", "Update an outstanding change", update),
        ("settings", "Update/view AutoTransform settings", settings),
        ("init", "Initialize AutoTransform for the user/repo", initialize),
    ]

    for command, help_text, module in commands:
        command_parser = subparsers.add_parser(command, help=help_text)
        module.add_args(command_parser)

    return parser


def main():
    """Parse the arguments of a script run and execute the command invoked."""

    parser = get_arg_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:  # pylint: disable=broad-except
            EventHandler.get().handle(RunCommandFailedEvent({"error": e}))
            raise e
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
