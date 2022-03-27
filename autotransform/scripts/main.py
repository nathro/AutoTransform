# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A script for running autotransform commands"""

from argparse import ArgumentParser

from autotransform.scripts.commands import config, instance, run


def get_arg_parser() -> ArgumentParser:
    """Gets the argument parser for AutoTransform

    Returns:
        ArgumentParser: The arg parser with all args set up
    """
    parser = ArgumentParser(
        description="AutoTransform is a tool for structured, automated code modifcation",
        prog="AutoTransform",
    )
    subparsers = parser.add_subparsers()

    # Add instance command
    instance_parser = subparsers.add_parser(
        "instance",
        help="Run an instance of an AutoTransform process worker, see ProcessWorker",
        aliases=["i"],
    )
    instance.add_args(instance_parser)

    # Add run command
    run_parser = subparsers.add_parser(
        "run",
        help="Execute a full run of AutoTransform",
        aliases=["r"],
    )
    run.add_args(run_parser)

    # Add config command
    config_parser = subparsers.add_parser(
        "config",
        help="Updates/lists values in the config",
        aliases=["c"],
    )
    config.add_args(config_parser)

    return parser


def main():
    """Run autotransform commands"""
    parser = get_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
