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
        ("run", run, "Execute a full run of AutoTransform"),
        ("schedule", schedule, "Schedule runs of AutoTransform schemas"),
        ("manage", manage, "Manage outstanding Changes"),
        ("update", update, "Update an outstanding change"),
        ("settings", settings, "Update/view AutoTransform settings"),
        ("init", initialize, "Initialize AutoTransform for the user/repo"),
    ]

    for command, module, help_text in commands:
        command_parser = subparsers.add_parser(command, help=help_text)
        module.add_args(command_parser)

    return parser


def main():
    """Parse the arguments of a script run and execute the command invoked."""

    parser = get_arg_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
