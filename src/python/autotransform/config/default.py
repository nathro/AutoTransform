# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A ConfigFetcher that uses config files for configuration."""

from autotransform.config import CONFIG_FILE_NAME, get_cwd_config_dir, get_repo_config_dir
from autotransform.config.config import Config
from autotransform.config.fetcher import ConfigFetcher
from autotransform.util.package import get_config_dir


# pylint: disable=too-few-public-methods
class DefaultConfigFetcher(ConfigFetcher):
    """The default configuration fetcher that pulls from the config files. Three possible
    files are used:
     - a file within the AutoTransform package itself, located at autotransform-config/config.json
     - a file within the repo, located at {repo_root}/autotransform/config.json
     - a file relative to the current working directory, located at {cwd}/autotransform/config.json
    Settings from files later in the list will override settings from files earlier in the list. CWD
    configs will have the greatest priority, followed by repo configs, then the overall config.

    """

    def get_config(self) -> Config:
        """Fetch the Config.

        Returns:
            Config: The Config for AutoTransform.
        """

        potential_paths = [
            get_config_dir(),
            get_repo_config_dir(),
            get_cwd_config_dir(),
        ]
        config_paths = [
            f"{path}/{CONFIG_FILE_NAME}" for path in potential_paths if path is not None
        ]
        config = Config()
        for path in config_paths:
            config = config.merge(Config.read(path))
        return config
