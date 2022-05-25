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
import subprocess
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from getpass import getpass
from typing import Any, Dict, Mapping, Tuple

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


def initialize_config_credentials(
    get_token: bool, prev_inputs: Mapping[str, Any]
) -> Tuple[Dict[str, Any], Mapping[str, Any]]:
    """Initialize the credentials section of a config.

    Args:
        get_token (bool): Whether to get a Github Token.
        prev_inputs (Mapping[str, Any]): Previously used input values.

    Returns:
        Tuple[Dict[str, Any], Mapping[str, Any]]: A tuple containing the new section and the
            supplied inputs.
    """

    use_github = get_yes_or_no("Do you want to configure AutoTransform to use Github?")
    if not use_github:
        return {}, {"use_github": False}

    section = {}
    inputs: Dict[str, Any] = {"use_github": True}
    # Github tokens should only ever be used in user configs
    if get_token:
        github_token = getpass(f"{QUESTION_COLOR}Enter your Github Token: {RESET_COLOR}")
        section["github_token"] = github_token

    if get_yes_or_no("Use Github Enterprise?"):
        prev_base_url = prev_inputs.get("github_base_url")
        if prev_base_url is not None and get_yes_or_no(f"Use previous GHE URL ({prev_base_url})?"):
            github_base_url = prev_base_url
        else:
            github_base_url = input(
                f"{QUESTION_COLOR}Enter the base URL for GHE API requests"
                + f"(i.e. https://api.your_org-github.com): {RESET_COLOR}"
            )
        section["github_base_url"] = github_base_url
        inputs["github_base_url"] = github_base_url
    else:
        inputs["github_base_url"] = None

    return section, inputs


def initialize_config_imports(
    prev_inputs: Mapping[str, Any]
) -> Tuple[Dict[str, Any], Mapping[str, Any]]:
    """Initialize the imports section of a config.

    Args:
        prev_inputs (Mapping[str, Any]): Previously used input values.

    Returns:
        Tuple[Dict[str, Any], Mapping[str, Any]]: A tuple containing the new section and the
            supplied inputs.
    """

    use_custom_components = get_yes_or_no("Would you like to use custom component modules?")
    if not use_custom_components:
        return {}, {}

    section = {}
    inputs: Dict[str, Any] = {}

    prev_custom_components = prev_inputs.get("import_components")
    if prev_custom_components and get_yes_or_no(
        f"Use previous custom components ({prev_custom_components})?"
    ):
        custom_components = prev_custom_components
    else:
        custom_components = input(
            f"{QUESTION_COLOR}Enter a comma separated list of custom components: {RESET_COLOR}"
        )
    section["components"] = custom_components
    inputs["import_components"] = custom_components

    return section, inputs


def initialize_config_runner(
    prev_inputs: Mapping[str, Any]
) -> Tuple[Dict[str, Any], Mapping[str, Any]]:
    """Initialize the runner section of a config.

    Args:
        prev_inputs (Mapping[str, Any]): Previously used input values.

    Returns:
        Tuple[Dict[str, Any], Mapping[str, Any]]: A tuple containing the new section and the
            supplied inputs.
    """

    section = {}
    inputs: Dict[str, Any] = {}

    # Get local runner
    prev_local_runner = prev_inputs.get("runner_local")
    default_local_runner = json.dumps(LocalRunner({}).bundle())
    if (
        prev_local_runner is not None
        and prev_local_runner != default_local_runner
        and get_yes_or_no(f"Use previous local runner({prev_local_runner})?")
    ):
        local_runner = prev_local_runner
    elif get_yes_or_no("Would you like to use the default local runner?"):
        local_runner = default_local_runner
    else:
        local_runner = input(
            f"{QUESTION_COLOR}Enter a JSON encoded runner for local runs: {RESET_COLOR}"
        )
    section["local"] = local_runner
    inputs["runner_local"] = local_runner

    # Get remote runner
    prev_remote_runner = prev_inputs.get("runner_remote")
    default_remote_runner = json.dumps(
        GithubRunner(
            {
                "run_workflow": "autotransform_run.yml",
                "update_workflow": "autotransform_update.yml",
            }
        ).bundle()
    )
    if (
        prev_remote_runner is not None
        and prev_remote_runner != default_remote_runner
        and get_yes_or_no(f"Use previous remote runner({prev_remote_runner})?")
    ):
        remote_runner = prev_remote_runner
    elif get_yes_or_no("Would you like to use the default Github remote runner?"):
        remote_runner = default_remote_runner
    else:
        remote_runner = input(
            f"{QUESTION_COLOR}Enter a JSON encoded runner for remote runs: {RESET_COLOR}"
        )
    section["remote"] = remote_runner
    inputs["runner_remote"] = remote_runner

    return section, inputs


def initialize_config(
    config_path: str, config_name: str, prev_inputs: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Sets up the config and returns inputs that will be used for later setup.

    Args:
        config_path (str): The path to the config.
        config_name (str): The name of the config: user, repo, or cwd.
        prev_inputs (Mapping[str, Any]): Previously specified values.

    Returns:
        Mapping[str, Any]: The inputs that were obtained when setting up the config.
    """

    print(f"{INFO_COLOR}Initializing {config_name} config located at: {config_path}{RESET_COLOR}")

    if os.path.exists(config_path):
        reset_config = get_yes_or_no("An existing config was found, replace it?")
        if not reset_config:
            return {}

    config = ConfigParser()
    config["IMPORTS"] = {}
    config["RUNNER"] = {}
    inputs: Dict[str, Any] = {}

    # Set up credentials configuration
    credentials_section, credentials_inputs = initialize_config_credentials(
        config_name == "user", prev_inputs
    )
    config["CREDENTIALS"] = credentials_section
    for key, value in credentials_inputs.items():
        inputs[key] = value

    # Set up custom component configuration
    imports_section, imports_inputs = initialize_config_imports(prev_inputs)
    config["IMPORTS"] = imports_section
    for key, value in imports_inputs.items():
        inputs[key] = value

    # Set up runner configuration
    runner_section, runner_inputs = initialize_config_runner(prev_inputs)
    config["RUNNER"] = runner_section
    for key, value in runner_inputs.items():
        inputs[key] = value

    with open(config_path, "w", encoding="utf-8") as config_file:
        config.write(config_file)

    return inputs


def initialize_command_main(_args: Namespace) -> None:
    """The main method for the schedule command, handles the actual execution of scheduling runs.

    Args:
        _args (Namespace): The arguments supplied to the initialize command.
    """

    print(f"{INFO_COLOR}Setting up user level configuration{RESET_COLOR}")
    user_config_path = (
        f"{DefaultConfigFetcher.get_user_config_dir()}/{DefaultConfigFetcher.CONFIG_NAME}"
    )
    inputs = initialize_config(user_config_path, "user", {})

    # Set up repo
    try:
        dir_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
        print(f"{INFO_COLOR}Repo found at {repo_dir}{RESET_COLOR}")
        setup_repo = get_yes_or_no("Initialize the repo?")
    except Exception:  # pylint: disable=broad-except
        print(
            f"{INFO_COLOR}No git repo to set up, "
            + f"run inside a git repo to initialize the repo{RESET_COLOR}"
        )
        setup_repo = False

    if setup_repo:
        print(f"{INFO_COLOR}Setting up repo level configuration{RESET_COLOR}")
        repo_config_path = (
            f"{DefaultConfigFetcher.get_repo_config_dir()}/{DefaultConfigFetcher.CONFIG_NAME}"
        )
        initialize_config(repo_config_path, "repo", inputs)
