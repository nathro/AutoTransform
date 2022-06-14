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
from typing import ClassVar, Optional

from autotransform.config.config import Config
from autotransform.config.fetcher import ConfigFetcher
from autotransform.util.package import get_config_dir


class DefaultConfigFetcher(ConfigFetcher):
    """The default configuration fetcher that pulls from the config files. Three possible
    files are used:
     - a file within the AutoTransform package itself, located at autotransform-config/config.json
     - a file within the repo, located at {repo_root}/autotransform/config.json
     - a file relative to the current working directory, located at {cwd}/autotransform/config.json
    Settings from files later in the list will override settings from files earlier in the list. CWD
    configs will have the greatest priority, followed by repo configs, then the overall config.

    Attributes:
        FILE_NAME (ClassVar[str]): The name of the file that stores the Config.
    """

    FILE_NAME: ClassVar[str] = "config.json"

    def get_config(self) -> Config:
        """Fetch the Config.

        Returns:
            Config: The Config for AutoTransform.
        """

        potential_paths = [
            get_config_dir(),
            self.get_repo_config_dir(),
            self.get_cwd_config_dir(),
        ]
        config_paths = [f"{path}/{self.FILE_NAME}" for path in potential_paths if path is not None]
        config = Config()
        for path in config_paths:
            config = config.merge(Config.read(path))
        return config

    @staticmethod
    def get_repo_config_dir() -> Optional[str]:
        """Gets the directory where a repo-specific AutoTransform config file would be located. None
        if git fails. The environment variable AUTO_TRANSFORM_REPO_CONFIG_PATH can be used to set
        the relative path to the config.json file for repo configs.

        Returns:
            Optional[str]: The directory of the repo config file. None if git fails.
        """

        try:
            dir_cmd = ["git", "rev-parse", "--show-toplevel"]
            repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
            return f"{repo_dir}/{DefaultConfigFetcher.get_repo_config_relative_path()}"
        except Exception:  # pylint: disable=broad-except
            return None

    @staticmethod
    def get_repo_config_relative_path() -> str:
        """Gets the relative path used for the repo config directory.

        Returns:
            str: The relative path to the config.
        """

        return os.getenv("AUTO_TRANSFORM_REPO_CONFIG_PATH", "autotransform")

    @staticmethod
    def get_cwd_config_dir() -> str:
        """Gets the directory where an AutoTransform config file would be located relative to the
        current working directory. The environment variable AUTO_TRANSFORM_CWD_CONFIG_PATH can be
        used to set the relative path to the config.json file for CWD configs.

        Returns:
            str: The directory of the cwd config file.
        """

        relative_path = os.getenv("AUTO_TRANSFORM_CWD_CONFIG_PATH", "autotransform")
        cwd = os.getcwd().replace("\\", "/")
        return f"{cwd}/{relative_path}"
