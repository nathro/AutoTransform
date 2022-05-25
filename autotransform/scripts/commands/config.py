# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The config command is used to update the config files for AutoTransform."""

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from getpass import getpass
from typing import List, Optional, Tuple, TypedDict, TypeVar

from autotransform.config.default import DefaultConfigFetcher

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


def choose_option(
    prompt: str, options: List[Tuple[str, T]], allow_none: bool = True
) -> Optional[T]:
    """Allows the user to select one of a set of options and returns the corresponding selection.

    Args:
        prompt (str): The prompt to ask the user.
        options (List[Tuple[str, T]]): The list of potential options.
        allow_none (bool, optional): Whether to allow None as an option for the user. Defaults
            to True.

    Returns:
        Optional[T]: The selected option.
    """

    max_choice = len(options) + 1 if allow_none else len(options)
    while True:
        print(prompt)
        for i, option in enumerate(options):
            print(f"\t{i + 1}) {option[0]}")
        if allow_none:
            print(f"\t{len(options) + 1}) Done.")
        inp = input("Enter choice: ")
        if not inp.isdigit():
            print(f"Choice must be a number: {inp}")
            continue
        choice = int(inp) - 1
        if choice in range(len(options)):
            return options[choice][1]
        if choice == len(options) and allow_none:
            return None
        print(f"Invalid choice {choice}: Please select a number between 1 and {max_choice}")


def get_all_config_paths() -> List[Tuple[str, str]]:
    """Gets all of the config paths as options for the user to choose.

    Returns:
        List[Tuple[str, str]]: A list of config descriptions and paths.
    """

    options = [
        ("The user config file.", DefaultConfigFetcher.get_user_config_dir()),
    ]
    repo_path = DefaultConfigFetcher.get_repo_config_dir()
    if repo_path is not None:
        options.append(("The Repo's config file.", repo_path))
    options.append(
        (
            "The current working directory config file.",
            DefaultConfigFetcher.get_cwd_config_dir(),
        ),
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
    config_paths = get_all_config_paths()
    config_settings = [
        (f"{setting['name']}: {setting['description']}", setting)
        for setting in get_all_config_settings()
    ]
    config_setting_actions = [("Get existing value", False), ("Update value", True)]

    while True:
        path = choose_option("Select config to update or view", config_paths)
        if path is None:
            break
        path = f"{path}/{DefaultConfigFetcher.CONFIG_NAME}"
        parser = ConfigParser()
        print(f"Reading config at path: {path}\n\n")
        parser.read(path)

        has_updates = False
        while True:
            config_setting = choose_option("Choose a config setting", config_settings)
            print("\n")
            if config_setting is None:
                break
            is_update = choose_option(
                f"What action would you like to take on setting {config_setting['name']}",
                config_setting_actions,
                allow_none=False,
            )

            if is_update:
                has_updates = True
                if config_setting["secret"]:
                    new_value = getpass(f"Input new {config_setting['name']}: ")
                else:
                    new_value = input(f"Input new {config_setting['name']}: ")
                if config_setting["section"] not in parser:
                    parser[config_setting["section"]] = {}
                parser[config_setting["section"]][config_setting["setting"]] = new_value
                print("\n")
                continue

            if config_setting["section"] not in parser:
                print(f"No value for setting {config_setting['name']}\n\n")
                continue

            section = parser[config_setting["section"]]
            if config_setting["setting"] not in section:
                print(f"No existing value for setting {config_setting['name']}\n\n")
                continue
            print(f"{config_setting['name']}: {section[config_setting['setting']]}\n\n")

        if has_updates:
            with open(path, "w", encoding="utf-8") as config_file:
                parser.write(config_file)
