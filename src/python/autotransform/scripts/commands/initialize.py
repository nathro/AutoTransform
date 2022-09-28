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
from typing import Optional, Tuple

from autotransform.config import (
    CONFIG_FILE_NAME,
    get_cwd_config_dir,
    get_repo_config_dir,
    get_repo_config_relative_path,
)
from autotransform.config.config import Config
from autotransform.repo.base import RepoName
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.console import choose_yes_or_no, info
from autotransform.util.enums import SchemaType
from autotransform.util.manager import Manager
from autotransform.util.package import get_config_dir, get_examples_dir
from autotransform.util.scheduler import Scheduler


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to initialize AutoTransform.

    Args:
        parser (ArgumentParser): The parser for the initialization.
    """

    parser.add_argument(
        "-s",
        "--simple",
        dest="simple",
        action="store_true",
        required=False,
        help="Tells the script to perform a simple set-up, selecting smart defaults.",
    )
    github_group = parser.add_mutually_exclusive_group()
    github_group.add_argument(
        "--github",
        dest="github",
        action="store_true",
        required=False,
        help="Tells the script that Github is being used.",
    )
    github_group.add_argument(
        "--no-github",
        dest="github",
        action="store_false",
        required=False,
        help="Tells the script that Github is not being used.",
    )

    jenkins_group = parser.add_mutually_exclusive_group()
    jenkins_group.add_argument(
        "--jenkins",
        dest="jenkins",
        action="store_true",
        required=False,
        help="Tells the script that Jenkins is being used.",
    )
    jenkins_group.add_argument(
        "--no-jenkins",
        dest="jenkins",
        action="store_false",
        required=False,
        help="Tells the script that Jenkins is not being used.",
    )

    parser.set_defaults(func=initialize_command_main, simple=False, github=None, jenkins=None)


# pylint: disable=too-many-arguments
def initialize_config(
    config_path: str,
    config_name: str,
    prev_config: Optional[Config] = None,
    simple: bool = False,
    use_github: Optional[bool] = None,
    use_jenkins: Optional[bool] = None,
) -> Tuple[Config, Optional[bool], Optional[bool]]:
    """Gets all of the inputs required to create a config file and write it.

    Args:
        config_path (str): The path to the config.
        config_name (str): The name of the config: user, repo, or cwd.
        prev_config (Optional[Config[, optional]): Previously input Config. Defaults to None.
        simple (bool, optional): Whether to use the simple setup. Defaults to False.
        use_github (bool, optional): Whether to use Github or not. Defaults to None.
        use_jenkins (bool, optional): Whether to use Jenkins or not. Defaults to None.

    Returns:
        Tuple[Config, Optional[bool]]: The input Config and whether it uses Github and Jenkins.
    """

    info(f"Initializing {config_name} config located at: {config_path}")

    if os.path.exists(config_path):
        reset_config = not simple and choose_yes_or_no("An existing config was found, replace it?")
        existing_config = Config.read(config_path)
        if not reset_config:
            return (existing_config, use_github, use_jenkins)
        if prev_config is not None:
            prev_config = existing_config.merge(prev_config)
        else:
            prev_config = existing_config

    config, github, jenkins = Config.from_console(
        prev_config=prev_config,
        simple=simple,
        use_github=use_github,
        use_jenkins=use_jenkins,
        user_config=config_name == "user",
    )
    config.write(config_path)
    return (config, github, jenkins)


def initialize_workflows(repo_dir: str, examples_dir: str, prev_config: Optional[Config]) -> None:
    """Set up the workflow files for using Github workflows.

    Args:
        repo_dir (str): The top level directory of the repo.
        examples_dir (str): Where example files are located.
        prev_config (Optional[Config]): Previously input Config.
    """

    component_directory = prev_config.component_directory if prev_config is not None else None
    relative_config_dir = get_repo_config_relative_path()

    workflows = [
        "autotransform.manage.yml",
        "autotransform.run.yml",
        "autotransform.schedule.yml",
        "autotransform.update.yml",
    ]
    for workflow in workflows:
        with open(f"{examples_dir}/workflows/{workflow}", "r", encoding="UTF-8") as workflow_file:
            workflow_text = workflow_file.read()

        workflow_text = workflow_text.replace("<CONFIG DIR>", relative_config_dir)

        if component_directory is not None:
            workflow_text = workflow_text.replace("<CUSTOM COMPONENTS>", component_directory)
        else:
            workflow_text = "\n".join(
                [line for line in workflow_text.split("\n") if "<CUSTOM COMPONENTS>" not in line]
            )

        workflow_file_path = f"{repo_dir}/.github/workflows/{workflow}"
        os.makedirs(os.path.dirname(workflow_file_path), exist_ok=True)
        with open(workflow_file_path, "w+", encoding="UTF-8") as workflow_file:
            workflow_file.write(workflow_text)
            workflow_file.flush()


def initialize_docker(repo_dir: str, examples_dir: str) -> None:
    """Set up the workflow files for using Github workflows.

    Args:
        repo_dir (str): The top level directory of the repo.
        examples_dir (str): Where example files are located.
    """

    relative_config_dir = get_repo_config_relative_path()

    docker_files = [
        "docker_autotransform.sh",
        "Dockerfile",
        "entrypoint.sh",
    ]
    for file in docker_files:
        with open(f"{examples_dir}/docker/{file}", "r", encoding="UTF-8") as docker_file:
            docker_file_text = docker_file.read()

        docker_file_path = f"{repo_dir}/{relative_config_dir}/docker/{file}"
        os.makedirs(os.path.dirname(docker_file_path), exist_ok=True)
        with open(docker_file_path, "w+", encoding="UTF-8") as workflow_file:
            workflow_file.write(docker_file_text)
            workflow_file.flush()


def initialize_repo(
    repo_dir: str,
    prev_config: Optional[Config],
    simple: bool = False,
    use_github: Optional[bool] = None,
    use_jenkins: Optional[bool] = None,
) -> None:
    """Set up a repo to work with AutoTransform.

    Args:
        repo_dir (str): The top level directory of the repo.
        prev_config (Optional[Config]): Previously input Config.
        simple (bool, optional): Whether to use the simple setup. Defaults to False.
        use_github (bool, optional): Whether to use Github or not. Defaults to None.
        use_jenkins (bool, optional): Whether to use Jenkins or not. Defaults to None.
    """

    examples_dir = get_examples_dir()
    repo_config_dir = get_repo_config_dir()

    github = use_github
    if github is None:
        github = choose_yes_or_no("Do you want to configure AutoTransform to use Github?")

    # Set up workflow files
    use_github_actions = github and (
        simple or choose_yes_or_no("Use Github Actions for AutoTransform?")
    )
    if use_github_actions:
        initialize_workflows(repo_dir, examples_dir, prev_config)
    elif use_jenkins:
        initialize_docker(repo_dir, examples_dir)

    # Get the Manager
    manager = Manager.init_from_console(
        repo_name=RepoName.GITHUB if github else RepoName.GIT,
        simple=simple,
    )

    # Set up the sample schema
    use_sample_schema = simple or choose_yes_or_no("Would you like to include the sample schema?")
    schema_map = {}
    if use_sample_schema:
        sample_schema_path = f"{examples_dir}/schemas/black_format.json"
        schema_map["Black Format"] = {"type": SchemaType.FILE, "target": sample_schema_path}
        with open(sample_schema_path, "r", encoding="UTF-8") as sample_schema_file:
            schema = AutoTransformSchema.from_data(json.loads(sample_schema_file.read()))
        schema.repo = manager.repo  # pylint: disable=protected-access

        schema_path = f"{repo_config_dir}/schemas/black_format.json"
        os.makedirs(os.path.dirname(schema_path), exist_ok=True)
        with open(schema_path, "w+", encoding="UTF-8") as schema_file:
            schema_file.write(json.dumps(schema.bundle(), indent=4))
            schema_file.flush()

        # Get requirements
        with open(f"{examples_dir}/requirements.txt", "r", encoding="UTF-8") as requirements_file:
            requirements = requirements_file.read()
    else:
        requirements = ""

    # Set up requirements file
    requirements_path = f"{repo_config_dir}/requirements.txt"
    os.makedirs(os.path.dirname(requirements_path), exist_ok=True)
    with open(requirements_path, "w+", encoding="UTF-8") as requirements_file:
        requirements_file.write(requirements)
        requirements_file.flush()

    # Set up schema map file
    schema_map_path = f"{repo_config_dir}/schema_map.json"
    os.makedirs(os.path.dirname(schema_map_path), exist_ok=True)
    with open(schema_map_path, "w+", encoding="UTF-8") as schema_map_file:
        schema_map_file.write(json.dumps(schema_map))
        schema_map_file.flush()

    # Set up manage file
    manager_path = f"{repo_config_dir}/manager.json"
    manager.write(manager_path)

    # Set up schedule file
    scheduler = Scheduler.init_from_console(use_sample_schema, simple)
    scheduler_path = f"{repo_config_dir}/scheduler.json"
    scheduler.write(scheduler_path)

    if use_github_actions:
        info(
            "Please ensure there is a repository secret of AUTO_TRANSFORM_BOT_GITHUB_TOKEN "
            + "that contains a Github token for your bot account"
        )
        info(
            "This token must have permissions to push branches, "
            + "create pull requests, and trigger workflows."
        )


def initialize_command_main(args: Namespace) -> None:
    """The main method for the schedule command, handles the actual execution of scheduling runs.

    Args:
        _args (Namespace): The arguments supplied to the initialize command.
    """

    simple = args.simple
    github = args.github
    jenkins = args.jenkins

    user_config_path = f"{get_config_dir()}/{CONFIG_FILE_NAME}"
    config, github, jenkins = initialize_config(
        user_config_path, "user", None, simple=simple, use_github=github, use_jenkins=jenkins
    )

    # Set up repo
    try:
        dir_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
        info(f"Repo found at {repo_dir}")
        setup_repo = choose_yes_or_no("Should AutoTransform set up the repo?")
    except Exception:  # pylint: disable=broad-except
        info("No git repo to set up, run inside a git repo to set it up.")
        repo_dir = ""
        setup_repo = False

    if setup_repo:
        repo_config_path = f"{get_repo_config_dir()}/{CONFIG_FILE_NAME}"
        config, github, jenkins = initialize_config(
            repo_config_path, "repo", config, simple=simple, use_github=github, use_jenkins=jenkins
        )
        initialize_repo(repo_dir, config, simple=simple, use_github=github, use_jenkins=jenkins)

    if repo_dir == "" and choose_yes_or_no("Set up configuration for current working directory?"):
        cwd_config_path = f"{get_cwd_config_dir()}/{CONFIG_FILE_NAME}"
        initialize_config(
            cwd_config_path,
            "current working directory",
            config,
            simple=simple,
            use_github=github,
            use_jenkins=jenkins,
        )
