# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The Config represents settings that control how AutoTransform operates."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

from autotransform.runner.base import FACTORY as runner_factory
from autotransform.runner.base import Runner
from autotransform.runner.github import GithubRunner
from autotransform.runner.local import LocalRunner
from autotransform.util.component import ComponentModel
from autotransform.util.console import choose_yes_or_no, get_str


class Config(ComponentModel):
    """A collection of settings for configuring the functionality of AutoTransform.

    Attributes:
        component_directory (Optional[str], optional): The directory where custom component
            JSON files are located. If not provided, autotransform/ will be used.
            Defaults to None.
        github_token (Optional[str], optional): The Github token to use for authentication.
            Defaults to None.
        github_base_url (Optional[str], optional): The base URL for API requests to Github.
            Used for Github Enterprise. Defaults to None.
        local_runner (Optional[Runner], optional): The Runner to use for local runs.
            Defaults to None.
        remote_runner (Optional[Runner], optional): The runner to use for remote runs.
            Defaults to None.
    """

    component_directory: Optional[str] = None
    github_token: Optional[str] = None
    github_base_url: Optional[str] = None
    local_runner: Optional[Runner] = None
    remote_runner: Optional[Runner] = None

    def write(self, file_path: str) -> None:
        """Writes the Config to a file as JSON.

        Args:
            file_path (str): The file to write the Config to.
        """

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+", encoding="UTF-8") as schedule_file:
            schedule_file.write(json.dumps(self.bundle(), indent=4))
            schedule_file.flush()

    @staticmethod
    def read(file_path: str) -> Config:
        """Reads the Config from a JSON encoded file.

        Args:
            file_path (str): The path where the JSON for the Config is located.

        Returns:
            Config: The Config from the file.
        """

        try:
            with open(file_path, "r", encoding="UTF-8") as config_file:
                config_json = config_file.read()
            return Config.from_json(config_json)
        except FileNotFoundError:
            return Config()

    @staticmethod
    def from_json(config_json: str) -> Config:
        """Builds a Config from JSON encoded values.

        Args:
            config_json (str): The JSON encoded Config.

        Returns:
            Config: The Config from the JSON.
        """

        return Config.from_data(json.loads(config_json))

    @staticmethod
    def from_data(data: Dict[str, Any]) -> Config:
        """Produces an instance of the Config from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            Config: An instance of the Config.
        """

        github_token = data.get("github_token", None)
        if github_token is not None:
            assert isinstance(github_token, str)

        github_base_url = data.get("github_base_url", None)
        if github_base_url is not None:
            assert isinstance(github_base_url, str)

        component_directory = data.get("component_directory", None)
        if component_directory is not None:
            assert isinstance(component_directory, str)

        local_runner = data.get("local_runner", None)
        if local_runner is not None:
            local_runner = runner_factory.get_instance(local_runner)

        remote_runner = data.get("remote_runner", None)
        if remote_runner is not None:
            remote_runner = runner_factory.get_instance(remote_runner)

        return Config(
            github_token=github_token,
            github_base_url=github_base_url,
            component_directory=component_directory,
            local_runner=local_runner,
            remote_runner=remote_runner,
        )

    @staticmethod
    def get_github_token_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
        user_config: bool = False,
    ) -> Optional[str]:
        """Gets the Github token using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.
            user_config (bool, optional): Whether this configuration is for a user level Config.
                Defaults to False.

        Returns:
            Optional[str]: The Github token.
        """

        if not user_config:
            return None
        if prev_config is not None and (simple or choose_yes_or_no("Use previous Github Token?")):
            return prev_config.github_token

        github_token = get_str(
            "Enter the Github token to use(empty to not include one): ", secret=True
        )
        if github_token in ["", "None"]:
            return None

        return github_token

    @staticmethod
    def get_github_base_url_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
    ) -> Optional[str]:
        """Gets the Github base URL using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[str]: The Github base URL.
        """

        # Potentially use previous GHE information
        if prev_config is not None and (
            simple
            or choose_yes_or_no(f"Use previous Github base url: {prev_config.github_base_url}?")
        ):
            return prev_config.github_base_url

        # Simple setups assume no Github Enterprise
        if simple:
            return None

        github_base_url = get_str(
            "Enter the base URL for Github API requests (i.e. https://api.<org>-github.com): "
        )
        if github_base_url in ["", "None"]:
            return None
        return github_base_url

    @staticmethod
    def get_component_directory_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
    ) -> Optional[str]:
        """Gets the component directory using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[str]: The component directory.
        """

        # Potentially use previous information
        if prev_config is not None and (
            simple
            or choose_yes_or_no(
                f"Use previous component directory: {prev_config.component_directory}?"
            )
        ):
            return prev_config.component_directory

        # Simple setups assume no custom components
        if simple:
            return None

        component_directory = get_str("Enter the directory with custom component JSON files: ")
        if component_directory in ["", "None"]:
            return None
        return component_directory

    @staticmethod
    def get_local_runner_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
    ) -> Optional[Runner]:
        """Gets the local runner using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[Runner]: The local runner.
        """

        default_runner = LocalRunner()

        args: Dict[str, Any] = {
            "default_value": default_runner,
            "simple": simple,
        }
        if prev_config is not None:
            args["previous_value"] = prev_config.local_runner
        return runner_factory.from_console("local runner", **args)

    @staticmethod
    def get_remote_runner_from_console(
        prev_config: Optional[Config] = None,
        use_github: bool = False,
        simple: bool = False,
    ) -> Optional[Runner]:
        """Gets the remote runner using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            use_github (bool, optional): Whether to use Github or not. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[Runner]: The local runner.
        """

        args: Dict[str, Any] = {
            "simple": simple,
        }
        if use_github:
            args["default_value"] = GithubRunner(
                run_workflow="autotransform.run.yml", update_workflow="autotransform.update.yml"
            )
        if prev_config is not None:
            args["previous_value"] = prev_config.remote_runner
        return runner_factory.from_console("remote runner", **args)

    @staticmethod
    def from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
        use_github: Optional[bool] = None,
        user_config: bool = False,
    ) -> Tuple[Config, bool]:
        """Gets a Config using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.
            use_github (bool, optional): Whether to use Github or not. Defaults to None.
            user_config (bool, optional): Whether this configuration is for a user level Config.
                Defaults to False.

        Returns:
            Tuple[Config, bool]: The input Config and whether it uses github.
        """

        # Determine whether to include Github settings
        if use_github:
            github = True
        elif use_github is not None:
            github = False
        else:
            github = choose_yes_or_no("Use Github for this config?")

        if not github:
            github_token = None
            github_base_url = None
        else:
            github_token = Config.get_github_token_from_console(
                prev_config=prev_config, simple=simple, user_config=user_config
            )
            github_base_url = Config.get_github_base_url_from_console(
                prev_config=prev_config, simple=simple
            )

        return (
            Config(
                github_token=github_token,
                github_base_url=github_base_url,
                component_directory=Config.get_component_directory_from_console(
                    prev_config=prev_config, simple=simple
                ),
                local_runner=Config.get_local_runner_from_console(
                    prev_config=prev_config, simple=simple
                ),
                remote_runner=Config.get_remote_runner_from_console(
                    prev_config=prev_config, use_github=github, simple=simple
                ),
            ),
            github,
        )

    def merge(self, other: Config) -> Config:
        """Merges the Config with another Config. Settings in the other Config will override
        those in this Config.

        Args:
            other (Config): The Config to be merged with.

        Returns:
            Config: The merged Config.
        """

        return Config(
            github_token=other.github_token or self.github_token,
            github_base_url=other.github_base_url or self.github_base_url,
            component_directory=other.component_directory or self.component_directory,
            local_runner=other.local_runner or self.local_runner,
            remote_runner=other.remote_runner or self.remote_runner,
        )
