# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The config command is used to update the config files for AutoTransform."""

import os
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from typing import List, Optional, Tuple, TypedDict, TypeVar

from autotransform.config.default import DefaultConfigFetcher
from autotransform.util.console import choose_option_from_list, get_str, info
from autotransform.util.package import get_config_dir

T = TypeVar("T")


class ConfigSetting(TypedDict):
    """The information required to display and update a configuration setting from a config.ini
    file."""

    description: str
    name: str
    secret: bool
    section: str
    setting: str


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to update/view configs.

    Args:
        parser (ArgumentParser): The parser for the schema run.
    """

    parser.set_defaults(func=config_command_main)


def get_config_options() -> List[Tuple[Optional[str], str]]:
    """Gets all of the config paths as options for the user to choose.

    Returns:
        List[Tuple[str, str]]: A list of config paths and descriptions.
    """

    options: List[Tuple[Optional[str], str]] = [
        (get_config_dir(), "The user config file."),
    ]
    repo_path = DefaultConfigFetcher.get_repo_config_dir()
    if repo_path is not None:
        options.append((repo_path, "The Repo's config file."))
    options.extend(
        [
            (
                DefaultConfigFetcher.get_cwd_config_dir(),
                "The current working directory config file.",
            ),
            (None, "Quit."),
        ]
    )
    return options


def get_all_config_settings() -> List[ConfigSetting]:
    """Gets a list of config setting options that provide the user with potential

    Returns:
        List[ConfigSetting]: A list of all possible Config settings.
    """
    return [
        ConfigSetting(
            {
                "description": "The token used to authenticate with Github.",
                "name": "Github Token",
                "secret": True,
                "section": "CREDENTIALS",
                "setting": "github_token",
            }
        ),
        ConfigSetting(
            {
                "description": "The base URL for api requests to a Github Entrerprise instance.",
                "name": "Github URL",
                "secret": False,
                "section": "CREDENTIALS",
                "setting": "github_base_url",
            }
        ),
        ConfigSetting(
            {
                "description": "A list of modules mapping names to custom components.",
                "name": "Custom Components",
                "secret": False,
                "section": "IMPORTS",
                "setting": "components",
            }
        ),
        ConfigSetting(
            {
                "description": "A JSON encoded Runner object used when performing a local run.",
                "name": "Local Runner",
                "secret": False,
                "section": "RUNNER",
                "setting": "local",
            }
        ),
        ConfigSetting(
            {
                "description": "A JSON encoded Runner object used when performing a remote run.",
                "name": "Remote Runner",
                "secret": False,
                "section": "RUNNER",
                "setting": "remote",
            }
        ),
    ]


def config_command_main(_args: Namespace) -> None:
    """The main method for the config command, handles the actual execution of updating and viewing
    configs.

    Args:
        _args (Namespace): The arguments supplied to the config command.
    """
    config_options: List[Tuple[Optional[str], str]] = get_config_options()
    config_setting_options: List[Tuple[Optional[ConfigSetting], str]] = [
        (setting, f"{setting['name']}: {setting['description']}")
        for setting in get_all_config_settings()
    ]
    config_setting_options.append((None, "Done."))
    config_setting_action_options = [(False, "Get existing value"), (True, "Update value")]

    while True:
        path = choose_option_from_list("Select config to update or view", config_options)
        if path is None:
            break
        path = f"{path}/{DefaultConfigFetcher.CONFIG_NAME}"
        parser = ConfigParser()
        info(f"Reading config at path: {path}\n\n")
        parser.read(path)

        has_updates = False
        while True:
            config_setting = choose_option_from_list(
                "Choose a config setting", config_setting_options
            )
            print("\n")
            if config_setting is None:
                break
            is_update = choose_option_from_list(
                f"What action would you like to take on setting {config_setting['name']}",
                config_setting_action_options,
            )

            if is_update:
                has_updates = True
                new_value = get_str(
                    f"Input new {config_setting['name']}: ", secret=config_setting["secret"]
                )
                if config_setting["section"] not in parser:
                    parser[config_setting["section"]] = {}
                parser[config_setting["section"]][config_setting["setting"]] = new_value
                print("\n")
                continue

            if config_setting["section"] not in parser:
                info(f"No value for setting {config_setting['name']}\n\n")
                continue

            section = parser[config_setting["section"]]
            if config_setting["setting"] not in section:
                info(f"No existing value for setting {config_setting['name']}\n\n")
                continue
            info(f"{config_setting['name']}: {section[config_setting['setting']]}\n\n")

        if has_updates:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w+", encoding="UTF-8") as config_file:
                parser.write(config_file)
