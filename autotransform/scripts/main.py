# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The AutoTransform script, responsible for handling AutoTransform CLI invocations.
Different CLI commands are handled as subparsers. Includes the following commands
    Run: Executes a full run of AutoTransform.
    Config: Lists or updates config values."""

from argparse import ArgumentParser

from autotransform.scripts.commands import config, manage, run, schedule, update


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

    # Add run command
    run_parser = subparsers.add_parser(
        "run",
        help="Execute a full run of AutoTransform",
        aliases=["r"],
    )
    run.add_args(run_parser)

    # Add schedule command
    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Schedule runs of AutoTransform schemas",
        aliases=["s"],
    )
    schedule.add_args(schedule_parser)

    # Add manage command
    manage_parser = subparsers.add_parser(
        "manage",
        help="Manage outstanding Changes",
        aliases=["m"],
    )
    manage.add_args(manage_parser)

    # Add update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update an outstanding change",
        aliases=["u"],
    )
    update.add_args(update_parser)

    # Add config command
    config_parser = subparsers.add_parser(
        "config",
        help="Updates/lists values in the config",
        aliases=["c"],
    )
    config.add_args(config_parser)

    return parser


def main():
    """Parse the arguments of a script run and execute the command invoked."""

    parser = get_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
