# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.repo.base import Repo, RepoBundle
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.repo.type import RepoType

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class RepoFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[RepoType, Callable[[Mapping[str, Any]], Repo]] = {
        RepoType.GIT: GitRepo.from_data,
        RepoType.GITHUB: GithubRepo.from_data,
        # Section reserved for custom getters to reduce merge conflicts
        # BEGIN CUSTOM GETTERS
        # END CUSTOM GETTERS
    }

    @staticmethod
    def get(repo: RepoBundle) -> Repo:
        return RepoFactory._getters[repo["type"]](repo["params"])
