# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The settings command is used to update AutoTransform settings, such as scheduler.json files,
manager.json files, configs and imported components."""

from argparse import ArgumentParser, Namespace

from autotransform.config.config import Config
from autotransform.config.default import DefaultConfigFetcher
from autotransform.util.console import info
from autotransform.util.package import get_config_dir


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to update/view settings.

    Args:
        parser (ArgumentParser): The parser for the command.
    """

    setting_type_group = parser.add_mutually_exclusive_group(required=True)
    setting_type_group.add_argument(
        "--user-config",
        dest="setting_type",
        action="store_const",
        const="user_config",
        help="Update or view the user configuration for AutoTransform",
    )
    setting_type_group.add_argument(
        "--repo-config",
        dest="setting_type",
        action="store_const",
        const="repo_config",
        help="Update or view the repo configuration for AutoTransform",
    )
    setting_type_group.add_argument(
        "--cwd-config",
        dest="setting_type",
        action="store_const",
        const="cwd_config",
        help="Update or view the current working directory configuration for AutoTransform",
    )

    parser.add_argument("--update", dest="update_settings", action="store_true")

    parser.set_defaults(func=settings_command_main, update_settings=False)


def settings_command_main(args: Namespace) -> None:
    """The main method for the settings command, handles the actual execution of updating
    and viewing settings.

    Args:
        args (Namespace): The arguments supplied to the settings command.
    """

    if args.setting_type == "user_config":
        path = f"{get_config_dir}/{DefaultConfigFetcher.FILE_NAME}"
        config = Config.read(path)
        if not args.update_settings:
            info(f"Current User Config: {config!r}")
        else:
            config.from_console(config, user_config=True)[0].write(path)
    elif args.setting_type == "repo_config":
        path = f"{DefaultConfigFetcher.get_repo_config_dir()}/{DefaultConfigFetcher.FILE_NAME}"
        config = Config.read(path)
        if not args.update_settings:
            info(f"Current Repo Config: {config!r}")
        else:
            config.from_console(config, user_config=False)[0].write(path)
    elif args.setting_type == "cwd_config":
        path = f"{DefaultConfigFetcher.get_cwd_config_dir()}/{DefaultConfigFetcher.FILE_NAME}"
        config = Config.read(path)
        if not args.update_settings:
            info(f"Current CWD Config: {config!r}")
        else:
            config.from_console(config, user_config=False)[0].write(path)
