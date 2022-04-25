# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Repos from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.repo.base import Repo, RepoBundle
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.repo.type import RepoType


class RepoFactory:
    """The factory class for Repos. Maps a type to a Repo.

    Attributes:
        _map (Dict[RepoType, Callable[[Mapping[str, Any]], Repo]]): A mapping from
            RepoType to the from_data function of the appropriate Repo.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[RepoType, Callable[[Mapping[str, Any]], Repo]] = {
        RepoType.GIT: GitRepo.from_data,
        RepoType.GITHUB: GithubRepo.from_data,
    }

    @staticmethod
    def get(bundle: RepoBundle) -> Repo:
        """Simple get method using the _map attribute.

        Args:
            bundle (RepoBundle): The bundled Repo type and params.

        Returns:
            Repo: An instance of the associated Repo.
        """

        if bundle["type"] in RepoFactory._map:
            return RepoFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "REPOS") and bundle["type"] in module.REPOS:
                return module.REPOS[bundle["type"]](bundle["params"])
        raise ValueError(f"No repo found for type {bundle['type']}")
