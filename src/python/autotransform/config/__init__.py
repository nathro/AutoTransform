# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides configuration to AutoTransform. By default this configuration is pulled from
config files. The configuration fetcher used can be overridden using the AUTO_TRANSFORM_CONFIG
environment variable. This can support different methods of configuration, such as environment
variables or a custom approach where the environment variable is set to
"{'class_name': <A ConfigFetcher Class>, 'module': <The module where the class is located>}".
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
from functools import cache
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from autotransform.config.config import Config

CONFIG_FILE_NAME = "config.json"


def get_repo_config_relative_path() -> str:
    """Gets the relative path used for the repo config directory.

    Returns:
        str: The relative path to the config.
    """

    return os.getenv("AUTO_TRANSFORM_REPO_CONFIG_PATH", "autotransform")


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
        return f"{repo_dir}/{get_repo_config_relative_path()}"
    except Exception:  # pylint: disable=broad-except
        return None


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


@cache
def get_config() -> Config:
    """Gets the Config for AutoTransform.

    Returns:
        Config: The cached Config.
    """

    # pylint: disable=import-outside-toplevel
    from autotransform.config.default import DefaultConfigFetcher
    from autotransform.config.environment import EnvironmentConfigFetcher
    from autotransform.config.fetcher import ConfigFetcher, ConfigFetcherName

    fetcher_to_use = os.getenv("AUTO_TRANSFORM_CONFIG")

    fetchers: Dict[str, ConfigFetcher] = {
        ConfigFetcherName.DEFAULT: DefaultConfigFetcher(),
        ConfigFetcherName.ENVIRONMENT: EnvironmentConfigFetcher(),
    }

    if fetcher_to_use is not None:
        if fetcher_to_use in fetchers:
            fetcher: ConfigFetcher = fetchers[fetcher_to_use]
        else:
            try:
                fetcher_info = json.loads(fetcher_to_use)
                module = importlib.import_module(fetcher_info["module"])
                fetcher = getattr(module, fetcher_info["class_name"]).from_data(
                    fetcher_info.get("data", {})
                )
                assert isinstance(fetcher, ConfigFetcher)
            except Exception:  # pylint: disable=broad-except
                fetcher = DefaultConfigFetcher()
    else:
        fetcher = DefaultConfigFetcher()

    return fetcher.get_config()
