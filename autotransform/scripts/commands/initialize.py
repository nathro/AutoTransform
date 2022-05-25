# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The config command is used to update the config files for AutoTransform."""

import json
import os
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from getpass import getpass
from typing import Any, Dict, Mapping

from colorama import Fore

from autotransform.config.default import DefaultConfigFetcher
from autotransform.runner.github import GithubRunner
from autotransform.runner.local import LocalRunner

ERROR_COLOR = Fore.RED
INFO_COLOR = Fore.YELLOW
QUESTION_COLOR = Fore.GREEN
RESET_COLOR = Fore.RESET


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to initialize AutoTransform.

    Args:
        parser (ArgumentParser): The parser for the schema run.
    """

    parser.set_defaults(func=initialize_command_main)


def get_yes_or_no(prompt: str) -> bool:
    """Gets a yes or no answer to the prompt.

    Args:
        prompt (str): The question being asked

    Returns:
        bool: Whether the answer is yes.
    """

    while True:
        answer = input(f"{QUESTION_COLOR}{prompt}(Y/n) {RESET_COLOR}").lower()
        if answer in ["y", "yes"]:
            return True
        if answer in ["n", "no"]:
            return False
        print(f"{ERROR_COLOR}Invalid answer, please choose y(es) or n(o){RESET_COLOR}")


def initialize_config(config_path: str, config_name: str) -> Mapping[str, Any]:
    """Sets up the config and returns inputs that will be used for later setup.

    Args:
        config_path (str): The path to the config.
        config_name (str): The name of the config: user, repo, or cwd.

    Returns:
        Mapping[str, Any]: The inputs that were obtained when setting up the config.
    """

    # pylint: disable=too-many-branches

    print(f"{INFO_COLOR}Initializing {config_name} config located at: {config_path}{RESET_COLOR}")

    if os.path.exists(config_path):
        reset_config = get_yes_or_no("An existing config was found, replace it?")
        if not reset_config:
            return {}

    config = ConfigParser()
    config["CREDENTIALS"] = {}
    config["IMPORTS"] = {}
    config["RUNNER"] = {}

    # Set up credentials configuration
    use_github = get_yes_or_no("Do you want to configure AutoTransform to work with Github?")
    inputs: Dict[str, Any] = {"use_github": use_github}
    if use_github:
        # Github tokens should only ever be used in user configs
        if config_name == "user":
            github_token = getpass(f"{QUESTION_COLOR}Enter your Github Token: {RESET_COLOR}")
            config["CREDENTIALS"]["github_token"] = github_token

        use_ghe = get_yes_or_no("Will you be using exclusively Github Enterprise repos?")
        if use_ghe:
            github_base_url = input(
                f"{QUESTION_COLOR}Enter the base URL for GHE API requests"
                + f"(i.e. https://api.your_org-github.com): {RESET_COLOR}"
            )
            config["CREDENTIALS"]["github_base_url"] = github_base_url
            inputs["github_base_url"] = github_base_url
        else:
            inputs["github_base_url"] = None

    # Set up custom component configuration
    use_custom_components = get_yes_or_no("Would you like to use custom component modules?")
    if use_custom_components:
        custom_components = input(
            f"{QUESTION_COLOR}Enter a comma separated list of custom components: {RESET_COLOR}"
        )
        config["IMPORTS"]["components"] = github_base_url
        inputs["custom_components"] = custom_components
    else:
        inputs["custom_components"] = None

    # Set up runner configuration
    use_default_local_runner = get_yes_or_no("Would you like to use the default local runner?")
    if use_default_local_runner:
        local_runner = json.dumps(LocalRunner({}).bundle())
    else:
        local_runner = input(
            f"{QUESTION_COLOR}Enter a JSON encoded runner for local runs: {RESET_COLOR}"
        )
    config["RUNNER"]["local"] = local_runner
    inputs["local_runner"] = local_runner

    remote_runner = None
    if use_github:
        use_default_remote_runner = get_yes_or_no(
            "Would you like to use the default remote runner?"
        )
        if use_default_remote_runner:
            remote_runner = json.dumps(
                GithubRunner(
                    {
                        "run_workflow": "autotransform_run.yml",
                        "update_workflow": "autotransform_update.yml",
                    }
                ).bundle()
            )
    if remote_runner is None:
        remote_runner = input(
            f"{QUESTION_COLOR}Enter a JSON encoded runner for remote runs: {RESET_COLOR}"
        )
    config["RUNNER"]["remote"] = remote_runner
    inputs["remote_runner"] = remote_runner

    with open(config_path, "w", encoding="utf-8") as config_file:
        config.write(config_file)

    return inputs


def initialize_command_main(_args: Namespace) -> None:
    """The main method for the schedule command, handles the actual execution of scheduling runs.

    Args:
        _args (Namespace): The arguments supplied to the initialize command.
    """
    user_config_path = (
        f"{DefaultConfigFetcher.get_user_config_dir()}/{DefaultConfigFetcher.CONFIG_NAME}"
    )
    initialize_config(user_config_path, "user")
