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

SETTING_TYPES = {
    "user_config": (get_config_dir, "User"),
    "repo_config": (get_repo_config_dir, "Repo"),
    "cwd_config": (get_cwd_config_dir, "CWD"),
}


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to update/view settings.

    Args:
        parser (ArgumentParser): The parser for the command.
    """

    setting_type_group = parser.add_mutually_exclusive_group(required=True)
    for setting_type, (_, desc) in SETTING_TYPES.items():
        setting_type_group.add_argument(
            f"--{setting_type}",
            dest="setting_type",
            action="store_const",
            const=setting_type,
            help=f"Update or view the {desc} configuration for AutoTransform",
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

    if args.setting_type in SETTING_TYPES:
        func, desc = SETTING_TYPES[args.setting_type]
        path = f"{func()}/{CONFIG_FILE_NAME}"
        handle_config(path, desc, args.update_settings)


def handle_config(path: str, config_type: str, update: bool) -> None:
    """Handles updating a config file.

    Args:
        path (str): The path to the file.
        config_type (str): The type of config being updated (i.e. user).
        update (bool): Whether to update the config.
    """

    config = Config.read(path)
    info(f"Current {config_type} Config\n{config!r}")
    if not update:
        return
    config.from_console(config, user_config=config_type == "User")[0].write(path)
