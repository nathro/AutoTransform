# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from abc import ABC, abstractmethod
from typing import Optional


class ConfigFetcher(ABC):
    @abstractmethod
    def get_github_token(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_github_username(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_github_password(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_github_base_url(self) -> Optional[str]:
        pass
