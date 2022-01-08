# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pathlib
from configparser import ConfigParser
from typing import Optional

from autotransform.config.fetcher import ConfigFetcher


class DefaultConfigFetcher(ConfigFetcher):
    """The default configuration fetcher that pulls from the config file.

    Attributes:
        config ([ConfigParser]): The parser created from the config file
    """

    CONFIG_LOCATION: str = "/data/config.ini"

    config: ConfigParser

    def __init__(self):
        """A simple constructor that parses the default config file"""
        config_path: str = (
            str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/")
            + "/data/config.ini"
        )
        config = ConfigParser()
        config.read(config_path)
        self.config = config

    def get_github_token(self) -> Optional[str]:
        """Pulls the github authentication token from the config file

        Returns:
            Optional[str]: The github authentication token if present
        """
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_token", None)

    def get_github_username(self) -> Optional[str]:
        """Pulls the github username from the config file

        Returns:
            Optional[str]: The github username if present
        """
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_username", None)

    def get_github_password(self) -> Optional[str]:
        """Pulls the github password from the config file

        Returns:
            Optional[str]: The github password if present
        """
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_password", None)

    def get_github_base_url(self) -> Optional[str]:
        """Pulls the github base URL from the config file

        Returns:
            Optional[str]: The github base URL if present
        """
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_base_url", None)
