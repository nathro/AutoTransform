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
from typing import Any, Dict, List, Optional, Tuple

from autotransform.event.notifier.base import FACTORY as notifier_factory
from autotransform.event.notifier.base import EventNotifier, EventNotifierName
from autotransform.event.notifier.console import ConsoleEventNotifier
from autotransform.repo.base import FACTORY as repo_factory
from autotransform.repo.base import Repo
from autotransform.runner.base import FACTORY as runner_factory
from autotransform.runner.base import Runner
from autotransform.runner.github import GithubRunner
from autotransform.runner.jenkins import JenkinsAPIRunner
from autotransform.runner.local import LocalRunner
from autotransform.util.component import ComponentModel
from autotransform.util.console import choose_yes_or_no, get_str
from pydantic import Field


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
        jenkins_user (Optional[str], optional): The Jenkins username for authentication. Defaults
            to None.
        jenkins_token (Optional[str], optional): The Jenkins token to use for authentication.
            Defaults to None.
        jenkins_base_url (Optional[str], optional): The base URL for requests to Jenkins.
            Defaults to None.
        local_runner (Optional[Runner], optional): The Runner to use for local runs.
            Defaults to None.
        anthropic_api_key (Optional[str], optional): The API key to use for Anthropic completitions.
            Defaults to None.
        open_ai_api_key (Optional[str], optional): The API key to use for OpenAI completitions.
            Defaults to None.
        remote_runner (Optional[Runner], optional): The runner to use for remote runs.
            Defaults to None.
        repo_override (Optional[Repo], optional): A repo to use in place of any schema repos.
            Defaults to None.
        event_notifiers (List[Dict[str, Any]], optional): The EventNotifiers to use. Defaults to
            a list containing just the ConsoleEventNotifier bundle.
    """

    component_directory: Optional[str] = None
    github_token: Optional[str] = Field(default=None, exclude=True)
    github_base_url: Optional[str] = None
    jenkins_user: Optional[str] = None
    jenkins_token: Optional[str] = Field(default=None, exclude=True)
    jenkins_base_url: Optional[str] = None
    local_runner: Optional[Runner] = None
    anthropic_api_key: Optional[str] = None
    open_ai_api_key: Optional[str] = None
    remote_runner: Optional[Runner] = None
    repo_override: Optional[Repo] = None
    event_notifiers: List[Dict[str, Any]] = Field(
        default=[ConsoleEventNotifier().bundle()]
    )

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

        jenkins_user = data.get("jenkins_user", None)
        if jenkins_user is not None:
            assert isinstance(jenkins_user, str)

        jenkins_token = data.get("jenkins_token", None)
        if jenkins_token is not None:
            assert isinstance(jenkins_token, str)

        jenkins_base_url = data.get("jenkins_base_url", None)
        if jenkins_base_url is not None:
            assert isinstance(jenkins_base_url, str)

        anthropic_api_key = data.get("anthropic_api_key", None)
        if anthropic_api_key is not None:
            assert isinstance(anthropic_api_key, str)

        open_ai_api_key = data.get("open_ai_api_key", None)
        if open_ai_api_key is not None:
            assert isinstance(open_ai_api_key, str)

        component_directory = data.get("component_directory", None)
        if component_directory is not None:
            assert isinstance(component_directory, str)

        local_runner = data.get("local_runner", None)
        if local_runner is not None:
            local_runner = runner_factory.get_instance(local_runner)

        remote_runner = data.get("remote_runner", None)
        if remote_runner is not None:
            remote_runner = runner_factory.get_instance(remote_runner)

        repo_override = data.get("repo_override", None)
        if repo_override is not None:
            repo_override = repo_factory.get_instance(repo_override)

        event_notifiers = data.get("event_notifiers", None)
        if event_notifiers is None:
            event_notifiers = [ConsoleEventNotifier().bundle()]

        return Config(
            github_token=github_token,
            github_base_url=github_base_url,
            jenkins_user=jenkins_user,
            jenkins_token=jenkins_token,
            jenkins_base_url=jenkins_base_url,
            component_directory=component_directory,
            local_runner=local_runner,
            anthropic_api_key=anthropic_api_key,
            open_ai_api_key=open_ai_api_key,
            remote_runner=remote_runner,
            repo_override=repo_override,
            event_notifiers=event_notifiers,
        )

    def get_event_notifiers(self) -> List[EventNotifier]:
        """Gets the EventNotifier objects.

        Returns:
            List[EventNotifier]: The list of EventNotifier objects.
        """

        return [
            notifier_factory.get_instance(notifier)
            for notifier in self.event_notifiers  # pylint: disable=not-an-iterable
        ]

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
        if prev_config is not None and (
            simple or choose_yes_or_no("Use previous Github Token?")
        ):
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
            or choose_yes_or_no(
                f"Use previous Github base url: {prev_config.github_base_url}?"
            )
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
    def get_jenkins_user_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
    ) -> Optional[str]:
        """Gets the Jenkins user using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[str]: The Jenkins user.
        """

        # Potentially use previous Jenkins information
        if prev_config is not None and (
            simple
            or choose_yes_or_no(
                f"Use previous Jenkins user: {prev_config.jenkins_user}?"
            )
        ):
            return prev_config.jenkins_user

        # Simple setups assume no Jenkins
        if simple:
            return None

        jenkins_user = get_str("Enter the Jenkins user: ")
        if jenkins_user in ["", "None"]:
            return None
        return jenkins_user

    @staticmethod
    def get_jenkins_token_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
        user_config: bool = False,
    ) -> Optional[str]:
        """Gets the Jenkins token using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.
            user_config (bool, optional): Whether this configuration is for a user level Config.
                Defaults to False.

        Returns:
            Optional[str]: The Jenkins token.
        """

        if not user_config:
            return None
        if prev_config is not None and (
            simple or choose_yes_or_no("Use previous Jenkins Token?")
        ):
            return prev_config.jenkins_token

        jenkins_token = get_str(
            "Enter the Jenkins token to use(empty to not include one): ", secret=True
        )
        if jenkins_token in ["", "None"]:
            return None

        return jenkins_token

    @staticmethod
    def get_jenkins_base_url_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
    ) -> Optional[str]:
        """Gets the Jenkins base URL using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[str]: The Jenkins base URL.
        """

        # Potentially use previous Jenkins information
        if prev_config is not None and (
            simple
            or choose_yes_or_no(
                f"Use previous Jenkins base url: {prev_config.jenkins_base_url}?"
            )
        ):
            return prev_config.jenkins_base_url

        # Simple setups assume no Jenkins
        if simple:
            return None

        jenkins_base_url = get_str(
            "Enter the base URL for Jenkins requests (i.e. https://<org>.jenkins.com): "
        )
        if jenkins_base_url in ["", "None"]:
            return None
        return jenkins_base_url

    @staticmethod
    def get_anthropic_api_key_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
        user_config: bool = False,
    ) -> Optional[str]:
        """Gets the Anthropic API key using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.
            user_config (bool, optional): Whether this configuration is for a user level Config.
                Defaults to False.

        Returns:
            Optional[str]: The Anthropic API key.
        """

        if not user_config:
            return None
        if prev_config is not None and (
            simple or choose_yes_or_no("Use previous Anthropic API Key?")
        ):
            return prev_config.anthropic_api_key

        anthropic_api_key = get_str(
            "Enter the Anthropic API key(empty to not include one): ", secret=True
        )
        if anthropic_api_key in ["", "None"]:
            return None

        return anthropic_api_key

    @staticmethod
    def get_open_ai_api_key_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
        user_config: bool = False,
    ) -> Optional[str]:
        """Gets the OpenAI API key using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.
            user_config (bool, optional): Whether this configuration is for a user level Config.
                Defaults to False.

        Returns:
            Optional[str]: The OpenAI API key.
        """

        if not user_config:
            return None
        if prev_config is not None and (
            simple or choose_yes_or_no("Use previous OpenAI API Key?")
        ):
            return prev_config.open_ai_api_key

        open_ai_api_key = get_str(
            "Enter the OpenAI API key(empty to not include one): ", secret=True
        )
        if open_ai_api_key in ["", "None"]:
            return None

        return open_ai_api_key

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

        component_directory = get_str(
            "Enter the directory with custom component JSON files: "
        )
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
        use_jenkins: bool = False,
        simple: bool = False,
    ) -> Optional[Runner]:
        """Gets the remote runner using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            use_github (bool, optional): Whether to use Github or not. Defaults to False.
            use_jenkins (bool, optional): Whether to use Jenkins or not. Defaults to False.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[Runner]: The local runner.
        """

        args: Dict[str, Any] = {
            "simple": simple,
        }
        if use_jenkins:
            args["default_value"] = JenkinsAPIRunner(job_name="autotransform")
        elif use_github:
            args["default_value"] = GithubRunner(
                run_workflow="autotransform.run.yml",
                update_workflow="autotransform.update.yml",
            )

        if prev_config is not None:
            args["previous_value"] = prev_config.remote_runner
        return runner_factory.from_console("remote runner", **args)

    @staticmethod
    def get_repo_override_from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
    ) -> Optional[Repo]:
        """Gets the repo override using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.

        Returns:
            Optional[Repo]: The repo override.
        """

        args: Dict[str, Any] = {
            "simple": simple,
        }
        if prev_config is not None:
            args["previous_value"] = prev_config.repo_override

        return repo_factory.from_console("repo override", **args)

    @staticmethod
    def from_console(
        prev_config: Optional[Config] = None,
        simple: bool = False,
        use_github: Optional[bool] = None,
        use_jenkins: Optional[bool] = None,
        user_config: bool = False,
    ) -> Tuple[Config, bool, bool]:
        """Gets a Config using console inputs.

        Args:
            prev_config (Optional[Config], optional): Previously input Config. Defaults to None.
            simple (bool, optional): Whether to use the simple setup. Defaults to False.
            use_github (bool, optional): Whether to use Github or not. Defaults to None.
            use_jenkins (bool, optional): Whether to use Jenkins or not. Defaults to None.
            user_config (bool, optional): Whether this configuration is for a user level Config.
                Defaults to False.

        Returns:
            Tuple[Config, bool, bool]: The input Config and whether it uses Github and Jenkins.
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

        if use_jenkins:
            jenkins = True
        elif use_jenkins is not None:
            jenkins = False
        else:
            jenkins = choose_yes_or_no("Use Jenkins for this config?")

        if not jenkins:
            jenkins_user = None
            jenkins_token = None
            jenkins_base_url = None
        else:
            jenkins_user = Config.get_jenkins_user_from_console(
                prev_config=prev_config, simple=simple
            )
            jenkins_token = Config.get_jenkins_token_from_console(
                prev_config=prev_config, simple=simple, user_config=user_config
            )
            jenkins_base_url = Config.get_jenkins_base_url_from_console(
                prev_config=prev_config, simple=simple
            )

        return (
            Config(
                github_token=github_token,
                github_base_url=github_base_url,
                jenkins_user=jenkins_user,
                jenkins_token=jenkins_token,
                jenkins_base_url=jenkins_base_url,
                component_directory=Config.get_component_directory_from_console(
                    prev_config=prev_config, simple=simple
                ),
                local_runner=Config.get_local_runner_from_console(
                    prev_config=prev_config, simple=simple
                ),
                anthropic_api_key=Config.get_anthropic_api_key_from_console(
                    prev_config=prev_config,
                    simple=simple,
                ),
                open_ai_api_key=Config.get_open_ai_api_key_from_console(
                    prev_config=prev_config,
                    simple=simple,
                ),
                remote_runner=Config.get_remote_runner_from_console(
                    prev_config=prev_config,
                    use_github=github,
                    use_jenkins=jenkins,
                    simple=simple,
                ),
                repo_override=Config.get_repo_override_from_console(
                    prev_config=prev_config, simple=simple
                ),
            ),
            github,
            jenkins,
        )

    def merge(self, other: Config) -> Config:
        """Merges the Config with another Config. Settings in the other Config will override
        those in this Config.

        Args:
            other (Config): The Config to be merged with.

        Returns:
            Config: The merged Config.
        """

        if (
            len(other.event_notifiers) == 1
            and other.event_notifiers[0].get("name") == EventNotifierName.CONSOLE
        ):
            event_notifiers = self.event_notifiers
        else:
            event_notifiers = other.event_notifiers

        return Config(
            github_token=other.github_token or self.github_token,
            github_base_url=other.github_base_url or self.github_base_url,
            jenkins_user=other.jenkins_user or self.jenkins_user,
            jenkins_token=other.jenkins_token or self.jenkins_token,
            jenkins_base_url=other.jenkins_base_url or self.jenkins_base_url,
            component_directory=other.component_directory or self.component_directory,
            local_runner=other.local_runner or self.local_runner,
            anthropic_api_key=other.anthropic_api_key or self.anthropic_api_key,
            open_ai_api_key=other.open_ai_api_key or self.open_ai_api_key,
            remote_runner=other.remote_runner or self.remote_runner,
            repo_override=other.repo_override or self.repo_override,
            event_notifiers=event_notifiers,
        )
