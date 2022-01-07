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

from typing import Any, Callable, Dict, Mapping

from autotransform.repo.base import Repo, RepoBundle
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.repo.type import RepoType

# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class RepoFactory:
    """The factory class

    Attributes:
        _getters (Dict[RepoType, Callable[[Mapping[str, Any]], Repo]]): A mapping
            from RepoType to that repos's from_data function.

    Note:
        Custom repos should have their getters placed in the CUSTOM REPOS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[RepoType, Callable[[Mapping[str, Any]], Repo]] = {
        RepoType.GIT: GitRepo.from_data,
        RepoType.GITHUB: GithubRepo.from_data,
        # BEGIN CUSTOM REPOS
        # END CUSTOM REPOS
    }

    @staticmethod
    def get(bundle: RepoBundle) -> Repo:
        """Simple get method using the _getters attribute

        Args:
            bundle (RepoBundle): The decoded bundle from which to produce a Repo instance

        Returns:
            Repo: The Repo instance of the decoded bundle
        """
        return RepoFactory._getters[bundle["type"]](bundle["params"])
