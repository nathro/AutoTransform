# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Repos from type and param information

Note:
    Imports for custom Repos should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.remote.base import Remote, RemoteBundle
from autotransform.remote.github import GithubRemote
from autotransform.remote.type import RemoteType


class RemoteFactory:
    """The factory class

    Attributes:
        _getters (Dict[RemoteType, Callable[[Mapping[str, Any]], Remote]]): A mapping
            from RemoteType to that remote's from_data function.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[RemoteType, Callable[[Mapping[str, Any]], Remote]] = {
        RemoteType.GITHUB: GithubRemote.from_data,
    }

    @staticmethod
    def get(bundle: RemoteBundle) -> Remote:
        """Simple get method using the _getters attribute

        Args:
            bundle (RepoBundle): The decoded bundle from which to produce a Repo instance

        Returns:
            Repo: The Repo instance of the decoded bundle
        """
        if bundle["type"] in RemoteFactory._getters:
            return RemoteFactory._getters[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_custom_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "REMOTES") and bundle["type"] in module.REMOTES:
                return module.REMOTES[bundle["type"]](bundle["params"])
        raise ValueError(f"No remote found for type {bundle['type']}")
