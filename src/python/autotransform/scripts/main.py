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

    # Add run command
    run_parser = subparsers.add_parser(
        "run",
        help="Execute a full run of AutoTransform",
    )
    run.add_args(run_parser)

    # Add schedule command
    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Schedule runs of AutoTransform schemas",
    )
    schedule.add_args(schedule_parser)

    # Add manage command
    manage_parser = subparsers.add_parser(
        "manage",
        help="Manage outstanding Changes",
    )
    manage.add_args(manage_parser)

    # Add update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update an outstanding change",
    )
    update.add_args(update_parser)

    # Add settings command
    settings_parser = subparsers.add_parser(
        "settings",
        help="Update/view AutoTransform settings",
    )
    settings.add_args(settings_parser)

    # Add initialize command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize AutoTransform for the user/repo",
    )
    initialize.add_args(init_parser)

    return parser


def main():
    """Parse the arguments of a script run and execute the command invoked."""

    parser = get_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
