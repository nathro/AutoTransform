# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A ConfigFetcher that uses the data/config.ini file to supply configuration."""

import pathlib
from configparser import ConfigParser
from typing import List, Optional

from autotransform.config.fetcher import ConfigFetcher


class DefaultConfigFetcher(ConfigFetcher):
    """The default configuration fetcher that pulls from the config file.
    See the sample config in /data/sample_config.ini.

    Attributes:
        config (ConfigParser): The parser created from the config file.
    """

    CONFIG_LOCATION: str = "/data/config.ini"

    config: ConfigParser

    def __init__(self):
        """A simple constructor that parses the default config file."""

        config = ConfigParser()
        config.read(self.get_config_path())
        self.config = config

    @staticmethod
    def get_config_path() -> str:
        """Gets the path where the config file is located.

        Returns:
            str: The path to the config file.
        """

        return (
            str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
            + "/data/config.ini"
        )

    def get_credentials_github_token(self) -> Optional[str]:
        """Pulls the github authentication token from the config file.

        Returns:
            Optional[str]: The github authentication token if present.
        """

        if "CREDENTIALS" not in self.config:
            return None
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_token", None)

    def get_credentials_github_username(self) -> Optional[str]:
        """Pulls the github username from the config file.

        Returns:
            Optional[str]: The github username if present.
        """

        if "CREDENTIALS" not in self.config:
            return None
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_username", None)

    def get_credentials_github_password(self) -> Optional[str]:
        """Pulls the github password from the config file.

        Returns:
            Optional[str]: The github password if present.
        """

        if "CREDENTIALS" not in self.config:
            return None
        credentials = self.config["CREDENTIALS"]
        return credentials.get("github_password", None)

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
