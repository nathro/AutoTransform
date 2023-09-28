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

from autotransform.config.config import Config
from autotransform.config.default import DefaultConfigFetcher
from autotransform.config.fetcher import ConfigFetcher
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

        local_runner = self._get_instance_from_env("AUTO_TRANSFORM_LOCAL_RUNNER")
        remote_runner = self._get_instance_from_env("AUTO_TRANSFORM_REMOTE_RUNNER")
        repo_override = self._get_instance_from_env("AUTO_TRANSFORM_REPO_OVERRIDE")

        config = Config(
            github_token=os.getenv("AUTO_TRANSFORM_GITHUB_TOKEN"),
            github_base_url=os.getenv("AUTO_TRANSFORM_GITHUB_BASE_URL"),
            jenkins_user=os.getenv("AUTO_TRANSFORM_JENKINS_USER"),
            jenkins_token=os.getenv("AUTO_TRANSFORM_JENKINS_TOKEN"),
            jenkins_base_url=os.getenv("AUTO_TRANSFORM_JENKINS_BASE_URL"),
            component_directory=os.getenv("AUTO_TRANSFORM_COMPONENT_DIRECTORY"),
            local_runner=local_runner,
            open_ai_api_key=os.getenv("AUTO_TRANSFORM_OPEN_AI_API_KEY"),
            remote_runner=remote_runner,
            repo_override=repo_override,
        )

        if os.getenv("AUTO_TRANSFORM_CONFIG_USE_FALLBACK", "true").lower() != "false":
            config = DefaultConfigFetcher().get_config().merge(config)

        return config

    @staticmethod
    def _get_instance_from_env(env_var: str):
        """Fetch the instance from environment variable.

        Args:
            env_var (str): The environment variable.

        Returns:
            Instance or None: The instance or None if the environment variable is not set.
        """
        instance_json = os.getenv(env_var)
        return runner_factory.get_instance(json.loads(instance_json)) if instance_json else None
