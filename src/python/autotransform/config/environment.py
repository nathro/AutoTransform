# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A config fetcher that utilizes environment variables for storing config settings."""

import json
import os
from typing import Any, Dict, List

from autotransform.config.config import Config
from autotransform.config.default import DefaultConfigFetcher
from autotransform.config.fetcher import ConfigFetcher
from autotransform.event.notifier.console import ConsoleEventNotifier
from autotransform.repo.base import FACTORY as repo_factory
from autotransform.runner.base import FACTORY as runner_factory


class EnvironmentConfigFetcher(ConfigFetcher):  # pylint: disable=too-few-public-methods
    """A ConfigFetcher that utilizes environment variables as configuration storage.
    Environment variable names are of the form AUTO_TRANSFORM_<SETTING> using the settings
    from the Config class. The DefaultConfigFetcher will be used for fallbacks where
    environment variables are not present. Set AUTO_TRANSFORM_CONFIG_USE_FALLBACK to "False"
    if you do not want to use a fallback.
    """

    def get_config(self) -> Config:
        """Fetch the Config.

        Returns:
            Config: The Config for AutoTransform.
        """

        local_runner_json = os.getenv("AUTO_TRANSFORM_LOCAL_RUNNER")
        if local_runner_json is not None:
            local_runner = runner_factory.get_instance(json.loads(local_runner_json))
        else:
            local_runner = None

        remote_runner_json = os.getenv("AUTO_TRANSFORM_REMOTE_RUNNER")
        if remote_runner_json is not None:
            remote_runner = runner_factory.get_instance(json.loads(remote_runner_json))
        else:
            remote_runner = None

        repo_override_json = os.getenv("AUTO_TRANSFORM_REPO_OVERRIDE")
        if repo_override_json is not None:
            repo_override = repo_factory.get_instance(json.loads(repo_override_json))
        else:
            repo_override = None

        event_notifiers_json = os.getenv("AUTO_TRANSFORM_EVENT_NOTIFIERS")
        if event_notifiers_json is None:
            event_notifiers: List[Dict[str, Any]] = [ConsoleEventNotifier().bundle()]
        else:
            event_notifiers = json.loads(event_notifiers_json)

        config = Config(
            github_token=os.getenv("AUTO_TRANSFORM_GITHUB_TOKEN"),
            github_base_url=os.getenv("AUTO_TRANSFORM_GITHUB_BASE_URL"),
            jenkins_user=os.getenv("AUTO_TRANSFORM_JENKINS_USER"),
            jenkins_token=os.getenv("AUTO_TRANSFORM_JENKINS_TOKEN"),
            jenkins_base_url=os.getenv("AUTO_TRANSFORM_JENKINS_BASE_URL"),
            component_directory=os.getenv("AUTO_TRANSFORM_COMPONENT_DIRECTORY"),
            local_runner=local_runner,
            anthropic_api_key=os.getenv("AUTO_TRANSFORM_ANTHROPIC_API_KEY"),
            open_ai_api_key=os.getenv("AUTO_TRANSFORM_OPEN_AI_API_KEY"),
            remote_runner=remote_runner,
            repo_override=repo_override,
            event_notifiers=event_notifiers,
        )

        if os.getenv("AUTO_TRANSFORM_CONFIG_USE_FALLBACK", "true").lower() != "false":
            config = DefaultConfigFetcher().get_config().merge(config)

        return config
