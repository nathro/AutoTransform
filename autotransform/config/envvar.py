# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A config fetcher that utilizes environment variables for storing config settings."""

import os
from typing import List, Optional

from autotransform.config.fetcher import ConfigFetcher


class EnvironmentVariableConfigFetcher(ConfigFetcher):
    """A ConfigFetcher that utilizes environment variables as configuration storage.
    Environment variable names are of the form AUTO_TRANSFORM_<SECTION>_<SETTING>, using
    the sections and settings from autotransform/config/sample_config.ini"""

    def get_credentials_github_token(self) -> Optional[str]:
        """Fetch the github token from AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN.

        Returns:
            Optional[str]: The github token,
        """

        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN")

    def get_credentials_github_username(self) -> Optional[str]:
        """Fetch the github username from AUTO_TRANSFORM_CREDENTIALS_GITHUB_USERNAME.

        Returns:
            Optional[str]: The github username.
        """

        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_USERNAME")

    def get_credentials_github_password(self) -> Optional[str]:
        """Fetch the github password from AUTO_TRANSFORM_CREDENTIALS_GITHUB_PASSWORD.

        Returns:
            Optional[str]: The github password.
        """

        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_PASSWORD")

    def get_credentials_github_base_url(self) -> Optional[str]:
        """Fetch the github base URL from AUTO_TRANSFORM_CREDENTIALS_GITHUB_BASE_URL.

        Returns:
            Optional[str]: The github base URL.
        """

        return os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_BASE_URL")

    def get_imports_components(self) -> List[str]:
        """The modules containing the custom components to use: see
        autotransform.thirdparty.components from AUTO_TRANSFORM_CREDENTIALS_IMPORTS_COMPONENTS.

        Returns:
            List[str]: A list of the modules containing custom components that are not part base
                AutoTransform.
        """

        module_list = os.getenv("AUTO_TRANSFORM_IMPORTS_COMPONENTS")
        if module_list is None or module_list == "":
            return []
        return [module.strip() for module in module_list.split(",")]

    def get_runner_local(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for local runs.

        Returns:
            str: The JSON encoded Runner component to use for local runs.
        """

        return os.getenv("AUTO_TRANSFORM_RUNNER_LOCAL")

    def get_runner_remote(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for remote runs.

        Returns:
            str: The JSON encoded Runner component to use for remote runs.
        """

        return os.getenv("AUTO_TRANSFORM_RUNNER_REMOTE")
