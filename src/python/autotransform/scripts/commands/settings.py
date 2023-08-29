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

from autotransform.config import CONFIG_FILE_NAME, get_cwd_config_dir, get_repo_config_dir
from autotransform.config.config import Config
from autotransform.util.console import info
from autotransform.util.package import get_config_dir


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to update/view settings.

    Args:
        parser (ArgumentParser): The parser for the command.
    """

    setting_type_group = parser.add_mutually_exclusive_group(required=True)
    setting_types = [
        ("--user-config", "user_config", "Update or view the user configuration for AutoTransform"),
        ("--repo-config", "repo_config", "Update or view the repo configuration for AutoTransform"),
        (
            "--cwd-config",
            "cwd_config",
            "Update or view the current working directory configuration for AutoTransform",
        ),
        ("--custom-components", "custom_components", "Update or view custom components"),
        ("--manager", "manager", "Update or view manager settings"),
        ("--scheduler", "scheduler", "Update or view scheduler settings"),
        ("--schema-map", "schema_map", "Update or view schema map settings"),
    ]

    for arg, dest, help_text in setting_types:
        setting_type_group.add_argument(
            arg,
            dest="setting_type",
            action="store_const",
            const=dest,
            help=help_text,
        )

    setting_type_group.add_argument(
        "--schema",
        type=str,
        help="The path to an existing or to be created JSON encoded schema.",
    )

    parser.add_argument(
        "--update",
        dest="update_settings",
        action="store_true",
        help="Used to indicate updates are to be made to the settings.",
    )

    parser.set_defaults(func=settings_command_main, update_settings=False)


def settings_command_main(args: Namespace) -> None:
    """The main method for the settings command, handles the actual execution of updating
    and viewing settings.

    Args:
        args (Namespace): The arguments supplied to the settings command.
    """

    config_paths = {
        "user_config": f"{get_config_dir()}/{CONFIG_FILE_NAME}",
        "repo_config": f"{get_repo_config_dir()}/{CONFIG_FILE_NAME}",
        "cwd_config": f"{get_cwd_config_dir()}/{CONFIG_FILE_NAME}",
    }

    if args.setting_type in config_paths:
        handle_config(
            config_paths[args.setting_type], args.setting_type.capitalize(), args.update_settings
        )
    else:
        # handle other setting types
        pass


def handle_config(path: str, config_type: str, update: bool) -> None:
    """Handles updating a config file.

    Args:
        path (str): The path to the file.
        config_type (str): The type of config being updated (i.e. user).
        update (bool): Whether to update the config.
    """

    config = Config.read(path)
    info(f"Current {config_type} Config\n{config!r}")
    if update:
        config.from_console(config, user_config=config_type == "User")[0].write(path)
