# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A ConfigFetcher that uses config files for configuration."""

import os
import subprocess
from configparser import ConfigParser
from typing import List, Optional

from autotransform.config.fetcher import ConfigFetcher
from autotransform.util.package import get_config_dir


class DefaultConfigFetcher(ConfigFetcher):
    """The default configuration fetcher that pulls from the config files. Three possible
    files are used:
     - a file within the AutoTransform package itself, located at autotransform/config/config.ini
     - a file within the repo, located at {repo_root}/autotransform/config.ini
     - a file relative to the current working directory, located at {cwd}/autotransform/config.ini
    Settings from files later in the list will override settings from files earlier in the list. CWD
    configs will have the greatest priority, followed by repo configs, then the overall config.

    Attributes:
        config (ConfigParser): The parser created from the config file.
    """

    CONFIG_NAME: str = "config.ini"

    config: ConfigParser

    def __init__(self):
        """A simple constructor that parses the default config files."""

        config = ConfigParser()
        config_paths = [
            get_config_dir(),
            self.get_repo_config_dir(),
            self.get_cwd_config_dir(),
        ]
        config_paths = [f"{path}/{self.CONFIG_NAME}" for path in config_paths if path is not None]
        config.read(config_paths)
        self.config = config

    @staticmethod
    def get_repo_config_dir() -> Optional[str]:
        """Gets the directory where a repo-specific AutoTransform config file would be located. None
        if git fails. The environment variable AUTO_TRANSFORM_REPO_CONFIG_PATH can be used to set
        the relative path to the config.ini file for repo configs.

        Returns:
            Optional[str]: The directory of the repo config file. None if git fails.
        """

        try:
            dir_cmd = ["git", "rev-parse", "--show-toplevel"]
            repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
            relative_path = os.getenv("AUTO_TRANSFORM_REPO_CONFIG_PATH", "autotransform")
            return f"{repo_dir}/{relative_path}"
        except Exception:  # pylint: disable=broad-except
            return None

    @staticmethod
    def get_cwd_config_dir() -> str:
        """Gets the directory where an AutoTransform config file would be located relative to the
        current working directory. The environment variable AUTO_TRANSFORM_CWD_CONFIG_PATH can be
        used to set the relative path to the config.ini file for CWD configs.

        Returns:
            str: The directory of the cwd config file.
        """

        relative_path = os.getenv("AUTO_TRANSFORM_CWD_CONFIG_PATH", "autotransform")
        cwd = os.getcwd().replace("\\", "/")
        return f"{cwd}/{relative_path}"

    def get_credentials_github_token(self) -> Optional[str]:
        """Pulls the github authentication token from the config file.

        Returns:
            Optional[str]: The github authentication token if present.
        """

        if "CREDENTIALS" not in self.config:
            return None
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_token", None)

    def get_credentials_github_base_url(self) -> Optional[str]:
        """Pulls the github base URL from the config file.

        Returns:
            Optional[str]: The github base URL if present.
        """

        if "CREDENTIALS" not in self.config:
            return None
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_base_url", None)

    def get_imports_components(self) -> List[str]:
        """The modules containing the custom components to use: see
        autotransform.thirdparty.components.

        Returns:
            List[str]: A list of the modules containing custom components that are not part base
                AutoTransform.
        """

        if "IMPORTS" not in self.config:
            return []
        imports = self.config["IMPORTS"]
        module_list = imports.get("components", None)
        if module_list is None:
            return []
        return [module.strip() for module in module_list.split(",")]

    def get_runner_local(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for local runs.

        Returns:
            str: The JSON encoded Runner component to use for local runs.
        """

        if "RUNNER" not in self.config:
            return None
        runner = self.config["RUNNER"]
        return runner.get("local", None)

    def get_runner_remote(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for remote runs.

        Returns:
            str: The JSON encoded Runner component to use for remote runs.
        """

        if "RUNNER" not in self.config:
            return None
        runner = self.config["RUNNER"]
        return runner.get("remote", None)
