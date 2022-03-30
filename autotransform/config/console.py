# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A ConfigFetcher that asks for input from the user."""

from getpass import getpass
from typing import Dict, List, Optional

from autotransform.config.fetcher import ConfigFetcher


class ConsoleConfigFetcher(ConfigFetcher):
    """A config that uses user input as the source.

    Attributes:
        config (Dict[str, Optional[str]]): A cache of all requested config information
            from the current run.
    """

    config: Dict[str, Optional[str]]

    def __init__(self):
        """A simple constructor to initialize the cache."""
        self.config = {}

    def get_github_token(self) -> Optional[str]:
        """Requests a github authentication token from the user and caches it.

        Returns:
            Optional[str]: The provided token or None if not provided
        """
        if "github_token" in self.config:
            return self.config["github_token"]
        token: Optional[str] = getpass("Github Token(empty to use username and password): ")
        if token == "":
            token = None
        self.config["github_token"] = token
        return token

    def get_github_username(self) -> Optional[str]:
        """Requests a github username from the user and caches it.

        Returns:
            Optional[str]: The provided username or None if not provided
        """
        if "github_username" in self.config:
            return self.config["github_username"]
        username: Optional[str] = input("Github Username: ")
        if username == "":
            username = None
        self.config["github_username"] = username
        return username

    def get_github_password(self) -> Optional[str]:
        """Requests a github password from the user and caches it.

        Returns:
            Optional[str]: The provided password or None if not provided
        """
        if "github_password" in self.config:
            return self.config["github_password"]
        password: Optional[str] = getpass("Github Password: ")
        if password == "":
            password = None
        self.config["github_password"] = password
        return password

    def get_github_base_url(self) -> Optional[str]:
        """Requests a github base URL for enterprise usecase and caches it.

        Returns:
            Optional[str]: The provided base URL or None if not provided
        """
        if "github_base_url" in self.config:
            return self.config["github_base_url"]
        base_url: Optional[str] = input("Github Base URL(empty for default): ")
        if base_url == "":
            base_url = None
        self.config["github_base_url"] = base_url
        return base_url

    def get_custom_component_imports(self) -> List[str]:
        """The modules containing the custom components to use: see autotransform.thirdparty.example

        Returns:
            List[str]: A list of the modules containing custom components that are not part base
                AutoTransform
        """
        component_module_string: str = input(
            "Please provide a command separated list of custom component modules to import: "
        )
        if component_module_string == "":
            return []
        return [module.strip() for module in component_module_string.split(",")]
