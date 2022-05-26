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
import pathlib
import subprocess
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from getpass import getpass
from typing import Any, Dict, List, Mapping, Tuple

from colorama import Fore

from autotransform.change.state import ChangeState
from autotransform.config.default import DefaultConfigFetcher
from autotransform.repo.base import Repo
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.runner.github import GithubRunner
from autotransform.runner.local import LocalRunner
from autotransform.schema.schema import AutoTransformSchema
from autotransform.step.action import ActionType
from autotransform.step.base import Step
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.state import ChangeStateCondition
from autotransform.step.condition.updated import UpdatedAgoCondition
from autotransform.step.conditional import ConditionalStep

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

    with open(config_path, "w", encoding="UTF-8") as config_file:
        config.write(config_file)

    return inputs


def initialize_workflows(repo_dir: str, examples_dir: str, prev_inputs: Mapping[str, Any]) -> None:
    """Set up the workflow files for using Github workflows.

    Args:
        repo_dir (str): The top level directory of the repo.
        examples_dir (str): Where example files are located.
        prev_inputs (Mapping[str, Any]): Previous inputs from configuration.
    """

    bot_email = input(
        f"{QUESTION_COLOR}Enter the email of the account used for automation: {RESET_COLOR}"
    )
    bot_name = input(
        f"{QUESTION_COLOR}Enter the name of the account used for automation: {RESET_COLOR}"
    )
    custom_components = prev_inputs.get("import_components")
    workflows = [
        "autotransform_manage.yml",
        "autotransform_run.yml",
        "autotransform_schedule.yml",
        "autotransform_update.yml",
    ]
    for workflow in workflows:
        with open(f"{examples_dir}/workflows/{workflow}", "r", encoding="UTF-8") as workflow_file:
            workflow_text = workflow_file.read()
        workflow_text = workflow_text.replace("<BOT EMAIL>", bot_email)
        workflow_text = workflow_text.replace("<BOT NAME>", bot_name)
        if custom_components is not None:
            workflow_text = workflow_text.replace("<CUSTOM COMPONENTS>", custom_components)
        else:
            workflow_text = "\n".join(
                [line for line in workflow_text.split("\n") if "<CUSTOM COMPONENTS>" not in line]
            )
        with open(
            f"{repo_dir}/.github/workflows/{workflow}", "w", encoding="UTF-8"
        ) as workflow_file:
            workflow_file.write(workflow_text)
            workflow_file.flush()


def get_manage_bundle(
    use_github_actions: bool, repo: Repo, prev_inputs: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Initialize the manage.json file.

    Args:
        use_github_actions (bool): Whether the repo uses Github Actions.
        repo (Repo): The repo being managed.
        prev_inputs (Mapping[str, Any]): Previous inputs from configuration.
    """
    if use_github_actions:
        remote_runner: Any = GithubRunner(
            {
                "run_workflow": "autotransform_run.yml",
                "update_workflow": "autotransform_update.yml",
            }
        ).bundle()
    else:
        remote_runner = prev_inputs.get("runner_remote")
        if remote_runner is None:
            remote_runner = input(
                f"{QUESTION_COLOR}Enter a JSON encoded runner for remote runs: {RESET_COLOR}"
            )
        remote_runner = json.loads(remote_runner)
    steps: List[Step] = []

    # Merge approved changes
    if get_yes_or_no("Automatically merge approved changes?"):
        steps.append(
            ConditionalStep(
                {
                    "condition": ChangeStateCondition(
                        {"comparison": ComparisonType.EQUAL, "state": ChangeState.APPROVED}
                    ),
                    "action_type": ActionType.MERGE,
                }
            )
        )

    # Abandon rejected changes
    if get_yes_or_no("Automatically abandon rejected changes?"):
        steps.append(
            ConditionalStep(
                {
                    "condition": ChangeStateCondition(
                        {"comparison": ComparisonType.EQUAL, "state": ChangeState.CHANGES_REQUESTED}
                    ),
                    "action_type": ActionType.ABANDON,
                }
            )
        )

    # Update stale changes
    if get_yes_or_no("Automatically update stale changes?"):
        days_stale: int = 0
        while days_stale == 0:
            num_days = input(
                f"{QUESTION_COLOR}How many days to consider a change stale?{RESET_COLOR}"
            )
            if num_days.isdigit():
                days_stale = int(num_days)
                if days_stale <= 0:
                    print(f"{ERROR_COLOR}Invalid input, enter a number greater than 0{RESET_COLOR}")
            else:
                print(f"{ERROR_COLOR}Invalid input, enter a number{RESET_COLOR}")
        steps.append(
            ConditionalStep(
                {
                    "condition": UpdatedAgoCondition(
                        {
                            "comparison": ComparisonType.GREATER_THAN_OR_EQUAL,
                            "time": days_stale * 24 * 60 * 60,
                        }
                    ),
                    "action_type": ActionType.ABANDON,
                }
            )
        )

    return {
        "repo": repo.bundle(),
        "remote_runner": remote_runner,
        "steps": [step.bundle() for step in steps],
    }


def initialize_repo(repo_dir: str, prev_inputs: Mapping[str, Any]) -> None:
    """Set up a repo to work with AutoTransform.

    Args:
        repo_dir (str): The top level directory of the repo.
        prev_inputs (Mapping[str, Any]): Previous inputs from configuration.
    """

    package_dir = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    examples_dir = f"{package_dir}/examples"

    use_github = prev_inputs.get("use_github")
    if use_github is None:
        use_github = get_yes_or_no("Do you want to configure AutoTransform to use Github?")

    # Set up workflow files
    use_github_actions = get_yes_or_no("Use Github Actions for AutoTransform?")
    if use_github and use_github_actions:
        initialize_workflows(repo_dir, examples_dir, prev_inputs)

    # Get the repo
    base_branch_name = input(
        f"{QUESTION_COLOR}Enter the name of the base branch "
        + f"for the repo(i.e. main,master): {RESET_COLOR}"
    )
    if use_github:
        github_name = input(
            f"{QUESTION_COLOR}Enter the fully qualified name of "
            + f"the github repo (owner/repo): {RESET_COLOR}"
        )
        repo: Repo = GithubRepo(
            {"base_branch_name": base_branch_name, "full_github_name": github_name}
        )
    else:
        repo = GitRepo({"base_branch_name": base_branch_name})

    # Set up the sample schema
    use_sample_schema = get_yes_or_no("Would you like to include the sample schema?")
    if use_sample_schema:
        with open(
            f"{examples_dir}/schemas/black_format.json", "r", encoding="UTF-8"
        ) as schema_file:
            schema = AutoTransformSchema.from_json(schema_file.read())
        schema._repo = repo  # pylint: disable=protected-access
        with open(
            f"{repo_dir}/autotransform/schemas/black_format.json", "w", encoding="UTF-8"
        ) as schema_file:
            schema_file.write(schema.to_json(pretty=True))
            schema_file.flush()

        # Get requirements
        with open(f"{examples_dir}/requirements.txt", "r", encoding="UTF-8") as requirements_file:
            requirements = requirements_file.read()
    else:
        requirements = ""

    # Set up requirements file
    with open(
        f"{repo_dir}/autotransform/requirements.txt", "w", encoding="UTF-8"
    ) as requirements_file:
        requirements_file.write(requirements)
        requirements_file.flush()

    # Set up manage file
    manage_bundle = get_manage_bundle(use_github_actions, repo, prev_inputs)
    with open(f"{repo_dir}/autotransform/manage.json", "w", encoding="UTF-8") as manage_file:
        manage_file.write(json.dumps(manage_bundle, indent=4))
        manage_file.flush()


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
        repo_dir = ""
        setup_repo = False

    if setup_repo:
        repo_config_path = (
            f"{DefaultConfigFetcher.get_repo_config_dir()}/{DefaultConfigFetcher.CONFIG_NAME}"
        )
        inputs = initialize_config(repo_config_path, "repo", inputs)
        initialize_repo(repo_dir, inputs)

    if repo_dir == "" and get_yes_or_no("Set up configuration for current working directory?"):
        cwd_config_path = (
            f"{DefaultConfigFetcher.get_cwd_config_dir()}/{DefaultConfigFetcher.CONFIG_NAME}"
        )
        initialize_config(cwd_config_path, "current working directory", inputs)
