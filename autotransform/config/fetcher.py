# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A base class for configuration fetching."""

from abc import ABC, abstractmethod
from typing import Optional


class ConfigFetcher(ABC):
    @abstractmethod
    def get_github_token(self) -> Optional[str]:
        """Fetch the github token from configuration

        Returns:
            Optional[str]: The github token
        """

    @abstractmethod
    def get_github_username(self) -> Optional[str]:
        """Fetch the github username from configuration

        Returns:
            Optional[str]: The github username
        """

    @abstractmethod
    def get_github_password(self) -> Optional[str]:
        """Fetch the github password from configuration

        Returns:
            Optional[str]: The github password
        """

    @abstractmethod
    def get_github_base_url(self) -> Optional[str]:
        """Fetch the github base URL from configuration

        Returns:
            Optional[str]: The github base URL
        """
