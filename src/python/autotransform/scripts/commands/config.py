# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The config command is used to update the config files for AutoTransform."""

import json
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from autotransform.config.config import Config
from autotransform.config.default import DefaultConfigFetcher
from autotransform.runner.base import FACTORY as runner_factory
from autotransform.util.console import (
    choose_option_from_list,
    choose_yes_or_no,
    error,
    get_str,
    info,
)
from autotransform.util.package import get_config_dir


@dataclass(frozen=True, kw_only=True)
class ConfigSetting:
    """The information required to display and update a configuration setting from a config.json
    file.

    Attributes:
        description (str): Describes the setting being updated.
        name (str): A simple name for the setting being updated.
        secret (bool): Whether to hide the input of this value.
        field (str): The field on the config object this setting represents.
    """

    description: str
    name: str
    secret: bool
    field: str


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
            description="The token used to authenticate with Github.",
            name="Github Token",
            secret=True,
            field="github_token",
        ),
        ConfigSetting(
            description="The base URL for api requests to a Github Entrerprise instance.",
            name="Github URL",
            secret=False,
            field="github_base_url",
        ),
        ConfigSetting(
            description="The directory where custom components are stored.",
            name="Custom Component Directory",
            secret=False,
            field="component_directory",
        ),
        ConfigSetting(
            description="A JSON encoded Runner object used when performing a local run.",
            name="Local Runner",
            secret=False,
            field="local_runner",
        ),
        ConfigSetting(
            description="A JSON encoded Runner object used when performing a remote run.",
            name="Remote Runner",
            secret=False,
            field="remote_runner",
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
        (setting, f"{setting.name}: {setting.description}") for setting in get_all_config_settings()
    ]
    config_setting_options.append((None, "Done."))

    # pylint: disable=too-many-nested-blocks
    while True:
        path = choose_option_from_list("Select config to update or view", config_options)
        if path is None:
            break
        path = f"{path}/{DefaultConfigFetcher.FILE_NAME}"

        info(f"Reading config at path: {path}\n\n")
        config = Config.read(path)

        has_updates = False
        while True:
            config_setting = choose_option_from_list(
                "Choose a config setting", config_setting_options
            )
            print("\n")
            if config_setting is None:
                break
            is_update = choose_yes_or_no(
                f"Would you like to update the value of {config_setting.name}",
            )

            if is_update:
                has_updates = True
                valid = False
                while not valid:
                    new_value: Any = get_str(
                        f"Input new {config_setting.name}: ", secret=config_setting.secret
                    )
                    if config_setting.field in ["local_runner", "remote_runner"]:
                        try:
                            new_value = runner_factory.get_instance(json.loads(new_value))
                            valid = True
                        except Exception as err:  # pylint: disable=broad-except
                            error(f"Invalid runner object: {err}")
                    else:
                        valid = True
                if new_value == "":
                    new_value = None
                setattr(config, config_setting.field, new_value)
                print("\n")
                continue

            config_value = getattr(config, config_setting.field)
            if config_value is None:
                info(f"No value for setting {config_setting.name}\n\n")
                continue

            info(f"{config_setting.name}: {config_value}\n\n")

        if has_updates:
            config.write(path)
