# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A script for running autotransform commands"""

from argparse import ArgumentParser

from autotransform.scripts.commands import instance


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
    instance_parser = subparsers.add_parser(
        "instance",
        help="Run an instance of an AutoTransform process worker, see ProcessWorker",
        aliases=["i"],
    )
    instance.add_args(instance_parser)
    return parser


def main():
    """Run autotransform commands"""
    parser = get_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
