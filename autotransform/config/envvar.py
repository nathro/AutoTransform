# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A config fetcher that utilizes environment variables for storing config settings."""

import os
from typing import List, Optional

from autotransform.config.fetcher import ConfigFetcher


class EnvironmentVariableConfigFetcher(ConfigFetcher):
    """An object representing the API needed for config fetching."""

    def get_github_token(self) -> Optional[str]:
        """Fetch the github token from configuration

        Returns:
            Optional[str]: The github token
        """
        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN")

    def get_github_username(self) -> Optional[str]:
        """Fetch the github username from configuration

        Returns:
            Optional[str]: The github username
        """
        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_USERNAME")

    def get_github_password(self) -> Optional[str]:
        """Fetch the github password from configuration

        Returns:
            Optional[str]: The github password
        """
        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_PASSWORD")

    def get_github_base_url(self) -> Optional[str]:
        """Fetch the github base URL from configuration

        Returns:
            Optional[str]: The github base URL
        """
        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_BASE_URL")

    def get_custom_component_imports(self) -> List[str]:
        """The modules containing the custom components to use: see autotransform.thirdparty.example

        Returns:
            List[str]: A list of the modules containing custom components that are not part base
                AutoTransform
        """
        module_list = os.getenv("AUTO_TRANSFORM_IMPORTS_CUSTOM_COMPONENTS")
        if module_list is None or module_list == "":
            return []
        return [module.strip() for module in module_list.split(",")]

    def get_remote(self) -> Optional[str]:
        """Gets the JSON encoded Remote component to use

        Returns:
            str: The JSON encoded Remote component to use
        """
        return os.getenv("AUTO_TRANSFORM_REMOTE_RUNNER")
