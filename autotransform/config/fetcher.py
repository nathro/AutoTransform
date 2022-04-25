# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A base class for configuration fetching. Defines the API for fetching configuration
so that different components can be used that store configuration in different ways."""

from abc import ABC, abstractmethod
from typing import List, Optional


class ConfigFetcher(ABC):
    """An object representing the API needed for config fetching."""

    @abstractmethod
    def get_credentials_github_token(self) -> Optional[str]:
        """Fetch the github token from configuration.

        Returns:
            Optional[str]: The github token.
        """

    @abstractmethod
    def get_credentials_github_username(self) -> Optional[str]:
        """Fetch the github username from configuration.

        Returns:
            Optional[str]: The github username.
        """

    @abstractmethod
    def get_credentials_github_password(self) -> Optional[str]:
        """Fetch the github password from configuration.

        Returns:
            Optional[str]: The github password.
        """

    @abstractmethod
    def get_credentials_github_base_url(self) -> Optional[str]:
        """Fetch the github base URL from configuration.

        Returns:
            Optional[str]: The github base URL.
        """

    @abstractmethod
    def get_imports_components(self) -> List[str]:
        """The modules containing the custom components to use: see
        autotransform.thirdparty.components.

        Returns:
            List[str]: A list of the modules containing custom components that are not part base
                AutoTransform.
        """

    @abstractmethod
    def get_runner_local(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for local runs.

        Returns:
            str: The JSON encoded Runner component to use for local runs.
        """

    @abstractmethod
    def get_runner_remote(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for remote runs.

        Returns:
            str: The JSON encoded Runner component to use for remote runs.
        """
